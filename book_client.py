import asyncio
import grpc

# Import the generated stubs and messages
import book_pb2
import book_pb2_grpc


async def run():
    # Connect to the gRPC server
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        # Create a stub (client) object
        stub = book_pb2_grpc.BookServiceStub(channel)

        # 1. Create the Book message
        new_book_data = book_pb2.Book(
            title="The Grand gRPC Adventure",
            author="Gemini Model"
        )

        # 2. Create the Request message, wrapping the Book
        request = book_pb2.CreateBookRequest(book=new_book_data)

        print(f"Client sending request to create book: '{new_book_data.title}'...")

        try:
            # 3. Call the RPC method
            response = await stub.CreateBook(request)

            # 4. Handle the Response
            print("\n--- Server Response ---")
            if response.success:
                print(f"SUCCESS: {response.message}")
            else:
                print(f"FAILURE: {response.message}")
            print("-----------------------")

        except grpc.RpcError as e:
            print(f"An RPC Error Occurred: {e}")



if __name__ == '__main__':
    asyncio.run(run())