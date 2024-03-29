import requests

import component.parameter as param

__all__ = [
    "get_thresholds",
    "get_confidence_color",
    "parse_offset",
]


def get_thresholds(lower):
    """Get the upper limit based on the lower value"""

    thres = sorted(param.CONFIDENCE["disc"].keys(), reverse=True)
    upper = 100 if thres.index(lower) == 0 else thres[thres.index(lower) - 1]

    return (upper, lower)


def parse_offset(offset):
    """it will return a parsed integer from text offsets available in
    offset_days widget items.

    Example:
        [parse_ofsset(offset) for offset in ['24 hours', '48 hours', '3 days']]
        [1, 2, 3]
    """

    number = int("".join(filter(str.isdigit, offset)))
    return number if number < 11 else int(number / 24)


def get_confidence_color(satsource, value):
    """Return confidence color depending on the satellite type

    Args:
        satsource (str): Satellite soure, depending on the satellite source,
            the confidence will be categorical (high, nominal, low )
            or discrete (raging from 0-100)
        value (int, str): The confidence value
    """

    # Get the type of the confidence representation, categorical or discrete
    type_ = "disc" if satsource in ["modis_sp", "modis_nrt"] else "cat"

    # Get category name and color into a dictionary
    confidence_color = {k: v[1] for k, v in param.CONFIDENCE[type_].items()}

    if type_ == "disc":

        thresholds = sorted(param.CONFIDENCE["disc"].keys(), reverse=True)

        for threshold in thresholds:
            if int(value) >= threshold:
                break

        return confidence_color[threshold]

    else:
        return confidence_color[value]
