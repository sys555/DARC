import grpc
import masrpc_pb2
import masrpc_pb2_grpc

import json
from loguru import logger

def run():
    # 创建与服务器的通道
    with grpc.insecure_channel('localhost:50051') as channel:
        # 创建存根
        stub = masrpc_pb2_grpc.MasRPCStub(channel)

        # 调用 Load 方法
        load_request = masrpc_pb2.LoadRequest(graph_id="36f9144c-e071-4e6f-a6fa-e020eca699c3")
        load_response = stub.Load(load_request)
        print("Load response:", load_response.status)

        # 调用 Send 方法
        send_request = masrpc_pb2.SendRequest(uid="2d934217-d28e-48fd-aafc-1a61675afa10", message={"content": "hi"})
        send_response = stub.Send(send_request)
        print("Send response:", send_response.status)

        # # 调用 GetLog 方法
        import time
        time.sleep(24)
        get_log_request = masrpc_pb2.GetLogRequest(uid="2d934217-d28e-48fd-aafc-1a61675afa10")
        get_log_response = stub.GetLog(get_log_request)
        print("GetLog response:", get_log_response.status)
        print("Logs:", get_log_response.logs)
        for log in get_log_response.logs:
            data = json.loads(log)
            print(data)

if __name__ == '__main__':
    run()