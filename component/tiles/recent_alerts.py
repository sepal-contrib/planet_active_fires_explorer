import geopandas as gpd

from traitlets import Int, Unicode, link
import ipyvuetify as v

from os.path import expanduser

from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su
from component.message import cm
from component.scripts.scripts import *
from component.widget.custom_widgets import *

COUNTRIES = gpd.read_file('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json')



