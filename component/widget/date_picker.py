from datetime import datetime

import ipyvuetify as v
import sepal_ui.sepalwidgets as sw
from traitlets import Bool, link, observe

__all__ = ["DatePicker"]


class DatePicker(sw.Layout):
    """
    Custom input widget to provide a reusable DatePicker. It allows to choose date as a string in the following format YYYY-MM-DD

    Args:
        label (str, optional): the label of the datepicker field
        kwargs (optional): any parameter from a v.Layout abject. If set, 'children' will be overwritten.

    """

    menu = None
    "v.Menu: the menu widget to display the datepicker"

    date_text = None
    "v.TextField: the text field of the datepicker widget"

    disabled = Bool(False).tag(sync=True)
    "traitlets.Bool: the disabled status of the Datepicker object"

    def __init__(self, label="Date", **kwargs):

        kwargs["v_model"] = kwargs.get("v_model", "")

        # create the widgets
        self.date_picker = v.DatePicker(no_title=True, scrollable=True, **kwargs)

        self.date_text = v.TextField(
            label=label,
            hint="YYYY-MM-DD format",
            persistent_hint=True,
            prepend_icon="event",
            readonly=True,
            v_on="menuData.on",
        )

        self.menu = v.Menu(
            min_width="290px",
            transition="scale-transition",
            offset_y=True,
            v_model=False,
            close_on_content_click=False,
            children=[self.date_picker],
            v_slots=[
                {
                    "name": "activator",
                    "variable": "menuData",
                    "children": self.date_text,
                }
            ],
        )

        # set the default parameter
        layout_kwargs = {
            "v_model": None,
            "row": True,
            "class_": "pa-5",
            "align_center": True,
            "children": [v.Flex(xs10=True, children=[self.menu])],
        }

        # call the constructor
        super().__init__(**layout_kwargs)

        link((self.date_picker, "v_model"), (self.date_text, "v_model"))
        link((self.date_picker, "v_model"), (self, "v_model"))

    @observe("v_model")
    def check_date(self, change):
        """
        A method to check if the value of the set v_model is a correctly formated date
        Reset the widget and display an error if it's not the case
        """

        self.date_text.error_messages = None

        # exit immediately if nothing is set
        if not change["new"]:
            return

        # change the error status
        if not self.is_valid_date(change["new"]):
            msg = self.date_text.hint
            self.date_text.error_messages = msg

        return

    @observe("v_model")
    def close_menu(self, change):
        """A method to close the menu of the datepicker programatically"""

        # set the visibility
        self.menu.v_model = False

        return

    @observe("disabled")
    def disable(self, change):
        """A method to disabled the appropriate components in the datipkcer object"""

        self.menu.v_slots[0]["children"].disabled = self.disabled

        return

    @staticmethod
    def is_valid_date(date):
        """
        Check if the date is provided using the date format required for the widget

        Args:
            date (str): the date to test in YYYY-MM-DD format

        Return:
            (bool): the date to test
        """

        try:
            date = datetime.strptime(date, "%Y-%m-%d")
            valid = True

        except Exception:
            valid = False

        return valid
