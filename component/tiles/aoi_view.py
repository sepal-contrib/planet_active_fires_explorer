import geopandas as gpd
import json

from ipyleaflet import GeoJSON

import ipyvuetify as v

import sepal_ui.sepalwidgets as sw
from sepal_ui.scripts import utils as su

from component.message import cm
import component.parameter as param
import component.widget as cw

__all__ = ["AoiView"]

COUNTRIES = gpd.read_file(param.COUNTRIES_JSON)


class AoiView(v.Card):
    def __init__(self, model, map_, *args, **kwargs):

        self.model = model
        self.map_ = map_

        super().__init__(*args, **kwargs)

        # We are not using the sepal_ui AOI tile because its high impact
        # On the performance when clipping the alerts, we should
        # find a better approach to clip the alerts
        # self.view = AoiView(methods=['-POINTS'], gee=False)
        # self.view.elevation = 0

        self.model = model

        self.w_aoi_method = cw.Select(
            label=cm.ui.aoi_method,
            v_model="draw",
            items=[
                {"text": cm.aoi.method.draw, "value": "draw"},
                {"text": cm.aoi.method.country, "value": "country"},
            ],
        )

        self.w_countries = cw.Select(
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

        self.map_.remove_layers()

        if change["new"] == "country":
            self.map_.hide_dc()
            su.show_component(self.w_countries)

        else:
            su.hide_component(self.w_countries)
            self.w_countries.v_model = ""
            self.map_.show_dc()

    def add_country_event(self, change):
        """Add the selected country in the map"""

        self.map_.remove_layers()

        if change["new"]:

            country_df = COUNTRIES[COUNTRIES["name"] == change["new"]]
            geometry = country_df.iloc[0].geometry

            lon, lat = [xy[0] for xy in geometry.centroid.xy]

            data = json.loads(country_df.to_json())

            self.model.aoi_geometry = data

            aoi = GeoJSON(
                data=data,
                name=change["new"],
                style={"color": "green", "fillOpacity": 0, "weight": 3},
            )

            bounds = geometry.bounds

            self.map_.zoom_bounds(bounds)
            self.map_.center = (lat, lon)
            self.map_.add_layer(aoi)
