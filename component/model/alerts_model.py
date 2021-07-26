from traitlets import Any, Unicode, Int
from sepal_ui import model



class AlertModel(model.Model):
    
    # Input parameters
    timespan = Unicode('24 hours').tag(sync=True)
    
    # Planet parameters
    
    cloud_cover = Int(20).tag(sync=True)
    days_before = Int(0).tag(sync=True)
    max_images = Int(6).tag(sync=True)
    api_key = Unicode('').tag(sync=True)
    
    
    alerts_type = Unicode('Recent').tag(sync=True)
    start_date = Any().tag(sync=True)
    end_date = Any().tag(sync=True)