import os
from pathlib import Path
import geopandas as gpd
from traitlets import Unicode, link, observe
import ipyvuetify as v 
import sepal_ui.sepalwidgets as sw
from component.widget.custom_widgets import *

class AOI(v.Layout):
    
    shapefile = Unicode('').tag(sync=True)
    
    def __init__(self, statebar=None, **kwargs):
    
        super().__init__(**kwargs)
        
        self.gdf = None
        
        # Parameters
        self.out_path = Path('')
        self.json_path = None
        
        # Widgets
        self.shape_input = sw.FileInput(['.shp'], os.getcwd())
        
        self.w_state_bar = sw.StateBar(done=True) if not statebar else statebar
        
        # Link behaviours 
        
        link((self.shape_input, 'file'), (self, 'shapefile'))
        
        # View
        
        self.children=[
            v.Layout(row=True, children=[
                self.shape_input,
            ])
        ]
        
        # Add a statebar if there is not provided an external one
        if not statebar: self.children = self.children + [self.w_state_bar]

    @observe('shapefile')
    def shape_to_geojson(self, change):
        """ Converts shapefile into Json file"""
        
        shp_file_path = Path(self.shapefile)
        if shp_file_path.suffix == '.shp':

            self.gdf = gpd.read_file(str(shp_file_path))
            self.gdf = self.gdf.to_crs("EPSG:4326")
            
            self.json_path = shp_file_path.parent/f'{shp_file_path.stem}.geojson'
            
            if not self.json_path.exists():
                self.w_state_bar.add_msg('Converting shape to GeoJSON', done=False)
                self.gdf.to_file(str(self.json_path), driver='GeoJSON')
                self.w_state_bar.add_msg('Done', done=True)
            else:
                self.w_state_bar.add_msg('Geojson file already created', done=True)
                
    def get_ipyleaflet_geojson(self):
        """Returns GeoJSON ipyleaflet object from Json file"""
        
        if self.json_path:
            self.w_state_bar.add_msg('Converting shape to GeoJSON', done=False)
            with open(self.json_path) as f:
                data = json.load(f)        
                ipygeojson = GeoJSON(
                    data=data,
                    name=self.json_path.stem, 
                    style={'color': 'green', 'fillOpacity': 0, 'weight': 3})

            self.w_state_bar.add_msg('Done', done=True)
        
            return ipygeojson
        else:
            self.w_state_bar.add_msg('There is not a shapefile selected.', done=True)

            
class PlanetTile(v.Flex):
    
    def __init__(self, planet_key, w_state=None, *args, **kwargs):
        
        self.class_='align-center mb-2'
        self.row = True
        
        super().__init__(*args, **kwargs)
        
        self.api_key = ''
        self.valid_planet = False
        self.client = None
        self.planet_key = planet_key
        
#         self.w_state = StateBar(done=True) if not w_state else w_state
        
        self.not_connected = Tooltip(
            widget=v.Icon(children=['mdi-circle'], color='red', x_small=True),
            tooltip='Not connected to Planet')
        
        self.connected = Tooltip(
            widget=v.Icon(children=['mdi-circle'], color='green', x_small=True),
            tooltip='Connected to Planet')
        
        self.w_api_key = sw.PasswordField(label='Planet API key', v_model=self.api_key)
        w_api_btn = sw.Btn('Validate ', small=True,)
        
        w_api_key = v.Flex(class_='d-flex align-center mb-2', 
               row=True, 
               children =[self.w_api_key, w_api_btn]
        )
        
        self.children = [
            self.not_connected,
            w_api_key,
        ]
        # Events
        w_api_btn.on_event('click', self._validate_api_event)

        # Add a statebar if there is not provided an external one
            
    def _validate_api_event(self, widget, change, data):
        
        self.api_key = self.w_api_key.v_model
        
        planet_key = self.planet_key(self.api_key)
        self.client = planet_key.client()
        
        self.valid_planet = planet_key.is_active()
        
        if self.valid_planet:
            self.children.pop(0)
            self.children = [self.connected] + self.children
        else:
            self.children.pop(0)
            self.children = [self.not_connected] + self.children
