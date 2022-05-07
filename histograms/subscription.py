from ariadne import SubscriptionType

from .common import  commsep_to_int
import asyncio
import datetime

subscription = SubscriptionType()

""" Asynchronous generator
"""

SUB_SLEEP_TIME = 1 # [seconds] to wait in between subscription calls

from .query import _filter_histograms

@subscription.source("getLiveHistograms")
async def source_live_histograms(obj, info):
    while True:
        await asyncio.sleep(SUB_SLEEP_TIME)
        yield await _filter_histograms(ids=None, types=None, minDate=None, maxDate=None, 
                        minBins=None, maxBins=None, isLive=True)

"""
Subscription
"""

@subscription.field("getLiveHistograms")
def resolve_live_histograms(histograms, info):
    if histograms:
        for i, hist in enumerate(histograms):
            histograms[i].data = commsep_to_int( hist.data )
        return histograms
    else:
        return []