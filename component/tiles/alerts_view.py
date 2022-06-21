import pytz
import datetime
import warnings
from numpy import float64

from ipywidgets import Output
import ipyvuetify as v

import sepal_ui.sepalwidgets as sw
from sepal_ui.scripts import utils as su

from component.message import cm
from component.scripts.scripts import get_thresholds
import component.widget as cw
import component.parameter as param

__all__ = ["AlertsView"]


class AlertsView(v.Card):
    def __init__(self, model, aoi, planet, map_, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.model = model
        self.aoi = aoi
        self.map_ = map_
        self.planet = planet

        # Widgets
        self.alert = sw.Alert()

        # Buttons
        self.btn = sw.Btn(cm.alerts.wlabel.get_alerts, class_="ma-2")
        self.download_btn = sw.Btn(
            cm.alerts.wlabel.download_btn, "mdi-download", class_="ma-2", disabled=True
        )

        buttons = v.Flex(children=[self.btn, self.download_btn])

        # Create an output for the progress tqdm bar
        self.dwbar_output = Output()

        # Satellite
        self.w_satellite = cw.Select(label=cm.alerts.wlabel.satellite, v_model="viirs")
        self.get_sat_sources()

        # Recent alerts
        self.w_recent = cw.Select(
            label=cm.alerts.wlabel.in_the_last,
            items=[
                {"text": text, "value": value}
                for value, text in param.TIME_SPAN.items()
            ],
            v_model=self.model.timespan,
        )

        # Historic Alerts
        self.w_start = sw.DatePicker(
            label=cm.alerts.wlabel.start,
            min="2000-01-01",
            max=self.get_max_date(),
            v_model="",
        )

        self.w_end = sw.DatePicker(
            class_="ml-5",
            label=cm.alerts.wlabel.end,
            min="2000-01-01",
            max=self.get_max_date(),
            v_model="",
        )

        self.w_historic = cw.Flex(
            class_="d-flex", children=[self.w_start, self.w_end]
        ).hide()

        # Selection type
        self.w_alerts_type = v.RadioGroup(
            label=cm.alerts.wlabel.alert_type,
            row=True,
            v_model=self.model.alerts_type,
            children=[
                v.Radio(key=1, label=cm.alerts.wlabel.recent, value="recent"),
                v.Radio(key=2, label=cm.alerts.wlabel.historical, value="historical"),
            ],
        )

        self.children = [
            self.w_alerts_type,
            self.w_satellite,
            self.w_recent,
            self.w_historic,
            buttons,
            self.alert,
        ]

        self.model.bind(self.w_alerts_type, "alerts_type").bind(
            self.w_satellite, "satsource"
        ).bind(self.w_recent, "timespan").bind(self.w_start, "start_date").bind(
            self.w_end, "end_date"
        )
        # Decorate buttons
        self.get_alerts = su.loading_button(self.alert, self.btn, True)(self.get_alerts)

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

    def write_alerts(self, *args):
        """Write AOI alerts into a shapefile on the module results"""

        folder, name = self.model.write_alerts()

        self.alert.add_msg(
            msg=cm.alerts.exported.format(param.ALERTS_DIR / folder, name),
            type_="success",
        )

    def get_sat_sources(self):
        """Get the corresponding items for the satellite source dropdown widget
        depending on the alerts type
        """

        if self.model.alerts_type == "recent":
            self.w_satellite.items = [
                {"text": v[0], "value": k} for k, v in param.SATSOURCE.items()
            ]
        else:
            # For historic periods only download the MODIS alerts
            # because the other sources are really heavy so it's difficult to
            # incorporate all this data in the maps
            # TODO: Find a solution to download any type of satellite alerts
            self.w_satellite.items = [
                {"text": v[0], "value": k}
                for k, v in param.SATSOURCE.items()
                if k not in ["viirs", "viirsnoa"]
            ]

        self.w_satellite.v_model = self.w_satellite.items[0]["value"]

    def get_max_date(self):
        """Get the maximum available date for the historical data"""

        now = datetime.datetime.now(tz=pytz.timezone("UTC"))
        year = now.year

        # The maximum available historic date is the current year - 1
        return datetime.datetime.strftime(
            datetime.datetime(year - 1, 12, 31), "%Y-%m-%d"
        )

    def toggle_components(self, change):
        """Display recent or historical widget based on radios selection"""

        self.get_sat_sources()

        if change["new"] == "recent":
            su.show_component(self.w_recent)
            su.hide_component(self.w_historic)

        elif change["new"] == "historical":
            su.show_component(self.w_historic)
            su.hide_component(self.w_recent)

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

        self.alert.add_live_msg(cm.ui.downloading_alerts, type_="info")

        # Capture the tqdm bar with the output
        with self.dwbar_output:

            self.dwbar_output.clear_output()
            self.alert.children = self.alert.children + [self.dwbar_output]

            # Get the corresponding alerts
            self.model.download_alerts()

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
                    len(self.model.aoi_alerts), self.model.timespan
                )
            else:
                msg = cm.ui.historic.alert_number.format(
                    len(self.model.aoi_alerts),
                    self.model.start_date,
                    self.model.end_date,
                )

            self.alert.add_msg(msg, type_="success")

        else:
            warnings.warn(
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

                upper, lower = get_thresholds(lower=confidence)
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
