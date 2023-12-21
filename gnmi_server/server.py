import grpc
import os
from concurrent import futures
import time
from utils import create_subscribe_response
from protos import gnmi_pb2,gnmi_pb2_grpc
import json
from datetime import datetime
import sys


class gnmi_server(gnmi_pb2_grpc.gNMIServicer):

    def Capabilities(self, request, context):
        if is_cred_valid(context):
            try:
                response = gnmi_pb2.CapabilityResponse()
                model = response.supported_models.add()
                model.name = "openconfig-model"
                model.version = "1.0"
                response.supported_encodings.extend(["JSON_IETF"])
                response.gNMI_version="23.3"
                return response
            except Exception as e:
                print(f"Exception in capabilities:{e}")
                context.set_code(grpc.StatusCode.UNKNOWN)
                context.set_details(f"Exception calling application: {str(e)}")
                return gnmi_pb2.CapabilityResponse()
            
    def Get(self, request, context):
        resp_dict=create_subscribe_response.create_get_response_val()
        notification_list=[]
        if is_cred_valid(context):
            for i in request.path:
                path_string=""
                for j in i.elem:
                    path_string=path_string+"/"+j.name
                    if j.key:
                        for key,value in j.key.items():
                            path_string=path_string+"["+key+"="+value+"]"
                val=None
                if resp_dict.get(path_string) is not None:
                    _value_dict={}
                    _value_dict[path_string.rsplit('/', 1)[1]] = resp_dict[path_string]
                    final_value = json.dumps(_value_dict)
                    val = gnmi_pb2.TypedValue(json_ietf_val=final_value.encode('utf-8'))
                i.elem.pop()
                _request = i
                update_msg = gnmi_pb2.Update(
                    path=_request,
                    val=val
                )
                current_datetime = datetime.now()
                epoch_in_millisec = int(current_datetime.timestamp()*1e9)
                notification = gnmi_pb2.Notification(
                    timestamp = epoch_in_millisec,
                    update = [update_msg]
                )
                notification_list.append(notification)
            return gnmi_pb2.GetResponse(notification=notification_list)

    def Subscribe(self, request_iterator, context):
        if is_cred_valid(context):
            sub_count = 0
            once_count = 0
            for req in request_iterator:
                if req.subscribe.mode==0:
                    if sub_count==0:
                        sub_count=sub_count+1
                        while True:
                            sub_resp = create_subscribe_response.create_response()
                            for i in sub_resp:
                                yield i
                else:
                    if once_count == 0:
                        once_count=once_count+1
                        sub_resp = create_subscribe_response.create_response()
                        sync_resp = create_subscribe_response.create_sync_response()
                        for i in sub_resp:
                            yield i
                        for j in sync_resp:
                            yield j
                    else:
                        once_count=0
                        break
        
def serve():    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    gnmi_pb2_grpc.add_gNMIServicer_to_server(gnmi_server(),server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("gNMI server started on port 50051")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

def is_cred_valid(context):
        metadata = dict(context.invocation_metadata())
        username = metadata.get("username", "")
        password = metadata.get("password", "")
        if username != user or password != passwd:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("Invalid credentials")
            return False
        return True

if __name__ == "__main__":
    user = os.environ.get("USER_NAME","admin")
    passwd = os.environ.get("PASSWORD","Vema@123")
    serve()