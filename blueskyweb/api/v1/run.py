"""bluesky.web.api.v1.run"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import copy
import io
import json
import logging
import os
import uuid
import tornado.web
import traceback

#from bluesky.web.lib.auth import b_auth
from bluesky import modules, models, process
from bluesky.exceptions import BlueSkyImportError, BlueSkyModuleError

# TODO: import vs call executable?
from bsslib.scheduling.schedulers.bsp.runs import BspRunScheduler

# TODO: not sure where is the best place to define this...maybe it should be
#  defined in bsslib?...or let it be defined as env var
# QUEUES = {
#     'DRI6km': 'dri',
#     'DRI2km': 'dri',
#     ''
# }

EXPORT_CONFIGURATIONS = {
    "localsave": {
        "dest_dir": (os.environ.get('BSPWEB_EXPORT_LOCALSAVE_DEST_DIR')
            or "/bluesky/playground-output/")  # TODO: fill in appropriate default
    },
    "upload": {
        "scp": {
            "user": os.environ.get('BSPWEB_EXPORT_UPLOAD_SCP_USER') or "bluesky",
            # host will be set to hostname in api request if not defined in env var
            "host": os.environ.get('BSPWEB_EXPORT_UPLOAD_SCP_HOST'),
            "port": os.environ.get('BSPWEB_EXPORT_UPLOAD_SCP_PORT') or 22,
            "dest_dir": (os.environ.get('BSPWEB_EXPORT_UPLOAD_SCP_DEST_DIR')
                or "/bluesky/playground-output/")
        }
    }
}
EXPORT_MODE = (os.environ.get('BSPWEB_EXPORT_MODE') or 'upload').lower()
if EXPORT_MODE not in EXPORT_CONFIGURATIONS:
    raise ValueError("Invalid value for BSPWEB_EXPORT_MODE - {}. Must be one"
        " of the following: {}".format(EXPORT_MODE,
        ', '.join(EXPORT_CONFIGURATIONS.keys())))
EXPORT_CONFIGURATION = EXPORT_CONFIGURATIONS[EXPORT_MODE]

# TODO: require host to be specified if uploading?
# if EXPORT_MODE == "upload" and not EXPORT_CONFIGURATION['scp']['host']:
#     raise ValueError("Specify scp host for upload")

class RunHandlerBase(tornado.web.RequestHandler):

    def _get_host(self, data):
        # TODO: set it to hostname in request?
        pass

class RunExecuter(RunHandlerBase):
    # def _bad_request(self, msg):
    #     self.set_status(400)
    #     self.write({"error": msg})

    def _run_asynchronously(self, data):
      # TODO: check if request query string contains 'run_asynch';
      # if so, return True;  this is probably only for development
      if self.get_query_argument('run_asynch', default=None) is not None:
          return True

      # if computing hysplit dispersion, run asynch
      if "dispersion" in data['modules']:
          d_config = data.get('config', {}).get('dispersion', {})
          # default model is hysplit
          if not d_config.get('module') or d_config['module'] == 'hysplit':
              return True

      # Also asynch if *visualizing* hysplit dispersion
      if "visualization" in data['modules']:
          v_config = data.get('config',{}).get('visualization', {})
          # default target is hysplit
          if not v_config.get('target') or v_config['target'] == 'dispersion':
              if data.get('dispersion', {}).get('model') == 'hysplit':
                  return True

      # Otherwise, run in process
      return False

    def _configure_export(self, data):
        # only allow email export to be specified nin request
        if 'export' in data['modules']:
            if set(data.get('config', {}).get('export', {}).get('modes', [])) - set(['email']):
                self.set_status(400, "Bad request: only 'email' export mode allowed")
                return
            # Make sure 'export' module is executed only once, at that it
            # happens at the end
            data['modules'] = [e for e in data['modules'] if e != 'export'] + ['export']
        else:
            data['modules'].append('export')

        # add upload export, configured to scp
        # Note: we need to use 'upload' export, esince we don't know where bsp workers
        #  will be run.  The bsp code should (or at least will) dynamically switch
        #  to saving locally instead of scp'ing if the hostname of the server it's running
        #  on is the sam
        data['config'] = data.get('config', {})
        data['config']['export'] = data['config'].get('export', {})
        data['config']['export']['modes'] = data['config']['export'].get('modes', [])
        data['config']['export']['modes'].append(EXPORT_MODE)
        data['config']['export']['extra_exports'] = ["dispersion", "visualization"]
        # TODO: no real need to copy.deepcopy
        data['config']['export'][EXPORT_MODE] = copy.deepcopy(EXPORT_CONFIGURATION)
        if EXPORT_MODE == 'upload':
            if not data['config']['export']['upload']['scp']['host']:
                data['config']['export']['upload']['scp']['host'] = self._get_host()
        elif EXPORT_MODE == 'localsave':
            # TODO: set any values?
            pass

    def post(self):
        if not self.request.body:
            self.set_status(400, 'Bad request: empty post data')
            return

        data = json.loads(self.request.body)
        if "modules" not in data:
            self.set_status(400, "Bad request: 'modules' not specified")
        elif "fire_information" not in data:
            self.set_status(400, "Bad request: 'fire_information' not specified")
        else:
            try:
                if self._run_asynchronously(data):
                    if not data.get('run_id'):
                        data['run_id'] = str(uuid.uuid1())

                    self._configure_export(data)

                    # TODO: determine appropriate queue from met domain
                    queue_name = 'all-met'

                    # TODO: import vs call bss-scheduler?
                    BspRunScheduler().schedule(queue_name, data)
                    self.write({"run_id": data['run_id']})
                else:
                    # Don't allow any export when run synchrounously
                    if 'export' in data['modules']:
                        self.set_status(400, 'Bad request: empty post data')
                        return

                    fires_manager = models.fires.FiresManager()
                    try:
                        fires_manager.load(data)
                        fires_manager.run()
                    except BlueSkyModuleError, e:
                        # Exception was caught while running modules and added to
                        # fires_manager's meta data, and so will be included in
                        # the output data
                        # TODO: should module error not be reflected in http error status?
                        pass
                    except BlueSkyImportError, e:
                        self.set_status(400, "Bad request: {}".format(e.message))
                    except Exception, e:
                        logging.error('Exception: {}'.format(e))
                        self.set_status(500)

                    # If you pass a dict into self.write, it will dump it to json and set
                    # content-type to json;  we need to specify a json encoder, though, so
                    # we'll manaually set the header adn dump the json
                    self.set_header('Content-Type', 'application/json') #; charset=UTF-8')
                    fires_manager.dumps(output_stream=self)
            except Exception, e:
                # IF exceptions aren't caught, the traceback is returned as
                # the response body
                logging.debug(traceback.format_exc())
                logging.error('Exception: {}'.format(e))
                self.set_status(500)



## ***
## *** TODO: REPLACE DUMMY DATA WITH REAL!!!
## ***
## *** Will need to add configuration options to web service to point
## *** to source of data (e.g. url of mongodb containing the data vs.
## *** root url or path to crawl for data given run id vs. something else...)
## ***

class RunStatus(RunHandlerBase):

    def get(self, run_id):
        # TODO: Look at EXPORT_MODE and EXPORT_CONFIGURATION to decide where
        # to look for exported output
        self.write({
            "complete": False,
            "percent": 90.0,
            "failed": False,
            "message": "This is dummy data",
            "IS_DUMMY_DATA": True
        })

class RunOutput(RunHandlerBase):

    def get(self, run_id):
        # TODO: Look at EXPORT_MODE and EXPORT_CONFIGURATION to decide where
        # to look for exported output
        self.write({
           "output": {
               "root_url": "http://smoke.airfire.org/bluesky-daily/output/standard/PNW-4km/2015082800/",
               "images": {
                   "hourly": [
                       "images/hourly/1RedColorBar/hourly_201508280000.png",
                       "images/hourly/1RedColorBar/hourly_201508280100.png",
                       "images/hourly/1RedColorBar/hourly_201508280200.png",
                       "images/hourly/1RedColorBar/hourly_201508280300.png",
                       "images/hourly/1RedColorBar/hourly_201508280400.png",
                       "images/hourly/1RedColorBar/hourly_201508280500.png",
                       "images/hourly/1RedColorBar/hourly_201508280600.png"
                   ],
                   "daily": {
                       "average": [
                           "images/daily_average/1RedColorBar/daily_average_20150828.png",
                            "images/daily_average/1RedColorBar/daily_average_20150829.png"
                       ],
                       "maximum": [
                            "images/daily_average/1RedColorBar/daily_maximum_20150828.png",
                            "images/daily_average/1RedColorBar/daily_maximum_20150829.png"
                       ],
                   }
               },
               "netCDF": "data/ smoke_dispersion.nc",
               "kmz": "smoke_dispersion.kmz",
               "fireLocations": "data/fire_locations.csv",
               "fireEvents": "data/fire_events.csv",
               "fireEmissions": "data/fire_emissions.csv"
           }
        })
