import sys
import grpc

import mailbox_pb2
import mailbox_pb2_grpc

MAILMAN_ADDRESS = 'localhost:50051'

REGISTER_MAILBOX = 'register_mailbox'

def print_usage():
    print('TODO: display commandline usage')

def register_mailbox(name):
    request = mailbox_pb2.RegisterMailboxRequest(name=name)
    with grpc.insecure_channel(MAILMAN_ADDRESS) as channel:
        stub = mailbox_pb2_grpc.MailManStub(channel)
        response = stub.RegisterMailbox(request)
    if response.password: print(f'Your mailbox password is {response.password}')
    else: print(response.error)


def run():
    try:
        request_type = sys.argv[1]

        if request_type == REGISTER_MAILBOX:
            try:
                name = sys.argv[2]
                register_mailbox(name=name)
            except:
                print_usage()
        else:
            print_usage()
    except:
        print_usage()


if __name__ == '__main__':
    run()
