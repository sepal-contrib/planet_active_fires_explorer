import requests

from planet import api
from planet.api import filters

# from requests.auth import HTTPBasicAuth


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

def remove_layers_if(map_, prop, equals_to, _metadata=False):
    """Remove layers with a given property and value
    
    Args:
    
        map_ (ipyleaflet, geemap, SepalMap): Map with Layers to remove
        prop (str): Property or key (if using _metadata) of Layer
        equals_to (str): Value of property or key (if using _metadata) in Layer
        metadata (Bool): Whether the Layers have _metadata attribute or not
        
    Example:
    
        Adding Markers and removing them by '_metadata' property
        
        marker = Marker(location=(lat, lon))
        
        # As ipyleaflet.Markers doesn't have _metadata property, we could create it
        marker.__setattr__('_metadata', {'type':'manual'})
        
        map_.add_layer(marker)
        
        remove_layers_if(map_, 'type', 'manual', _metadata=True)
        It will remove all Layers with _metadata['type']=='manual'
    """
    if _metadata:
        for layer in map_.layers:
            if hasattr(layer, '_metadata'):
                if layer._metadata[prop]==equals_to: map_.remove_layer(layer)
    else:
        for layer in map_.layers:
            if hasattr(layer, prop):
                if layer.attribution==equals_to: map_.remove_layer(layer)