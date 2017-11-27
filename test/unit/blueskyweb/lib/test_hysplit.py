import pytest

from blueskyweb.lib import hysplit

class MockHTTPError(RuntimeError):
    pass

class MockRequestHandler(object):
    def __init__(self, **query_args):
        self._query_args = query_args

    def _raise_error(self, *args, **kwargs):
        raise MockHTTPError(*args, **kwargs)

    def get(self, key, default=None):
        return self._query_args.get(key) or default

    def __getattr__(self, name):
        if name.startswith('get_'):
            return self.get

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

    def test_multiple_fire_objects(self):
        input_data = {
            "config": {"dispersion": {}},
            "fire_information": [
                {"growth": [{"location": {"latitude": 37.0,
                    "longitude": -89.0}}]},
                {"growth": [{"location": {"latitude": 32.0,
                    "longitude": -112.0}}]}
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            MockRequestHandler(), input_data, ARCHIVE_INFO)
        with pytest.raises(MockHTTPError) as e:
            hycon._configure_hysplit_reduced_grid()

    def test_not_single_lat_lng(self):
        input_data = {
            "config": {"dispersion": {}},
            "fire_information": [
                {"growth": [{"location": {
                    "longitude": -89.0}}]}
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            MockRequestHandler(), input_data, ARCHIVE_INFO)
        with pytest.raises(MockHTTPError) as e:
            hycon._configure_hysplit_reduced_grid()

    def test_not_reduced(self):
        """This tests the case where the grid is not reduced - it
        is left as defined for the archive.
        """
        input_data = {
            "config": {"dispersion": {}},
            "fire_information": [
                {"growth": [{"location": {"latitude": 37.0,
                    "longitude": -89.0}}]}
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            MockRequestHandler(), input_data, ARCHIVE_INFO)
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
            "fire_information": [
                {"growth": [{"location": {"latitude": 37.0,
                    "longitude": -84.0}}]}
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            MockRequestHandler(grid_size=0.50),
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
            "fire_information": [
                {"growth": [{"location": {"latitude": 37.0,
                    "longitude": -94.0}}]}
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            MockRequestHandler(grid_size=0.50),
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
            "fire_information": [
                {"growth": [{"location": {"latitude": 31.0,
                    "longitude": -64.0}}]}
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            MockRequestHandler(grid_size=0.50),
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