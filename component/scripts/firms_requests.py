import os

import pandas as pd
import requests

import component.message as cm
import component.parameter as param


def get_availability(firms_key=None):
    """request data availability (dates) from a request on the fly.

    Args:
        firms_key (str, optional): api key if not found environment key.
    """

    firms_key = os.getenv("FIRMS_API_KEY") or firms_key

    if not firms_key:
        raise Exception(cm.errors.no_firms_key)

    request_url = param.AVAILABILITY_URL.format(firms_key)

    # response = requests.get(request_url)

    # if response.status_code == 200:
    return pd.read_csv(request_url)
    # else:
    #     raise Exception(cm.errors.invalid_firms_key)
