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
        histograms = await _filter_histograms(ids=None, names=None, types=None, 
                                        minDate=None, maxDate=None, isLive=True)
        if histograms:
            for i, hist in enumerate(histograms):
                histograms[i].x = commsep_to_int( hist.x )
                histograms[i].y = commsep_to_int( hist.y )
                if histograms[i].x and histograms[i].y:
                    histograms[i].xCurrent = histograms[i].x[-1]
                    histograms[i].yCurrent = histograms[i].y[-1]
            yield histograms


"""
Subscription
"""

@subscription.field("getLiveHistograms")
def resolve_live_histograms(histograms, info):
    return histograms
