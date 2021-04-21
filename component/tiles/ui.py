import json
from pathlib import Path
import pytz
import geopandas as gpd
import pandas as pd
from numpy import float64

from shapely.geometry import Point, Polygon
from shapely_geojson import dumps

from ipyleaflet import GeoJSON, TileLayer, Marker
import ipyvuetify as v

from sepal_ui import sepalwidgets as sw
from ..message import cm
from ..scripts.scripts import *
from ..widget.custom_widgets import *


class UI(v.Layout):

    def __init__(self, fire_parameters, planet_parameters, map_, **kwargs):
        
        """ User interface for Planet Active Fires Explorer
        
        Args:
            fire_parameters (v.Card tile): Parameters to explore alerts
            planet_parameters (v.Card tile): Planet tile to validate API keys
            map_ (AlertMap): Module map based on SepalMap
        
        """
        
        self.class_='pa-2'

        super().__init__(**kwargs)
        
        # Start workspace
        self.root_dir, self.data_dir = self._workspace()
        
        self.alerts = None
        self.aoi = None
        self.aoi_alerts = None
        self.current_alert = None

        self.lat = None
        self.lon = None
        
        # Widgets
        self.param = fire_parameters
        self.planet_param = planet_parameters
        self.map_=map_
        
        self.w_alerts = DynamicSelect(disabled=True)

        # Events

        self.w_alerts.observe(self.alert_list_event, 'v_model')
        self.w_alerts.observe(self.filter_confidence, 'confidence')
        
        
        self.map_.reload_btn.on_click(self.add_layers)
        
        
        self.param.w_run.on_event('click', self._get_alerts)
        
        # Map events
        
        self.map_.on_interaction(self._return_coordinates)
        
        # View
        
        self.children = [
            # Left flex options panel
            v.Flex(
                xs3 =True, 
                children =[
                    self.param,
                    self.planet_param,
            ]),
            v.Flex(
                class_='ml-2', 
                xs9 = True, 
                children =[
                    self.w_alerts,
                    self.map_
            ])
        ]

        
    def filter_confidence(self, change):
        """Filter alert list by confidence"""
        
        confidence = change['new']
        # Restart previous selected indexes
        self.w_alerts.v_model = ''
        
        if confidence != 'All':
            self.w_alerts.items = self.aoi_alerts[self.aoi_alerts.confidence==confidence.lower()].index.to_list()
        else:
            self.w_alerts.items = self.aoi_alerts.index.to_list()

    def _get_metadata(self, alert_id):
        """Awful way to get a metadata table of alert and display it 
        within self.map_ as control
        
        """
        col_names = ['latitude','longitude','acq_date','acq_time','confidence']
        headers= [f'{col_name.capitalize()}: ' for col_name in col_names]
        
        values=self.aoi_alerts.loc[alert_id, col_names].to_list()
        values=[round(val,2) if isinstance(val, float64) else val for val in values]
        
        self.aoi_alerts.loc[self.current_alert,]
        confidence = {'low':'red', 'high':'green', 'nominal':'orange'}

        data='<tbody>'
        for header, value in zip(headers, values):
            if header=='Confidence:':
                color = confidence[values[4]]
                data+=f'<tr><th>{header}</th><td><v-chip small color={color}>{value}</v-chip></td></tr>'
            else:
                data+=f'<tr><th>{header}</th><td style="font-size:90%">{value}</td></tr>'
        data+='</tbody>'

        html=f"""
          <v-simple-table dense>
                {data}
          </v-simple-table>
        """
        class Table(v.VuetifyTemplate):

            template = Unicode(html).tag(sync=True)

        with self.map_.metadata_output:
            self.map_.metadata_output.clear_output()
            display(v.Card(width='200px', children=[Table()]))
                    
    def _return_coordinates(self, **kwargs):

        if kwargs.get('type') == 'click':

            # Remove markdown if there is one
            remove_layers_if(self.map_, 'type', equals_to='manual', _metadata=True)

            self.lat, self.lon = kwargs.get('coordinates')

            marker = Marker(location=kwargs.get('coordinates'), 
                            alt='Manual', 
                            title='Manual', 
                            draggable=False,
                            name='Manual marker'
                           )
            marker.__setattr__('_metadata', {'type':'manual', 'id': None})

            self.map_.add_layer(marker)
        
    def _get_items(self):

        geom = json.loads(dumps(Point(self.lon, self.lat).buffer(0.001, cap_style=3)))
        
        # Get the current year/month/day
        now = datetime.datetime.now(tz=pytz.timezone('UTC'))
        
        days_before = ([x[1] for x in list(zip(self.param.TIME_SPAN,[1,2,7],)) if self.param.timespan == x[0]])[0]
        days_before += self.planet_param.days_before
        start_date = now-datetime.timedelta(days=days_before)
        req = build_request(geom, start_date, now, cloud_cover=self.planet_param.cloud_cover/100)
        items = get_items('Alert', req, self.planet_param.client)
        
        return items
    
    def _prioritize_items(self):
        
        self.map_.w_state_bar.add_msg(cm.ui.searching_planet, loading=True)
        
        items = self._get_items()
        items = [(item['properties']['item_type'], 
                  item['id'],
                  pd.to_datetime(item['properties']['acquired']).strftime('%Y-%m-%d-%H:%M')
                 ) for item in items[1]]
        
        items_df = pd.DataFrame(data=items, columns=['item_type', 'id', 'date'])
        items_df.sort_values(by=['item_type'])
        items_df.drop_duplicates(subset=['date', 'id'])
        
        # If more than one day is selected, get one image per day.
        
        if self.planet_param.days_before:
            items_df.date = pd.to_datetime(items_df.date)
            items_df = items_df.groupby(
                [items_df.date.dt.year, items_df.date.dt.day]
            ).nth(1).reset_index(drop=True)
            
        if self.planet_param.max_images:
            items_df = items_df.head(self.planet_param.max_images)
        
        if len(items_df) == 1:
            self.map_.w_state_bar.add_msg(cm.ui.one_image.format(len(items_df)), loading=False)
        elif len(items_df):
            self.map_.w_state_bar.add_msg(cm.ui.number_images.format(len(items_df)), loading=False)
        else:
            self.map_.w_state_bar.add_msg(cm.ui.no_planet, loading=False)
        
        return items_df

    def add_layers(self, event=None):
        """Search planet imagery and add them to self.map_"""
        
        # Validate whether Planet API Key is valid,
        # and if there is already selected coordinates.
        
        if self.validate_state_bar(): 
        
            items_df = self._prioritize_items()

            # remove all previous loaded assets

            remove_layers_if(self.map_, 'attribution', 'Imagery © Planet Labs Inc.')

            for i, row in items_df.iterrows():
                layer = TileLayer(
                    url=f'https://tiles0.planet.com/data/v1/{row.item_type}/{row.id}/{{z}}/{{x}}/{{y}}.png?api_key={self.planet_param.api_key}',
                    name=f'{row.item_type}, {row.date}',
#                     max_zoom=15,
                    attribution='Imagery © Planet Labs Inc.'
                )
                layer.__setattr__('_metadata', {'type':row.item_type, 'id':row.id})
                if row.id not in [layer._metadata['id'] for layer in self.map_.layers if hasattr(layer, '_metadata')]:
                    self.map_+layer
    
    def validate_state_bar(self):
        
        if not self.planet_param.valid_api:
            self.map_.w_state_bar.add_msg(cm.ui.no_key, loading=False)
            
        elif not all((self.planet_param.valid_api, self.lat, self.lon)):
            self.map_.w_state_bar.add_msg(cm.ui.no_latlon, loading=False)
            
        else:
            return True            
            

    def alert_list_event(self, change):
        """ Update map zoom, center when selecting an alert
        and add metadata to map
        
        """
        
        # Get fire alert id
        self.current_alert = change['new']
        
        # Filter dataframe to get lat,lon
        
        self.lat = self.aoi_alerts.loc[self.current_alert]['latitude']
        self.lon = self.aoi_alerts.loc[self.current_alert]['longitude']
        
        self.map_.center=((self.lat,self.lon))
        self.map_.zoom=15
        self._get_metadata(self.current_alert)
        
        # Search and add layers to map
        if self.planet_param.valid_api: self.add_layers()
        
        
    def validate_inputs(self):
        
        if not self.param.aoi:
            self.param.w_alert.add_msg(cm.ui.valid_aoi,type_='error')
            self.restore_widgets()

            raise
    
    def restore_widgets(self):
        
        self.w_run.disabled=False
        self.w_run.loading=False
        self.w_alerts.items = []
        self.w_alerts.v_model = None

    def _get_url(self, satellite):
        
        satellites = {
            'viirs': ('SUOMI_VIIRS_C2', 'suomi-npp-viirs-c2'),
            'modis': ('MODIS_C6', 'c6'),
            'viirsnoa': ('J1_VIIRS_C2', 'noaa-20-viirs-c2'),
        
        }
        
        sat = satellites[satellite]
        timespan = self.param.timespan.replace(' hours', 'h').replace(' days','d')
        
        url=f"https://firms.modaps.eosdis.nasa.gov/data/active_fire/{sat[1]}/csv/{sat[0]}_Global_{timespan}.csv"
        return url
        
    def _get_alerts(self, widget, change, data):
        
        self.validate_inputs()
        widget.toggle_loading()
        
        self.param.w_alert.add_live_msg(cm.ui.downloading_alerts, type_='info')
        
        url = self._get_url('viirs')
        
        df = pd.read_csv(url)
        alerts_gdf = gpd.GeoDataFrame(df, 
                                      geometry=gpd.points_from_xy(df.longitude, 
                                                                  df.latitude), 
                                      crs="EPSG:4326")
        
        self.alerts = alerts_gdf
        
        self.aoi_alerts = self._clip_to_aoi()

        self.param.w_alert.add_msg(
            cm.ui.alert_number.format(len(self.aoi_alerts), self.param.timespan), 
            type_='success')
        
        alert_list_item = list(self.aoi_alerts.index)
        self.w_alerts.items = alert_list_item
                
        # Convert alert's geometries to 54009 (projected crs) and use 375m as buffer 
        geometry_col = self.aoi_alerts.to_crs('EPSG:3116')['geometry'].buffer(187.5, cap_style=3).copy()
        self.aoi_alerts = self.aoi_alerts.assign(geometry=geometry_col)
        json_aoi_alerts = json.loads(self.aoi_alerts.to_crs('EPSG:4326').to_json())
        
        json_aoi_alerts = GeoJSON(data=json_aoi_alerts,
                                name='Alerts', 
                                style={                                    
                                     'color': 'red', 
                                     'fillOpacity': 0.1, 
                                     'weight': 2
                                 },
                                hover_style={
                                    'color': 'white', 
                                    'dashArray': '0', 
                                    'fillOpacity': 0.5
                                },)
        
        
        self.map_+json_aoi_alerts
        self.w_alerts.disabled = False
        widget.toggle_loading()
    
    def _clip_to_aoi(self):
        
        # Clip alerts_gdf to the selected aoi
        ""
        self.param.w_alert.add_live_msg(msg=cm.ui.clipping,type_='info')
        
        clip_geometry = Polygon(self.param.aoi['coordinates'][0])
        
        alerts = self.alerts[self.alerts.geometry.intersects(clip_geometry)]
        
        return alerts
    
    def _workspace(self):
        """ Creates the workspace necessary to store and manipulate the module

        return:
            Returns environment Paths

        """

        base_dir = Path('~', 'module_results').expanduser()
        root_dir = base_dir/'Planet_fire_explorer'
        data_dir = root_dir/'data'
        
        base_dir.mkdir(exist_ok=True)
        root_dir.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)

        return root_dir, data_dir