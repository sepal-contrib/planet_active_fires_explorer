from datetime import datetime
from urllib.request import urlretrieve
from pathlib import Path
from zipfile import ZipFile
import json


import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon

from traitlets import Any, Unicode, Int
from ipyleaflet import GeoJSON

from sepal_ui import model

from component.parameter import *


class AlertModel(model.Model):
    
    # Input parameters
    timespan = Unicode('24 hours').tag(sync=True)
    
    # Planet parameters
    
    cloud_cover = Int(20).tag(sync=True)
    days_before = Int(0).tag(sync=True)
    max_images = Int(6).tag(sync=True)
    api_key = Unicode('').tag(sync=True)
    
    # Aoi parameters
    aoi_method = Unicode('').tag(sync=True)
    country = Unicode('').tag(sync=True)
    
    # Alerts type parameters 
    alerts_type = Unicode('Recent').tag(sync=True)
    start_date = Unicode('').tag(sync=True)
    end_date = Unicode('').tag(sync=True)
    
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        # Alerts
        self.alerts = None
        self.aoi_alerts = None
        self.current_alert = None 
        
        # Planet
        self.client = None
        self.valid_api = False
                
        # It will store both draw and country geometry
        self.aoi_geometry = None
        
    
    def get_historical_alerts(self):
        """Get historical alerts"""

        start = datetime.strptime(self.start_date, '%Y-%m-%d')
        end = datetime.strptime(self.end_date, '%Y-%m-%d')                

        # Validate y2 >= y1
        if end < start:
            raise Exception('End date must be older than starting')


        # Get unique year(s)
        years = list(range(start.year, end.year+1))

        # Download all the fires between the given dates
        all_dfs = []
        for y in years:

            # Verify if the files is not previously downloaded
            out_file = HISTORIC_DIR/f'historic_fires_{y}.zip'

            if not out_file.exists():
                urlretrieve(HISTORIC_URL.format(y), out_file)

            # Open all fires into the zipped files and merge 
            # thme into one single DataFrame

            zip_file = ZipFile(out_file)
            dfs = pd.concat([
                pd.read_csv(zip_file.open(text_file.filename))
                for text_file in zip_file.infolist()
                if text_file.filename.endswith('.csv')
            ])
            all_dfs.append(dfs)

        dfs = pd.concat(all_dfs)

        # Filter them with its date
        dfs.acq_date = pd.to_datetime(dfs.acq_date)

        return dfs[(dfs.acq_date>=start) & (dfs.acq_date<=end)]
    
    def get_url(self, satellite):
        """ Get the proper recent url based on the input satallite"""
        
        satellites = {
            'viirs': ('SUOMI_VIIRS_C2', 'suomi-npp-viirs-c2'),
            'modis': ('MODIS_C6', 'c6'),
            'viirsnoa': ('J1_VIIRS_C2', 'noaa-20-viirs-c2'),
        }
        
        sat = satellites[satellite]

        timespan = self.timespan.replace(' hours', 'h').replace(' days','d')
        url = RECENT_URL.format(sat[1], sat[0], timespan)
            
        return url
    
    def get_recent_alerts(self):
        """Donwload and create a geodataframe based on the recent alerts"""
        
        url = self.get_url('viirs')
        
        df = pd.read_csv(url)
        
        alerts_gdf = gpd.GeoDataFrame(
            df, 
            geometry=gpd.points_from_xy(df.longitude, df.latitude), 
            crs="EPSG:4326"
        )
        
        return alerts_gdf
    
    def clip_to_aoi(self):
        """Clip recent or historical geodataframe with area of interest"""
        
        if not self.aoi_geometry:
            raise Exception(cm.ui.valid_aoi)
        
        alerts = self.alerts
        clip_geometry = gpd.GeoDataFrame.from_features(
            self.aoi_geometry
        ).set_crs('EPSG:4326').iloc[0].geometry
        
        return alerts[alerts.geometry.intersects(clip_geometry)]
    
    def alerts_to_squares(self):
        
        # Convert alert's geometries to 54009 (projected crs) 
        # and use 375m as buffer 
        geometry_col = self.aoi_alerts\
                .to_crs('EPSG:3116')['geometry']\
                .buffer(187.5, cap_style=3).copy()
        
        self.aoi_alerts = self.aoi_alerts.assign(geometry=geometry_col)
        
        json_aoi_alerts = json.loads(
            self.aoi_alerts.to_crs('EPSG:4326').to_json()
        )
        
        return GeoJSON(
            data=json_aoi_alerts, name='Alerts', 
            style={                                    
                'color': 'red', 'fillOpacity': 0.1, 'weight': 2
            },
            hover_style={
                'color': 'white', 'dashArray': '0', 'fillOpacity': 0.5
            },
        )