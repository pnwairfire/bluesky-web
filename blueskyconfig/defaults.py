DEFAULTS = {
    # Note: domain grid information provided by Susan and STI.
    #  Bounding box info can also be determined by running chk_arl
    #  For example:
    #   $ chk_arl file /data/ARL/DRI/2km/2016040400/wrfout_d3.2016040400.f00-11_12hr01.arl |grep corner
    #     Lower left corner:   32.5980 -124.2761
    #    Upper right corner:   41.8444 -113.0910
    "domains": {
        "NAM84": {
            "grid": {
                "spacing": 12,
                "projection": "LCC",
                "boundary": {
                    "sw": {"lng": -130.0, "lat": 22.5},
                    "ne": {"lng": -60, "lat": 52.5}
                },
                "grid_size_options": {
                    "100": "xy(km): 7800 x 2400",
                    "75": "xy(km): 5800 x 1800",
                    "50": "xy(km): 3900 x 1200",
                    "25": "xy(km): 1900 x 600",
                }
            },
            "arl_index_file": "NAM84_ARL_index.csv",
            "time_step": 3
        },
        "GFS": {
            "grid": {
                "spacing": 50,
                "projection": "LCC",
                "boundary": {
                    "sw": {"lng": -130.0, "lat": 22.5},
                    "ne": {"lng": -60, "lat": 52.5}
                },
                "grid_size_options": {
                    "100": "xy(km): 7800 x 2400",
                    "75": "xy(km): 5800 x 1800",
                    "50": "xy(km): 3900 x 1200",
                    "25": "xy(km): 1900 x 600"
                }
            },
            "arl_index_file": None, # TODO: set correctly
            "time_step": 3
        },
        "PNW1.33km": {
            "grid": {
                "spacing": 1.33,
                "projection": "LCC",
                "boundary": {
                    "sw": {"lng": -126, "lat": 41.5},
                    "ne": {"lng": -113.5, "lat": 49.5}
                },
                "grid_size_options": {
                    "100": "xy(km): 1400 x 600",
                    "75": "xy(km): 1000 x 500",
                    "50": "xy(km): 700 x 300",
                    "25": "xy(km): 300 x 200"
                }
            },
            "arl_index_file": "arl12hrindex.csv",
            "time_step": 1
        },
        "PNW4km": {
            "grid": {
                "spacing": 4,
                "projection": "LCC",
                "boundary": {
                    "sw": {"lng": -128.6, "lat": 40},
                    "ne": {"lng": -107, "lat": 49.7}
                },
                "grid_size_options": {
                    "100": "xy(km): 2400 x 800",
                    "75": "xy(km): 1800 x 600",
                    "50": "xy(km): 1200 x 400",
                    "25": "xy(km): 600 x 200"
                }
            },
            "arl_index_file": "arl12hrindex.csv",
            "time_step": 1
        },
        "DRI2km": {
            "grid": {
                "spacing": 2,
                "projection": "LCC",
                "boundary": {
                    "sw": {"lng": -124.3, "lat": 32.5},
                    "ne": {"lng": -113.0, "lat": 41.8}
                },
                "grid_size_options": {
                    "100": "xy(km): 1300 x 700",
                    "75": "xy(km): 900 x 600",
                    "50": "xy(km): 600 x 400",
                    "25": "xy(km): 300 x 200"
                }
            },
            "arl_index_file": "arl12hrindex.csv",
            "time_step": 1
        },
        "DRI6km": {
            "grid": {
                "spacing": 6,
                "projection": "LCC",
                "boundary": {
                    "sw": {"lng": -128.5, "lat": 28.7},
                    "ne": {"lng": -107.0, "lat": 44.6}
                },
                "grid_size_options": {
                    "100": "xy(km): 2400 x 1300",
                    "75": "xy(km): 1800 x 900",
                    "50": "xy(km): 1200 x 600",
                    "25": "xy(km): 600 x 300"
                }
            },
            "arl_index_file": "arl12hrindex.csv",
            "time_step": 1
        },
        "UofA1.8km": {
            "grid": {
                "spacing": 1.8,
                "projection": "LCC",
                "boundary": {
                    "sw": {"lng": -115, "lat": 30},
                    "ne": {"lng": -102, "lat": 36.2}
                },
                "grid_size_options": {
                    "100": "xy(km): 1400 x 500",
                    "75": "xy(km): 1100 x 400",
                    "50": "xy(km): 700 x 200",
                    "25": "xy(km): 400 x 100"
                }
            },
            "arl_index_file": None, # TODO: set correctly
            "time_step": 1
        },
        "NAM3km": {
            "grid": {
                "spacing": 3,
                "projection": "LCC",
                "boundary": {
                    "sw": {"lng": -130.0, "lat": 22.5},
                    "ne": {"lng": -60, "lat": 52.5}
                },
                "grid_size_options": {
                    "100": "xy(km): 7800 x 2400",
                    "75": "xy(km): 5800 x 1800",
                    "50": "xy(km): 3900 x 1200",
                    "25": "xy(km): 1900 x 600"
                }
            },
            "arl_index_file": "nam3km_arlindex.csv",
            "time_step": 1
        },
        "LakeStates4km": {
            "grid": {
                "spacing": 4,
                "projection": "LCC",
                "boundary": {
                    "sw": {"lng": -123.75, "lat": 33.25},
                    "ne": {"lng": -114.25, "lat": 41.75}
                },
                "grid_size_options": {
                    "100": "xy(km): 1100 x 700",
                    "75": "xy(km): 800 x 500",
                    "50": "xy(km): 500 x 300",
                    "25": "xy(km): 300 x 200"
                }
            },
            "arl_index_file": None, # TODO: set correctly
            "time_step": 1
        },
        "Alaska12km": {
            "grid": {
                "spacing": 12,
                "projection": "LCC",
                "boundary": {
                    "sw": {"lng": -178.6, "lat": 40.6},
                    "ne": {"lng": -98, "lat": 66.3}
                },
                "grid_size_options": {
                    "100": "xy(km): 8900 x 2000",
                    "75": "xy(km): 6700 x 1500",
                    "50": "xy(km): 4500 x 1000",
                    "25": "xy(km): 2200 x 500"
                }
            },
            "arl_index_file": None, # TODO: set correctly
            "time_step": 1
        },
        "NWS-06Z-1km-2018-CA-NV": {
            "grid": {
                "spacing": 1,
                "projection": "LCC",
                "boundary": {
                    "sw": {"lng": -125.3, "lat": 39.5},
                    "ne": {"lng": -121, "lat": 44.4}
                },
                "grid_size_options": {
                    "100": None,
                    "75": None,
                    "50": None,
                    "25": None
                }
            },
            "arl_index_file": None, # TODO: set correctly
            "time_step": 1
        },
        "NWS-00Z-1km-2018-MT": {
            "grid": {
                "spacing": 1,
                "projection": "LCC",
                "boundary": {
                    "sw": {"lng": -115.8, "lat": 44.7},
                    "ne": {"lng": -110.6, "lat": 49.2}
                },
                "grid_size_options": {
                    "100": None,
                    "75": None,
                    "50": None,
                    "25": None
                }
            },
            "arl_index_file": None, # TODO: set correctly
            "time_step": 1
        }
    },
    "archives": {
        "fast": {
            # TODO: add entries here once archives are available
        },
        "standard": {
            "national_12-km": {
                "title": "National 12-km",
                "domain_id": "NAM84"
            },
            "global":{
                "title": "Global",
                "domain_id": "GFS"
            },
            # TODO: Keep an eye out for mpi hysplit failing
            #   with exit code 132 for NAM3k runs
            "national_3-km": {
                "title": "National 3-km",
                "domain_id": "NAM3km"
            },
            "pacific_northwest_1.33-km": {
                "title": "Pacific Northwest 1.33-km",
                "domain_id": "PNW1.33km"
            },
            "pacific_northwest_4-km": {
                "title": "Pacific Northwest 4-km",
                "domain_id": "PNW4km"
            },
            "ca-nv_2-km": {
                "title": "CA/NV 2-km",
                "domain_id": "DRI2km"
            },
            "ca-nv_6-km": {
                "title": "CA/NV 6-km",
                "domain_id": "DRI6km"
            },
            "AZ-NM_1.8-km": {
                "title": "AZ/NM 1.8-km",
                "domain_id": "UofA1.8km"
            },
            "lakestates_4-km": {
                "title": "Lake States 4-km",
                "domain_id": "LakeStates4km"
            },
            "alaska_12-km": {
                "title": "Alaska 12-km",
                "domain_id": "Alaska12km"
            }
        },
        "special": {
            "CA-OR-2018-1km06Z": {
                "title": "NWS 1km 06Z CA/OR",
                "domain_id": "NWS-06Z-1km-2018-CA-NV",
            },
            "MT-2018-1km00Z": {
                "title": "NWS 1km 00Z Montana",
                "domain_id": "NWS-00Z-1km-2018-MT",
            }
        }
    },
    # These are defaults for internal hysplit settings
    # (i.e. what's passed on to the pipeline)
    "hysplit": {
        "NUMPAR": 2000,
        "MAXPAR": 1000000000, # don"t want to ever hit MAXPAR
        "VERTICAL_EMISLEVELS_REDUCTION_FACTOR": 5,
        "VERTICAL_LEVELS": [100],
        "INITD": 0,
        "NINIT": 0,
        "DELT": 0.0,
        "KHMAX": 72, # number of hours after which particles are removed
        # Note: MPI and NCPUS are not allowed to be overridden
        "MPI": True,
        "NCPUS": 4
    },
    # These are met-specific defaults for internal hysplit settings
    "hysplit_met_specific": {
        "NAM3km": {
            "DISPERSION_OFFSET": 1
        }
    },
    # These prevent users from setting values to low or high
    "hysplit_settings_restrictions": {
        "TOP_OF_MODEL_DOMAIN": {
            "max": 30000.0
        }
    },
    # These are options that get translated to internal hysplit settings
    "hysplit_options": {
        # For PGv3 standard runs
        "dispersion_speed": {
            "faster": {
                "grid_resolution_factor": 1.5,
                "numpar": 1000
            },
            "balanced": {
                "grid_resolution_factor": 1.0,
                "numpar": 2000
            },
            "slower": {
                "grid_resolution_factor": 0.5,
                "numpar": 3000
            }
        },
        # For PGv3 advanced and expert runs
        "number_of_particles": {
            "low": 1000,
            "medium": 2000,
            "high": 3000
        },
        "grid_resolution": {
            "low": 1.5,
            "medium": 1.0,
            "high": 0.5
        }
    },
}
