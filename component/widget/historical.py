import ipyvuetify as v
import sepal_ui.sepalwidgets as sw


class Historical(v.Card):
    
    
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        w_start_date = sw.DatePicker(label='Start date (inclusive)')
        w_end_date = sw.DatePicker(label='End date (inclusive)')
        w_alert = sw.Alert()
        btn = sw.Btn()
        
        
        self.children=[
            
        ]