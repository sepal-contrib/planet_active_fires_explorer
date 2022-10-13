API_URL = "https://firms.modaps.eosdis.nasa.gov/api/"

# FIRMS_KEY, sat_source, bounds, offset_days
REQUEST_RECENT = API_URL + "area/csv/{}/{}/{}/{}"

# Just add the last parameter "start_date"
REQUEST_HISTORIC = REQUEST_RECENT + "/{}"

# {firms_api_key}: get satellite sources and availability dates
AVAILABILITY_URL = API_URL + "data_availability/csv/{}/ALL"

PLANET_TILES_URL = (
    "https://tiles0.planet.com/data/v1/{}/{}/{{z}}/{{x}}/{{y}}.png?api_key={}"
)

# Use a light Countries geoJson file to improve speed of loading and clipping
COUNTRIES_JSON = (
    "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
)
