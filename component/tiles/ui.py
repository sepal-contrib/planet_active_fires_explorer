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

    def __init__(self, map_, **kwargs):
        
        self.class_='pa-2'

        super().__init__(**kwargs)
        
        # Start workspace
        
        
        

        # Events



        
        
        
        self.param.w_run.on_event('click', self._get_alerts)
        
        # Map events
        
        self.map_.on_interaction(self._return_coordinates)
        
        # View
        self.children = [
            self.w_alerts,
            self.map_
        ]
        

    
