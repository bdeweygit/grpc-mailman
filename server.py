from concurrent import futures
import time
import random
import string
import grpc

import mailbox_pb2
import mailbox_pb2_grpc

ONE_DAY_IN_SECONDS = 60 * 60 * 24
PASSWORD_LENGTH = 8

class Mailbox():
    def __init__(self, name):
        self.NAME = name
        self.PASSWORD = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(PASSWORD_LENGTH))


class MailMan(mailbox_pb2_grpc.MailManServicer):
    def __init__(self):
        self.mailboxes = {}

    def RegisterMailbox(self, request, context):
        name = request.name

        response = mailbox_pb2.RegisterMailboxReply()
        if name in self.mailboxes:
            response.error = 'mailbox name is already taken'
        else:
            mailbox = Mailbox(name=name)
            self.mailboxes[name] = mailbox
            response.password = mailbox.PASSWORD

        return response


    def RemoveMailbox(self, request, context):
        name = request.name
        password = request.password

        response = mailbox_pb2.RemoveMailboxReply()
        mailbox = self.mailboxes.get(name, False)
        if mailbox:
            if mailbox.PASSWORD == password: del self.mailboxes[name]
            else: response.error = 'wrong password'
        else: response.error = 'mailbox does not exist'

        return response

    def GetMail(self, request, context):
        pass

    def SendMail(self, request, context):
        pass

    def GetMailboxes(self, request, context):
        query = request.query

        response = mailbox_pb2.GetMailboxesReply()
        names = [*self.mailboxes]
        if query:
            filtered_names = [*filter(lambda name: query.lower() in name.lower(), names)]
            response.names.extend(filtered_names)
        else:
            response.names.extend(names)

        return response


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
