import asyncio
import websockets

async def greet_client(websocket, path):
    greeting = "안녀하세요"
    await websocket.send(greeting)
    print(f"Sent greeting: {greeting}")

async def main():
    async with websockets.serve(greet_client, "localhost", 9999):
        await asyncio.Future()  # 이벤트 루프를 무한 대기 상태로 유지

if __name__ == "__main__":
    asyncio.run(main())
