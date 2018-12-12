from concurrent import futures
from threading import Timer
import math
import time
import random
import string
import grpc

import mailbox_pb2
import mailbox_pb2_grpc

ONE_YEAR_IN_SECONDS = 60 * 60 * 24 * 365


class Mail():
    def __init__(self, timestamp, source_name, destination_name, message):
        self.TIMESTAMP = timestamp
        self.SOURCE_NAME = source_name
        self.DESTINATION_NAME = destination_name
        self.MESSAGE = message


class Mailbox():
    def __init__(self, name):
        self.NAME = name
        self.PASSWORD = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        self.mails = []
        self.flag_is_up = False


class MailMan(mailbox_pb2_grpc.MailManServicer):
    def __init__(self):
        self.mailboxes = {}
        self.next_delivery_time = 0
        self.DELIVERY_INTERVAL = 60 # seconds
        self._Work()

    def _Now(self):
        return (math.floor(time.time()) / 1000)


    def _Work(self):
        Timer(self.DELIVERY_INTERVAL, self._Work).start()
        self.next_delivery_time = self._Now() + self.DELIVERY_INTERVAL
        self._DeliverMail()

    def _DeliverMail(self):
        bag = []
        for _, mailbox in self.mailboxes.items():
            if mailbox.flag_is_up:
                bag.extend(mailbox.mails)
                mailbox.mails.clear()
                mailbox.flag_is_up = False

        for mail in bag:
            destination_mailbox = self.mailboxes.get(mail.DESTINATION_NAME, False)
            if destination_mailbox: destination_mailbox.mails.append(mail)

    def RegisterMailbox(self, request, context):
        name = request.name

        response = mailbox_pb2.RegisterMailboxReply()
        if name in self.mailboxes:
            response.error = f'mailbox name "{name}" is already taken'
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
        else: response.error = f'{name} does not exist'

        return response

    def GetMail(self, request, context):
        name = request.name
        password = request.password

        response = mailbox_pb2.GetMailReply()
        mailbox = self.mailboxes.get(name, False)
        if not mailbox: response.error = f'{name} does not exist'
        elif password != mailbox.PASSWORD: response.error = 'wrong password'
        elif mailbox.flag_is_up: response.error = 'mailbox flag is up'
        else:
            for mail in mailbox.mails:
                t_stamp = mail.TIMESTAMP
                s_name = mail.SOURCE_NAME
                d_name = mail.DESTINATION_NAME
                msg = mail.MESSAGE
                response.mails.add(timestamp=t_stamp, source_name=s_name, destination_name=d_name, message=msg)
            mailbox.mails.clear()

        return response

    def SendMail(self, request, context):
        password = request.password
        mail = request.mail
        timestamp = mail.timestamp
        source_name = mail.source_name
        destination_name = mail.destination_name
        message = mail.message

        response = mailbox_pb2.SendMailReply()
        source_mailbox = self.mailboxes.get(source_name, False)
        if not source_mailbox: response.error = f'{source_name} does not exist'
        elif password != source_mailbox.PASSWORD: response.error = 'wrong password'
        elif destination_name not in self.mailboxes: response.error = f'{destination_name} does not exist'
        else:
            if not source_mailbox.flag_is_up:
                for stale_mail in source_mailbox.mails:
                    t_stamp = stale_mail.TIMESTAMP
                    s_name = stale_mail.SOURCE_NAME
                    d_name = stale_mail.DESTINATION_NAME
                    msg = stale_mail.MESSAGE
                    response.mails.add(timestamp=t_stamp, source_name=s_name, destination_name=d_name, message=msg)
                source_mailbox.mails.clear()
            outgoing_mail = Mail(timestamp=timestamp, source_name=source_name, destination_name=destination_name, message=message)
            source_mailbox.mails.append(outgoing_mail)
            source_mailbox.flag_is_up = True
            response.time_until_pickup = self.next_delivery_time - self._Now()

        return response

    def ListMailboxes(self, request, context):
        query = request.query

        response = mailbox_pb2.ListMailboxesReply()
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
        while True: time.sleep(ONE_YEAR_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
