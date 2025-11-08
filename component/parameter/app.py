from component.message import cm

__all__ = [
    "SAT_SOURCE",
    "CONFIDENCE",
    "TIME_SPAN",
    "BAR_FORMAT",
    "MAX_ALERTS",
    "METADATA_ROWS",
]

# sat_source and hard-coded start date from alerts.
SAT_SOURCE = {
    "nrt": {
        "modis_nrt": "MODIS_NRT",
        "viirs_noaa_nrt": "VIIRS_NOAA20_NRT",
        "viirs_snpp_nrt": "VIIRS_SNPP_NRT",
    },
    "historic": {
        "modis_sp": "MODIS_SP",
        "viirs_sp": "VIIRS_SNPP_SP",
        "modis_nrt": "MODIS_NRT",
        "viirs_noaa_nrt": "VIIRS_NOAA20_NRT",
        "viirs_snpp_nrt": "VIIRS_SNPP_NRT",
    },
}

CONFIDENCE = {
    # Used for VIIRS (S-NPP & NOAA-20)
    "cat": {
        "high": ["high", "green"],
        "nominal": ["nominal", "orange"],
        "low": ["low", "red"],
        # Some data has changed, now they're using the abbreviation.
        "h": ["high", "green"],
        "n": ["nominal", "orange"],
        "l": ["low", "red"],
    },
    "disc": {80: [">80", "green"], 50: [">50, <80", "orange"], 30: ["<50", "red"]},
}

# Time span for recent alerts
TIME_SPAN = {
    "24h": cm.alerts.hour24,
    "48h": cm.alerts.hour48,
}

TIME_SPAN.update({f"{i}d": f"{i} {cm.alerts.days}" for i in range(3, 11, 1)})

# Specify format for the tqdm progress bar
BAR_FORMAT = "{l_bar}{bar}{n_fmt}/{total_fmt}"

# Maxiumum number of alerts to display on the map
MAX_ALERTS = 20000

# Columns to be retreived in the
METADATA_ROWS = {
    "index": cm.alerts.metadata.index,
    "latitude": cm.alerts.metadata.latitude,
    "longitude": cm.alerts.metadata.longitude,
    "acq_date": cm.alerts.metadata.acq_date,
    "acq_time": cm.alerts.metadata.acq_time,
    "confidence": cm.alerts.metadata.confidence,
    "reviewed": cm.alerts.metadata.reviewed,
    "observ": cm.alerts.metadata.observation,
}

GEE_SOURCES = {
    "MODIS": {
        "asset_id": "FIRMS",
        "scale": 926,
        "bands": ["T21", "confidence", "line_number"],
        "start_date": "2000-11-01",
        "end_date": None,  # present
    },
    "VIIRS_SNPP": {
        "asset_id": "NASA/LANCE/SNPP_VIIRS/C2",
        "scale": 926,
        "bands": [
            "Bright_ti4",
            "Bright_ti5",
            "Confidence",
            "line_number",
            "frp",
            "acq_epoch",
            "acq_time",
            "DayNight",
        ],
        "start_date": "2023-09-03",
        "end_date": None,  # present
    },
    "VIIRS_NOAA20": {
        "asset_id": "NASA/LANCE/NOAA20_VIIRS/C2",
        "scale": 926,
        "bands": [
            "Bright_ti4",
            "Bright_ti5",
            "confidence",
            "line_number",
            "frp",
            "acq_epoch",
            "acq_time",
            "DayNight",
        ],
        "start_date": "2023-10-08",
        "end_date": None,  # present
    },
}
