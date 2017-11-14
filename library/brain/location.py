import logging, json, math, time, threading
from hestiarpi.library.helper import geo
from hestiarpi.config import common

_STATUS_NOT_CHANGED = 0
_STATUS_BIGGER = 1
_STATUS_SMALLER = 2
_STATUS_CONTINUOUS_BIGGER = 3
_STATUS_CONTINUOUS_SMALER = 4

_TIME_INTERNAL = 60 # one minute for save location info to var `_last_entry`
_TIME_INTERNAL_4_MONITOR = 60 # for `monitor interval`
_TIME_MAX_PAST_4_MONITOR = 600 # for monitor `max past time`, within which to operate
_DIS_HOME_BOUNDARY = 1000 # for `home boundary`, by which to determine back home or leave home

_last_entry = {"last_dis" : 0, "last_time" : 0, "last_status" : _STATUS_NOT_CHANGED}

_start_monitor = False
_did_leave_home = False
_did_back_home = False

def execute(msg):
    logging.info("[library.brain.location:execute] msg:" + msg)
    global _start_monitor
    _set_status(msg)
    if _start_monitor == False:
        _start_monitor = True
        t1 = threading.Thread(target=_monitor)
        t1.setDaemon(True)
        t1.start()

def _set_status(msg):
    global _last_entry

    # get dis
    msg_obj = json.loads(msg)
    dis = geo.get_distance_hav(msg_obj["data"]["lnt"], msg_obj["data"]["lat"], common.HOME_LNG, common.HOME_LAT)
    dis = int(math.floor(dis * 1000))
    logging.info("[library.brain.location:_set_status] dis:" + str(dis) + "m")

    # frequency
    if _last_entry["last_time"] + _TIME_INTERNAL >= int((math.floor(time.time()))):
        logging.info("[library.brain.location:_set_status] return by frequency limit")
        return

    # set status
    if dis == _last_entry["last_dis"] or 0 == _last_entry["last_dis"]:
        logging.info('no changes')
        _last_entry["last_status"] = _STATUS_NOT_CHANGED
    elif dis < _last_entry["last_dis"] and (_last_entry["last_status"] == _STATUS_SMALLER
            or _last_entry["last_status"] == _STATUS_CONTINUOUS_SMALER):
        logging.info("c smaller")
        _last_entry["last_status"] = _STATUS_CONTINUOUS_SMALER
    elif dis > _last_entry["last_dis"] and (_last_entry["last_status"] == _STATUS_BIGGER
            or _last_entry["last_status"] == _STATUS_CONTINUOUS_BIGGER):
        logging.info("c bigger")
        _last_entry["last_status"] = _STATUS_CONTINUOUS_BIGGER
    elif dis < _last_entry["last_dis"] and (_last_entry["last_status"] == _STATUS_NOT_CHANGED
            or _last_entry["last_status"] == _STATUS_BIGGER or _last_entry["last_status"] == _STATUS_CONTINUOUS_BIGGER):
        logging.info("smaller")
        _last_entry["last_status"] = _STATUS_SMALLER
    elif dis > _last_entry["last_dis"] and (_last_entry["last_status"] == _STATUS_NOT_CHANGED
            or _last_entry["last_status"] == _STATUS_SMALLER or _last_entry["last_status"] == _STATUS_CONTINUOUS_SMALER):
        logging.info("bigger")
        _last_entry["last_status"] = _STATUS_BIGGER
    else:
        logging.warning("[library.brain.location:_set_status] unknown status")

    _last_entry["last_dis"] = dis
    _last_entry["last_time"] = int(math.floor(time.time()))

    # print
    logging.info("[library.brain.location:_set_status] now entry info status:"
            + str(_last_entry["last_status"]) + " time:" + str(_last_entry["last_time"]))

# _last_entry = {"last_dis" : 0, "last_time" : 0, "last_status" : _STATUS_NOT_CHANGED}
def _monitor():
    global _last_entry
    while True:
        logging.info("[library.brain.location:_monitor] did start")
        if _last_entry["last_dis"] < _DIS_HOME_BOUNDARY and (_last_entry["last_status"] == _STATUS_SMALLER or _last_entry["last_status"] == _STATUS_CONTINUOUS_SMALER) and (int((math.floor(time.time()))) - _last_entry["last_time"] < _TIME_MAX_PAST_4_MONITOR):
                   # back home
            _back_home()
        elif _last_entry["last_dis"] >= _DIS_HOME_BOUNDARY and (_last_entry["last_status"] == _STATUS_BIGGER or _last_entry["last_status"] == _STATUS_CONTINUOUS_BIGGER) and (int((math.floor(time.time()))) - _last_entry["last_time"] < _TIME_MAX_PAST_4_MONITOR):
                   # leave home
            _leave_home()
        # sleep
        time.sleep(_TIME_INTERNAL_4_MONITOR)

def _leave_home():
    logging.info("[library.brain.location:_leave_home] did start")
    global _did_leave_home
    global _did_back_home
    if _did_leave_home == True:
        return
    _did_leave_home = True
    _did_back_home = False

def _back_home():
    logging.info("[library.brain.location:_back_home] did start")
    global _did_leave_home
    global _did_back_home
    if _did_back_home == True:
        return
    _did_back_home = True
    _did_leave_home = False
