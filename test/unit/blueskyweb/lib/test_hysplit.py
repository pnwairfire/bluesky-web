import copy

import pytest

from blueskyweb.lib import hysplit

class MockHTTPError(RuntimeError):
    def __init__(self, *args, **kwargs):
        super(MockHTTPError, self).__init__(*args, **kwargs)
        self.status_code = args[0]
        self.msg = args[1]

def handle_error(*args, **kwargs):
    raise MockHTTPError(*args, **kwargs)


ARCHIVE_INFO = {
    "id": "dummy-archive-2km",
    "title": "Dummy Archive 2km",
    "domain_id": "DRI2km",
    "grid": {
        "spacing": 2,
        "projection": "LCC",
        "boundary": {
            "sw": {"lng": -100.0, "lat": 30.0},
            "ne": {"lng": -60.0, "lat": 40.0}
        }
    },
    "arl_index_file": "arl12hrindex.csv",
    "time_step": 1
}


class TestHysplitConfiguratorConfigureReducedGrid(object):
    """Unit tests for grid reduction logic.
    """

    def test_multiple_fire_objects(self):
        input_data = {
            "config": {"dispersion": {}},
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 37.0, "lng": -89.0, "area": 10}],
                    "ecoregion": "western","utc_offset": '-05:00'}]}]},
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 32.0, "lng": -112.0, "area": 15}],
                    "ecoregion": "western","utc_offset": '-06:00'}]}]},
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            {}, handle_error, input_data, ARCHIVE_INFO)
        with pytest.raises(MockHTTPError) as e:
            hycon._configure_hysplit_reduced_grid()
        assert e.value.status_code == 400
        assert e.value.msg == hysplit.ErrorMessages.SINGLE_FIRE_ONLY

    def test_missing_lat(self):
        input_data = {
            "config": {"dispersion": {}},
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lng": -89.0, "area": 10}],
                    "ecoregion": "western","utc_offset": '-05:00'}]}]},
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            {}, handle_error, input_data, ARCHIVE_INFO)
        with pytest.raises(MockHTTPError) as e:
            hycon._configure_hysplit_reduced_grid()
        assert e.value.status_code == 400
        assert e.value.msg == hysplit.ErrorMessages.INVALID_FIRE_LOCATION_INFO

    def test_not_reduced(self):
        """This tests the case where the grid is not reduced - it
        is left as defined for the archive.
        """
        input_data = {
            "config": {"dispersion": {}},
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 37.0, "lng": -89.0, "area": 10}],
                    "ecoregion": "western","utc_offset": '-05:00'}]}]},
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            {}, handle_error, input_data, ARCHIVE_INFO)
        hycon._configure_hysplit_reduced_grid()
        expected_grid = {
            'boundary': {
                "sw": {"lng": -100.0, "lat": 30.0},
                "ne": {"lng": -60.0, "lat": 40.0}
            },
            'projection': 'LCC',
            'spacing': 2.0
        }
        assert hycon._hysplit_config['grid'] == expected_grid

    def test_reduced_fire_in_middle(self):
        """This tests the case where the grid is reduced, and the fire
        is central enough so that the reduced grid can be centered
        around it.
        """
        input_data = {
            "config": {"dispersion": {}},
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 37.0, "lng": -84.0, "area": 10}],
                    "ecoregion": "western","utc_offset": '-05:00'}]}]},
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            dict(grid_size=0.50), handle_error,
            input_data, ARCHIVE_INFO)
        hycon._configure_hysplit_reduced_grid()
        expected_grid = {
            'boundary': {
                "sw": {"lng": -94.0, "lat": 34.5},
                "ne": {"lng": -74.0, "lat": 39.5}
            },
            'projection': 'LCC',
            'spacing': 2.0
        }
        assert hycon._hysplit_config['grid'] == expected_grid

    def test_reduced_fire_in_middle_left(self):
        """This tests the case where the grid is reduced, and the fire
        is central enough in one dimension for the reduced grid to
        be centered around it, but not in the other.
        """
        input_data = {
            "config": {"dispersion": {}},
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 37.0, "lng": -94.0, "area": 10}],
                    "ecoregion": "western","utc_offset": '-05:00'}]}]},
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            dict(grid_size=0.50), handle_error,
            input_data, ARCHIVE_INFO)
        hycon._configure_hysplit_reduced_grid()
        expected_grid = {
            'boundary': {
                "sw": {"lng": -100.0, "lat": 34.5},
                "ne": {"lng": -80.0, "lat": 39.5}
            },
            'projection': 'LCC',
            'spacing': 2.0
        }
        assert hycon._hysplit_config['grid'] == expected_grid

    def test_reduced_fire_in_upper_right(self):
        """This tests the case where the grid is reduced, and the fire
        is far enough in the corner of the archive's full grid that
        it's also toward the corner in the reduced grid.
        """
        input_data = {
            "config": {"dispersion": {}},
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 31.0, "lng": -64.0, "area": 10}],
                    "ecoregion": "western","utc_offset": '-05:00'}]}]},
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            dict(grid_size=0.50), handle_error,
            input_data, ARCHIVE_INFO)
        hycon._configure_hysplit_reduced_grid()
        expected_grid = {
            'boundary': {
                "sw": {"lng": -80.0, "lat": 30.0},
                "ne": {"lng": -60.0, "lat": 35.0}
            },
            'projection': 'LCC',
            'spacing': 2.0
        }
        assert hycon._hysplit_config['grid'] == expected_grid

    def test_polygon_reduced_fire_in_middle(self):
        """This tests the case where the grid is reduced, and the fire
        is central enough so that the reduced grid can be centered
        around it, and the fire has polygon geometry.
        """
        input_data = {
            "config": {"dispersion": {}},
            "fires": [{
                "activity": [{
                    "active_areas": [{
                        "perimeter": {
                            "area": 10,
                            "polygon": [
                                [-85.0, 38.0],
                                [-85.0, 36.0],
                                [-83.0, 36.0],
                                [-83.0, 38.0],
                                [-85.0, 38.0]
                            ]
                        }
                    }]
                }]
            }]
        }
        hycon = hysplit.HysplitConfigurator(
            dict(grid_size=0.50), handle_error,
            input_data, ARCHIVE_INFO)
        hycon._configure_hysplit_reduced_grid()
        expected_grid = {
            'boundary': {
                "sw": {"lng": -94.0, "lat": 34.5},
                "ne": {"lng": -74.0, "lat": 39.5}
            },
            'projection': 'LCC',
            'spacing': 2.0
        }
        assert hycon._hysplit_config['grid'] == expected_grid

class TestHysplitConfiguratorGetCentralLatLng(object):

    SPECIFIED_POINTS_A = {
        "specified_points": [{
            # centroid (31, -64)
            "lat": 31.0,
            "lng": -64.0,
            "area": 200
        }]
    }

    SPECIFIED_POINTS_B = {
        "specified_points": [{
            # centroid (31, -67)
            "lat": 33.0,
            "lng": -67.0,
            "area": 100
        }]
    }

    PERIMETER = {
        "perimeter": {
            "area": 150,
            # centroid (37, -84)
            "polygon": [
                [-85.0, 38.0],
                [-85.0, 36.0],
                [-83.0, 36.0],
                [-83.0, 38.0],
                [-85.0, 38.0] # last coord not required by geoutils.get_centroid
            ]
        }
    }


    def setup(self):
        input_data = {
            "config": {"dispersion": {}},
            "fires": [{
                "activity": [{
                    "active_areas": []
                }]
            }]
        }
        self.active_areas = input_data["fires"][0]["activity"][0]["active_areas"]
        self.hycon = hysplit.HysplitConfigurator(
            {}, handle_error, input_data, ARCHIVE_INFO)

    def test_multiple_fires(self):
        self.hycon._input_data["fires"].append({"activity":[]})
        with pytest.raises(MockHTTPError) as e:
            self.hycon._get_central_lat_lng()
        assert e.value.status_code == 400
        assert e.value.msg == hysplit.ErrorMessages.SINGLE_FIRE_ONLY

    def test_missing_location_info(self):
        # missing growth info
        with pytest.raises(MockHTTPError) as e:
            self.hycon._get_central_lat_lng()
        assert e.value.status_code == 400
        assert e.value.msg == hysplit.ErrorMessages.NO_ACTIVITY_INFO

        # missing specified points and perimeter info
        self.active_areas.append({"sdf": 3})
        with pytest.raises(MockHTTPError) as e:
            self.hycon._get_central_lat_lng()
        assert e.value.status_code == 400
        assert e.value.msg == hysplit.ErrorMessages.INVALID_FIRE_LOCATION_INFO

        # specified point is missing lat and lng
        self.active_areas[0] = {"specified_points": [{}]}
        with pytest.raises(MockHTTPError) as e:
            self.hycon._get_central_lat_lng()
        assert e.value.status_code == 400
        assert e.value.msg == hysplit.ErrorMessages.INVALID_FIRE_LOCATION_INFO

        # missing longitude
        self.active_areas[0]["specified_points"][0] = {"lat": 45.1, "area": 1000}
        with pytest.raises(MockHTTPError) as e:
            self.hycon._get_central_lat_lng()
        assert e.value.status_code == 400
        assert e.value.msg == hysplit.ErrorMessages.INVALID_FIRE_LOCATION_INFO


    def test_lat_lng(self):
        self.active_areas.append(self.SPECIFIED_POINTS_A)
        assert self.hycon._get_central_lat_lng() == (31, -64)

    def test_perimeter(self):
        self.active_areas.append(self.PERIMETER)
        assert self.hycon._get_central_lat_lng() == (37, -84)

    def test_lat_lng_and_perimeter(self):
        self.active_areas.append(self.SPECIFIED_POINTS_A)
        self.active_areas.append(self.PERIMETER)
        assert self.hycon._get_central_lat_lng() == (34, -74)

    def test_two_lat_lngs(self):
        self.active_areas.append(self.SPECIFIED_POINTS_A)
        self.active_areas.append(self.SPECIFIED_POINTS_B)
        assert self.hycon._get_central_lat_lng() == (32, -65.5)


class TestHysplitConfiguratorConfigureGrid(object):
    """Unit tests for grid configuration.

    Note: See unit tests, above, for grid reduction
    """

    def test_too_many_grid_definitions(self):
        input_data = {
            "config": {
                "dispersion": {
                    "hysplit": {
                        # 'grid'
                        "grid": {
                            "spacing": 2,
                            "projection": "LCC",
                            "boundary": {
                                "sw": {"lng": -100.0, "lat": 30.0},
                                "ne": {"lng": -60.0, "lat": 40.0}
                            }
                        },
                        # 'USER_DEFINED_GRID'
                        "USER_DEFINED_GRID": True,
                        "CENTER_LATITUDE": 40,
                        "CENTER_LONGITUDE": -80,
                        "HEIGHT_LATITUDE": 20,
                        "WIDTH_LONGITUDE": 40,
                        "SPACING_LONGITUDE": 2,
                        "SPACING_LATITUDE": 2,
                        # 'compute_grid'
                        "compute_grid": True
                    },
                }
            },
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 31.0, "lng": -64.0, "area": 10}]}]}]},
            ]
        }
        with pytest.raises(MockHTTPError) as e:
            hycon = hysplit.HysplitConfigurator(
                {}, handle_error, input_data, ARCHIVE_INFO)
        assert e.value.status_code == 400
        assert e.value.msg == hysplit.ErrorMessages.TOO_MANY_GRID_SPECIFICATIONS


    def test_with_grid(self):
        input_data = {
            "config": {
                "dispersion": {
                    "hysplit": {
                        # 'grid'
                        "grid": {
                            "spacing": 2,
                            "projection": "LCC",
                            "boundary": {
                                "sw": {"lng": -100.0, "lat": 30.0},
                                "ne": {"lng": -60.0, "lat": 40.0}
                            }
                        }
                    }
                }
            },
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 31.0, "lng": -64.0, "area": 10}]}]}]},
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            {}, handle_error, input_data, ARCHIVE_INFO)
        assert 'USER_DEFINED_GRID' not in hycon._hysplit_config
        assert 'compute_grid' not in hycon._hysplit_config
        expected_grid = {
            "spacing": 2,
            "projection": "LCC",
            "boundary": {
                "sw": {"lng": -100.0, "lat": 30.0},
                "ne": {"lng": -60.0, "lat": 40.0}
            }
        }
        assert hycon._hysplit_config['grid'] == expected_grid


    def test_user_defined_grid(self):
        input_data = {
            "config": {
                "dispersion": {
                    "hysplit": {
                        # 'USER_DEFINED_GRID'
                        "USER_DEFINED_GRID": True,
                        "CENTER_LATITUDE": 40,
                        "CENTER_LONGITUDE": -80,
                        "HEIGHT_LATITUDE": 20,
                        "WIDTH_LONGITUDE": 40,
                        "SPACING_LONGITUDE": 2,
                        "SPACING_LATITUDE": 2,
                    }
                }
            },
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 31.0, "lng": -64.0, "area": 10}]}]}]},
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            {}, handle_error, input_data, ARCHIVE_INFO)
        assert 'grid' not in hycon._hysplit_config
        assert 'compute_grid' not in hycon._hysplit_config
        expected_params = {
            "USER_DEFINED_GRID": True,
            "CENTER_LATITUDE": 40,
            "CENTER_LONGITUDE": -80,
            "HEIGHT_LATITUDE": 20,
            "WIDTH_LONGITUDE": 40,
            "SPACING_LONGITUDE": 2,
            "SPACING_LATITUDE": 2,
        }
        for k in expected_params:
            assert hycon._hysplit_config[k] == expected_params[k]

    def test_compute_grid(self):
        input_data = {
            "config": {
                "dispersion": {
                    "hysplit": {
                        "compute_grid": True
                    }
                }
            },
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 31.0, "lng": -64.0, "area": 10}]}]}]},
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            {}, handle_error, input_data, ARCHIVE_INFO)
        assert 'grid' not in hycon._hysplit_config
        assert 'USER_DEFINED_GRID' not in hycon._hysplit_config
        assert hycon._hysplit_config['compute_grid'] == True

    def test_use_default_grid(self):
        input_data = {
            "config": {
                "dispersion": {
                    "hysplit": {
                    }
                }
            },
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 31.0, "lng": -64.0, "area": 10}]}]}]},
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            {}, handle_error, input_data, ARCHIVE_INFO)
        assert 'USER_DEFINED_GRID' not in hycon._hysplit_config
        assert 'compute_grid' not in hycon._hysplit_config
        assert hycon._hysplit_config['grid'] == ARCHIVE_INFO['grid']


class TestHysplitOptions(object):
    """Unit tests for hysplit options (disperion_speed, etc.)
    """
    def test_no_options(self):
        input_data = {
            "config": {
                "dispersion": {
                    "hysplit": {}
                }
            },
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 31.0, "lng": -64.0, "area": 10}]}]}]},
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            {}, handle_error, input_data, ARCHIVE_INFO)
        expected_hysplit_config = {
            'DELT': 0.0,
            'INITD': 0,
            'KHMAX': 72,
            'MAXPAR': 1000000000,
            'MPI': True,
            'NCPUS': 4,
            'NINIT': 0,
            'NUMPAR': 2000,
            'VERTICAL_EMISLEVELS_REDUCTION_FACTOR': 5,
            'VERTICAL_LEVELS': [100],
            'grid': {
                'boundary': {
                    'ne': {'lat': 40.0, 'lng': -60.0},
                    'sw': {'lat': 30.0, 'lng': -100.0}
                },
                'projection': 'LCC',
                'spacing': 2.0
            }
        }
        assert hycon._hysplit_config == expected_hysplit_config

    def test_no_options_nam3km(self):
        input_data = {
            "config": {
                "dispersion": {
                    "hysplit": {}
                }
            },
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 31.0, "lng": -64.0, "area": 10}]}]}]},
            ]
        }
        archive_info = copy.deepcopy(ARCHIVE_INFO)
        archive_info['domain_id'] = 'NAM3km'
        hycon = hysplit.HysplitConfigurator(
            {}, handle_error, input_data, archive_info)
        expected_hysplit_config = {
            'DELT': 0.0,
            'INITD': 0,
            'KHMAX': 72,
            'MAXPAR': 1000000000,
            'MPI': True,
            'NCPUS': 4,
            'NINIT': 0,
            'NUMPAR': 2000,
            'VERTICAL_EMISLEVELS_REDUCTION_FACTOR': 5,
            'VERTICAL_LEVELS': [100],
            'DISPERSION_OFFSET': 1,
            'grid': {
                'boundary': {
                    'ne': {'lat': 40.0, 'lng': -60.0},
                    'sw': {'lat': 30.0, 'lng': -100.0}
                },
                'projection': 'LCC',
                'spacing': 2.0
            }
        }
        assert hycon._hysplit_config == expected_hysplit_config

    def test_invalid_options(self):
        input_data = {
            "config": {
                "dispersion": {
                    "hysplit": {}
                }
            },
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 31.0, "lng": -64.0, "area": 10}]}]}]},
            ]
        }

        with pytest.raises(MockHTTPError) as e:
            hycon = hysplit.HysplitConfigurator(
                dict(dispersion_speed='sdfsdf'),
                handle_error, input_data, ARCHIVE_INFO)
        assert e.value.status_code == 400
        assert e.value.msg == hysplit.ErrorMessages.INVALID_DISPERSION_SPEED.format('sdfsdf')

        with pytest.raises(MockHTTPError) as e:
            hycon = hysplit.HysplitConfigurator(
                dict(number_of_particles='sdfsdf'),
                handle_error, input_data, ARCHIVE_INFO)
        assert e.value.status_code == 400
        assert e.value.msg == hysplit.ErrorMessages.INVALID_NUMBER_OF_PARTICLES.format('sdfsdf')

        with pytest.raises(MockHTTPError) as e:
            hycon = hysplit.HysplitConfigurator(
                dict(grid_resolution='sdfsdf'),
                handle_error, input_data, ARCHIVE_INFO)
        assert e.value.status_code == 400
        assert e.value.msg == hysplit.ErrorMessages.INVALID_GRID_RESOLUTION.format('sdfsdf')

    def test_conflict_numpar_with_other_options(self):
        input_data = {
            "config": {
                "dispersion": {
                    "hysplit": {'NUMPAR': 4000}
                }
            },
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 31.0, "lng": -64.0, "area": 10}]}]}]},
            ]
        }

        with pytest.raises(MockHTTPError) as e:
            hycon = hysplit.HysplitConfigurator(
                dict(dispersion_speed='faster'),
                handle_error, input_data, ARCHIVE_INFO)
        assert e.value.status_code == 400
        assert e.value.msg == hysplit.ErrorMessages.NUMPAR_CONFLICTS_WITH_OTHER_OPTIONS

        with pytest.raises(MockHTTPError) as e:
            hycon = hysplit.HysplitConfigurator(
                dict(number_of_particles='medium'),
                handle_error, input_data, ARCHIVE_INFO)
        assert e.value.status_code == 400
        assert e.value.msg == hysplit.ErrorMessages.NUMPAR_CONFLICTS_WITH_OTHER_OPTIONS

    def test_conflict_speed_with_other_options(self):
        input_data = {
            "config": {
                "dispersion": {
                    "hysplit": {}
                }
            },
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 31.0, "lng": -64.0, "area": 10}]}]}]},
            ]
        }

        with pytest.raises(MockHTTPError) as e:
            hycon = hysplit.HysplitConfigurator(
                dict(dispersion_speed='balanced', number_of_particles='low'),
                handle_error, input_data, ARCHIVE_INFO)
        assert e.value.status_code == 400
        assert e.value.msg == hysplit.ErrorMessages.DISPERSION_SPEED_CONFLICTS_WITH_OTHER_OPTIONS

        with pytest.raises(MockHTTPError) as e:
            hycon = hysplit.HysplitConfigurator(
                dict(dispersion_speed='balanced', grid_resolution='low'),
                handle_error, input_data, ARCHIVE_INFO)
        assert e.value.status_code == 400
        assert e.value.msg == hysplit.ErrorMessages.DISPERSION_SPEED_CONFLICTS_WITH_OTHER_OPTIONS

    def test_grid_with_other_options(self):
        input_data = {
            "config": {
                "dispersion": {
                    "hysplit": {
                        'grid': {
                            'boundary': {
                                'ne': {'lat': 40.0, 'lng': -60.0},
                                'sw': {'lat': 30.0, 'lng': -100.0}
                            },
                            'projection': 'LCC',
                            'spacing': 2.0
                        }
                    }
                }
            },
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 31.0, "lng": -64.0, "area": 10}]}]}]},
            ]
        }

        with pytest.raises(MockHTTPError) as e:
            hycon = hysplit.HysplitConfigurator(
                dict(dispersion_speed='faster'),
                handle_error, input_data, ARCHIVE_INFO)
        assert e.value.status_code == 400
        assert e.value.msg == hysplit.ErrorMessages.GRID_CONFLICTS_WITH_OTHER_OPTIONS

        with pytest.raises(MockHTTPError) as e:
            hycon = hysplit.HysplitConfigurator(
                dict(grid_resolution='medium'),
                handle_error, input_data, ARCHIVE_INFO)
        assert e.value.status_code == 400
        assert e.value.msg == hysplit.ErrorMessages.GRID_CONFLICTS_WITH_OTHER_OPTIONS

    # TODO: implement more conflict tests

    def test_faster_dispersion_speed(self):
        input_data = {
            "config": {
                "dispersion": {
                    "hysplit": {}
                }
            },
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 31.0, "lng": -64.0, "area": 10}]}]}]},
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            dict(dispersion_speed='faster'), handle_error,
            input_data, ARCHIVE_INFO)
        expected_hysplit_config = {
            'DELT': 0.0,
            'INITD': 0,
            'KHMAX': 72,
            'MAXPAR': 1000000000,
            'MPI': True,
            'NCPUS': 4,
            'NINIT': 0,
            'NUMPAR': 1000,
            'VERTICAL_EMISLEVELS_REDUCTION_FACTOR': 5,
            'VERTICAL_LEVELS': [100],
            'grid': {
                'boundary': {
                    'ne': {'lat': 40.0, 'lng': -60.0},
                    'sw': {'lat': 30.0, 'lng': -100.0}
                },
                'projection': 'LCC',
                'spacing': 3.0
            }
        }
        assert hycon._hysplit_config == expected_hysplit_config

    def test_high_number_of_particles(self):
        input_data = {
            "config": {
                "dispersion": {
                    "hysplit": {}
                }
            },
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 31.0, "lng": -64.0, "area": 10}]}]}]},
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            dict(number_of_particles='high'), handle_error,
            input_data, ARCHIVE_INFO)
        expected_hysplit_config = {
            'DELT': 0.0,
            'INITD': 0,
            'KHMAX': 72,
            'MAXPAR': 1000000000,
            'MPI': True,
            'NCPUS': 4,
            'NINIT': 0,
            'NUMPAR': 3000,
            'VERTICAL_EMISLEVELS_REDUCTION_FACTOR': 5,
            'VERTICAL_LEVELS': [100],
            'grid': {
                'boundary': {
                    'ne': {'lat': 40.0, 'lng': -60.0},
                    'sw': {'lat': 30.0, 'lng': -100.0}
                },
                'projection': 'LCC',
                'spacing': 2.0
            }
        }
        assert hycon._hysplit_config == expected_hysplit_config


    def test_high_grid_resolution(self):
        input_data = {
            "config": {
                "dispersion": {
                    "hysplit": {}
                }
            },
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 31.0, "lng": -64.0, "area": 10}]}]}]},
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            dict(grid_resolution='high'), handle_error,
            input_data, ARCHIVE_INFO)
        expected_hysplit_config = {
            'DELT': 0.0,
            'INITD': 0,
            'KHMAX': 72,
            'MAXPAR': 1000000000,
            'MPI': True,
            'NCPUS': 4,
            'NINIT': 0,
            'NUMPAR': 2000,
            'VERTICAL_EMISLEVELS_REDUCTION_FACTOR': 5,
            'VERTICAL_LEVELS': [100],
            'grid': {
                'boundary': {
                    'ne': {'lat': 40.0, 'lng': -60.0},
                    'sw': {'lat': 30.0, 'lng': -100.0}
                },
                'projection': 'LCC',
                'spacing': 1.0
            }
        }
        assert hycon._hysplit_config == expected_hysplit_config

    def test_custom_numpar(self):
        input_data = {
            "config": {
                "dispersion": {
                    "hysplit": {"NUMPAR": 4500}
                }
            },
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 31.0, "lng": -64.0, "area": 10}]}]}]},
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            {}, handle_error, input_data, ARCHIVE_INFO)
        expected_hysplit_config = {
            'DELT': 0.0,
            'INITD': 0,
            'KHMAX': 72,
            'MAXPAR': 1000000000,
            'MPI': True,
            'NCPUS': 4,
            'NINIT': 0,
            'NUMPAR': 4500,
            'VERTICAL_EMISLEVELS_REDUCTION_FACTOR': 5,
            'VERTICAL_LEVELS': [100],
            'grid': {
                'boundary': {
                    'ne': {'lat': 40.0, 'lng': -60.0},
                    'sw': {'lat': 30.0, 'lng': -100.0}
                },
                'projection': 'LCC',
                'spacing': 2.0
            }
        }
        assert hycon._hysplit_config == expected_hysplit_config

    def test_custom_numpar_with_low_grid_resolution(self):
        input_data = {
            "config": {
                "dispersion": {
                    "hysplit": {"NUMPAR": 4500}
                }
            },
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 31.0, "lng": -64.0, "area": 10}]}]}]},
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            dict(grid_resolution='low'), handle_error,
            input_data, ARCHIVE_INFO)
        expected_hysplit_config = {
            'DELT': 0.0,
            'INITD': 0,
            'KHMAX': 72,
            'MAXPAR': 1000000000,
            'MPI': True,
            'NCPUS': 4,
            'NINIT': 0,
            'NUMPAR': 4500,
            'VERTICAL_EMISLEVELS_REDUCTION_FACTOR': 5,
            'VERTICAL_LEVELS': [100],
            'grid': {
                'boundary': {
                    'ne': {'lat': 40.0, 'lng': -60.0},
                    'sw': {'lat': 30.0, 'lng': -100.0}
                },
                'projection': 'LCC',
                'spacing': 3.0
            }
        }
        assert hycon._hysplit_config == expected_hysplit_config

    def test_user_configured_grid_and_number_of_particles(self):
        input_data = {
            "config": {
                "dispersion": {
                    "hysplit": {
                        'grid': {
                            'boundary': {
                                'ne': {'lat': 40.0, 'lng': -60.0},
                                'sw': {'lat': 20.0, 'lng': -100.0}
                            },
                            'projection': 'LCC',
                            'spacing': 4.0
                        }
                    }
                }
            },
            "fires": [
                {"activity": [{"active_areas": [{
                    "specified_points": [{"lat": 31.0, "lng": -64.0, "area": 10}]}]}]},
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            dict(number_of_particles='high'), handle_error,
            input_data, ARCHIVE_INFO)
        expected_hysplit_config = {
            'DELT': 0.0,
            'INITD': 0,
            'KHMAX': 72,
            'MAXPAR': 1000000000,
            'MPI': True,
            'NCPUS': 4,
            'NINIT': 0,
            'NUMPAR': 3000,
            'VERTICAL_EMISLEVELS_REDUCTION_FACTOR': 5,
            'VERTICAL_LEVELS': [100],
            'grid': {
                'boundary': {
                    'ne': {'lat': 40.0, 'lng': -60.0},
                    'sw': {'lat': 20.0, 'lng': -100.0}
                },
                'projection': 'LCC',
                'spacing': 4.0
            }
        }
        assert hycon._hysplit_config == expected_hysplit_config
