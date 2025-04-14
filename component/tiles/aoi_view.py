import json

import geopandas as gpd
import ipyvuetify as v
import sepal_ui.sepalwidgets as sw
from ipyleaflet import GeoJSON
from sepal_ui.scripts import utils as su
from traitlets import Bool
import component.parameter as param
from component.message import cm
from component.scripts.logger import logger

__all__ = ["AoiView"]

COUNTRIES = gpd.read_file(param.COUNTRIES_JSON)


class AoiView(v.Flex):

    close_dialog = Bool(False).tag(sync=True)

    def __init__(self, model, map_, *args, **kwargs):

        self.model = model
        self.map_ = map_

        super().__init__(*args, **kwargs)

        # We are not using the sepal_ui AOI tile because its high impact
        # On the performance when clipping the alerts, we should
        # find a better approach to clip the alerts

        self.model = model

        self.w_aoi_method = sw.Select(
            label=cm.ui.aoi_method,
            v_model="country",
            items=[
                {"text": cm.aoi.method.draw, "value": "draw"},
                {"text": cm.aoi.method.country, "value": "country"},
            ],
        )

        self.w_countries = sw.Select(
            label=cm.aoi.method.country,
            v_model="",
            items=COUNTRIES.name.to_list(),
        ).hide()

        # Bind selected parameters
        self.model.bind(self.w_countries, "country").bind(
            self.w_aoi_method, "aoi_method"
        )

        self.children = [self.w_aoi_method, self.w_countries]

        self.w_aoi_method.observe(self.aoi_method_event, "v_model")
        self.w_countries.observe(self.add_country_event, "v_model")

    def aoi_method_event(self, change):
        """Toggle components"""
        logger.info("aoi_method_event", change)

        self.map_.remove_all()
        self.close_dialog = False

        if change["new"] == "country":
            self.map_.dc.hide()
            su.show_component(self.w_countries)

        else:
            su.hide_component(self.w_countries)
            self.w_countries.v_model = ""
            self.map_.dc.show()
            self.close_dialog = True

    def add_country_event(self, change):
        """Add the selected country in the map"""

        self.map_.remove_all()

        if change["new"]:

            country_df = COUNTRIES[COUNTRIES["name"] == change["new"]]
            geometry = country_df.iloc[0].geometry

            lon, lat = [xy[0] for xy in geometry.centroid.xy]

            data = json.loads(country_df.to_json())

            self.model.aoi_geometry = data

            aoi = GeoJSON(
                data=data,
                name=change["new"],
            )

            bounds = geometry.bounds

            self.map_.zoom_bounds(bounds)
            self.map_.center = (lat, lon)
            self.map_.add_layer(aoi)
