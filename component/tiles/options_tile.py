import ipyvuetify as v
import sepal_ui.sepalwidgets as sw

from component.model import AlertModel
from component.tiles import AlertsView, AoiView
from component.tiles.planet_view import PlanetView
from component.widget import Tabs

__all__ = ["PanelTile"]


class PanelTile(
    sw.Card,
):

    """Panel to incorporate each of the tabs that would be used for the end-
    user to validate their Planet API-key, select and area of interest and
    use whether a fixed short periods or the historical data.

    """

    def __init__(self, map_, model, *args, **kwargs):

        self.min_height = "370px"
        self.min_width = "462px"
        self.max_width = "462px"
        self.max_height = "550px"
        self.class_ = "pa-2"

        super().__init__(*args, **kwargs)

        self.model = model
        self.map_ = map_

        self.close = v.Icon(children=["mdi-close"])
        title = v.CardTitle(children=["Settings", v.Spacer(), self.close])

        tabs_title = ["Planet Imagery", "Area of Interest", "Alerts"]

        self.planet = PlanetView(self.model, self.map_)
        self.aoi = AoiView(self.model, self.map_)
        self.alerts = AlertsView(self.model, self.aoi, self.planet, self.map_)

        widgets = [self.planet, self.aoi, self.alerts]

        tabs = Tabs(tabs_title, widgets)

        self.children = [title, tabs]

        self.close.on_event("click", lambda *args: self.hide())

        # Open dialog when map parameters button is clicked
        self.map_.parameters_btn.on_event("click", self.parameters_btn_event)

    def parameters_btn_event(self, *args):
        """Toggle visualization of parameters panel and hide metadata if is
        visible
        """

        self.toggle_viz()

        if self.viz == True:
            self.map_.metadata_table.hide()
