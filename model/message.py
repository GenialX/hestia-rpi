#!/usr/bin/env python

import hestiarpi.config.common as htcommon

# UNKNOWN
MESSAGE_TYPE_UNKNOWN = 0

#  FROM iOS
MESSAGE_TYPE_IOS_DATA_LOCATION = 1000

# FROM CENTER SERVER
MESSAGE_TYPE_CSERVER_DATA_SOMEWHAT = 2000

# FROM RPi
MESSAGE_TYPE_RPI_DATA_DEVICE_INFO = 3000

# {'errno': 0, 'data': {'messge_type': 0, 'token': 'aaabbbccc'}, 'errmsg': 'successfully'}
def get_common_msg():
    result = {}
    data = {}
    result["errno"] = 0
    result["errmsg"] = "successfully"
    data["messge_type"] = MESSAGE_TYPE_UNKNOWN
    data["token"] = htcommon.SERVER_IDENTITY_TOKEN
    result["data"] = data
    return result

# {'errno': 0, 'data': {'messge_type': 0, 'token': 'aaabbbccc', 'message_type': 3000, 'client_key': 'raspberry_pi_client_key'}, 'errmsg': 'successfully'}
def get_rpi_data_device_info_message():
    result = get_common_msg()
    result["data"]["message_type"] = MESSAGE_TYPE_RPI_DATA_DEVICE_INFO
    result["data"]["client_key"] = htcommon.CLIENT_RPI_CLIENT_KEY
    return result
