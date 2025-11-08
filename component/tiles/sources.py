import ipyvuetify as v
from component.tiles.planet_view import PlanetView
from sepal_ui.sepalwidgets.vue_widgets import Tabs


class SourcesTile(v.Flex):
    def __init__(self, model, map_, *args, **kwargs):
        super().__init__(**kwargs)

        planet_view = PlanetView(model, map_)
        sentinel_view = v.Card()
        landsat_view = v.Card()

        self.children = [
            Tabs(
                titles=["Landsat", "Sentinel", "Planet"],
                content=[
                    sentinel_view,
                    landsat_view,
                    planet_view,
                ],
            )
        ]
