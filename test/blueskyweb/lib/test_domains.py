"""Unit tests for blueskyweb.lib.domains"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

from py.test import raises

from blueskyweb.lib import domains

# from numpy.testing import assert_approx_equal
#     assert_approx_equal(a, e, err_msg="...")


class TestGetMetBoundary(object):

    def test_invalid(self):
        with raises(domains.BlueSkyConfigurationError) as e_info:
            domains.get_met_boundary('dfsdf')
        assert e_info.value.message == "Unsupported met domain dfsdf"

        domains.DOMAINS['sdf'] = {}
        with raises(domains.BlueSkyConfigurationError) as e_info:
            domains.get_met_boundary('sdf')
        assert e_info.value.message == "Boundary not defined for met domain sdf"

    def test_valid(self):
        assert domains.DOMAINS['DRI2km']['boundary'] == domains.get_met_boundary('DRI2km')
