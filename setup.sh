#!/bin/bash
set +x
virtualenv -p python3 env
source ./env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. mailbox.proto
