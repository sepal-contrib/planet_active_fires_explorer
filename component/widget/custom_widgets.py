# -*- coding: utf-8 -*-

import datetime
from functools import partial

import ipyvuetify as v
from traitlets import (
    Unicode, observe, directional_link, 
    List, Int, Bool, Any, link
)

from sepal_ui.sepalwidgets.sepalwidget import SepalWidget, TYPES
from sepal_ui.frontend.styles import sepal_darker

    
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
        
        self.class_='d-flex align-center mb-2'
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
                
                
class Tooltip(v.Tooltip):
    
    def __init__(self, widget, tooltip, *args, **kwargs):
        """
        Custom widget to display tooltip when mouse is over widget

        Args:
            widget (DOM.widget): widget used to display tooltip
            tooltip (str): the text to display in the tooltip
            
        Example:
            
            btn = v.Btn(children=['Button'])
            Tooltip(widget=btn, tooltip='Click over the button')
        """
        
        self.bottom=True
        self.v_slots=[{
            'name': 'activator',
            'variable': 'tooltip',
            'children': widget
        }]
        widget.v_on = 'tooltip.on'
        
        self.children = [tooltip]
        
        super().__init__(*args, **kwargs)
        
    def __setattr__(self, name, value):
        """prevent set attributes after instantiate tooltip class"""
        
        if hasattr(self,'_model_id'):
            if self._model_id:
                raise RuntimeError(f"You can't modify the attributes of the {self.__class__} after instantiated")
        super().__setattr__(name, value)
        
class Tabs(v.Card):
    
    current = Int(0).tag(sync=True)
    
    def __init__(self, titles, content, **kwargs):
        
        self.background_color="primary"
        self.dark = True
        
        self.tabs = [v.Tabs(v_model=self.current, children=[
            v.Tab(children=[title], key=key) for key, title in enumerate(titles)
        ])]
        
        self.content = [v.TabsItems(
            v_model=self.current, 
            children=[
                v.TabItem(children=[content], key=key) for key, content in enumerate(content)
            ]
        )]
        
        self.children= self.tabs + self.content
        
        link((self.tabs[0], 'v_model'),(self.content[0], 'v_model'))
        
        super().__init__(**kwargs)