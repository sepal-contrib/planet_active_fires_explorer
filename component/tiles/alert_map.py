import json
import pytz

import pandas as pd

import geopandas as gpd
from pathlib import Path
from numpy import float64

from shapely.geometry import Point, Polygon
from shapely_geojson import dumps

from sepal_ui import mapping as m
from ipywidgets import Button, Layout, Output
from ipyleaflet import WidgetControl, FullScreenControl, GeoJSON, TileLayer, Marker

from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su
from ..message import cm
from ..scripts.scripts import *
from ..widget.custom_widgets import *

COUNTRIES = gpd.read_file('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json')

class AlertMap(m.SepalMap):
    
    def __init__(self, parameters, planet_parameters, *args, **kwargs):
        
        
        
        self.root_dir, self.data_dir = self._workspace()
        
        self.param = parameters
        self.planet_param = planet_parameters
        
        self.aoi = None
        self.alerts = None
        self.aoi_alerts = None
        self.current_alert = None

        self.lat = None
        self.lon = None
        
        
        super().__init__(
            basemaps=['Google Satellite'], 
            dc=True, 
            *args, 
            **kwargs
        )
        
        self.show_dc()
        self.add_control(FullScreenControl())
        
        self.reload_btn = Button(
            disabled=False,
            tooltip='Reload Planet imagery',
            icon='refresh',
            layout=Layout(
                width='30px', 
                height='30px', 
                line_height='30px', 
                padding='0px'
            )
        )
        
        # Create output space for metadata
        self.metadata_output = Output()
        
        # Add metadata_output as WidgetControl to the map
        metadata_control = WidgetControl(
            widget=self.metadata_output, 
            position='bottomright', 
            transparent_bg=True)
        self.add_control(metadata_control)
        
        # Add controls in this way to make the new one as first in the list
        self.controls = tuple([
                WidgetControl(
                    widget=self.reload_btn, 
                    position='topright', 
                    transparent_bg=True
                )] + 
            [c for c in self.controls]
        )
        
        self.w_state_bar = StateBar(loading=False)
        
        # Add controls in this way to make the new one as first in the list
        self.controls = tuple([
            WidgetControl(
                widget=self.w_state_bar)]+[c for c in self.controls]
        )
        
        # Add fires and planet parameters
        
        self.parameters_btn = Button(
            tooltip='Toggle parameters',
            icon='navicon',
            layout=Layout(
                width='30px', 
                height='30px', 
                line_height='30px', 
                padding='0px'
            )
        )
        options_control = WidgetControl(
            widget=self.parameters_btn, 
            position='topleft', 
            transparent_bt=True
        )
        
        self.add_control(options_control)
                
        self.close_param = v.Icon(children=['mdi-close'])
        self.w_parameters = Card(
            class_='px-2',
            children=[
                v.CardTitle(
                    children=['Settings', v.Spacer(),self.close_param]),
                v.Flex(class_='d-flex',children=[
                    self.planet_param,
                    v.Divider(vertical=True, class_='mx-4'),
                    self.param
                ])
            ]
        )
        
        parameters_control = WidgetControl(
            widget=self.w_parameters, 
            position='bottomright', 
            transparent_bg=True
        )
        self.controls  = tuple([parameters_control] + [c for c in self.controls])
        
        self.w_alerts = DynamicSelect(disabled=True)
        alerts_control = WidgetControl(widget=self.w_alerts, position='topright', transparent_bg=True)
        self.controls  = tuple([alerts_control] + [c for c in self.controls])
        
        self.parameters_btn.on_click(self.toggle_param_visualization)
        self.dc.on_draw(self.handle_draw)
        
        self.param.w_countries.observe(self.add_country_event, 'v_model')
        self.param.w_aoi_method.observe(self.aoi_method_event, 'v_model')
        
        self.w_alerts.observe(self.alert_list_event, 'v_model')
        self.w_alerts.observe(self.filter_confidence, 'confidence')
        
        self.reload_btn.on_click(self.add_layers)
        self.param.w_run.on_event('click', self._get_alerts)
        
        self.close_param.on_event('click', self.close_parameters)
        
        self.on_interaction(self._return_coordinates)
    
    def close_parameters(self, *args):
        
        self.w_parameters.hide()
        
    def toggle_param_visualization(self, *args):
        
        self.w_parameters.toggle_viz()
        
    def remove_layers(self):
        
        # get map layers
        layers = self.layers
        
        # loop and remove layers 
        [self.remove_last_layer() for _ in range(len(layers))]
        
        
    def add_country_event(self, change):
        
        self.remove_layers()
        
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
        
        bounds = geometry.bounds

        self.zoom_bounds(bounds)
        self.center = (lat, lon)
        self.add_layer(aoi)
        
    def aoi_method_event(self, change):
        
        self.remove_layers()
        
        if change['new'] == 'Select country':
            self.hide_dc()
            su.show_component(self.param.w_countries)

        else:
            su.hide_component(self.param.w_countries)
            self.show_dc()
            
            
    def handle_draw(self, target, action, geo_json):
        
        self.remove_layers()
        if action == 'created':
            self.aoi = geo_json['geometry']
            
    def filter_confidence(self, change):
        """Filter alert list by confidence"""
        
        confidence = change['new']
        
        if confidence != 'All':
            self.w_alerts.items = self.aoi_alerts[self.aoi_alerts.confidence==confidence.lower()].index.to_list()
        else:
            self.w_alerts.items = self.aoi_alerts.index.to_list()
        
        # Select first item
        self.w_alerts.v_model = self.w_alerts.items[0]

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

        with self.metadata_output:
            self.metadata_output.clear_output()
            display(v.Card(width='200px', children=[Table()]))
                    
    def _return_coordinates(self, **kwargs):

        if kwargs.get('type') == 'click':

            # Remove markdown if there is one
            remove_layers_if(self, 'type', equals_to='manual', _metadata=True)

            self.lat, self.lon = kwargs.get('coordinates')

            marker = Marker(location=kwargs.get('coordinates'), 
                            alt='Manual', 
                            title='Manual', 
                            draggable=False,
                            name='Manual marker'
                           )
            marker.__setattr__('_metadata', {'type':'manual', 'id': None})

            self.add_layer(marker)
        
    def _get_items(self):

        geom = json.loads(dumps(Point(self.lon, self.lat).buffer(0.001, cap_style=3)))
        
        # Get the current year/month/day
        #now = datetime.datetime.now(tz=pytz.timezone('UTC'))
        
        #now = datetime.datetime(2020, 12, 31, 0, 0, 0, 0, pytz.UTC)
        #start_date = datetime.datetime(2020, 1, 1, 0, 0, 0, 0, pytz.UTC)
        
        now = datetime.datetime.strptime(self.acqdate, '%Y-%m-%d')
        #days_before = ([x[1] for x in list(zip(self.param.TIME_SPAN,[1,2,7],)) if self.param.timespan == x[0]])[0]
        days_before = self.planet_param.days_before
        future = now+datetime.timedelta(days=days_before)
        start_date = now-datetime.timedelta(days=days_before)
        req = build_request(geom, start_date, future, cloud_cover=self.planet_param.cloud_cover/100)
        items = get_items('Alert', req, self.planet_param.client)
        
        return items
    
    def _prioritize_items(self):
        
        self.w_state_bar.add_msg(cm.ui.searching_planet, loading=True)
        
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
            self.w_state_bar.add_msg(cm.ui.one_image.format(len(items_df)), loading=False)
        elif len(items_df):
            self.w_state_bar.add_msg(cm.ui.number_images.format(len(items_df)), loading=False)
        else:
            self.w_state_bar.add_msg(cm.ui.no_planet, loading=False)
        
        return items_df

    def add_layers(self, event=None):
        """Search planet imagery and add them to self"""
        
        # Validate whether Planet API Key is valid,
        # and if there is already selected coordinates.
        
        if self.validate_state_bar(): 
        
            items_df = self._prioritize_items()

            # remove all previous loaded assets

            remove_layers_if(self, 'attribution', 'Imagery © Planet Labs Inc.')

            for i, row in items_df.iterrows():
                layer = TileLayer(
                    url=f'https://tiles0.planet.com/data/v1/{row.item_type}/{row.id}/{{z}}/{{x}}/{{y}}.png?api_key={self.planet_param.api_key}',
                    name=f'{row.item_type}, {row.date}',
#                     max_zoom=15,
                    attribution='Imagery © Planet Labs Inc.'
                )
                layer.__setattr__('_metadata', {'type':row.item_type, 'id':row.id})
                if row.id not in [layer._metadata['id'] for layer in self.layers if hasattr(layer, '_metadata')]:
                    self+layer
    
    def validate_state_bar(self):
        
        if not self.planet_param.valid_api:
            self.w_state_bar.add_msg(cm.ui.no_key, loading=False)
            
        elif not all((self.planet_param.valid_api, self.lat, self.lon)):
            self.w_state_bar.add_msg(cm.ui.no_latlon, loading=False)
            
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
        self.acqdate = self.aoi_alerts.loc[self.current_alert]['acq_date']
        
        self.center=((self.lat,self.lon))
        self.zoom=15
        self._get_metadata(self.current_alert)
        
        # Search and add layers to map
        if self.planet_param.valid_api: self.add_layers()
        
        
    def validate_inputs(self):
        
        if not self.aoi:
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
        if self.param.timespan=='Historic':
            #print(self.param.input_file.v_model)
            url=Path(self.param.input_file.v_model)
            
        else:
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
        
        
        self+json_aoi_alerts
        self.w_alerts.disabled = False
        widget.toggle_loading()
    
    def _clip_to_aoi(self):
        
        # Clip alerts_gdf to the selected aoi
        ""
        self.param.w_alert.add_live_msg(msg=cm.ui.clipping,type_='info')
        
        clip_geometry = Polygon(self.aoi['coordinates'][0])
        
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