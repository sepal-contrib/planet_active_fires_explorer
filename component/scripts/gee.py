from typing import Literal

import ee

from component.parameter.app import GEE_SOURCES


def _merge_hist(current, previous):
    """merge two dictionaries by summing counts for each confidence key."""
    current = ee.Dictionary(current)
    previous = ee.Dictionary(previous)
    keys = current.keys()

    def _accumulate(key, acc):
        acc = ee.Dictionary(acc)
        k = ee.String(key)
        # sum the counts, defaulting to 0 if key missing
        return acc.set(k, ee.Number(acc.get(k, 0)).add(ee.Number(current.get(k))))

    return ee.List(keys).iterate(_accumulate, previous)


def summarize_alerts(
    name: Literal["MODIS", "SNPP", "NOAA20"],
    start_date: str,  # YYYY-MM-DD
    end_date: str,  # YYYY-MM-DD
    geom: ee.Geometry,
    confidence_threshold,
):
    """
    Returns a single ee.Feature with properties:
      - 'dataset': the dataset name
      - 'total_alerts': total pixels >= threshold across all images
      - 'confidence_histogram': merged histogram of confidence values
    """

    source = GEE_SOURCES[name]

    filtered = ee.ImageCollection(source["asset_id"]).filterDate(start_date, end_date)

    def per_image(image):
        conf = image.select(source["bands"])
        masked = conf.updateMask(conf.gte(confidence_threshold))
        hist = masked.reduceRegion(
            reducer=ee.Reducer.frequencyHistogram(),
            geometry=geom,
            scale=source["scale"],
            maxPixels=1e13,
            bestEffort=True,
        ).get("confidence")
        hist = ee.Dictionary(hist)
        return ee.Feature(None, {"confidence_histogram": hist})

    stats_fc = filtered.map(per_image)

    hist_list = stats_fc.aggregate_array("confidence_histogram")
    summed = ee.Dictionary(ee.List(hist_list).iterate(_merge_hist, ee.Dictionary({})))

    total = ee.Number(summed.values().reduce(ee.Reducer.sum()))

    return ee.Feature(
        None, {"dataset": name, "total_alerts": total, "confidence_histogram": summed}
    )
