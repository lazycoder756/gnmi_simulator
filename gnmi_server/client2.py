from protos import gnmi_pb2,gnmi_pb2_grpc
import grpc
from concurrent import futures
import time

class AuthInterceptor(grpc.UnaryUnaryClientInterceptor):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def intercept_unary_unary(self, continuation, client_call_details, request):
        metadata = [
            ('username', self.username),
            ('password', self.password),
        ]
        client_call_details = client_call_details._replace(metadata=metadata)
        return continuation(client_call_details, request)


def create_gnmi_client():
    channel = grpc.intercept_channel(grpc.insecure_channel('localhost:50051'), AuthInterceptor('your_username', 'your_password'))
    stub = gnmi_pb2_grpc.gNMIStub(channel)
    return stub

def create_subscribe_request():
    #while(True):
        path = gnmi_pb2.Path(
            elem = [gnmi_pb2.PathElem(name="system")]
        )
        subscr = gnmi_pb2.Subscription(
            path = path,
            mode = gnmi_pb2.SubscriptionMode.ON_CHANGE
        )
        sub_list = gnmi_pb2.SubscriptionList(
            subscription = [subscr],
            mode = gnmi_pb2.SubscriptionList.ONCE,
            encoding = gnmi_pb2.Encoding.JSON_IETF
        )

        sub_request = gnmi_pb2.SubscribeRequest()
        sub_request.subscribe.CopyFrom(sub_list)


        path1 = gnmi_pb2.Path(
            elem = [gnmi_pb2.PathElem(name="clock")]
        )
        subscr1 = gnmi_pb2.Subscription(
            path = path1,
            mode = gnmi_pb2.SubscriptionMode.ON_CHANGE
        )
        sub_list1 = gnmi_pb2.SubscriptionList(
            subscription = [subscr1],
            mode = gnmi_pb2.SubscriptionList.STREAM,
            encoding = gnmi_pb2.Encoding.JSON_IETF
        )

        sub_request1 = gnmi_pb2.SubscribeRequest()
        sub_request1.subscribe.CopyFrom(sub_list1)
        for i in  sub_request1,sub_request:  
            yield i

def main():
    metadata = [('username', 'admin'), ('password', 'Vema@123')]
    stub = create_gnmi_client()
    su_resp = stub.Subscribe(create_subscribe_request(),metadata=metadata)
    for i in su_resp:
        if not i.sync_response:
            print(i)

if __name__ == "__main__":
    main()