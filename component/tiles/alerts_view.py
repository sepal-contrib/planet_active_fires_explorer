import datetime

import ipyvuetify as v
import pandas as pd
import pytz
import sepal_ui.sepalwidgets as sw
from ipyleaflet import GeoJSON
from numpy import float64
from sepal_ui import color
from sepal_ui.scripts import utils as su
from sepal_ui.scripts.decorator import loading_button, switch
from sepal_ui.scripts.warning import SepalWarning
from traitlets import link

import component.parameter as param
import component.scripts as scripts
import component.widget as cw
from component.message import cm

__all__ = ["AlertsTile"]


class AlertsTile(sw.ExpansionPanels):
    """Alerts tile component is the tab where the firms authentication process is done
    as well as the process to request the alerts from the FIRMS API"""

    def __init__(self, model, aoi, planet, map_):

        self.v_model = 0

        super().__init__()

        self.model = model
        self.aoi = aoi
        self.map_ = map_
        self.planet = planet

        self.alertsstep_view = AlertsView(self.model, self.aoi, self.map_, self.planet)
        self.authstep_view = AuthenticationView(self.model, self, self.alertsstep_view)

        self.children = [self.authstep_view, self.alertsstep_view]


class AuthenticationView(sw.ExpansionPanel):
    def __init__(self, model, panels, alerts_view):

        super().__init__()

        self.model = model
        self.panels = panels
        self.alert = sw.Alert()
        self.btn = sw.Btn(cm.alerts.auth.btn, small=True)

        states = {
            "valid": ("Authenticated", color.success),
            "non_valid": ("No authenticated", color.error),
        }
        self.w_auth_icon = cw.StateIcon(values="non_valid", states=states)
        self.w_header = sw.ExpansionPanelHeader(
            children=[
                cm.alerts.steps.auth,
                sw.Spacer(),
                v.Flex(style_="max-width:20px;", children=[self.w_auth_icon]),
            ]
        )

        self.alerts_view = alerts_view

        w_description = sw.Markdown(cm.alerts.auth.description)
        w_description.class_ = "px-3"

        self.w_auth_method = sw.Select(
            v_model="sepal",
            label=cm.alerts.auth.method.label,
            items=[
                {"value": "sepal", "text": cm.alerts.auth.method.sepal},
                {"value": "custom", "text": cm.alerts.auth.method.custom},
            ],
        )
        self.w_firms_api_key = sw.PasswordField(
            label=cm.alerts.wlabel.firms_api,
            v_model="",
        ).hide()

        w_api = sw.Layout(
            class_="align-center", children=[self.w_firms_api_key, self.btn]
        )

        self.children = [
            self.w_header,
            v.ExpansionPanelContent(
                children=[w_description, self.w_auth_method, w_api, self.alert]
            ),
        ]

        self.btn.on_event("click", self.authenticate_event)
        self.w_auth_method.observe(self.reset_auth_widget, "v_model")
        link((self.model, "firms_api_key"), (self.w_firms_api_key, "v_model"))

    def reset_auth_widget(self, change):
        """Toggle w_auth_method widget visibility and empty its v_model value"""

        self.alert.reset()
        self.w_firms_api_key.error_messages = None
        self.w_firms_api_key.toggle_viz()
        self.w_firms_api_key.v_model = ""

    @loading_button(debug=True)
    def authenticate_event(self, *args):
        """Trigger authentication process"""

        self.w_firms_api_key.error_messages = None

        if self.w_auth_method.v_model == "custom":
            if not self.w_firms_api_key.v_model:
                # raise error onw_firms_api_key widget
                self.w_firms_api_key.error_messages = cm.alerts.auth.errors.no_input
                return

        self.panels.v_model = 0
        self.panels.children[1].disabled = True
        self.w_auth_icon.values = "non_valid"

        self.model.get_availability()
        self.alerts_view.w_historic.set_min_max_dates()

        self.w_auth_icon.values = "valid"
        self.panels.v_model = 1
        self.panels.children[1].disabled = False


class AlertsView(sw.ExpansionPanel):
    def __init__(self, model, aoi, map_, planet):

        self.disabled = True

        super().__init__()

        self.model = model
        self.aoi = aoi
        self.map_ = map_
        self.planet = planet
        self.alert = sw.Alert()

        self.w_header = sw.ExpansionPanelHeader(children=[cm.alerts.steps.alerts])

        # Selection type
        self.w_alerts_type = v.RadioGroup(
            small=True,
            class_="ma-0",
            row=True,
            v_model=self.model.alerts_type,
            children=[
                v.Radio(key=1, label=cm.alerts.wlabel.recent, value="nrt"),
                v.Radio(key=2, label=cm.alerts.wlabel.historical, value="historic"),
            ],
        )

        self.btn = sw.Btn(cm.alerts.wlabel.get_alerts, class_="ma-2", small=True)
        self.download_btn = sw.Btn(
            cm.alerts.wlabel.download_btn,
            "mdi-download",
            class_="ma-2",
            disabled=True,
            small=True,
        )
        buttons = v.Flex(children=[self.btn, self.download_btn])

        self.w_satellite = sw.Select(
            label=cm.alerts.wlabel.satellite, v_model="MODIS_NRT"
        )
        self.w_historic = WidgetHistoric(self.model).hide()

        self.get_sat_sources()

        self.w_timespan = sw.Select(
            label=cm.alerts.wlabel.in_the_last,
            items=[
                {"text": text, "value": value}
                for value, text in param.TIME_SPAN.items()
            ],
            v_model=self.model.offset_days,
        )

        self.model.bind(self.w_alerts_type, "alerts_type")
        self.model.bind(self.w_satellite, "satsource")
        link((self.model, "offset_days"), (self.w_timespan, "v_model"))

        self.children = [
            self.w_header,
            sw.ExpansionPanelContent(
                children=[
                    self.w_alerts_type,
                    self.w_satellite,
                    self.w_timespan,
                    self.w_historic,
                    buttons,
                    self.alert,
                ]
            ),
        ]

        # Decorate buttons
        self.write_alerts = su.loading_button(self.alert, self.download_btn, True)(
            self.write_alerts
        )

        # View interactions
        self.w_alerts_type.observe(self.toggle_components)

        # Interatcions with map widgets
        self.map_.w_alerts.observe(self.filter_confidence, "confidence")
        self.map_.w_alerts.observe(self.alert_list_event, "v_model")

        self.btn.on_event("click", self.get_alerts)
        self.download_btn.on_event("click", self.write_alerts)

        # Every time a satellite has changed, we fill the min or max dates
        self.w_satellite.observe(self.w_historic.set_min_max_dates, "v_model")

    def get_sat_sources(self):
        """Get the corresponding items for the satellite source dropdown widget
        depending on the alerts type"""

        self.w_satellite.items = [
            {"text": v, "value": k}
            for k, v in param.SAT_SOURCE[self.model.alerts_type].items()
        ]

        self.w_satellite.v_model = self.w_satellite.items[0]["value"]

    def write_alerts(self, *args):
        """Write AOI alerts into a shapefile on the module results"""

        folder, name = self.model.write_alerts()

        self.alert.add_msg(
            msg=cm.alerts.exported.format(param.ALERTS_DIR / folder, name),
            type_="success",
        )

    def toggle_components(self, change):
        """Display recent or historical widget based on radios selection"""

        self.get_sat_sources()

        if change["new"] == "nrt":
            self.w_historic.hide()
            self.w_timespan.show()

        elif change["new"] == "historic":
            self.w_historic.show()
            self.w_timespan.hide()

    @loading_button(debug=True)
    def get_alerts(self, widget, change, data):
        """
        Get the corresponding alerts clipped to the area of interest
        and display them into the map.

        """

        # reset model values
        self.model.reset = True

        self.download_btn.disabled = True

        if not self.model.aoi_geometry:
            raise Exception(cm.ui.valid_aoi)

        if self.model.aoi_method == "draw":
            self.map_.dc.clear()
            self.map_.add_layer(GeoJSON(data=self.model.aoi_geometry))

        self.alert.add_live_msg(cm.ui.downloading_alerts, type_="info")

        self.model.get_firms_alerts()

        # Clip alerts_gdf to the selected aoi
        self.alert.add_msg(msg=cm.ui.clipping, type_="info")

        self.model.clip_to_aoi()

        # Reformat geodataframe
        self.model.format_gdf()

        # If there are more alerts thatn the threhsold, avoid display them
        # into the map

        if len(self.model.aoi_alerts) <= param.MAX_ALERTS:

            # Update map dropdown alerts
            self.map_.w_alerts.items = list(self.model.aoi_alerts.index)
            self.map_.w_alerts.w_conf.items = self.model.get_confidence_items()

            # Convert aoi alert points into squares
            square_alerts = self.model.alerts_to_squares()

            # Create an event for the alerts
            def geojson_callback(**kwargs):
                self.map_.w_alerts.v_model = int(kwargs["id"])

            square_alerts.on_click(geojson_callback)

            # Add layer  into the map
            self.map_ + square_alerts

            self.map_.w_alerts.disabled = False
            self.map_.w_alerts.show()

            if self.model.alerts_type == "recent":
                msg = cm.ui.alert_number.format(
                    len(self.model.aoi_alerts), self.model.offset_days
                )
            else:
                msg = cm.ui.historic.alert_number.format(
                    len(self.model.aoi_alerts),
                    self.model.start_date,
                    self.model.offset_days,
                )

            self.alert.add_msg(msg, type_="success")

        else:
            SepalWarning(
                cm.alerts.overloaded.format(
                    len(self.model.aoi_alerts), param.MAX_ALERTS
                )
            )

        self.download_btn.disabled = False

        self.model.reset = False

    def filter_confidence(self, change):
        """Filter alert list by confidence"""

        confidence = change["new"]

        if confidence != "All":
            #
            if self.model.satsource != "modis":
                self.map_.w_alerts.items = self.model.aoi_alerts[
                    self.model.aoi_alerts.confidence == confidence.lower()
                ].index.to_list()

            else:

                upper, lower = scripts.get_thresholds(lower=confidence)
                self.map_.w_alerts.items = self.model.aoi_alerts[
                    (self.model.aoi_alerts.confidence <= upper)
                    & (self.model.aoi_alerts.confidence > lower)
                ].index.to_list()

        else:
            self.map_.w_alerts.items = self.model.aoi_alerts.index.to_list()

        # Select first item
        self.map_.w_alerts.v_model = self.map_.w_alerts.items[0]

    def _get_metadata(self, alert_id):
        """Get a metadata table of alert and display as control widget on map

        Args:
            alert_id (str): Current alert id index
        """

        headers, values = list(
            zip(
                *[
                    (col_name, self.model.aoi_alerts.loc[alert_id, col_name])
                    for col_name in param.METADATA_ROWS
                ]
            )
        )

        values = [round(val, 2) if isinstance(val, float64) else val for val in values]

        data = zip(headers, values)

        # Update metadata table content
        self.map_.metadata_table.update(self.model.satsource, data)

    def alert_list_event(self, change):
        """Update map zoom, center when selecting an alert and add metadata to
        map"""

        if self.model.reset is False:
            # Get fire alert id
            self.model.current_alert = change["new"]

            # Filter dataframe to get lat,lon
            self.map_.lat = self.model.aoi_alerts.loc[self.model.current_alert][
                "latitude"
            ]

            self.map_.lon = self.model.aoi_alerts.loc[self.model.current_alert][
                "longitude"
            ]

            self.map_.center = (self.map_.lat, self.map_.lon)
            self.map_.zoom = 15
            self._get_metadata(self.model.current_alert)

            # Search and add layers to map
            if self.model.planet_model.active:
                self.planet.add_planet_imagery()


class WidgetHistoric(sw.Layout):
    """Historic widget containing three components: start date, add_icon, and offset
    days selection llist. It will be used to caputure the user's input related with
    the historic data. The widget allow to capture and perform the user interactions."""

    def __init__(self, model):

        self.model = model
        self.class_ = "d-flex"
        self.align_center = True

        super().__init__()

        # Historic Alerts
        self.w_date = cw.DatePicker(
            label=cm.alerts.wlabel.start, style_="min-width:181px", v_model=""
        )

        self.w_days = sw.Select(
            label=cm.alerts.wlabel.plus_offset,
            style_="min-width:151px",
            items=[
                {"text": text, "value": value}
                for value, text in param.TIME_SPAN.items()
            ],
            v_model=self.model.offset_days,
        )

        add_icon = v.Btn(
            children=[
                v.Icon(
                    children=["mdi-plus"],
                )
            ],
            fab=True,
            x_small=True,
        )

        self.model.bind(self.w_date, "start_date")
        link((self.model, "offset_days"), (self.w_days, "v_model"))

        self.children = [
            v.Flex(xs5=True, children=[self.w_date]),
            v.Flex(xs2=True, class_="mx-2", children=[add_icon]),
            v.Flex(xs5=True, children=[self.w_days]),
        ]

        add_icon.on_event("click", self.add_days)

    def set_min_max_dates(self, *args):
        """from a request. use the already available availability df to set min and max
        dates in the date_picker."""

        if self.model.availability is not None:

            # Get the picker as it is embbeded into the menu that wraps the widget.
            data = self.model.availability
            _, self.w_date.date_picker.min, self.w_date.date_picker.max = (
                data[
                    data.data_id
                    == param.SAT_SOURCE[self.model.alerts_type][self.model.satsource]
                ]
                .values[0]
                .tolist()
            )
            self.w_date.date_picker.v_model = self.w_date.date_picker.max

    def add_days(self, *args):
        """set the next of the current value from the w_days items"""

        items_value = [item["value"] for item in self.w_days.items]
        self.w_days.v_model = items_value[
            min(items_value.index(self.w_days.v_model) + 1, len(items_value) - 1)
        ]
