import ipyvuetify as v
from traitlets import Unicode, List, Int, Any, link

from sepal_ui.sepalwidgets import SepalWidget
from component.parameter import CONFIDENCE
import component.scripts.scripts as cs

class Card(v.Card, SepalWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Flex(v.Flex, SepalWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Select(v.Select, SepalWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DatePicker(v.Layout, SepalWidget):
    """
    Custom input widget to provide a reusable DatePicker. It allows to choose
    date as a string in the following format YYYY-MM-DD

    Args:
        label (str, optional): the label of the datepicker field

    Attributes:
        menu (v.Menu): the menu widget to display the datepicker

    """

    def __init__(self, *args, label='Date', **kwargs):

        self.v_model = ''
        self.row = True
        self.align_center = True

        super().__init__(*args, **kwargs)

        date_picker = v.DatePicker(no_title=True, scrollable=True, **kwargs)

        date_text = v.TextField(
            class_='ml-3',
            label=label,
            hint='YYYY-MM-DD format',
            persistent_hint=True,
            prepend_icon='event',
            readonly=True,
            v_on='menuData.on',
        )

        self.menu = v.Menu(
            min_width='290px',
            transition='scale-transition',
            offset_y=True,
            value=False,
            close_on_content_click=False,
            children=[date_picker],
            v_slots=[
                {
                    'name': 'activator',
                    'variable': 'menuData',
                    'children': date_text,
                }
            ],
        )

        self.children = [v.Flex(xs10=True, children=[self.menu])]

        link((date_picker, 'v_model'), (date_text, 'v_model'))
        link((self, 'v_model'), (date_picker, 'v_model'))


class DynamicSelect(v.Card, SepalWidget):

    """Widget to navigate with next and previous buttons over a list

    Args:
        items (list) : List of items to be displayed in select list
        label (str) : Label to display into widget

    Parameters:
        v_model (traitlets.Any): Current element from select list

    """

    items = List([]).tag(sync=True)
    v_model = Any().tag(sync=True)
    confidence = Any('All').tag(sync=True)

    def __init__(self, label='', **kwargs):

        self.row = True
        self.label = label
        self.dense=True

        super().__init__(**kwargs)
        

        self.close = v.Icon(children=['mdi-close'], small=True)
        title = v.CardTitle(class_='pa-0 ma-0',children=[v.Spacer(), self.close])

        self.w_prev = v.Btn(
            _metadata={'name': 'previous'},
            x_small=True,
            children=[v.Icon(left=True, children=['mdi-chevron-left']), 'prev'],
        )

        self.w_next = v.Btn(
            _metadata={'name': 'next'},
            x_small=True,
            children=[v.Icon(small=True, children=['mdi-chevron-right']), 'nxt'],
        )
        self.w_conf = v.Select(
            x12s=True,
            class_='ma-2',
            label='Confidence',
            v_model='All',
        )

        self.w_list = v.Select(
            class_='ma-2', label=self.label, items=self.items, v_model=''
        )

        self.children = [
            title,
            v.Flex(
                class_ = 'd-flex align-center',
                children=[
                    self.w_prev, 
                    self.w_conf, 
                    self.w_list, 
                    self.w_next
                ]
            )
        ]

        link((self.w_list, 'items'), (self, 'items'))
        link((self.w_list, 'v_model'), (self, 'v_model'))
        link((self.w_conf, 'v_model'), (self, 'confidence'))

        self.w_prev.on_event('click', self.prev_next_event)
        self.w_next.on_event('click', self.prev_next_event)
        self.close.on_event('click', lambda *args: self.hide())        

    def prev_next_event(self, widget, change, data):

        current = self.w_list.v_model
        position = -1 if not current else self.w_list.items.index(current)
        last = len(self.w_list.items) - 1

        if widget._metadata['name'] == 'next':
            if position < last:
                self.w_list.v_model = self.w_list.items[position + 1]
        elif widget._metadata['name'] == 'previous':
            if position > 0:
                self.w_list.v_model = self.w_list.items[position - 1]


class Tabs(v.Card):

    current = Int(0).tag(sync=True)

    def __init__(self, titles, content, **kwargs):

        self.background_color = 'primary'
        self.dark = True

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

        link((self.tabs[0], 'v_model'), (self.content[0], 'v_model'))

        super().__init__(**kwargs)


class MetadataTable(v.SimpleTable, SepalWidget):
    """Widget to get a simple table displaying the metadata of the alerts
    
    Args:
        satsource (str model.satsource): Satellite source
    """

    def __init__(self, data, satsource, *args, **kwargs):

        self.dense = True
        self.satsource=satsource

        # Create table
        super().__init__(*args, **kwargs)

        # Build table
        self.get_table(data)

    def get_table(self, data):
        
        def get_row(header, value):

            if header == 'Confidence: ':
                value = v.Chip(
                    small=True, 
                    color=cs.get_confidence_color(self.satsource, value), 
                    children=[value]
                )
                
            return [v.Html(tag='th', children=[header])] + [
                v.Html(tag='td', children=[value])
            ]

        rows = [
            v.Html(tag='tr', children=get_row(str(row_header), str(row_value)))
            for row_header, row_value in data
        ]

        self.children = [v.Html(tag='tbody', children=rows)]
