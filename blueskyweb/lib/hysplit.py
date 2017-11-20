import copy
import blueskyconfig
import tornado.log

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

        tornado.log.gen_log.debug("hysplit configuration: %s",
            self._hysplit_config)

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
                    self._raise_error(400, "{} ({}) can't be greater than {} ".format(
                        k, self._hysplit_config[k], restrictions[k]['max']))
                if 'min' in restrictions[k] and (
                        self._hysplit_config[k] < restrictions[k]['min']):
                    self._raise_error(400, "{} ({}) can't be less than {} ".format(
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
            if 'NUMPAR' in self._hysplit_config:
                self._raise_error(400, "You can't specify NUMPAR along with"
                    "dispersion_speed, grid_resolution, or number_of_particles.")

            if any([self._hysplit_config.get(k) for k in
                    ('grid', 'USER_DEFINED_GRID', 'compute_grid')]):
                self._raise_error(400, "You can't specify 'grid', "
                    "'USER_DEFINED_GRID', or 'compute_grid' in the hysplit"
                    " config along with options 'dispersion_speed', "
                    " 'grid_resolution', or 'number_of_particles'.")

            if speed is not None:
                if res is not None or num_par is not None:
                    self._raise_error(400, "You can't specify "
                        "dispersion_speed along with either grid_resolution "
                        "or number_of_particles.")
                speed = speed.lower()
                speed_options = blueskyconfig.get('hysplit_options',
                    'dispersion_speed')
                if speed not in speed_options:
                    self._raise_error(400, 'Invalid value for '
                        'dispersion_speed: {}'.format(speed))
                self._hysplit_config['NUMPAR'] = speed_options[speed]['numpar']
                self._grid_resolution_factor = speed_options[speed]['grid_resolution_factor']

            else:
                if num_par is not None:
                    num_par_options = blueskyconfig.get('hysplit_options',
                        'number_of_particles')
                    if num_par not in num_par_options:
                        self._raise_error(400, 'Invalid value for '
                            'number_of_particles: {}'.format(num_par))
                    self._hysplit_config['NUMPAR'] = num_par_options[num_par]

                if res is not None:
                    res_options = blueskyconfig.get('hysplit_options',
                        'grid_resolution')
                    if res not in res_options:
                        self._raise_error(400, 'Invalid value for '
                            'grid_resolution: {}'.format(res))
                    self._grid_resolution_factor = res_options[res]

        else:
            if len([v for v in [k in self._hysplit_config for k in
                    ('grid', 'USER_DEFINED_GRID', 'compute_grid')] if v]) > 1:
                self._raise_error(400, "You can't specify more than one of "
                    "the following in the hysplit config: 'grid', "
                    "'USER_DEFINED_GRID', or 'compute_grid'.")

        self._grid_size_factor = 1.0
        size = self._request_handler.get_float_arg('grid_size', default=None)
        if size is not None:
            if size <= 0 or size > 1:
                self._raise_error(400,
                    "grid_size ({}) must be > 0 and <= 100".format(size))
            self._grid_size_factor = size

    def _fill_in_defaults(self):
        # fill config with defaults
        hysplit_defaults = blueskyconfig.get('hysplit')
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
        """From Robert:
          >  here is some logic to pass along about how to work out the hysplit domain with reduced met domain size. in this logic it keeps the hysplit domain equal in area to the reduced fraction size, ie, if a 50% reduction equals an area representing 25% of the met domain to be used but located as best as possible to keep the fire and that 25% of area all in the met domain (does that make sense?). The 50% is a reduction of the X and Y extents which means a 75% reduction in area....
          >
          >  Consider a met domain defined by bounds
          >
          >  Xmin, Xmax, Ymin, Ymax
          >
          >  Midpoint (Xc,Yc) = ( (Xmax + Xmin)/2, (Ymax + Ymin)/2 )
          >
          >  and length, width given by
          >
          >  X = Xmax - Xmin
          >  Y = Ymax - Ymin
          >
          >  a fire location given by (Xf,Yf)
          >
          >  and F is a reduction factor, ie, what fraction do we modify the X and Y extents by...
          >
          >  if F = 1 then hysplit domain is same as met domain:
          >
          >     with midpoint (Xc,Yc) and length,width of X,Y and bounds Xmin,Xmax,Ymin,Ymax
          >     although you can go through the remaining calcs and end up with the same answer
          >
          >  else:
          >
          >    new extents (length and width) are:
          >
          >    X' = X*F
          >    Y' = Y*F
          >
          >    new bounding box is for X:
          >
          >    X'min = Xf - X'/2
          >    X'max = Xf + X'/2
          >
          >    if  X'min < Xmin
          >
          >      X'max = X'max + Xmin - X'min
          >      X'min = Xmin
          >
          >    else if  X'max > Xmax
          >
          >      X'min = X'min + X`max - Xmax
          >      X'max = Xmax
          >
          >    end
          >
          >    similarly for Y:
          >
          >    Y'min = Yf - Y'/2
          >    Y'max = Yf + Y'/2
          >
          >    if  Y'min < Ymin
          >
          >      Y'max = Y'max + Ymin - Y'min
          >      Y'min = Ymin
          >
          >    else if Y'max > Ymax
          >
          >      Y'min = Y'min + Y`max - Ymax
          >      Y'max = Ymax
          >
          >    end
          >
          >    new hysplit center point is:
          >
          >    (X'c,Y'c) = ((X'max+X'min)/2,(Y'max+Y'min)/2)
          >
          >  end
          >
          >  This is one way of doing it. Another would be to define the extents as X/2 and Y/2 then truncate relative to fire location as the fire get closer to a boundary....is potentially faster as it makes the hysplit domain smaller more rapidly...however, it also doesn't default to the full domain for F = 1 when the fire isn't in the center as the above method does.
          >
          >  anyway, let me know if i need to explain it more clearly :P
        """
        # TODO: compute smaller grid (using Robert's calculations?)
        self._raise_error(501, "grid_size option not yet supported")
