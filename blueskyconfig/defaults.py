"""blueskyconfig.defaults"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

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
                    "1.0": "xy(km): 7800 x 2400",
                    "0.75": "xy(km): 5800 x 1800",
                    "0.50": "xy(km): 3900 x 1200",
                    "0.25": "xy(km): 1900 x 600",
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
                    "1.0": "xy(km): 7800 x 2400",
                    "0.75": "xy(km): 5800 x 1800",
                    "0.50": "xy(km): 3900 x 1200",
                    "0.25": "xy(km): 1900 x 600"
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
                    "ne": {"lng": -114.6, "lat": 49.4}
                },
                "grid_size_options": {
                    "1.0": "xy(km): 1300 x 600",
                    "0.75": "xy(km): 1000 x 500",
                    "0.50": "xy(km): 600 x 300",
                    "0.25": "xy(km): 300 x 200"
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
                    "sw": {"lng": -128.6, "lat": 40.125},
                    "ne": {"lng": -107.05, "lat": 49.8}
                },
                "grid_size_options": {
                    "1.0": "xy(km): 2400 x 800",
                    "0.75": "xy(km): 1800 x 600",
                    "0.50": "xy(km): 1200 x 400",
                    "0.25": "xy(km): 600 x 200"
                }
            },
            "arl_index_file": "arl12hrindex.csv",
            "time_step": 1
        },
        "DRI1.33km": {
            "grid": {
                "spacing": 2,
                "projection": "LCC",
                "boundary": {
                    "sw": {"lng": -124.0, "lat": 32.5},
                    "ne": {"lng": -114.0, "lat": 42.0}
                },
                "grid_size_options": {
                    "1.0": "xy(km): 1100 x 800",
                    "0.75": "xy(km): 900 x 600",
                    "0.50": "xy(km): 600 x 400",
                    "0.25": "xy(km): 300 x 200"
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
                    "ne": {"lng": -114.0, "lat": 42.0}
                },
                "grid_size_options": {
                    "1.0": "xy(km): 1100 x 800",
                    "0.75": "xy(km): 900 x 600",
                    "0.50": "xy(km): 600 x 400",
                    "0.25": "xy(km): 300 x 200"
                }
            },
            "arl_index_file": "arl12hrindex.csv",
            "time_step": 1
        },
        "DRI4km": {
            "grid": {
                "spacing": 2,
                "projection": "LCC",
                "boundary": {
                    "sw": {"lng": -128.5, "lat": 28.8},
                    "ne": {"lng": -109.5, "lat": 44.8}
                },
                "grid_size_options": {
                    "1.0": "xy(km): 1100 x 800",
                    "0.75": "xy(km): 900 x 600",
                    "0.50": "xy(km): 600 x 400",
                    "0.25": "xy(km): 300 x 200"
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
                    "sw": {"lng": -128.5, "lat": 29.0},
                    "ne": {"lng": -109.0, "lat": 44.7}
                },
                "grid_size_options": {
                    "1.0": "xy(km): 2100 x 1200",
                    "0.75": "xy(km): 1600 x 900",
                    "0.50": "xy(km): 1100 x 600",
                    "0.25": "xy(km): 500 x 300"
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
                    "1.0": "xy(km): 1400 x 500",
                    "0.75": "xy(km): 1100 x 400",
                    "0.50": "xy(km): 700 x 200",
                    "0.25": "xy(km): 400 x 100"
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
                    "sw": {"lng": -125.0, "lat": 25.0},
                    "ne": {"lng": -65.0, "lat": 50.0}
                },
                "grid_size_options": {
                    "1.0": "xy(km): 6700 x 2000",
                    "0.75": "xy(km): 5000 x 1500",
                    "0.50": "xy(km): 3300 x 1000",
                    "0.25": "xy(km): 1700 x 500"
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
                    "1.0": "xy(km): 1100 x 700",
                    "0.75": "xy(km): 800 x 500",
                    "0.50": "xy(km): 500 x 300",
                    "0.25": "xy(km): 300 x 200"
                }
            },
            "arl_index_file": None, # TODO: set correctly
            "time_step": 1
        },
        "Alaska12km": {
            "grid": {
                "spacing": 12, # 0.08
                "projection": "LCC",
                "boundary": {
                    "sw": {"lng": -174.5, "lat": 50.0},
                    "ne": {"lng": -135.5, "lat": 75.0}
                },
                "grid_size_options": {
                    "1.0": "xy(km): 8900 x 2000",
                    "0.75": "xy(km): 6700 x 1500",
                    "0.50": "xy(km): 4500 x 1000",
                    "0.25": "xy(km): 2200 x 500"
                }
            },
            "arl_index_file": 'AK12km_ARL_index.csv',
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
                    "1.0": None,
                    "0.75": None,
                    "0.50": None,
                    "0.25": None
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
                    "1.0": None,
                    "0.75": None,
                    "0.50": None,
                    "0.25": None
                }
            },
            "arl_index_file": None, # TODO: set correctly
            "time_step": 1
        },
        "Bend-OR-1km": {
            "grid": {
                "spacing": 1,
                "projection": "LCC",
                "boundary": {
                    "sw": {"lng": -121.7421, "lat": 43.7762},
                    "ne": {"lng": -120.9540, "lat": 44.3425}
                },
                "grid_size_options": {
                    "1.0": "xy(km): 1100 x 800",
                    "0.75": "xy(km): 900 x 600",
                    "0.50": "xy(km): 600 x 400",
                    "0.25": "xy(km): 300 x 200"
                }
            },
            "arl_index_file": "arl12hrindex.csv",
            "time_step": 1
        },
        "Bend-OR-333m": {
           "grid": {
               "spacing": 0.333,
               "projection": "LCC",
               "boundary": {
                   "sw": {"lng": -121.6908, "lat": 43.8107},
                   "ne": {"lng": -121.0264, "lat": 44.2883}
               },
               "grid_size_options": {
                   "1.0": "xy(km): 1100 x 800",
                   "0.75": "xy(km): 900 x 600",
                   "0.33": "xy(km): 600 x 400",
                   "0.15": "xy(km): 300 x 200"
               }
           },
           "arl_index_file": "arl12hrindex.csv",
           "time_step": 1
       },
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
            "ca-nv_1.33-km": {
                "title": "CA/NV 1.33-km",
                "domain_id": "DRI1.33km"
            },
            "ca-nv_4-km": {
                "title": "CA/NV 4-km",
                "domain_id": "DRI4km"
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
            "ca-nv_2km-sep-2015": {
                "title": "Rough Fire",
                "domain_id": "DRI2km"
            },
            "CA-OR-2018-1km06Z": {
                "title": "NWS 1km 06Z CA/OR",
                "domain_id": "NWS-06Z-1km-2018-CA-NV",
            },
            "MT-2018-1km00Z": {
                "title": "NWS 1km 00Z Montana",
                "domain_id": "NWS-00Z-1km-2018-MT",
            },
            "Bend-OR-1km-2015": {
                "title": "Bend, OR 1km 2015",
                "domain_id": "Bend-OR-1km",
            },
            "Bend-OR-333m-2015": {
                "title": "Bend, OR 333m 2015",
                "domain_id": "Bend-OR-333m",
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
                # TODO: Change to:
                #  - grid size factor 25%
                #  - grid_resolution_factor 1.0 or greater
                #  - numpar reduced from 'balanced' setting
                "grid_resolution_factor": 1.5,
                "numpar": 1000
            },
            "balanced": {
                # TODO: Change to:
                #  - grid size factor 33%
                #  - grid_resolution_factor 1.0
                #  - numpar reduced from 'slower' setting
                "grid_resolution_factor": 1.0,
                "numpar": 2000
            },
            "slower": {
                # TODO: Change to:
                #  - grid size factor 50%
                #  - grid_resolution_factor 1.0
                #  - numpar what we use in daily runs
                "grid_resolution_factor": 0.5,
                "numpar": 3000
            }
        },
        # For PGv3 advanced and expert runs
        "number_of_particles": {
            # TODO: Change these to match the values
            #   in the 'dispersion_speed' translations, above
            "low": 1000,
            "medium": 2000,
            "high": 3000
        },
        "grid_resolution": {
            # TODO: change to something like:
            # - 'nominal': 1.0
            # - 'sub-sample': something less that 1.0
            "low": 1.5,
            "medium": 1.0,
            "high": 0.5
        }
    }
}
