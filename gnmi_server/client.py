from protos import gnmi_pb2,gnmi_pb2_grpc
import grpc
from concurrent import futures
import time
from threading import Thread


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
        path = gnmi_pb2.Path(
            elem = [gnmi_pb2.PathElem(name="system")]
        )
        subscr = gnmi_pb2.Subscription(
            path = path,
            mode = gnmi_pb2.SubscriptionMode.ON_CHANGE
        )
        sub_list = gnmi_pb2.SubscriptionList(
            subscription = [subscr],
            mode = gnmi_pb2.SubscriptionList.STREAM,
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

def create_subscribe_request_once():
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
            mode = gnmi_pb2.SubscriptionList.ONCE,
            encoding = gnmi_pb2.Encoding.JSON_IETF
        )

        sub_request1 = gnmi_pb2.SubscribeRequest()
        sub_request1.subscribe.CopyFrom(sub_list1)
        for i in  sub_request1,sub_request:  
            yield i

def call_subscribe(stub,metadata):
    while True:
        su_resp = stub.Subscribe(create_subscribe_request(),metadata=metadata)
        for i in su_resp:
            if not i.sync_response:
                print(i)

def call_subscribe_once(stub,metadata):
    su_resp = stub.Subscribe(create_subscribe_request(),metadata=metadata)
    for i in su_resp:
        if not i.sync_response:
            print("Upload scenario",i)

def create_get_request():
    path = gnmi_pb2.Path(
        elem = [gnmi_pb2.PathElem(name="system",key={"sad":"sd","sds":"sdsd"}),gnmi_pb2.PathElem(name="clock"),gnmi_pb2.PathElem(name="time")]
    )
    encoding = gnmi_pb2.Encoding.JSON_IETF

    get_req = gnmi_pb2.GetRequest(
        path=[path],
        encoding=encoding
    )
    return get_req



def main():
    metadata = [('username', 'admin'), ('password', 'Vema@123')]
    stub = create_gnmi_client()
    get_resp = stub.Get(create_get_request(),metadata=metadata)
    print(get_resp)
    #t1 = Thread(target=call_subscribe,args=(stub,metadata))
    #t2 = Thread(target=call_subscribe_once,args=(stub,metadata))
    #t1.start()
    #t2.start()

    #t1.join()
    #t2.join()

if __name__ == "__main__":
    main()