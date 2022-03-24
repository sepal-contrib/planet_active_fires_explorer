from ipywidgets import Button, Layout, Output
from ipyleaflet import WidgetControl, FullScreenControl, Marker

from sepal_ui import mapping as m
from sepal_ui import sepalwidgets as sw
from sepal_ui.frontend.styles import sepal_darker

from component.message import cm
import component.widget as cw

__all__ = ["AlertMap"]


class AlertMap(m.SepalMap):
    def __init__(self, model, *args, **kwargs):

        self.model = model

        self.lat = None
        self.lon = None
        
        kwargs["dc"] = True
        kwargs["gee"] = False
        kwargs["basemaps"] = ["Google Satellite"]
        kwargs["statebar"] = True

        super().__init__(*args, **kwargs)

        self.show_dc()
        self.add_control(m.FullScreenControl(position="topleft"))

        # Create widgets

        self.reload_btn = Button(
            disabled=False,
            tooltip="Reload Planet imagery",
            icon="refresh",
            layout=Layout(
                width="30px", height="30px", line_height="30px", padding="0px"
            ),
        )
        self.parameters_btn = Button(
            tooltip="Toggle parameters",
            icon="navicon",
            layout=Layout(
                width="30px", height="30px", line_height="30px", padding="0px"
            ),
        )

        self.navigate_btn = Button(
            tooltip="Navigate through Alerts",
            icon="fire",
            layout=Layout(
                width="30px", height="30px", line_height="30px", padding="0px"
            ),
        )

        self.metadata_btn = Button(
            tooltip="Fire alert metadata",
            icon="info",
            layout=Layout(
                width="30px", height="30px", line_height="30px", padding="0px"
            ),
        )

        self.w_alerts = cw.DynamicSelect(disabled=True).hide()
        self.w_state_bar = sw.StateBar(loading=False)
        self.w_state_bar.color = sepal_darker

        self.metadata_table = cw.MetadataTable()

        # Add widget as control to the map
        self.add_widget_as_control(self.reload_btn, "topright", first=True)
        self.add_widget_as_control(self.navigate_btn, "topright", first=True)
        self.add_widget_as_control(self.parameters_btn, "topleft")
        self.add_widget_as_control(self.w_alerts, "topright", first=True)
        self.add_widget_as_control(self.w_state_bar, "topleft", first=True)
        self.add_widget_as_control(self.metadata_btn, "topleft")
        self.add_widget_as_control(self.metadata_table, "bottomleft")

        # Map interactions
        self.dc.on_draw(self.handle_draw)
        self.on_interaction(self._return_coordinates)

        # show/hide elements
        self.navigate_btn.on_click(lambda *args: self.w_alerts.toggle_viz())
        self.metadata_btn.on_click(lambda *args: self.metadata_table.toggle_viz())

        self.model.observe(self.reset, "reset")

        self.metadata_table.observe(self.model.metadata_change, "validate")
        self.metadata_table.observe(self.model.metadata_change, "observ")

    def reset(self, change):
        """Remove all alerts from the map view"""

        if change["new"] is True:
            # Remove previous alert layers
            self.remove_layers_if("name", equals_to="Alerts")
            self.w_alerts.reset()
            self.metadata_table.reset()

    def add_widget_as_control(self, widget, position, first=False):
        """Add widget as control in the given position

        Args:
            widget (dom.widget): Widget to convert as map control
            position (str): 'topleft', 'topright', 'bottomright', 'bottomlreft'
            first (Bool): Whether set the control as first or last element
        """

        new_control = WidgetControl(
            widget=widget, position=position, transparent_bg=True
        )

        if first == True:

            self.controls = tuple(
                [new_control] + [control for control in self.controls]
            )
        else:

            self.controls = self.controls + tuple([new_control])

    def remove_layers(self):
        """Remove all layers in map. Except the basemap"""
        # get map layers
        layers = self.layers

        # loop and remove layers
        [self.remove_last_layer() for _ in range(len(layers))]

    def handle_draw(self, target, action, geo_json):
        """Store geometry geometry in the model"""

        self.remove_layers()
        if action == "created":
            self.model.aoi_geometry = {"type": "FeatureCollection", "features": []}

            self.model.aoi_geometry["features"].append(geo_json)

    def remove_layers_if(self, prop, equals_to, _metadata=False):
        """Remove layers with a given property and value

        Args:
            prop (str): Property or key (if using _metadata) of Layer
            equals_to (str): Value of property or key (if using _metadata) in Layer
            metadata (Bool): Whether the Layers have _metadata attribute or not

        """
        if _metadata:
            for layer in self.layers:
                if hasattr(layer, "_metadata"):
                    if layer._metadata[prop] == equals_to:
                        self.remove_layer(layer)
        else:
            for layer in self.layers:
                if hasattr(layer, prop):
                    if layer.__dict__["_trait_values"][prop] == equals_to:
                        self.remove_layer(layer)

    def _return_coordinates(self, **kwargs):

        # Only active when method different to draw and there is a valid key
        if all([self.model.aoi_method != "draw", self.model.valid_api]):

            if kwargs.get("type") == "click":

                # Remove markdown if there is one
                self.remove_layers_if("type", equals_to="manual", _metadata=True)

                self.lat, self.lon = kwargs.get("coordinates")

                marker = Marker(
                    location=kwargs.get("coordinates"),
                    alt="Manual",
                    title="Manual",
                    draggable=False,
                    name="Manual marker",
                )
                marker.__setattr__("_metadata", {"type": "manual", "id": None})

                self.add_layer(marker)
