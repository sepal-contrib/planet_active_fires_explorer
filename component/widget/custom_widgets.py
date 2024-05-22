import ipyvuetify as v
import sepal_ui.sepalwidgets as sw
from traitlets import Any, Int, List, Unicode, link

import component.parameter as param
import component.scripts.scripts as cs
from component.message import cm

__all__ = [
    "DynamicSelect",
    "AlertMenu",
    "Tabs",
    "MetadataTable",
]


class DynamicSelect(sw.Card):
    """Widget to navigate with next and previous buttons over a list

    Args:
        items (list) : List of items to be displayed in select list
        label (str) : Label to display into widget

    Parameters:
        v_model (traitlets.Any): Current element from select list

    """

    items = List([]).tag(sync=True)
    v_model = Any().tag(sync=True)
    confidence = Any("All").tag(sync=True)

    def __init__(self, label="", **kwargs):

        self.label = label
        self.dense = True
        self.max_width = "520"

        super().__init__(**kwargs)

        self.close = v.Icon(children=["mdi-close"], small=True)
        title = sw.CardTitle(class_="pa-0 ma-0", children=[v.Spacer(), self.close])

        self.w_prev = v.Btn(
            _metadata={"name": "previous"},
            x_small=True,
            children=[v.Icon(left=True, children=["mdi-chevron-left"]), "prev"],
            value=-1,
        )

        self.w_next = v.Btn(
            _metadata={"name": "next"},
            x_small=True,
            children=[v.Icon(small=True, children=["mdi-chevron-right"]), "nxt"],
            value=1,
        )
        self.w_conf = v.Select(
            x12s=True,
            class_="mt-4",
            dense=True,
            label="Confidence",
            v_model="All",
        )

        self.w_list = v.Select(
            class_="mt-4 ml-2",
            label=self.label,
            items=self.items,
            v_model="",
            dense=True,
        )

        widgets = [self.w_prev, self.w_conf, self.w_list, self.w_next]

        self.children = [
            v.Row(
                no_gutters=True,
                align="center",
                children=[
                    v.Col(cols=f"{col}", class_="text-center", children=[widget])
                    for col, widget in zip([2, 3, 5, 2], widgets)
                ],
            )
        ]

        link((self.w_list, "items"), (self, "items"))
        link((self.w_list, "v_model"), (self, "v_model"))
        link((self.w_conf, "v_model"), (self, "confidence"))

        self.w_prev.on_event("click", self.prev_next_event)
        self.w_next.on_event("click", self.prev_next_event)
        self.close.on_event("click", lambda *args: self.hide())

    def prev_next_event(self, widget, change, data):
        """go to the next value. loop to the first or last one if we reach the end"""

        increm = widget.value

        # get the current position in the list
        val = self.w_list.v_model
        if val in self.w_list.items:
            pos = self.w_list.items.index(val)

            pos += increm

            # check if loop is required
            if pos == -1:
                pos = len(self.w_list.items) - 1
            elif pos >= len(self.w_list.items):
                pos = 0

        # if none was selected always start by the first
        else:
            pos = 0

        self.w_list.v_model = self.w_list.items[pos]

    def reset(self):
        """Restore widgets and values to default"""

        self.items = []
        self.v_model = ""
        self.confidence = "All"

        self.w_conf.items = []


class AlertMenu(v.Menu):
    def __init__(self, widget, *args, **kwargs):

        self.value = False
        self.close_on_content_click = False
        self.nudge_width = 200
        self.offset_x = True

        super().__init__()

        self.nav_btn = v.Btn(
            v_on="menu.on",
            icon=True,
            children=[v.Icon(children=["mdi-cloud-download"])],
        )

        self.v_slots = [
            {"name": "activator", "variable": "menu", "children": self.nav_btn}
        ]

        self.children = [widget]


class Tabs(sw.Card):

    current = Int(0).tag(sync=True)

    def __init__(self, titles, content, **kwargs):

        self.background_color = "primary"

        self.tabs = [
            v.Tabs(
                v_model=self.current,
                children=[
                    v.Tab(children=[title], key=key) for key, title in enumerate(titles)
                ],
            )
        ]

        self.content = [
            v.TabsItems(
                v_model=self.current,
                children=[
                    v.TabItem(children=[content], key=key)
                    for key, content in enumerate(content)
                ],
            )
        ]

        self.children = self.tabs + self.content

        link((self.tabs[0], "v_model"), (self.content[0], "v_model"))

        super().__init__(**kwargs)


class MetadataTable(
    sw.Card,
):
    """Widget to get a simple table displaying the metadata of the alerts"""

    reviewed = Unicode("").tag(sync=True)
    observ = Unicode("").tag(sync=True)

    def __init__(self, *args, **kwargs):
        self.max_width = "250px"

        # Create table
        super().__init__(*args, **kwargs)

        self.close = v.Icon(children=["mdi-close"], small=True)
        self.title = sw.CardTitle(class_="pa-0 ma-0", children=[v.Spacer(), self.close])

        self.close.on_event("click", lambda *args: self.hide())

        self.w_validate = v.Select(
            items=[
                {"text": cm.alerts.metadata.items_.yes, "value": "yes"},
                {"text": cm.alerts.metadata.items_.no, "value": "not"},
            ],
            dense=True,
            v_model=self.reviewed,
        )
        self.w_observ = v.Textarea(dense=True, rows=2, v_model=self.observ)

        link((self, "reviewed"), (self.w_validate, "v_model"))
        link((self, "observ"), (self.w_observ, "v_model"))

    def update(self, satsource, data):
        """Create metadata Simple Table based on the given data

        Args:
            satsource (str model.satsource): Satellite source
            data (list of lists): Each element has to follow: [header, value]
        """

        def get_row(header, value):

            if header == "confidence":
                value = v.Chip(
                    small=True,
                    color=cs.get_confidence_color(satsource, value),
                    children=[value],
                )

            elif header == "reviewed":
                self.w_validate.v_model = value
                value = self.w_validate

            elif header == "observ":
                self.w_observ.v_model = value
                value = self.w_observ

            return [v.Html(tag="th", children=[f"{param.METADATA_ROWS[header]}: "])] + [
                v.Html(tag="td", children=[value])
            ]

        rows = [
            v.Html(tag="tr", children=get_row(str(row_header), str(row_value)))
            for row_header, row_value in data
        ]

        self.children = [self.title] + [
            v.SimpleTable(dense=True, children=[v.Html(tag="tbody", children=rows)])
        ]

    def reset(self):
        """Create an empty table"""

        self.children = []
