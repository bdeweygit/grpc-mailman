import sys
import grpc

import mailbox_pb2
import mailbox_pb2_grpc

MAILMAN_ADDRESS = 'localhost:50051'

REGISTER_MAILBOX = 'register_mailbox'
REMOVE_MAILBOX = 'remove_mailbox'
GET_MAILBOXES = 'get_mailboxes'

def print_usage():
    print('TODO: display commandline usage')

def register_mailbox(name):
    request = mailbox_pb2.RegisterMailboxRequest(name=name)
    with grpc.insecure_channel(MAILMAN_ADDRESS) as channel:
        stub = mailbox_pb2_grpc.MailManStub(channel)
        response = stub.RegisterMailbox(request)

    password = response.password
    error = response.error

    if password: print(f'your mailbox password is {password}')
    else: print(error)

def remove_mailbox(name, password):
    request = mailbox_pb2.RemoveMailboxRequest(name=name, password=password)
    with grpc.insecure_channel(MAILMAN_ADDRESS) as channel:
        stub = mailbox_pb2_grpc.MailManStub(channel)
        response = stub.RemoveMailbox(request)

    error = response.error

    if error: print(error)
    else: print('mailbox removed')

def get_mailboxes(query):
    request = mailbox_pb2.GetMailboxesRequest(query=query)
    with grpc.insecure_channel(MAILMAN_ADDRESS) as channel:
        stub = mailbox_pb2_grpc.MailManStub(channel)
        response = stub.GetMailboxes(request)

    names = response.names

    if len(names) > 0:
        for name in names: print(name)
    else: print('no results')


def run():
    try:
        request_type = sys.argv[1]

        if request_type == REGISTER_MAILBOX:
            try:
                name = sys.argv[2]
                register_mailbox(name=name)
            except: print_usage()

        elif request_type == REMOVE_MAILBOX:
            try:
                name = sys.argv[2]
                password = sys.argv[3]
                remove_mailbox(name=name, password=password)
            except: print_usage()

        elif request_type == GET_MAILBOXES:
            try: query = sys.argv[2]
            except: query = ''
            finally: get_mailboxes(query=query)

        else:
            print_usage()
    except:
        print_usage()


if __name__ == '__main__':
    run()
