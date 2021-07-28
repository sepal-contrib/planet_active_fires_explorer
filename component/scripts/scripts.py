import requests

from planet import api
from planet.api import filters

from component.parameter import *




class PlanetKey:
    
    def __init__(self, api_key):
        
        self.api_key = api_key
        self.url = 'https://api.planet.com/auth/v1/experimental/public/my/subscriptions'
        self.subs = None
        self.active = None
        
    def client(self):
        
        return api.ClientV1(api_key=self.api_key)
        
    def get_subscription(self):
        
        resp = requests.get(self.url, auth=(self.api_key, ''))
        subscriptions = resp.json()
        
        if resp.status_code == 200: return subscriptions
    
    def is_active(self):
        
        subs = self.get_subscription()
        active = [False]
        
        if subs: active = [True for sub in subs if sub['state'] == 'active']
        
        return any(active)
    
def validate_api_event(self, widget, change, data, alert):

    api_key = self.w_api_key.v_model

    planet_key = PlanetKey(api_key)
    self.client = planet_key.client()

    self.valid_api = planet_key.is_active()

    if self.valid_api:
        self.w_api_alert.add_msg(cm.ui.success_api.msg, cm.ui.success_api.type)
        self._toggle_planet_setts(on=True)
    else:
        self.w_api_alert.add_msg(cm.ui.fail_api.msg, cm.ui.fail_api.type)
        self._toggle_planet_setts(on=False)

def build_request(aoi_geom, start_date, stop_date, cloud_cover=100):
    """build a data api search request for PS imagery.

    Args:
        aoi_geom (geojson): 
        start_date (datetime.datetime)
        stop_date (datetime.datetime)

    Returns:
        Request
    """

    query = filters.and_filter(
        filters.geom_filter(aoi_geom),
        filters.range_filter('cloud_cover', lte=cloud_cover),
        filters.date_range('acquired', gt=start_date),
        filters.date_range('acquired', lt=stop_date)
    )

    # Skipping REScene because is not orthorrectified and 
    # cannot be clipped.

    return filters.build_search_request(query, [
        'PSScene3Band', 
        'PSScene4Band', 
        'PSOrthoTile',
        'REOrthoTile',
    ])

def get_items(id_name, request, client):
    """ Get items using the request with the given parameters
           
    """
    result = client.quick_search(request)
 
    items_pages = []
    limit_to_x_pages = None
    for page in result.iter(limit_to_x_pages):
        items_pages.append(page.get())

    items = [item for page in items_pages for item in page['features']]
    
    
    return (id_name, items)

