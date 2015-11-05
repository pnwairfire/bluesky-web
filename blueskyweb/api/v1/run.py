"""bluesky.web.api.v1.run"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import io
import json
import logging
import uuid
import tornado.web

#from bluesky.web.lib.auth import b_auth
from bluesky import modules, models, process
from bluesky.exceptions import BlueSkyImportError, BlueSkyModuleError

# TODO: import vs call executable?
from bsslib.scheduling.scheduler.bsp.runs import BspRunScheduler

class RunExecuter(tornado.web.RequestHandler):
    # def _bad_request(self, msg):
    #     self.set_status(400)
    #     self.write({"error": msg})

    def _must_run_asynchronously(self, data):
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
                if self._must_run_asynchronously(data):
                    run_id = str(uuid.uuid1())
                    if "dispersion" in data['modules']:
                        data['config'] = data.get('config', {})
                        data['config']['dispersion'] =  data['config'].get('dispersion', {})
                        data['config']['dispersion']['hysplit'] = data['config']['dispersion'].get('hysplit', {})
                        data['config']['dispersion']['hysplit']['run_id'] = run_id
                    else:
                        data['dispersion'] = data.get('dispersion', {})
                        data['dispersion']['output'] =  data['config'].get('output', {})
                        data['dispersion']['output']['run_id'] = run_id

                    # TODO: determine appropriate queue from met domain
                    queue_name = 'all-met'
                    # TODO: import vs call bss-scheduler?
                    BspRunScheduler().schedule(queue_name, data)
                    self.write({"run_id": run_id})
                else:
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
                logging.error('Exception: {}'.format(e))
                self.set_status(500)



## ***
## *** TODO: REPLACE DUMMY DATA WITH REAL!!!
## ***
## *** Will need to add configuration options to web service to point
## *** to source of data (e.g. url of mongodb containing the data vs.
## *** root url or path to crawl for data given run id vs. something else...)
## ***

class RunStatus(tornado.web.RequestHandler):

    def get(self, run_id):
        self.write({
            "complete": False,
            "percent": 90.0,
            "failed": False,
            "message": "This is dummy data",
            "IS_DUMMY_DATA": True
        })

class RunOutput(tornado.web.RequestHandler):

    def get(self, run_id):
        self.write({
           "output": {
               "directory": "http://smoke.airfire.org/bluesky-daily/output/standard/PNW-4km/2015082800/",
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
