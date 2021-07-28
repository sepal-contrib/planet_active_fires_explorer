import ipyvuetify as v
from ipywidgets import jslink
from traitlets import Unicode, List, Int, Any, link

from sepal_ui.sepalwidgets import SepalWidget

class Card(v.Card, SepalWidget):
    def __init__(self, *args,**kwargs):
        super().__init__(*args, **kwargs)
        
class Flex(v.Flex, SepalWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
class Select(v.Select, SepalWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
class DatePicker(v.Layout, SepalWidget):
    """
    Custom input widget to provide a reusable DatePicker. It allows to choose date as a string in the following format YYYY-MM-DD
    
    Args:
        label (str, optional): the label of the datepicker field
        
    Attributes:
        menu (v.Menu): the menu widget to display the datepicker
        
    """
    def __init__(self, *args, label="Date", **kwargs):
        
        self.v_model = ''
        self.row = True
        self.class_ = 'pa-5'
        self.align_center = True

        super().__init__(*args, **kwargs)
        
        date_picker = v.DatePicker(
            no_title = True, 
            v_model = '', 
            scrollable = True
        )

        date_text = v.TextField(
            v_model = '',
            label = label,
            hint = "YYYY-MM-DD format",
            persistent_hint = True, 
            prepend_icon = "event",
            readonly = True,
            v_on = 'menuData.on'
        )

        self.menu = v.Menu(
            min_width="290px",
            transition = "scale-transition",
            offset_y = True, 
            value = False,
            close_on_content_click = False,
            children = [date_picker],
            v_slots = [{
                'name': 'activator',
                'variable': 'menuData',
                'children': date_text,
            }]
        )

        self.children = [
            v.Flex(xs10=True, children=[self.menu])
        ]
        
        jslink((date_picker, 'v_model'), (date_text, 'v_model'))
        jslink((date_picker, 'v_model'), (self, 'v_model'))
    
class DynamicSelect(v.Card):
    
    """ Widget to navigate with next and previous buttons over a list
    
    Args:
        items (list) : List of items to be displayed in select list
        label (str) : Label to display into widget
        
    Parameters:
        v_model (traitlets.Any): Current element from select list
        
    Example:
        
        [1] ds = DynamicSelect(items=[1,2,3,4,5])
            ds # Display Dynamic select widget
        
        [2] # add behaviour once v_model changes
            ds.observe(lambda x: print(x), 'v_model')
    """
    
    items = List([]).tag(sync=True)
    v_model = Any().tag(sync=True)
    confidence = Unicode('All').tag(sync=True)
    
    def __init__(self, label='', **kwargs):
        
        self.class_='d-flex align-center px-2'
        self.row=True
        self.label = label
        
        super().__init__(**kwargs)
        
        self.w_prev = v.Btn(
            _metadata = {'name':'previous'},
            x_small=True, 
            children=[
                v.Icon(left=True,children=['mdi-chevron-left']),
                'prev'
            ])

        self.w_next = v.Btn(
            _metadata = {'name' : 'next'},
            x_small=True, 
            children=[
                v.Icon(children=['mdi-chevron-right']),
                'nxt'
            ])
        self.w_conf = v.Select(
            class_='ma-2', 
            label='Confidence', 
            v_model='All', 
            items=['All', 'Low','High', 'Nominal']
        )
        
        self.w_list = v.Select(
            class_='ma-2',
            label=self.label, 
            items=self.items,
            v_model=''
        )

        self.children = [
            self.w_prev,
            self.w_conf,
            self.w_list,
            self.w_next
        ]
        
        link((self.w_list, 'items'),(self, 'items'))
        link((self.w_list, 'v_model'),(self, 'v_model'))
        link((self.w_conf, 'v_model'),(self, 'confidence'))
        
        self.w_prev.on_event('click', self.prev_next_event)
        self.w_next.on_event('click', self.prev_next_event)
        
    def prev_next_event(self, widget, change, data):
        
        current = self.w_list.v_model
        position = -1 if not current else self.w_list.items.index(current)
        last = len(self.w_list.items) - 1
            
        if widget._metadata['name']=='next':
            if position < last:
                self.w_list.v_model = self.w_list.items[position+1]

        elif widget._metadata['name']=='previous':
            if position > 0:
                self.w_list.v_model = self.w_list.items[position-1]
                
class Tabs(v.Card):
    
    current = Int(0).tag(sync=True)
    
    def __init__(self, titles, content, **kwargs):
        
        self.background_color="primary"
        self.dark = True
        
        self.tabs = [
            v.Tabs(
                v_model=self.current, 
                children=[
                    v.Tab(children=[title], key=key) 
                    for key, title in enumerate(titles)
                ]
            )
        ]
        
        self.content = [
            v.TabsItems(
                v_model=self.current, 
                children=[
                    v.TabItem(children=[content], key=key) 
                    for key, content 
                    in enumerate(content)
                ]
            )
        ]
        
        self.children= self.tabs + self.content
        
        link((self.tabs[0], 'v_model'),(self.content[0], 'v_model'))
        
        super().__init__(**kwargs)

class MetadataTable(v.SimpleTable, SepalWidget):
    """Widget to get a simple table displaying the metadata alerts"""
    
    def __init__(self, data, *args, **kwargs):
        
        self.dense = True

        # Create table
        super().__init__(*args, **kwargs)
        
        # Build table
        self.get_table(data)
        
        
    def get_table(self, data):
                
        CONFIDENCE = {'low':'red', 'high':'green', 'nominal':'orange'}
        
        def get_row(header, value):
            
            if header == 'Confidence: ':
                value = v.Chip(
                    small=True, 
                    color=CONFIDENCE[value],
                    children=[value]
                )
            
            return [
                v.Html(tag = 'th', children=[header]) 
            ] + [v.Html(tag='td', children=[value])]
        
        rows = [
            v.Html(
                tag='tr', 
                children=get_row(str(row_header), str(row_value))
            ) for row_header, row_value in data
        ]
        
        self.children = [v.Html(tag = 'tbody', children = rows)]