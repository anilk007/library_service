(1) Generate the Protobuf Message File

protoc --js_out=import_style=commonjs,binary:. --proto_path=. book.proto
protoc --js_out=import_style=commonjs,binary:. --proto_path=. member.proto
protoc --js_out=import_style=commonjs,binary:. --proto_path=. borrowing_records.proto

(2) pip install grpcio grpcio-tools

python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. book.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. member.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. borrowing_records.proto

(3) py server.py

gRPC Book Service server is listening on port 50051.
