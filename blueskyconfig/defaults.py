DEFAULTS = {
    # Note: domain grid information provided by Susan and STI.
    #  Bounding box info can also be determined by running chk_arl
    #  For example:
    #   $ chk_arl file /data/ARL/DRI/2km/2016040400/wrfout_d3.2016040400.f00-11_12hr01.arl |grep corner
    #     Lower left corner:   32.5980 -124.2761
    #    Upper right corner:   41.8444 -113.0910
    'domains': {
        'DRI2km': {
            'queue': 'dri',
            "grid": {
                "resolution_km": 2,
                "boundary": {
                    "ne": {"lat": 41.8444, "lng": -113.0910},
                    "sw": {"lat": 32.5980, "lng": -124.2761}
                }
            },
            "index_filename_pattern": "arl12hrindex.csv",
            "time_step": 1
        },
        'DRI6km': {
            'queue': 'dri',
            "grid": {
                "resolution_km": 6,
                "boundary": {
                    "ne": {"lat": 44.5953, "lng": -107.1489},
                    "sw": {"lat": 28.7459, "lng": -128.4614}
                }
            },
            "index_filename_pattern": "arl12hrindex.csv",
            "time_step": 1
        },
        'PNW1.33km': {
            'queue': 'pnw',
            "grid": {
                "resolution_km": 1.33,
                "boundary": {
                    "ne": {"lat": 48.9398, "lng": -113.7484},
                    "sw": {"lat": 44.7056, "lng": -126.2475}
                }
            },
            "index_filename_pattern": "arl12hrindex.csv",
            "time_step": 1
        },
        'PNW4km': {
            'queue': 'pnw',
            "grid": {
                "resolution_km": 4.0,
                "boundary": {
                    "ne": {"lat": 49.6821, "lng": -107.4911},
                    "sw": {"lat": 40.0488, "lng": -128.5677}
                }
            },
            "index_filename_pattern": "arl12hrindex.csv",
            "time_step": 1
        },
        'NAM84': {
            'queue': 'nam',
            "grid": {
                "resolution_km": 12.0,
                "boundary": {
                    "ne": {"lat": 57.3290, "lng": -49.4167},
                    "sw": {"lat": 12.1900, "lng": -133.4600}
                }
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
