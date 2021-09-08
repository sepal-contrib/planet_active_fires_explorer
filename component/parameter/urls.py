# Path to download all historic fires for a given year
HISTORIC_URL = (
    "https://firms2.modaps.eosdis.nasa.gov/data/country/zips/{}_{}_all_countries.zip"
)

#  3gpd.read_file
RECENT_URL = (
    "https://firms.modaps.eosdis.nasa.gov/data/active_fire/{}/csv/{}_Global_{}.csv"
)

PLANET_TILES_URL = (
    "https://tiles0.planet.com/data/v1/{}/{}/{{z}}/{{x}}/{{y}}.png?api_key={}"
)

# Use a light Countries geoJson file to improve speed of loading and clipping
COUNTRIES_JSON = (
    "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
)
