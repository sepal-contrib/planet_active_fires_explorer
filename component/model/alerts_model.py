import json
import pytz
from datetime import datetime
import urllib
from pathlib import Path
from zipfile import ZipFile
from tqdm.auto import tqdm


import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon

from traitlets import Any, Unicode, Int
from ipyleaflet import GeoJSON

from sepal_ui.scripts.utils import random_string
from sepal_ui import model

from component.parameter import *
import component.scripts.scripts as cs


class AlertModel(model.Model):


    # Input parameters
    timespan = Unicode("24h").tag(sync=True)

    # Planet parameters

    cloud_cover = Int(20).tag(sync=True)
    days_before = Int(1).tag(sync=True)
    days_after = Int(1).tag(sync=True)
    max_images = Int(6).tag(sync=True)
    api_key = Unicode("").tag(sync=True)

    # Aoi parameters
    aoi_method = Unicode("").tag(sync=True)
    country = Unicode("").tag(sync=True)

    # Alerts type parameters
    satsource = Unicode('viirs').tag(sync=True)
    alerts_type = Unicode("recent").tag(sync=True)
    start_date = Unicode("2020-01-01").tag(sync=True)
    end_date = Unicode("2020-02-01").tag(sync=True)

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
        
    def get_alerts_name(self):
        """Create an output name for the aoi alerts"""
        
        now = datetime.now(tz=pytz.timezone('UTC'))
        now = now.strftime('%b%d')+random_string()
        
        method = f'custom_draw' if not self.country else self.country
        
        if self.alerts_type == 'recent':
            acq_date = f'last{self.timespan}' 
        else:
            acq_date = f'from{self.start_date}_to{self.start_date}'
            
        return f'{now}_{self.satsource}_{method}_{acq_date}'
        

    def download_alerts(self):
        """Download the corresponding alerts based on the selected alert type"""
        
        if self.alerts_type == "recent":
            # Donwload recent alerts
            df = pd.read_csv(self.get_url())
            
        else:
            # Download historical alerts
            start = datetime.strptime(self.start_date, "%Y-%m-%d")
            end = datetime.strptime(self.end_date, "%Y-%m-%d")
            
            # Get the corresponding sat name to concatenate the historic url
            sat = 'modis' if self.satsource == 'modis' else 'viirs-snpp'

            # Validate y2 >= y1
            if end < start:
                raise Exception("End date must be older than starting")
            # Get unique year(s)
            years = list(range(start.year, end.year + 1))

            # Download all the fires between the given dates
            all_dfs = []
            for y in years:

                # Verify if the files is not previously downloaded
                out_file = HISTORIC_DIR / f"historic_{sat}_fires_{y}.zip"
                
                if not out_file.exists():
                    
                    url = HISTORIC_URL.format(sat,y)
                    response = getattr(urllib, 'request', urllib).urlopen(url)
                    with tqdm(
                        unit='B', 
                        unit_scale=True, 
                        unit_divisor=1024, 
                        miniters=1,
                        desc='downloading...',
                        bar_format=BAR_FORMAT,
                        dynamic_ncols =True,
                        total=getattr(response, 'length')
                    ) as f:

                        def callback(b, bsize, tsize):
                            f.update(b * bsize - f.n)

                        urllib.request.urlretrieve(url, out_file, callback)

                        f.total = f.n
                        
                # Open all fires into the zipped files and merge
                # thme into one single DataFrame

                zip_file = ZipFile(out_file)
                dfs = pd.concat(
                    [
                        pd.read_csv(zip_file.open(text_file.filename))
                        for text_file in tqdm(
                            zip_file.infolist(),
                            desc='unzipping...',
                            dynamic_ncols =True,
                            bar_format=BAR_FORMAT,
                        )
                        if text_file.filename.endswith(".csv")
                    ]
                )
                all_dfs.append(dfs)
            dfs = pd.concat(all_dfs)

            # Filter them with its date
            dfs.acq_date = pd.to_datetime(dfs.acq_date)

            df = gpd.GeoDataFrame(dfs[(dfs.acq_date >= start) & (dfs.acq_date <= end)])

            # Cast again as string
            df["acq_date"] = df["acq_date"].astype(str)
            
        self.alerts = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326"
        ).reset_index()

    def get_url(self):
        """Get the proper recent url based on the input satallite"""

        sat = SATSOURCE[self.satsource]

        return RECENT_URL.format(sat[1], sat[0], self.timespan)

    def clip_to_aoi(self):
        """Clip recent or historical geodataframe with area of interest"""

        if not self.aoi_geometry:
            raise Exception(cm.ui.valid_aoi)
        alerts = self.alerts
        clip_geometry = (
            gpd.GeoDataFrame.from_features(self.aoi_geometry)
            .set_crs("EPSG:4326")
            .iloc[0]
            .geometry
        )

        return alerts[alerts.geometry.intersects(clip_geometry)]

    def alerts_to_squares(self):

        # Convert alert's geometries to 54009 (projected crs)
        # and use 375m as buffer
        geometry_col = (
            self.aoi_alerts.to_crs('ESRI:54009')['geometry']
            .buffer(187.5, cap_style=3)
            .copy()
        )

        self.aoi_alerts = self.aoi_alerts.assign(geometry=geometry_col)
        
        # Divide alerts into confidence categories
        
        def get_color(feature):
            confidence = feature['properties']['confidence']
            color = cs.get_confidence_color(self.satsource, confidence)
            return {
                'color': color,
                'fillColor': color,
            } 
        
        json_aoi_alerts = json.loads(self.aoi_alerts.to_crs('EPSG:4326').to_json())

        return GeoJSON(
            data=json_aoi_alerts,
            name='Alerts',
            style={'fillOpacity': 0.1, 'weight': 2},
            hover_style={'color': 'white', 'dashArray': '0', 'fillOpacity': 0.5},
            style_callback=get_color
        )
    

    def get_confidence_items(self):
        """Get the corresponding confidence items based on the satellite selection"""
        
        # Modis satellite is using a discrete range of values ranging from 0-100
        # We have divided its values in three categories (view app.py)
        
        type_ = 'disc' if self.satsource=='modis' else 'cat'
                    
        confidence_by_sat = [
            {'text':v[0], 'value':k} for k,v in CONFIDENCE[type_].items()
        ]
                
        return ['All'] + confidence_by_sat