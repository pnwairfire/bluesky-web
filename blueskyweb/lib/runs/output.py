"""blueskyweb.lib.runs.output"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import abc

from bluesky.marshal import Blueskyv4_0To4_1
from bluesky.models import fires

##
## Utilities for working with remote output
##

class remote_open(object):
    """Context manager that clones opens remote file and closes it on exit
    """

    def __init__(self, url):
        self.url = url

    def __enter__(self):
        self.f = urllib.request.urlopen(self.url)
        return self.f

    def __exit__(self, type, value, traceback):
        self.f.close()

def remote_exists(url):
    return requests.head(url).status_code != 404

# def get_output_server_info(run_id):
#     output_server_info = {} # TODO: Get info from mongodb
#     return output_server_info

# def get_output_url(run_id):
#     return "{}{}".format(get_output_root_url(run_id), url_root_dir)


##
## Post processing of for older version of API
##

class BlueskyProcessorBase(object, metaclass=abc.ABCMeta):

    def __init__(self, output_stream):
        self.output_stream = output_stream

    def write(self, data):
        if hasattr(data, 'lower'):
            data = json.loads(data)

        data = self._process(data)
        self.output_stream.write(data)


    @abc.abstractmethod
    def _process(self, data):
        pass


class BlueskyV1OutputProcessor(object):

    def _process(self, data)
        # covnerts data from v4.1 to v1 output structure

        if data.get('fires'):
            data['fire_information'] = [
                self.convert_fire(fires.Fire(f)) for f in data['fires']
            ]

        return data

    def convert_fire(self, fire):
        """Converts each location into a growth object

        It's easier to just create a separate growth object out of
        each active area, rather than group active areas by day
        """
        growth = []
        for aa in fire.active_areas:
            g = self.convert_active_area(aa)
            if g:
                growth.append(g)

        if growth:
            fire['growth'] = growth

        return fire

    def convert_active_area(self, aa):
        g = {
            "start": aa['start'],  # WILL BE FILLED IN
            "end": aa['end'],  # WILL BE FILLED IN
            "location": {
                "ecoregion": aa['ecoregion'],
                "utc_offset": aa['utc_offset']
            }
        }

        if aa.get('specified_points'):
            g['location']['geojson'] = {
                "type": "MultiPoint",
                "coordinates": [
                    [sp['lng'], s['lat']]
                        for sp in aa['specified_points']
                ]
            }
            g['location']['area'] = sum([sp['area']
                for sp in aa['specified_points']])

        elif aa.get('perimeter'):
            g['location']['geojson'] = {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        aa['perimeter']['polygon']
                    ]
                ]
            }
            g['location']['area'] = aa['perimeter']['area']

        else:
            return None

        return g

class BlueskyV4_1OutputProcessor(object):

    def _process(self, data)
        # covnerts older output data from v1 to v4.1 output structure
        if data.get('fire_information'):
            data['fires'] = Blueskyv4_0To4_1().marshal(
                data.pop('fire_information'))

        return data


def apply_output_processor(api_version, output_stream):
    if api_version = '1':
        return BlueskyV1OutputProcessor(output_stream)
    elif api_version = '4.1':
        return BlueskyV4_1OutputProcessor(output_stream)
    return output_stream



class BlueSkyRunOutput(object):

    def __init__(self, api_version, run_info, handle_error_func, output_stream):
        self.run_info = run_info
        self.handle_error = handle_error_func
        self.output_stream = apply_output_processor(api_version, output_stream)

    def process(self):
        if 'dispersion' in run['modules']:
            #if output['config']['dispersion'].get('model') != 'vsmoke'):
            self._get_dispersion(run)
        elif 'plumerising' in run['modules']:
            self._get_plumerise(run)
        else:
            # TODO: is returning raw input not ok?
            output = self._load_output(run)
            self.output_stream.write(output)

    ##
    ## Plumerise
    ##

    def _slice(self, info_dict, whitelist):
        # Need to create list of keys in order to pop within iteration
        for k in list(info_dict.keys()):
            if k not in whitelist:
                info_dict.pop(k)

    def _get_plumerise(self, run):
        version_info = run.get('version_info') or {}
        run_info = run if 'fires' in run else self._load_output(run)
        fires = run_info['fires']
        runtime_info = process_runtime(run_info.get('runtime'))

        self.output_stream.write(dict(run_id=run['run_id'],
            fires=fires,
            runtime=runtime_info,
            version_info=version_info))

    ##
    ## Dispersion
    ##

    def _get_dispersion(self, run):
        r = {
            "root_url": run['output_url'],
            "version_info": run.get('version_info') or {}
        }
        run_info = run if 'export' in run else self._load_output(run)

        # TODO: refine what runtime info is returned
        r['runtime'] = process_runtime(run_info.get('runtime'))

        export_info = run_info['export']

        vis_info = export_info['localsave'].get('visualization')
        if vis_info:
            # images
            self._parse_images(r, vis_info)

            # kmzs
            self._parse_kmzs_info(r, vis_info)

        disp_info = export_info['localsave'].get('dispersion')
        if disp_info:
            r.update(**{
                k: '{}/{}'.format(disp_info['sub_directory'], disp_info[k.lower()])
                for k in ('netCDF', 'netCDFs') if k.lower() in disp_info})

            # kmzs (vsmoke dispersion produces kmzs)
            self._parse_kmzs_info(r, disp_info)

        # TODO: list fire_*.csv if specified in output

        self.output_stream.write(r)

    def _parse_kmzs_info(self, r, section_info):
        kmz_info = section_info.get('kmzs', {})
        if kmz_info:
            r['kmzs'] = {k: '{}/{}'.format(section_info['sub_directory'], v)
                for k, v in list(kmz_info.items()) if k in ('fire', 'smoke')}

    def _parse_images(self, r, vis_info):
        r["images"] = vis_info.get('images')
        def _parse(r):
            if "directory" in d:
                d["directory"] = os.path.join(
                    vis_info['sub_directory'], d["directory"])
            else:
                for e in d:
                    _parse(e)


    ##
    ## Common methods
    ##

    def _load_output(self, run):
        # TODO: Maybe first try local no matter what, since is_same_host might
        #   give false negative and checking local shouldn't give false postive
        #   (only do this if is_same_host returns false negative in production)
        if is_same_host(run):
            tornado.log.gen_log.debug('Loading local output')
            return self._get(run['output_dir'], os.path.exists, open)
        else:
            tornado.log.gen_log.debug('Loading remote output')
            return self._get(run['output_url'], remote_exists, remote_open)

    def _get(self, output_location, exists_func, open_func):
        """Gets information about the outpu output, which may be in local dir
        or on remote host

        args:
         - output_location -- local pathname or url
         - exists_func -- function to check existence of dir or file
            (local or via http)
         - open_func -- function to open output json file (local or via http)
        """
        tornado.log.gen_log.debug('Looking for output in %s', output_location)
        if not exists_func(output_location):
            msg = "Output location doesn't exist: {}".format(output_location)
            self._raise_error(404, msg)

        # use join instead of os.path.join in case output_location is a remote url
        output_json_file = '/'.join([output_location.rstrip('/'), 'output.json'])
        if not exists_func(output_json_file):
            msg = "Output file doesn't exist: {}".format(output_json_file)
            self._raise_error(404, msg)

        with open_func(output_json_file) as f:
            try:
                j = f.read()
                if hasattr(j, 'decode'):
                    j = j.decode()
                return json.loads(j)
                # TODO: set fields here, using , etc.
            except:
                msg = "Failed to open output file: {}".format(output_json_file)
                self._raise_error(500, msg)

