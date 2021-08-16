import ipyvuetify as v
from traitlets import Unicode, List, Int, Any, link

from sepal_ui.sepalwidgets import SepalWidget
from component.parameter import *
from component.message import cm
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

        self.label = label
        self.dense=True
        self.max_width='520'
        
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
            class_='mt-4',
            dense=True,
            label='Confidence',
            v_model='All',
        )

        self.w_list = v.Select(
            class_='mt-4 ml-2', 
            label=self.label, 
            items=self.items, 
            v_model='',
            dense=True,
        )
        
        widgets = [self.w_prev,self.w_conf,self.w_list,self.w_next]
        
        self.children = [
            v.Row(
                no_gutters =True,
                align='center',
                children=[
                    v.Col(
                        cols=f'{col}',
                        class_='text-center',
                        children=[widget]
                    ) for col, widget in zip([2,3,5,2], widgets)
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
                
    def reset(self):
        """Restore widgets and values to default"""
        
        self.items = []
        self.v_model = ''
        self.confidence = 'All'
        
        self.w_conf.items = []
        
                

class AlertMenu(v.Menu):

    def __init__(self, widget, *args, **kwargs):

        self.value=False
        self.close_on_content_click = False
        self.nudge_width = 200
        self.offset_x=True

        super().__init__()
        
        self.nav_btn = v.Btn(
            v_on='menu.on',
            icon = True, 
            children=[v.Icon(children=['mdi-cloud-download'])]
        )
        
        self.v_slots = [{
            'name': 'activator',
            'variable': 'menu',
            'children': self.nav_btn
        }]
        
        self.children=[widget]

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


class MetadataTable(v.Card, SepalWidget):
    """Widget to get a simple table displaying the metadata of the alerts"""
    
    validate = Unicode('').tag(sync=True)
    observ = Unicode('').tag(sync=True)

    def __init__(self, *args, **kwargs):
        self.max_width='250px'

        # Create table
        super().__init__(*args, **kwargs)
        
        self.close = v.Icon(children=['mdi-close'], small=True)
        self.title = v.CardTitle(class_='pa-0 ma-0', children=[v.Spacer(), self.close])
                
        self.close.on_event('click', lambda *args: self.hide())
        
        self.w_validate = v.Select(
            items=[
                {'text':cm.alerts.metadata.items.yes, 'value':'yes'},
                {'text':cm.alerts.metadata.items.no, 'value':'not'}
            ], 
            dense=True, 
            v_model=self.validate
        )
        self.w_observ = v.Textarea(dense=True, rows=2, v_model=self.observ)
        
        link((self, 'validate'), (self.w_validate, 'v_model'))
        link((self, 'observ'), (self.w_observ, 'v_model'))
        

    def update(self, satsource, data):
        """Create metadata Simple Table based on the given data
        
        Args:
            satsource (str model.satsource): Satellite source
            data (list of lists): Each element has to follow: [header, value]
        """
        
        def get_row(header, value):

            if header == 'confidence':
                value = v.Chip(
                    small=True, 
                    color=cs.get_confidence_color(satsource, value), 
                    children=[value]
                )
            
            elif header == 'validate':
                self.w_validate.v_model = value
                value = self.w_validate
            
            elif header == 'observ':
                self.w_observ.v_model = value
                value = self.w_observ
                
            return [v.Html(tag='th', children=[f'{METADATA_ROWS[header]}: '])] + [
                v.Html(tag='td', children=[value])
            ]

        rows = [
            v.Html(tag='tr', children=get_row(str(row_header), str(row_value)))
            for row_header, row_value in data
        ]

        self.children = [self.title] + [
            v.SimpleTable(dense=True, children=[v.Html(tag='tbody', children=rows)])
        ]
    
    def reset(self):
        """Create an empty table"""
        
        self.children=[]
        