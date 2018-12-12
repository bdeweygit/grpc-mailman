from concurrent import futures
import time
import grpc

import mailbox_pb2
import mailbox_pb2_grpc

ONE_DAY_IN_SECONDS = 60 * 60 * 24


class MailMan(mailbox_pb2_grpc.MailManServicer):
    def RegisterMailbox(self, request, context):
        pass

    def RemoveMailbox(self, request, context):
        pass

    def GetMail(self, request, context):
        pass

    def SendMail(self, request, context):
        pass

    def GetMailboxes(self, request, context):
        pass


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mailbox_pb2_grpc.add_MailManServicer_to_server(MailMan(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('Starting server. Listening on port 50051.')

    try:
        while True: time.sleep(ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
