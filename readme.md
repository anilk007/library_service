

(1) py -m pip install asyncpg --only-binary=all

>pip install -r requirements.txt

py -m pip install -r requirements.txt

pip install fastapi uvicorn[standard] asyncpg pydantic python-dotenv

py -m pip install fastapi

py -m pip install uvicorn[standard]

py -m pip install pydantic

py -m pip install python-dotenv

py -m pip install asyncpg

py -m pip install 'pydantic[email]'

"C:\Users\hello\AppData\Local\Programs\Python\Python312\python.exe" -m venv venv

venv\Scripts\activate

>uvicorn main:app --reload

(2) PostgreSQL Schema script is available in postgresql_scripts folder.

(3) Generate the Protobuf Message File

protoc --js_out=import_style=commonjs,binary:. --proto_path=. book.proto
protoc --js_out=import_style=commonjs,binary:. --proto_path=. member.proto
protoc --js_out=import_style=commonjs,binary:. --proto_path=. borrowing_records.proto

(4) pip install grpcio grpcio-tools

python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. book.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. member.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. borrowing_records.proto

(5) py server.py

gRPC Book Service server is listening on port 50051.
