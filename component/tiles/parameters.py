import geopandas as gpd

from traitlets import Int, Unicode, link
import ipyvuetify as v

from os.path import expanduser

from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su
from ..message import cm
from ..scripts.scripts import *
from ..widget.custom_widgets import *

COUNTRIES = gpd.read_file('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json')

class Parameters(v.Card, sw.SepalWidget):
    
    TIME_SPAN = ['24 hours', '48 hours', '7 days', 'Historic']
    timespan = Unicode('24 hours').tag(sync=True)
    
    def __init__(self, **kwargs):
                
        super().__init__(**kwargs)
                
        self.w_alert = Alert()
        
        self.w_spantime = v.Select(
            label="In the last",
            items=self.TIME_SPAN,
            v_model=self.timespan,
        )
        
        home = expanduser("~")
        self.input_file = sw.FileInput(['.csv'], home)
        self.w_load = v.ExpansionPanels(children=[
            v.ExpansionPanel(children=[
                v.ExpansionPanelHeader(children=['Use a custom csv file']),
                v.ExpansionPanelContent(children=[
                    v.Flex(class_='d-flex align-center',
                        children=[
                            self.input_file
                        ]
                    )
                ])
            ])
        ])
        
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

        self.children = [
            v.CardTitle(children=['Alerts settings']),
            self.w_spantime,
            self.w_aoi_method,
            self.w_countries,
            self.w_load,
            self.w_run,
            self.w_alert,
        ]
        
        link((self.w_spantime, 'v_model'),(self, 'timespan'))


class PlanetParameters(v.Card, sw.SepalWidget):
    
    cloud_cover = Int(20).tag(sync=True)
    days_before = Int(0).tag(sync=True)
    max_images = Int(6).tag(sync=True)
    api_key = Unicode('').tag(sync=True)
    
    def __init__(self, **kwargs):
                
        super().__init__(**kwargs)
        
        self.valid_api = False
        self.client = None
        
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