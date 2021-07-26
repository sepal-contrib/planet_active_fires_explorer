import ipyvuetify as v
import sepal_ui.sepalwidgets as sw

from component.scripts.scripts import PlanetKey
from component.model import AlertModel
from component.message import cm

class PlanetTile(v.Card, sw.SepalWidget):
    
    """Stand-alone component to get the user planet inputs and validate its
    configuration.
    
    Args:
        model (Model): Model to store Planet parameters
    
    """
    
    def __init__(self, model, *args, **kwargs):
                
        super().__init__(**kwargs)
        
        self.model = model
        
        self.valid_api = False
        self.client = None
        
        self.w_api_alert = sw.Alert(
            children=[cm.ui.default_api], 
            type_='info'
        ).show()
        
        self.w_api_key = sw.PasswordField(
            label=cm.ui.insert_api,
            v_model=self.model.api_key
        )
        
        self.w_api_btn = sw.Btn('Check ', small=True,)
        
        self.w_days_before = sw.NumberField(
            label=cm.ui.days_before,
            max_=5,
            v_model=self.model.days_before,
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
            v_model=self.model.cloud_cover,
            disabled=True
        )

        
        # Capture parameters and bind them to the model
        self.model.bind(self.w_api_key, 'api_key')\
                .bind(self.w_days_before, 'days_before')\
                .bind(self.w_max_images, 'max_images')\
                .bind(self.w_cloud_cover, 'cloud_cover')\
                
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


# class PlanetTile(v.Flex):
    

    
#     def __init__(self, planet_key, w_state=None, *args, **kwargs):
        
#         self.class_='align-center mb-2'
#         self.row = True
        
#         super().__init__(*args, **kwargs)
        
#         self.api_key = ''
#         self.valid_planet = False
#         self.client = None
#         self.planet_key = planet_key
                
#         self.not_connected = sw.Tooltip(
#             widget=v.Icon(children=['mdi-circle'], color='red', x_small=True),
#             tooltip='Not connected to Planet')
        
#         self.connected = sw.Tooltip(
#             widget=v.Icon(children=['mdi-circle'], color='green', x_small=True),
#             tooltip='Connected to Planet')
        
#         self.w_api_key = sw.PasswordField(label='Planet API key', v_model=self.api_key)
#         w_api_btn = sw.Btn('Validate ', small=True,)
        
#         w_api_key = v.Flex(class_='d-flex align-center mb-2', 
#                row=True, 
#                children =[self.w_api_key, w_api_btn]
#         )
        
#         self.children = [
#             self.not_connected,
#             w_api_key,
#         ]
#         # Events
#         w_api_btn.on_event('click', self._validate_api_event)

#         # Add a statebar if there is not provided an external one
            
#     def _validate_api_event(self, widget, change, data):
        
#         self.api_key = self.w_api_key.v_model
        
#         planet_key = self.planet_key(self.api_key)
#         self.client = planet_key.client()
        
#         self.valid_planet = planet_key.is_active()
        
#         if self.valid_planet:
#             self.children.pop(0)
#             self.children = [self.connected] + self.children
#         else:
#             self.children.pop(0)
#             self.children = [self.not_connected] + self.children
