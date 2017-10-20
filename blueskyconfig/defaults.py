DEFAULTS = {
    'domains': {
        # TODO: add PNW 4km with boundaries [-128, 41, -109, 50]
        # TODO: add LS (Great Lakes?) 4km with boundaries [-96.1, 41.5, -81.5, 49.5]
        'DRI2km': {
            'queue': 'dri', # TODO: define elsewhere ? (see above)
            "grid": {
                "spacing": 2,
                "boundary": {
                    # STI provided the following corners:
                    #   CANV 2km - [-124.3549, 32.5479, -113.2558, 41.8884]
                    # Then, ran the following on haze:
                    #   $ chk_arl file /data/ARL/DRI/2km/2016040400/wrfout_d3.2016040400.f00-11_12hr01.arl |grep corner
                    #     Lower left corner:   32.5980 -124.2761
                    #    Upper right corner:   41.8444 -113.0910
                    "ne": {"lat": 41.8444, "lng": -113.0910},
                    "sw": {"lat": 32.5980, "lng": -124.2761}
                },
                "projection": "LLC"
            },
            "index_filename_pattern": "arl12hrindex.csv",
            "time_step": 1
        },
        'DRI6km': {
            'queue': 'dri', # TODO: define elsewhere ? (see above)
            "grid": {
                "spacing": 6,
                "boundary": {
                    # Ran the following on haze:
                    #   $ chk_arl file /data/ARL/DRI/6km/2016040400/wrfout_d2.2016040400.f00-11_12hr01.arl |grep corner
                    #     Lower left corner:   28.7459 -128.4614
                    #    Upper right corner:   44.5953 -107.1489
                    "ne": {"lat": 44.5953, "lng": -107.1489},
                    "sw": {"lat": 28.7459, "lng": -128.4614}
                },
                "projection": "LLC"
            },
            "index_filename_pattern": "arl12hrindex.csv",
            "time_step": 1
        },
        'PNW1.33km': {
            'queue': 'pnw', # TODO: define elsewhere ? (see above)
            "grid": {
                "spacing": 1.33,
                "boundary": {
                    # Ran the following on haze:
                    #   $ chk_arl file /data/ARL/PNW/1.33km/2016040400/wrfout_d4.2016040400.f12-23_12hr01.arl |grep corner
                    #     Lower left corner:   44.7056 -126.2475
                    #    Upper right corner:   48.9398 -113.7484
                    "ne": {"lat": 48.9398, "lng": -113.7484},
                    "sw": {"lat": 44.7056, "lng": -126.2475}
                },
                "projection": "LLC"
            },
            "index_filename_pattern": "arl12hrindex.csv",
            "time_step": 1
        },
        'PNW4km': {
            'queue': 'pnw', # TODO: define elsewhere ? (see above)
            # Ran the following on haze:
            #   $ chk_arl file /data/ARL/PNW/4km/2016040400/wrfout_d3.2016040400.f12-23_12hr01.arl |grep corner
            #     Lower left corner:   40.0488 -128.5677
            #    Upper right corner:   49.6821 -107.4911
            "grid": {
                "spacing": 4.0,
                "boundary": {
                    "ne": {"lat": 49.6821, "lng": -107.4911},
                    "sw": {"lat": 40.0488, "lng": -128.5677}
                },
                "projection": "LLC"
            },
            "index_filename_pattern": "arl12hrindex.csv",
            "time_step": 1
        },
        'NAM84': {
            'queue': 'nam', # TODO: define elsewhere ? (see above)
            "grid": {
                "spacing": 0.15,
                "boundary": {
                    # STI provided the following corners:
                    #   NAM 12km - [-131, 18, -64, 55]
                    # Then, ran the following on haze:
                    #   $ chk_arl file /data/ARL/NAM/12km/2016040400/nam_forecast-2016040400_00-84hr.arl |grep corner
                    #     Lower left corner:   12.1900 -133.4600
                    #    Upper right corner:   57.3290  -49.4167
                    "ne": {"lat": 57.3290, "lng": -49.4167},
                    "sw": {"lat": 12.1900, "lng": -133.4600}
                },
                "projection": "LatLon"
            },
            "index_filename_pattern": "NAM84_ARL_index.csv",
            "time_step": 3
        }
    },
    'hysplit': {
        "NUMPAR": 2000,
        "MAXPAR": 1000000000, # don't want to ever hit MAXPAR
        "VERTICAL_EMISLEVELS_REDUCTION_FACTOR": 5,
        "VERTICAL_LEVELS": [100],
        "INITD": 0,
        "NINIT": 0,
        "DELT": 0.0,
        "KHMAX": 72, # number of hours after which particles are removed
        # Note: MPI and NCPUS are not allowed to be overridden
        "MPI": True,
        "NCPUS": 4
    }
}
