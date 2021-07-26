import sepal_ui.sepalwidgets as sw
from component.tiles import RecentAlerts, HistoricAlerts
from sepal_ui.scripts import utils as su


class Flex(v.Flex):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        
class Flex(v.Select):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
    
    
class AlertsTile(v.Card):
    
    TIME_SPAN = ['24 hours', '48 hours', '7 days', 'Historic']
    
    def __init__(self, model, *args, **kwargs):
        
        self.model = model
        self.w_alert = sw.Alert()
        
        # Recent alerts
        self.w_recent = Select(
            label="In the last",
            items=self.TIME_SPAN,
            v_model=self.model.timespan,
        )
        
        # Historic Alerts
        self.w_start = sw.DatePicker(label='Start date (inclusive)')
        self.w_end = sw.DatePicker(label='End date (inclusive)')
        self.w_historic = Flex(
            class_='d-flex',
            children=[self.w_start, self.w_end]
        ).hide()
        
        # Selection type
        self.w_alerts_type = v.RadioGroup(
            label = "Type of alerts",
            row= True,
            v_model = self.model.alerts_type,
            children = [
                v.Radio(key=1, label='Recent', value='Recent'),
                v.Radio(key=2, label='Historical', value='Historical'),
            ]
        )
        
        self.children=[
            self.w_alerts_type,
            self.w_recent,
            self.w_historic,
        ]
        
        self.model.bind(self.w_alerts_type, 'alerts_type')\
                .bind(self.w_spantime, 'timespan')\
                .bind(self.self.w_start, 'start_date')\
                .bind(self.self.w_start, 'end_date')\
        
        self.w_alerts_type.observe(self.toggle_components)

        def toggle_components(self, change):
            """Toggle components based on Radio groups"""
            
            if change['new'] == 'Recent':
                su.show_component(self.w_recent)
                su.hide_component(self.w_historic)

            elif change['new'] == 'Historical':
                su.show_component(self.w_historic)
                su.hide_component(self.w_recent)
                

            