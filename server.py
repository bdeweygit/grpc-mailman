from concurrent import futures
from threading import Timer
import time
import random
import string
import grpc

import mailbox_pb2
import mailbox_pb2_grpc

ONE_DAY_IN_SECONDS = 60 * 60 * 24
PASSWORD_LENGTH = 8


class Mail():
    def __init__(self, timestamp, sender_name, receiver_name, message):
        self.TIMESTAMP = timestamp
        self.SENDER_NAME = sender_name
        self.RECEIVER_NAME = receiver_name
        self.MESSAGE = message


class Mailbox():
    def __init__(self, name):
        self.NAME = name
        self.PASSWORD = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(PASSWORD_LENGTH))
        self.mails = []
        self.flag_is_up = False


class MailMan(mailbox_pb2_grpc.MailManServicer):
    def __init__(self):
        self.mailboxes = {}
        self.Work()

    def Work():
        Timer(60, self.Work).start()
        self.DeliverMail()

    def DeliverMail():
        bag = []
        for mailbox in self.mailboxes:
            if mailbox.flag_is_up:
                bag.extend(mailbox.mails)
                mailbox.mails.clear()
                mailbox.flag_is_up = False

        for mail in bag:
            receiver_name = mail.receiver_name
            self.mailboxes[receiver_name].mails.append(mail)

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
        name = request.name
        password = request.password

        response = mailbox_pb2.GetMailReply()
        mailbox = self.mailboxes.get(name, False)
        if not mailbox: response.error = 'mailbox does not exist'
        elif password != mailbox.PASSWORD: response.error = 'wrong password'
        elif mailbox.flag_is_up: response.error = 'mailbox flag is up'
        else:
            for mail in mailbox.mails:
                t_stamp = mail.TIMESTAMP
                s_name = mail.SENDER_NAME
                r_name = mail.RECEIVER_NAME
                msg = mail.MESSAGE
                response.mails.add(timestamp=t_stamp, sender_name=s_name, receiver_name=r_name, message=msg)
            mailbox.mails.clear()

        return response

    def SendMail(self, request, context):
        password = request.password
        mail = request.mail
        timestamp = mail.timestamp
        sender_name = mail.sender_name
        receiver_name = mail.receiver_name
        message = mail.message

        response = mailbox_pb2.SendMailReply()
        sending_mailbox = self.mailboxes.get(sender_name, False)
        if not sending_mailbox: response.error = 'sending mailbox does not exist'
        elif password != sending_mailbox.PASSWORD: response.error = 'wrong password'
        elif receiver_name not in self.mailboxes: response.error = 'recipient mailbox does not exist'
        else:
            if not sending_mailbox.flag_is_up:
                for stale_mail in sending_mailbox.mails:
                    t_stamp = stale_mail.TIMESTAMP
                    s_name = stale_mail.SENDER_NAME
                    r_name = stale_mail.RECEIVER_NAME
                    msg = stale_mail.MESSAGE
                    response.mails.add(timestamp=t_stamp, sender_name=s_name, receiver_name=r_name, message=msg)
                sending_mailbox.mails.clear()
            outgoing_mail = Mail(timestamp=timestamp, sender_name=sender_name, receiver_name=receiver_name, message=message)
            sending_mailbox.mails.append(outgoing_mail)
            sending_mailbox.flag_is_up = True

        return response

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
