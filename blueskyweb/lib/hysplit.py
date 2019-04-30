import copy
import blueskyconfig
from geoutils.geojson import get_centroid

class ErrorMessages(object):
    SINGLE_FIRE_ONLY = "grid_size option only supported for single fire"
    INVALID_FIRE_LOCATION_INFO = "Fire growth data must contain lat and lng or geojson data"
    NUMPAR_CONFLICTS_WITH_OTHER_OPTIONS = ("You can't specify NUMPAR along with"
        " dispersion_speed or number_of_particles.")
    GRID_CONFLICTS_WITH_OTHER_OPTIONS = ("You can't specify 'grid',"
        " 'USER_DEFINED_GRID', or 'compute_grid' in the hysplit"
        " config along with options 'dispersion_speed' or "
        " 'grid_resolution'.")
    TOO_MANY_GRID_SPECIFICATIONS = ("You can't specify more than one of "
        "the following in the hysplit config: 'grid', "
        "'USER_DEFINED_GRID', or 'compute_grid'.")
    INVALID_DISPERSION_SPEED = 'Invalid value for dispersion_speed: {}'
    INVALID_NUMBER_OF_PARTICLES = 'Invalid value for number_of_particles: {}'
    INVALID_GRID_RESOLUTION = 'Invalid value for grid_resolution: {}'
    DISPERSION_SPEED_CONFLICTS_WITH_OTHER_OPTIONS = ("You can't specify "
        "dispersion_speed along with either grid_resolution "
        "or number_of_particles.")

class HysplitConfigurator(object):

    def __init__(self, request_handler, input_data, archive_info):
        self._request_handler = request_handler
        self._input_data = input_data
        self._archive_info = archive_info

        # Defaults must be filled in after input config and request
        # options are processed, so that we can validate that the
        # config and options don't conflict or overlap
        self._process_config()
        self._process_options()
        self._fill_in_defaults()
        self._configure_grid()

    @property
    def config(self):
        """Final processed and filled in config
        """
        return self._hysplit_config

    def _process_config(self):
        """Gets user-supplied hysplit config, or initializes if necessary
        """
        # validate
        self._hysplit_config = self._input_data['config']['dispersion'].get(
            'hysplit') or {}
        restrictions = blueskyconfig.get('hysplit_settings_restrictions')
        for k in self._hysplit_config:
            if k in restrictions:
                if 'max' in restrictions[k] and (
                        self._hysplit_config[k] > restrictions[k]['max']):
                    self._request_handler._raise_error(400, "{} ({}) can't be greater than {} ".format(
                        k, self._hysplit_config[k], restrictions[k]['max']))
                if 'min' in restrictions[k] and (
                        self._hysplit_config[k] < restrictions[k]['min']):
                    self._request_handler._raise_error(400, "{} ({}) can't be less than {} ".format(
                        k, self._hysplit_config[k], restrictions[k]['min']))

    def _process_options(self):
        """Parses hysplit query string options, makes sure they
        don't conflict with each other or with hysplit config settings
        in the input data, and translates them to hysplit config settings.
        """
        # get query_parameters
        speed = self._request_handler.get_query_argument('dispersion_speed', None)
        res = self._request_handler.get_query_argument('grid_resolution', None)
        num_par = self._request_handler.get_query_argument('number_of_particles', None)

        self._grid_resolution_factor = 1.0
        if any([k is not None for k in (speed, res, num_par)]):
            if (speed or num_par) and 'NUMPAR' in self._hysplit_config:
                self._request_handler._raise_error(400, ErrorMessages.NUMPAR_CONFLICTS_WITH_OTHER_OPTIONS)

            if (speed or res) and any([self._hysplit_config.get(k) for k in
                    ('grid', 'USER_DEFINED_GRID', 'compute_grid')]):
                self._request_handler._raise_error(400, ErrorMessages.GRID_CONFLICTS_WITH_OTHER_OPTIONS)

            if speed is not None:
                if res is not None or num_par is not None:
                    self._request_handler._raise_error(400,
                        ErrorMessages.DISPERSION_SPEED_CONFLICTS_WITH_OTHER_OPTIONS)
                speed = speed.lower()
                speed_options = blueskyconfig.get('hysplit_options',
                    'dispersion_speed')
                if speed not in speed_options:
                    self._request_handler._raise_error(400,
                        ErrorMessages.INVALID_DISPERSION_SPEED.format(speed))
                self._hysplit_config['NUMPAR'] = speed_options[speed]['numpar']
                self._grid_resolution_factor = speed_options[speed]['grid_resolution_factor']

            else:
                if num_par is not None:
                    num_par_options = blueskyconfig.get('hysplit_options',
                        'number_of_particles')
                    if num_par not in num_par_options:
                        self._request_handler._raise_error(400,
                            ErrorMessages.INVALID_NUMBER_OF_PARTICLES.format(num_par))
                    self._hysplit_config['NUMPAR'] = num_par_options[num_par]

                if res is not None:
                    res_options = blueskyconfig.get('hysplit_options',
                        'grid_resolution')
                    if res not in res_options:
                        self._request_handler._raise_error(400,
                            ErrorMessages.INVALID_GRID_RESOLUTION.format(res))
                    self._grid_resolution_factor = res_options[res]

        else:
            if len([v for v in [k in self._hysplit_config for k in
                    ('grid', 'USER_DEFINED_GRID', 'compute_grid')] if v]) > 1:
                self._request_handler._raise_error(400,
                    ErrorMessages.TOO_MANY_GRID_SPECIFICATIONS)

        self._grid_size_factor = 1.0
        size = self._request_handler.get_float_arg('grid_size', default=None)
        if size is not None:
            if size <= 0 or size > 1:
                self._request_handler._raise_error(400,
                    "grid_size ({}) must be > 0 and <= 100".format(size))
            self._grid_size_factor = size

    def _fill_in_defaults(self):
        # fill config with defaults
        hysplit_defaults = blueskyconfig.get('hysplit')
        hysplit_defaults.update(
            blueskyconfig.get('hysplit_met_specific').get(
                self._archive_info['domain_id'], {}))
        for k in hysplit_defaults:
            # use MPI and NCPUS defaults even if request specifies them
            if k in ('MPI', 'NCPUS') or k not in self._hysplit_config:
                self._hysplit_config[k] = hysplit_defaults[k]


    def _configure_grid(self):
        """Configures hysplit grid.

        Notes:
         - self._grid_resolution_factor and self._grid_size_factor
           are set in _process_options
         - _process_options will have made sure there are no
           conflicting options and settings
        """
        if not any([self._hysplit_config.get(k) for k in
                ('grid', 'USER_DEFINED_GRID', 'compute_grid')]):
            self._hysplit_config['grid'] = copy.deepcopy(self._archive_info['grid'])
            self._hysplit_config['grid']['spacing'] *= self._grid_resolution_factor
            if self._grid_size_factor != 1.0:
                self._configure_hysplit_reduced_grid()

        # else, nothing to do, since user configured grid

    def _configure_hysplit_reduced_grid(self):
        """Reduces the hyplit grid by a factor between 0.0 and 1.0,
        centering the reduced grid around the fire location as much as
        possible without going outside of the original archive domain.
        """
        lat, lng = self._get_central_lat_lng()
        sw = self._archive_info['grid']['boundary']['sw']
        ne = self._archive_info['grid']['boundary']['ne']
        # Note: none of the met domains cross the international
        # dateline, so we can safely subract sw from ne
        new_lat_diff = self._grid_size_factor * (ne['lat'] - sw['lat'])
        new_lng_diff = self._grid_size_factor * (ne['lng'] - sw['lng'])
        self._hysplit_config['grid']['boundary'] = {
            "sw": {
                "lat": min(max(lat - new_lat_diff / 2, sw['lat']),
                        ne['lat'] - new_lat_diff),
                "lng": min(max(lng - new_lng_diff / 2, sw['lng']),
                        ne['lng'] - new_lng_diff),
            },
            'ne': {
                "lat": max(min(lat + new_lat_diff / 2, ne['lat']),
                        sw['lat'] + new_lat_diff),
                "lng": max(min(lng + new_lng_diff / 2, ne['lng']),
                        sw['lng'] + new_lng_diff),
            }
        }
        if 'latitude' in self._location and 'longitude' in self._location:
            self._latitude = self._location['latitude']
            self._longitude = self._location['longitude']
        elif 'geojson' in self._location:
            coordinate = get_centroid(self._location['geojson'])
            self._latitude = coordinate[1]
            self._longitude = coordinate[0]

    def _get_central_lat_lng(self):
        if len(self._input_data['fire_information']) > 1:
            # input data could possibly specifu multiple fires at
            # the same location, but we won't bother trying to accept that
            self._request_handler._raise_error(400,
                ErrorMessages.SINGLE_FIRE_ONLY)

        centroids = []
        for g in self._input_data['fire_information'][0]['growth']:
            loc = g.get('location', {})
            if set(['latitude','longitude']).issubset(set(loc.keys())):
                centroids.append((loc['latitude'], loc['longitude']))

            elif 'geojson' in loc:
                coords = get_centroid(loc['geojson']) # returns lng, lat
                centroids.append((coords[1], coords[0]))

            else:
                self._request_handler._raise_error(400,
                    ErrorMessages.INVALID_FIRE_LOCATION_INFO)

        if len(centroids) > 1:
            multi_point = {
                "type": 'MultiPoint',
                "coordinates": [ [e[1], e[0]] for e in centroids ]
            }
            coords = get_centroid(multi_point)
            return (coords[1], coords[1])
        else:
            return centroids[0]
