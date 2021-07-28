from numpy import float64

import ipyvuetify as v

import sepal_ui.sepalwidgets as sw
from sepal_ui.scripts import utils as su

from component.message import cm
from component.scripts.scripts import *
from component.widget import *


class AlertsView(v.Card):
    
    TIME_SPAN = ['24 hours', '48 hours', '7 days', 'Historic']
    
    def __init__(self, model, aoi, planet, map_, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        self.model = model
        self.aoi = aoi
        self.map_ = map_
        self.planet = planet
        
        # Widgets
        self.alert = sw.Alert()
        self.btn = sw.Btn('Get Alerts')
        
        # Recent alerts
        self.w_recent = Select(
            label="In the last",
            items=self.TIME_SPAN,
            v_model=self.model.timespan,
        )
        
        # Historic Alerts
        self.w_start = DatePicker(label='Start date (inclusive)', v_model='')
        self.w_end = DatePicker(label='End date (inclusive)', v_model='')
        self.w_historic = Flex(
            class_='d-flex',
            children=[self.w_start, self.w_end]
        ).hide()
        
        # Selection type
        self.w_alerts_type = v.RadioGroup(
            label = "Type of alerts",
            row= True,
            v_model = self.model.alerts_type,
            children = [
                v.Radio(key=1, label='Recent', value='Recent'),
                v.Radio(key=2, label='Historical', value='Historical'),
            ]
        )
        
        self.children=[
            self.w_alerts_type,
            self.w_recent,
            self.w_historic,
            self.alert,
            self.btn
        ]
        
        self.model.bind(self.w_alerts_type, 'alerts_type')\
                .bind(self.w_recent, 'timespan')\
                .bind(self.w_start, 'start_date')\
                .bind(self.w_end, 'end_date')\
        
        # Decorate buttons
        self.get_alerts = su.loading_button(
            self.alert,self.btn,True
        )(self.get_alerts)
        
        # View interactions
        self.w_alerts_type.observe(self.toggle_components)
        
        # Interatcions with map widgets
        self.map_.w_alerts.observe(self.filter_confidence, 'confidence')
        self.map_.w_alerts.observe(self.alert_list_event, 'v_model')
        
        self.btn.on_event('click', self.get_alerts)

    def toggle_components(self, change):
        """Toggle components based on Radio groups"""

        if change['new'] == 'Recent':
            su.show_component(self.w_recent)
            su.hide_component(self.w_historic)

        elif change['new'] == 'Historical':
            su.show_component(self.w_historic)
            su.hide_component(self.w_recent)
                
    def get_alerts(self, widget, change, data):
        """Get the corresponding alerts clipped to the area of interest
        and display them into the map.
        
        """
        
        if not self.model.aoi_geometry:
            raise Exception(cm.ui.valid_aoi)
        
        self.alert.add_live_msg(cm.ui.downloading_alerts, type_='info')
        
        # Get the corresponding alerts
        if self.model.alerts_type == 'Recent':
            self.model.alerts = self.model.get_recent_alerts()
            
        elif self.model.alerts_type == 'Historical':
            self.model.alerts = self.model.get_historical_alerts()
        
        # Clip alerts_gdf to the selected aoi
        self.alert.add_live_msg(msg=cm.ui.clipping,type_='info')
        self.model.aoi_alerts = self.model.clip_to_aoi()

        self.alert.add_msg(
            cm.ui.alert_number.format(
                len(self.model.aoi_alerts), self.model.timespan
            ), 
            type_='success'
        )
        
        # Update map dropdown alerts
        self.map_.w_alerts.items = list(self.model.aoi_alerts.index)
        
        # Convert aoi alert points into squares
        square_alerts = self.model.alerts_to_squares()
        
        # Add them into the map
        self.map_ + square_alerts
        
        
        self.map_.w_alerts.disabled = False
    
    
    def filter_confidence(self, change):
        """Filter alert list by confidence"""
        
        confidence = change['new']
        
        if confidence != 'All':
            self.map_.w_alerts.items = self.model.aoi_alerts[
                self.model.aoi_alerts.confidence==confidence.lower()
            ].index.to_list()
        else:
            self.map_.w_alerts.items = self.model.aoi_alerts.index.to_list()
        
        # Select first item
        self.map_.w_alerts.v_model = self.map_.w_alerts.items[0]
        
        
    def _get_metadata(self, alert_id):
        """Get a metadata table of alert and display as control """
        
        col_names = ['latitude','longitude','acq_date','acq_time','confidence']
        headers= [f'{col_name.capitalize()}: ' for col_name in col_names]
        
        values=self.model.aoi_alerts.loc[alert_id, col_names].to_list()
        values=[
            round(val,2) 
            if isinstance(val, float64) 
            else val for val in values
        ]
        
        data = zip(headers, values)
        
        metadata_table = MetadataTable(data)

        with self.map_.metadata_output:
            self.map_.metadata_output.clear_output()
            display(v.Card(width='200px', children=[metadata_table]))

        
    def alert_list_event(self, change):
        """ Update map zoom, center when selecting an alert
        and add metadata to map
        """
        
        # Get fire alert id
        self.model.current_alert = change['new']
        
        # Filter dataframe to get lat,lon
        lat = self.model.aoi_alerts.loc[self.model.current_alert]['latitude']
        lon = self.model.aoi_alerts.loc[self.model.current_alert]['longitude']
        
        self.map_.center=((lat, lon))
        self.map_.zoom=15
        self._get_metadata(self.model.current_alert)
        
        # Search and add layers to map
        if self.model.valid_api: self.planet.add_planet_imagery()
            
            

        
            
            
