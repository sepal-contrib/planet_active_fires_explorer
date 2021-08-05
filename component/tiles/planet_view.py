import json
import datetime
from shapely.geometry import Point
import pandas as pd
from shapely_geojson import dumps

from ipyleaflet import TileLayer

import ipyvuetify as v
import sepal_ui.sepalwidgets as sw

from component.scripts.scripts import *
from component.model import AlertModel
from component.message import cm

class PlanetView(v.Card, sw.SepalWidget):
    
    """Stand-alone component to get the user planet inputs and validate its
    configuration.
    
    Args:
        model (Model): Model to store Planet parameters
    
    """
    
    def __init__(self, model, map_, *args, **kwargs):
                
        super().__init__(**kwargs)
        
        self.model = model
        self.map_ = map_
        
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
        
        self.w_days_after = sw.NumberField(
            label=cm.ui.days_after,
            max_=5,
            v_model=self.model.days_after,
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
            .bind(self.w_days_after, 'days_after')\
            .bind(self.w_max_images, 'max_images')\
            .bind(self.w_cloud_cover, 'cloud_cover')
                
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
            self.w_days_after,
            self.w_cloud_cover,
        ]
        
        
        # Interactions with Map
        
        self.map_.reload_btn.on_click(self.add_planet_imagery)

    def _toggle_planet_setts(self, on=True):
        
        if on:
            self.w_days_after.disabled = False
            self.w_days_before.disabled = False
            self.w_cloud_cover.disabled = False
            self.w_max_images.disabled = False
        else:
            self.w_days_after.disabled = True
            self.w_days_before.disabled = True
            self.w_cloud_cover.disabled = True
            self.w_max_images.disabled = True
            
    def validate_api_event(self, widget, change, data):
        """Event to validate the Planet API Key input and activate/deactivate
        view widgets.
        """
        
        api_key = self.w_api_key.v_model
        planet_key = PlanetKey(api_key)
        
        self.model.client = planet_key.client()
        self.model.valid_api = planet_key.is_active()
        
        if self.model.valid_api:
            self.w_api_alert.add_msg(
                cm.ui.success_api.msg, cm.ui.success_api.type
            )
            self._toggle_planet_setts(on=True)
        else:
            self.w_api_alert.add_msg(cm.ui.fail_api.msg, cm.ui.fail_api.type)
            self._toggle_planet_setts(on=False)

    def _get_items(self):
        """Get planet items based on the current coordinates"""
        
        # Get current map coordinates
        lat = self.map_.lat
        lon = self.map_.lon
        
        geom = json.loads(dumps(Point(lon, lat).buffer(0.001, cap_style=3)))

        acqdate = self.model.aoi_alerts.loc[self.model.current_alert].acq_date
        
        now = datetime.datetime.strptime(acqdate, '%Y-%m-%d')
        
        days_before = self.model.days_before
        days_after = self.model.days_after
        
        start_date = now-datetime.timedelta(days=days_before)
        future = now+datetime.timedelta(days=days_after+1)
        
        req = build_request(
            geom, start_date, future, cloud_cover=self.model.cloud_cover/100
        )
        
        return get_items('Alert', req, self.model.client)
    
    def _prioritize_items(self, items):
        """Prioritize planet items"""
        
        items = [
            (
                item['properties']['item_type'], 
                item['id'],
                pd.to_datetime(
                    item['properties']['acquired']
                ).strftime('%Y-%m-%d-%H:%M')
            ) for item in items[1]]
        
        items_df = pd.DataFrame(
            data=items, columns=['item_type', 'id', 'date']
        )
        items_df.sort_values(by=['item_type'])
        items_df.drop_duplicates(subset=['date', 'id'])
        
        # If more than one day is selected, get one image per day.
        
        if self.model.days_before:
            items_df.date = pd.to_datetime(items_df.date)
            items_df = items_df.groupby(
                [items_df.date.dt.year, items_df.date.dt.day]
            ).nth(1).reset_index(drop=True)
        
        if self.model.max_images:
            items_df = items_df.head(self.model.max_images)
        
        if len(items_df) == 1:
            self.map_.w_state_bar.add_msg(
                cm.ui.one_image.format(len(items_df)), 
                loading=False
            )
        elif len(items_df):
            self.map_.w_state_bar.add_msg(
                cm.ui.number_images.format(len(items_df)), 
                loading=False
            )
        else:
            self.map_.w_state_bar.add_msg(
                cm.ui.no_planet, 
                loading=False
            )
        
        return items_df

    def add_planet_imagery(self, event=None):
        """Search planet imagery and add them to self
        
        Args:
            event (optional): If the button is clicked, we need to pass this
                parameter, otherwise, we could trigger this function from 
                outside.
        """
        
        # Validate whether Planet API Key is valid,
        # and if there is already selected coordinates.
        
        if self.validate_state_bar():
            
            self.map_.w_state_bar.add_msg(cm.ui.searching_planet, loading=True)
            
            items = self._get_items()
            
            items_df = self._prioritize_items(items)

            # remove all previous loaded assets

            self.map_.remove_layers_if(
                'attribution', 'Imagery © Planet Labs Inc.'
            )

            for i, row in items_df.iterrows():
                layer = TileLayer(
                    url=PLANET_TILES_URL.format(
                        row.item_type, row.id, self.model.api_key
                    ),
                    name=f'{row.item_type}, {row.date}',
                    attribution='Imagery © Planet Labs Inc.'
                )
                layer.__setattr__(
                    '_metadata', {'type':row.item_type, 'id':row.id}
                )
                if row.id not in [layer._metadata['id'] 
                                  for layer 
                                  in self.map_.layers 
                                  if hasattr(layer, '_metadata')]:
                    self.map_+layer
                    
    def validate_state_bar(self):
        
        if not self.model.valid_api:
            self.map_.w_state_bar.add_msg(cm.ui.no_key, loading=False)
            
        elif not all((self.model.valid_api, self.map_.lat, self.map_.lon)):
            self.map_.w_state_bar.add_msg(cm.ui.no_latlon, loading=False)
            
        else:
            return True

            