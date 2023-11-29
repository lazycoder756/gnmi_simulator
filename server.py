import grpc
import os
from concurrent import futures
import time
from utils import create_subscribe_response
from protos import gnmi_pb2,gnmi_pb2_grpc


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
        
    
    def Subscribe(self, request_iterator, context):
        if is_cred_valid(context):        
            request_list = list(request_iterator)
            sub_check = False
            once_check = False

            for req in request_list:
                if req.subscribe.mode==0 and sub_check!=True:
                    sub_check = True
                if req.subscribe.mode==1 and once_check!=True:
                    once_check = True

            if sub_check:
                sub_resp = create_subscribe_response.create_response()
                for i in sub_resp:
                    yield i
                    time.sleep(1)

            if once_check:
                sub_resp = create_subscribe_response.create_response()
                sync_resp = create_subscribe_response.create_sync_response()
                for i in sub_resp:
                    yield i
                for j in sync_resp:
                    yield j
                once_check=False

                
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