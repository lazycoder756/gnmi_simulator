from datetime import datetime
from utils import parse_subscribe_input_file
import re
import json
import time
from protos import gnmi_pb2

square_pattern = r'\[.*?\]'

def create_response():
    subscribe_paths = parse_subscribe_input_file.read_txt_file("/app/paths/paths.txt")
    for subscribe_path in subscribe_paths:
        nodes = subscribe_path.split("/")
        path_elems = []
        for node in nodes[1:-1]:
            match = re.findall(square_pattern,node)
            if match:
                path_elem = gnmi_pb2.PathElem()
                elem_name = node.split("[")[0]
                path_elem.name = elem_name
                for key_val in match:
                    _key_val = key_val[1:-1].split("=")
                    path_elem.key[_key_val[0]]=_key_val[1]
                path_elems.append(path_elem)

            else:
                path_elem = gnmi_pb2.PathElem()
                path_elem.name = node
                path_elems.append(path_elem)
        _value = nodes[-1].split("=")
        _value_dict = {_value[0]:eval(_value[1])}
        final_value = json.dumps(_value_dict)
        val = gnmi_pb2.TypedValue(json_ietf_val=final_value.encode('utf-8'))
 
        update_message = gnmi_pb2.Update(
            path=gnmi_pb2.Path(elem = path_elems),
            val =val
        )
        current_datetime = datetime.now()
        epoch_in_millisec = int(current_datetime.timestamp()*1000)
        notification = gnmi_pb2.Notification(timestamp=epoch_in_millisec,update=[update_message])
        sub_response = gnmi_pb2.SubscribeResponse()
        sub_response.update.CopyFrom(notification)
        yield sub_response

def create_get_response_val():
    path_rep_dict={}
    get_paths = parse_subscribe_input_file.read_txt_file("paths.txt")
    for i in get_paths:
        key_val = i.rsplit('=', 1)
        path_rep_dict[key_val[0]]=eval(key_val[1])
    return path_rep_dict


def create_sync_response():
    sub_response = gnmi_pb2.SubscribeResponse()
    sub_response.sync_response = True
    yield sub_response
