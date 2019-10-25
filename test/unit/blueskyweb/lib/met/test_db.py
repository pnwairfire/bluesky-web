import copy

import pytest

from blueskyweb.lib.met import db

class TestApplyMinMax(object):

    def test_both_defined(self):
        assert db.apply_min_max(min, 1, 2) == 1
        assert db.apply_min_max(max, 1, 2) == 2

        # Handle zeros (i.e. don't interpret as undefined)
        assert db.apply_min_max(min, 0, 2) == 0
        assert db.apply_min_max(max, 0, 2) == 2
        assert db.apply_min_max(min, 1, 0) == 0
        assert db.apply_min_max(max, 1, 0) == 1


    def test_one_defined(self):
        assert db.apply_min_max(min, None, 2) == 2
        assert db.apply_min_max(max, None, 2) == 2
        assert db.apply_min_max(min, 1, None) == 1
        assert db.apply_min_max(max, 1, None) == 1

        # Handle zeros (i.e. don't interpret as undefined)
        assert db.apply_min_max(min, None, 0) == 0
        assert db.apply_min_max(max, None, 0) == 0
        assert db.apply_min_max(min, 0, None) == 0
        assert db.apply_min_max(max, 0, None) == 0

    def test_neither_defined(self):
        assert db.apply_min_max(min, None, None) == None
        assert db.apply_min_max(max, None, None) == None
        assert db.apply_min_max(min, None, None) == None
        assert db.apply_min_max(max, None, None) == None

    def test_different_types(self):
        with pytest.raises(TypeError) as e_info:
            db.apply_min_max(min, "sdf", 1)
        with pytest.raises(TypeError) as e_info:
            db.apply_min_max(max, 3.4, "SDFDSF")