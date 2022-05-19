from ariadne import SubscriptionType

from .common import EnumState, calc_time_elapsed
import asyncio

subscription = SubscriptionType()

""" Asynchronous generator
"""

SUB_SLEEP_TIME = 1 # [seconds] to wait in between subscription calls

from .query import _filter_runs

@subscription.source("getLiveRun")
async def source_live_run(obj, info):
    while True:
        # Keep checking the database until a live run appears
        await asyncio.sleep(SUB_SLEEP_TIME)
        run = await _filter_runs(names=None, minStartDate=None, maxStartDate=None, 
                                minSubDate=None, maxSubDate=None, status=EnumState['RUNNING']) 

        if run: 
            # subscription currently does not expect there to be more than one live
            # run at a time
            run[0].timeElapsed = calc_time_elapsed(run[0])
            yield run[0]
        else:
            yield None


"""
Subscription
"""

@subscription.field("getLiveRun")
def resolve_live_run(run, info):
    return run