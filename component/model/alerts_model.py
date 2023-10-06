import json
import os
import urllib
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

import geopandas as gpd
import pandas as pd
import pytz
from ipyleaflet import GeoJSON
from sepal_ui import model
from sepal_ui.scripts.utils import random_string
from shapely.geometry import Polygon
from tqdm.auto import tqdm
from traitlets import Any, Bool, Int, Unicode, observe

import component.parameter as param
import component.scripts as scripts
from sepal_ui.planetapi import PlanetModel


class AlertModel(model.Model):
    # If changed, propagate the status to all the tiles that are listening.
    reset = Bool(False).tag(sync=True)

    # Input parameters

    # Planet parameters

    cloud_cover = Int(20).tag(sync=True)
    days_before = Int(1).tag(sync=True)
    days_after = Int(1).tag(sync=True)
    max_images = Int(6).tag(sync=True)

    # Aoi parameters
    aoi_method = Unicode("").tag(sync=True)
    country = Unicode("").tag(sync=True)

    # Alerts type parameters
    firms_api_key = Unicode("").tag(sync=True)
    "str: firms api key. it will be either the sepal one or given by user. It will be gathered from authenticate_event."
    satsource = Unicode("modis_nrt").tag(sync=True)
    "str: source of satellite. the available values must match parameter.SAT_SOURCE"
    alerts_type = Unicode("nrt").tag(sync=True)
    "str: type of alerts, either nrt (near real time) or historic"
    start_date = Unicode("").tag(sync=True)
    "str (YYYY-MM-DD format): initial date. for historic queries"
    offset_days = Unicode("24h").tag(sync=True)
    "str: number of offset days after the start date. for historic queries."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Alerts
        self.alerts = None
        self.aoi_alerts = None
        self.current_alert = None

        self.planet_model = PlanetModel()

        # It will store both draw and country geometry
        self.aoi_geometry = None
        self.availability = None

    def get_alerts_url(self):
        """build the firms url to retrieve alerts depending on the users inputs stored
        in the model"""

        sat_source = param.SAT_SOURCE[self.alerts_type][self.satsource]
        bounds = ",".join(
            list(
                str(int(x))
                for x in gpd.GeoDataFrame.from_features(self.aoi_geometry).total_bounds
            )
        )
        offset_days = scripts.parse_offset(self.offset_days)
        start_date = self.start_date

        # Depending on the type of alerts, the args to the request will vary.
        args = [self.firms_api_key, sat_source, bounds, offset_days, start_date]

        if self.alerts_type == "nrt":
            return param.REQUEST_RECENT.format(*args[:-1])

        return param.REQUEST_HISTORIC.format(*args)

    def metadata_change(self, change):
        """Edit 'validate' and 'confidence' columns in the current aoi geodataframe.
        This event is trigged when metadata_table input values change

        """
        self.aoi_alerts.loc[self.current_alert, change["name"]] = change["new"]

    @observe("reset")
    def reset_alerts(self, change):
        """Remove previous downloaded alerts"""

        if change["new"] is True:
            self.alerts = None
            self.aoi_alerts = None
            self.current_alert = None

    def get_alerts_name(self):
        """Create an output name for the aoi alerts"""

        now = datetime.now(tz=pytz.timezone("UTC"))
        now = now.strftime("%b%d") + random_string()

        method = f"custom_draw" if not self.country else self.country

        if self.alerts_type == "recent":
            acq_date = f"last{self.timespan}"
        else:
            acq_date = f"from{self.start_date}_to{self.start_date}"

        return f"{now}_{self.satsource}_{method}_{acq_date}"

    def write_alerts(self):
        """Write clipped alerts in a new ESRI shapefile on the module results
        directory"""

        name = self.get_alerts_name()

        # Save shapefile files in a folder with the same name
        folder = param.ALERTS_DIR / name
        folder.mkdir(exist_ok=True, parents=True)

        output = param.ALERTS_DIR / folder / f"{name}.shp"

        # It will overwrite any previous created file.
        self.aoi_alerts.to_file(output)

        return folder, name

    def get_firms_alerts(self):
        """from a parsed API URL, perform the request by using a pandas geodataframe"""

        df = pd.read_csv(self.get_alerts_url())

        self.alerts = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326"
        ).reset_index()

    def clip_to_aoi(self):
        """Clip recent or historical geodataframe with area of interest and save it."""

        if not self.aoi_geometry:
            raise Exception(cm.ui.valid_aoi)

        alerts = self.alerts
        clip_geometry = (
            gpd.GeoDataFrame.from_features(self.aoi_geometry)
            .set_crs("EPSG:4326")
            .iloc[0]
            .geometry
        )

        self.aoi_alerts = alerts[alerts.geometry.intersects(clip_geometry)].copy()

    def format_gdf(self):
        """Reformat alerts aoi geodataframe to fit with the outputs needs.
        We are doing this here because we don't want to format needlessly the
        whole geodataframe.
        """

        # Create two new columns for user's inputs
        self.aoi_alerts["reviewed"] = ""
        self.aoi_alerts["observ"] = ""

        def parse(time):
            """Parse int time into string formated time"""
            time = str(time)
            return f"{time[:-2]}:{time[-2:]}"

        self.aoi_alerts["acq_time"] = self.aoi_alerts.acq_time.apply(parse)

    def alerts_to_squares(self):
        """Convert the point alerts into square polygons to display on map"""

        # Convert alert's geometries to 54009 (projected crs)
        # and use 375m as buffer
        geometry_col = (
            self.aoi_alerts.to_crs("ESRI:54009")["geometry"]
            .buffer(187.5, cap_style=3)
            .copy()
        )

        square_alerts = self.aoi_alerts.assign(geometry=geometry_col)

        # Divide alerts into confidence categories

        def get_color(feature):
            confidence = feature["properties"]["confidence"]
            color = scripts.get_confidence_color(self.satsource, confidence)
            return {
                "color": color,
                "fillColor": color,
            }

        json_aoi_alerts = json.loads(square_alerts.to_crs("EPSG:4326").to_json())

        return GeoJSON(
            data=json_aoi_alerts,
            name="Alerts",
            style={"fillOpacity": 0.1, "weight": 2},
            hover_style={"color": "white", "dashArray": "0", "fillOpacity": 0.5},
            style_callback=get_color,
        )

    def get_confidence_items(self):
        """Get the corresponding confidence items based on the satellite selection"""

        # Modis satellite is using a discrete range of values ranging from 0-100
        # We have divided its values in three categories (view app.py)

        type_ = "disc" if self.satsource == "modis" else "cat"

        confidence_by_sat = [
            {"text": v[0], "value": k} for k, v in param.CONFIDENCE[type_].items()
        ]

        return ["All"] + confidence_by_sat
