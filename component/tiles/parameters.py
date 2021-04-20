import json
from ipyleaflet import GeoJSON

from traitlets import (
    Int, Unicode, link
)

from sepal_ui.scripts import utils as su
import ..message as cm
from ..widget.custom_widgets import *
from ..scripts.scripts import *


COUNTRIES = gpd.read_file('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json')

class Parameters(v.Card):
    
    TIME_SPAN = ['24 hours', '48 hours', '7 days']
    timespan = Unicode('24 hours').tag(sync=True)
    
    def __init__(self, map_, **kwargs):
        
        self.class_='pa-2 mb-2'
        self.map_ = map_
        
        super().__init__(**kwargs)
        
        # Class parameters
        
        self.aoi = None
        
        self.w_alert = Alert()
        
        self.w_spantime = v.Select(
            label="In the last",
            items=self.TIME_SPAN,
            v_model=self.timespan,
        )
        
        self.w_aoi_method = v.Select(
            label=cm.ui.aoi_method,
            v_model='Draw on map',
            items=['Draw on map', 'Select country'],
            
        )
        self.w_countries = v.Select(
            label="Select country",
            v_model='',
            items=COUNTRIES.name.to_list(),
        )
        
        self.w_run = sw.Btn("Get Alerts")
        
        su.hide_component(self.w_countries)
        
        self.map_.dc.on_draw(self.handle_draw)

        self.w_countries.observe(self.add_country_event, 'v_model')
        self.w_aoi_method.observe(self.aoi_method_event, 'v_model')
        
        self.children = [
            v.CardTitle(children=['Alerts settings']),
            self.w_spantime,
            self.w_aoi_method,
            self.w_countries,
            self.w_run,
            self.w_alert,
        ]
        
        link((self.w_spantime, 'v_model'),(self, 'timespan'))
        
    def add_country_event(self, change):
        
        self.map_.remove_layers()
        
        country_df = COUNTRIES[COUNTRIES['name']==change['new']]
        geometry =  country_df.iloc[0].geometry
        
        lon, lat = [xy[0] for xy in geometry.centroid.xy]
        
        data = json.loads(country_df.to_json())
        
        aoi = GeoJSON(data=data,
                      name=change['new'], 
                     style={
                         'color': 'green',
                         'fillOpacity': 0, 
                         'weight': 3
                     }
                )
            
        self.aoi = aoi.data['features'][0]['geometry']
        
        min_lon, min_lat, max_lon, max_lat = geometry.bounds

        # Get (x, y) of the 4 cardinal points
        tl = (max_lat, min_lon)
        bl = (min_lat, min_lon)
        tr = (max_lat, max_lon)
        br = (min_lat, max_lon)
        
        self.map_.zoom_bounds([tl,bl, tr, br])
        self.map_.center = (lat, lon)
        self.map_.add_layer(aoi)
        
    def aoi_method_event(self, change):
        
        self.map_.remove_layers()
        
        if change['new'] == 'Select country':
            self.map_.hide_dc()
            su.show_component(self.w_countries)

        else:
            su.hide_component(self.w_countries)
            self.map_.show_dc()
            
            
    def handle_draw(self, target, action, geo_json):
        
        self.map_.remove_layers()
        if action == 'created':
            self.aoi = geo_json['geometry']
            
            
class PlanetParameters(v.Card):
    
    cloud_cover = Int(20).tag(sync=True)
    days_before = Int(0).tag(sync=True)
    max_images = Int(6).tag(sync=True)
    api_key = Unicode('').tag(sync=True)
    
    def __init__(self, **kwargs):
        
        class_='pa-2'
        
        super().__init__(**kwargs)
        
        
        self.w_api_alert = Alert(children=[cm.ui.default_api], type_='info').show()
        
        self.w_api_key = sw.PasswordField(
            label=cm.ui.insert_api,
            v_model=self.api_key
        )
        
        self.w_api_btn = sw.Btn('Check ', small=True,)
        
        self.w_days_before = sw.NumberField(
            label=cm.ui.days_before,
            max_=5,
            v_model=self.days_before,
            disabled=True
        )
        
        self.w_max_images = sw.NumberField(
            label=cm.ui.max_images,
            max_=6,
            min_=1,
            v_model=1,
            disabled=True
        )
        
        self.w_cloud_cover = v.Slider(
            label=cm.ui.cloud_cover,
            thumb_label=True,
            v_model=self.cloud_cover,
            disabled=True
        )

        
        # Links
        
        link((self.w_api_key, 'v_model'),(self, 'api_key'))
        
        link((self.w_days_before, 'v_model'),(self, 'days_before'))
        link((self.w_max_images, 'v_model'),(self, 'max_images'))
        link((self.w_cloud_cover, 'v_model'),(self, 'cloud_cover'))
        
        # Button events
        
        self.w_api_btn.on_event('click', self.validate_api_event)
        
        self.children = [
            v.CardTitle(children=[cm.ui.planet_title]),
            v.Flex(
                class_='d-flex align-center mb-2', 
                row=True, 
                children =[self.w_api_key, self.w_api_btn]
            ),
            self.w_api_alert, 
            self.w_max_images,
            self.w_days_before,
            self.w_cloud_cover,
        ]

    def _toggle_planet_setts(self, on=True):
        
        if on:
            self.w_days_before.disabled = False
            self.w_cloud_cover.disabled = False
            self.w_max_images.disabled = False
            
        else:
            self.w_days_before.disabled = True
            self.w_cloud_cover.disabled = True
            self.w_max_images.disabled = True
            
    def validate_api_event(self, widget, change, data):
        
        api_key = self.w_api_key.v_model
        
        planet_key = PlanetKey(api_key)
        self.client = planet_key.client()
        
        self.valid_api = planet_key.is_active()
        
        if self.valid_api:
            self.w_api_alert.add_msg(cm.ui.success_api.msg, cm.ui.success_api.type)
            self._toggle_planet_setts(on=True)
        else:
            self.w_api_alert.add_msg(cm.ui.fail_api.msg, cm.ui.fail_api.type)
            self._toggle_planet_setts(on=False)