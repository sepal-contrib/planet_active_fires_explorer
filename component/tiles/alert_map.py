from sepal_ui import mapping as m
from ipywidgets import Button, Layout, Output
from ipyleaflet import WidgetControl, FullScreenControl
from ..widget.custom_widgets import StateBar

class AlertMap(m.SepalMap):
    
    def __init__(self, *args, **kwargs):
        
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
            layout=Layout(width='30px', height='30px', line_height='30px', padding='0px')
        )
        
        # Create output space for metadata
        self.metadata_output = Output()
        
        # Add metadata_output as WidgetControl to the map
        metadata_control = WidgetControl(widget=self.metadata_output, position='bottomright', transparent_bg=True)
        self.add_control(metadata_control)
        
        # Add controls in this way to make the new one as first in the list
        self.controls = tuple([WidgetControl(widget=self.reload_btn, position='topright', transparent_bg=True)] + 
            [c for c in self.controls])
        
        self.w_state_bar = StateBar(loading=False)
        
        # Add controls in this way to make the new one as first in the list
        self.controls = tuple([WidgetControl(widget=self.w_state_bar)]+[c for c in self.controls])
        
    def remove_layers(self):
        
        # get map layers
        layers = self.layers
        
        # loop and remove layers 
        [self.remove_last_layer() for _ in range(len(layers))]
        