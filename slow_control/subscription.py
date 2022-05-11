from ariadne import SubscriptionType

from .common import EnumState, clean_live_run_output
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
        run = await _filter_runs(names=None, minStartDate=None,
                                maxStartDate=None, status=EnumState['RUNNING']) 

        if run: 
            # I expect either an empty list or a list with one item 
            # (should not be more than one live run at a time)
            yield clean_live_run_output(run[0])
        else:
            yield None

"""
Subscription
"""

@subscription.field("getLiveRun")
def resolve_live_run(run, info):
    return run