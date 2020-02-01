import asyncio

from aioworker import Worker


async def sleeping(loop):
    while True:
        print("Sleeping for 2 seconds...")
        await asyncio.sleep(2)


async def on_client_connect(reader, writer):
    """
    Read up tp 300 bytes of TCP. This could be parsed usign
    the HTTP protocol for example
    """
    data = await reader.read(300)
    print(f"TCP Server data received: {data} \n")
    writer.write(data)
    await writer.drain()
    writer.close()


if __name__ == "__main__":
    # Run the server using 1 worker processes.
    Worker(
        tasks=[sleeping], web_server_config={"client_connected_cb": on_client_connect}
    ).run(workers=1)
