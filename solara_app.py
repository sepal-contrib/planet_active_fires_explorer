from eeclient.client import EESession

from eeclient.exceptions import EEClientError
from typing import Dict

from traitlets import Bool, Float, HasTraits, List, Unicode, link, observe
import solara
import solara.server.settings
from solara.lab import headers
from solara.lab.components.theming import theme

import sepal_ui.sepalwidgets as sw
from sepal_ui.scripts.utils import init_ee
from sepal_ui.scripts.sepal_client import SepalClient


import ipyvuetify as v
from component.tiles import AlertMap
from component.model import AlertModel
from component.tiles import AlertsTile, AoiView
from component.tiles.sources import SourcesTile
from component.scripts.logger import logger
from sepal_ui.sepalwidgets.vue_app import MapApp
from sepal_ui.sepalwidgets.vue_app import ThemeToggle

init_ee()


def parse_cookie_string(cookie_string):
    cookies = {}
    for pair in cookie_string.split(";"):
        key_value = pair.strip().split("=", 1)
        if len(key_value) == 2:
            key, value = key_value
            cookies[key] = value
    return cookies


# solara.server.settings.main.root_path = "/api/app-launcher/seplan"
solara.server.settings.assets.fontawesome_path = (
    "/@fortawesome/fontawesome-free@6.7.2/css/all.min.css"
)
solara.server.settings.assets.extra_locations = ["./assets/"]


@solara.component
def Page():

    # This we have to create here because we need to pass it to all the maps
    # which doesn't have a builtin method to change the theme
    theme_toggle = ThemeToggle()
    theme_toggle.observe(lambda e: setattr(theme, "dark", e["new"]), "dark")

    solara.lab.theme.themes.dark.primary = "#76591e"
    solara.lab.theme.themes.dark.primary_contrast = "#bf8f2d"
    solara.lab.theme.themes.dark.secondary = "#363e4f"
    solara.lab.theme.themes.dark.secondary_contrast = "#5d76ab"
    solara.lab.theme.themes.dark.error = "#a63228"
    solara.lab.theme.themes.dark.info = "#c5c6c9"
    solara.lab.theme.themes.dark.success = "#3f802a"
    solara.lab.theme.themes.dark.warning = "#b8721d"
    solara.lab.theme.themes.dark.accent = "#272727"
    solara.lab.theme.themes.dark.anchor = "#f3f3f3"
    solara.lab.theme.themes.dark.main = "#24221f"
    solara.lab.theme.themes.dark.darker = "#1a1a1a"
    solara.lab.theme.themes.dark.bg = "#121212"
    solara.lab.theme.themes.dark.menu = "#424242"

    solara.lab.theme.themes.light.primary = "#5BB624"
    solara.lab.theme.themes.light.primary_contrast = "#76b353"
    solara.lab.theme.themes.light.accent = "#f3f3f3"
    solara.lab.theme.themes.light.anchor = "#f3f3f3"
    solara.lab.theme.themes.light.secondary = "#2199C4"
    solara.lab.theme.themes.light.secondary_contrast = "#5d76ab"
    solara.lab.theme.themes.light.main = "#2196f3"
    solara.lab.theme.themes.light.darker = "#ffffff"
    solara.lab.theme.themes.light.bg = "#FFFFFF"
    solara.lab.theme.themes.light.menu = "#FFFFFF"

    model = AlertModel()

    map_ = AlertMap(model, theme_toggle)

    logger.debug("After map initialized, theme dark is:", theme_toggle.dark)

    sources_tile = SourcesTile(model, map_)
    aoi_view = AoiView(model, map_)
    alerts_view = AlertsTile(model, aoi_view, map_)

    steps_data = [
        {
            "id": 2,
            "name": "Area of Interest",
            "icon": "mdi-map-marker-check",
            "display": "dialog",
            "actions": [
                {"label": "Cancel", "close": True, "cancel": True},
                {"label": "Next", "next": 3},
            ],
        },
        {
            "id": 3,
            "name": "Sources",
            "icon": "mdi-wrench",
            "display": "dialog",
            "actions": [
                {"label": "Cancel", "close": True, "cancel": True},
                {"label": "Prev", "next": 2},
                {"label": "Next", "next": 4},
            ],
        },
        {
            "id": 4,
            "name": "Get alerts",
            "icon": "mdi-fire",
            "display": "dialog",
            "actions": [
                {"label": "Cancel", "close": True, "cancel": True},
                {"label": "Prev", "next": 3},
                {"label": "Apply", "close": True},
            ],
        },
    ]

    steps_content = [aoi_view, sources_tile, alerts_view]

    MapApp.element(
        app_title="Fires explorer",
        app_icon="mdi-fire",
        main_map=[map_],
        steps_data=steps_data,
        steps_content=steps_content,
        theme_toggle=[theme_toggle],
        repo_url="https://github.com/sepal-contrib/planet_active_fires_explorer",
    )

    logger.debug("After APP initialized, theme dark is:", theme_toggle.dark)
    logger.debug("theme_toggle id is %s", id(theme_toggle))
    logger.debug("Solara theme is", theme.dark)
