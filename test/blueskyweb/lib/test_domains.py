"""Unit tests for blueskyweb.lib.domains"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

from py.test import raises

from bluesky.exceptions import BlueSkyConfigurationError
from blueskyweb.lib import domains

# from numpy.testing import assert_approx_equal
#     assert_approx_equal(a, e, err_msg="...")


class TestGetMetBoundary(object):

    def test_invalid(self):
        with raises(BlueSkyConfigurationError) as e_info:
            get_met_boundary('dfsdf')
        assert e_info.value.message == "Unsupported met domain dfsdf"

        domains.DOMAINS['sdf'] = {}
        with raises(BlueSkyConfigurationError) as e_info:
            get_met_boundary('sdf')
        assert e_info.value.message == "Boundary not defined for met domain sdf"

    def test_valid(self):
        assert domains.DOMAINS['DRI2km']['boundary'] == get_met_boundary('DRI2km')

def TestKmPerLng(self):

    def test_basic(self):
        assert 111.32 == domains.km_per_lng(0)
        assert 78.71512688168647 == domains.km_per_lng(45)
        assert 0 == domains.km_per_lng(90)

class TestSquareGridFromLatLng(object):

    def test_basic(self):
        e = {
            "CENTER_LATITUDE": 45.0,
            "CENTER_LONGITUDE": -118.0,
            "HEIGHT_LATITUDE": 0.9009009009009009,
            "WIDTH_LONGITUDE": 1.2704038469036067,
            "SPACING_LONGITUDE": domains.DOMAINS['NAM84']['boundary']['spacing_longitude'],
            "SPACING_LATITUDE": domains.DOMAINS['NAM84']['boundary']['spacing_latitude']
        }
        assert e == domains.square_grid_from_lat_lng(45.0, -118.0, 100, 'NAM84')

    # TODO: test location that could cross pole
    # TODO: test location that could equator
    # TODO: test any invalid cases
