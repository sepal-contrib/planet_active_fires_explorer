import ipyvuetify as v

import sepal_ui.sepalwidgets as sw

from sepal_ui.aoi.aoi_view import *

class AoiTile(v.Card):
    
    
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        self.view = AoiView(methods=['-POINTS'], gee=False)
        self.view.elevation = 0
        
        self.children=[
            self.view
        ]
