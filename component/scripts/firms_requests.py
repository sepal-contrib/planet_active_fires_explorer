import os

import pandas as pd
import requests

import component.parameter as param
from component.message import cm


def get_availability(firms_key):
    """request data availability (dates) from a request on the fly.

    Args:
        firms_key (str, optional): api key if not found environment key.
    """

    if not firms_key:
        raise Exception(cm.alerts.auth.errors.no_value)

    request_url = param.AVAILABILITY_URL.format(firms_key)
    response = requests.get(request_url)

    # It will return code "200" even if the key doesn't work. let's use the content
    # to determine if the connection was successfull
    if response.text != "Invalid MAP_KEY.":
        return pd.read_csv(request_url)
    else:
        raise Exception(cm.alerts.auth.errors.invalid_firms_key)
