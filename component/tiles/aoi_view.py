import geopandas as gpd
import json

from ipyleaflet import GeoJSON

import ipyvuetify as v

import sepal_ui.sepalwidgets as sw
from sepal_ui.scripts import utils as su


from component.message import cm
from component.parameter import *
from component.widget import *

COUNTRIES = gpd.read_file(COUNTRIES_JSON)

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
        
        self.w_aoi_method = Select(
            label=cm.ui.aoi_method,
            v_model='Draw on map',
            items=['Draw on map', 'Select country'],
            
        )
        self.w_countries = Select(
            label="Select country",
            v_model='',
            items=COUNTRIES.name.to_list(),
        ).hide()
        
        # Bind selected parameters
        self.model.bind(self.w_countries, 'country')
        
        self.children=[
            self.w_aoi_method,
            self.w_countries
        ]
        
        self.w_aoi_method.observe(self.aoi_method_event, 'v_model')
        self.w_countries.observe(self.add_country_event, 'v_model')
        
    def aoi_method_event(self, change):
        """Toggle components"""
        
        self.map_.remove_layers()
        
        if change['new'] == 'Select country':
            self.map_.hide_dc()
            su.show_component(self.w_countries)

        else:
            su.hide_component(self.w_countries)
            self.map_.show_dc()
            
    def add_country_event(self, change):
        """Add the selected country in the map"""
        
        self.map_.remove_layers()
        
        country_df = COUNTRIES[COUNTRIES['name']==change['new']]
        geometry =  country_df.iloc[0].geometry
        
        lon, lat = [xy[0] for xy in geometry.centroid.xy]
        
        data = json.loads(country_df.to_json())
        
        self.model.aoi_geometry = data
        
        aoi = GeoJSON(
            data=data,
            name=change['new'], 
            style={
                'color': 'green',
                'fillOpacity': 0, 
                'weight': 3
            }
        )
            
#         self.model.aoi_geometry = aoi.data['features'][0]['geometry']
        
        bounds = geometry.bounds

        self.map_.zoom_bounds(bounds)
        self.map_.center = (lat, lon)
        self.map_.add_layer(aoi)