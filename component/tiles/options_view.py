from component.model import AlertModel
from component.tiles import *


class PanelView(v.Card):
    
    """ Panel to incorporate each of the tabs that would be used for the end-
    user to validate their Planet API-key, select and area of interest and
    use whether a fixed short periods or the historical data.
    
    """
    
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        
        self.model = AlertModel()
        
        tabs_title = [
            'Planet Imagery',
            'Area of Interest',
            'Alerts'
        ]
        
        
        aoi_tile = AoiTile()
        planet_tile = PlanetTile(model=self.model)
        alerts_tile = AlertsTile(aoi=aoi_tile)
        
        widgets = [
            planet_tile,
            aoi_tile,
            alerts_tile
        ]
        
        tabs = Tabs(tabs_title, widgets)
        
        self.children = [tabs]
        
    
        