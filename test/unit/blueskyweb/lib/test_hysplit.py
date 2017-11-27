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
        return self._query_args.get('key') or default

    def __getattr__(self, name):
        if name.startswith('get_'):
            return self.get

ARCHIVE_INFO = {
    "id": "ca-nv_2-km",
    "title": "CA/NV 2-km",
    "domain_id": "DRI2km",
    "grid": {
        "spacing": 2,
        "projection": "LCC",
        "boundary": {
            "sw": {"lng": -124.3, "lat": 32.5},
            "ne": {"lng": -113.0, "lat": 41.8}
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
                {"growth": [{"location": {"latitude": 37.909644,
                    "longitude": -119.7615805}}]},
                {"growth": [{"location": {"latitude": 32.909644,
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
                    "longitude": -119.7615805}}]}
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            MockRequestHandler(), input_data, ARCHIVE_INFO)
        with pytest.raises(MockHTTPError) as e:
            hycon._configure_hysplit_reduced_grid()

    def test_not_reduced(self):
        input_data = {
            "config": {"dispersion": {}},
            "fire_information": [
                {"growth": [{"location": {"latitude": 37.909644,
                    "longitude": -119.7615805}}]}
            ]
        }
        hycon = hysplit.HysplitConfigurator(
            MockRequestHandler(), input_data, ARCHIVE_INFO)
        hycon._configure_hysplit_reduced_grid()
