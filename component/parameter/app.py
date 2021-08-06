"""Include app parameters"""

SATSOURCE = {
    "viirs": ("SUOMI_VIIRS_C2", "suomi-npp-viirs-c2"),
    "viirsnoa": ("J1_VIIRS_C2", "noaa-20-viirs-c2"),
    "modis": ("MODIS_C6", "c6"),
}

CONFIDENCE = {
    # Used for VIIRS (S-NPP & NOAA-20)
    'cat': {
        'high' : ['high', 'green'],
        'nominal' : ['nominal', 'orange'],
        'low' : ['low', 'red'],
    },
    'disc' : {
        80 : ['>80', 'green'],
        50 : ['>50, <80', 'orange'],
        30 : ['<50', 'red']
    }
}