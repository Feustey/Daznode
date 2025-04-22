#!/bin/bash

# Générer les fichiers protobuf
python -m grpc_tools.protoc \
    --python_out=. \
    --grpc_python_out=. \
    --proto_path=. \
    lightning.proto 