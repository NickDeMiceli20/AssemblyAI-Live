import websockets
import asyncio
import base64
import json
from streamlink import Streamlink
from config import AAI_API_KEY


stream_url = "https://youtu.be/Pd3kElWNjBU" #Change to current live stream url before running
FRAMES_PER_BUFFER = 3200


# Streamlink session
session = Streamlink()
streams = session.streams(stream_url)
stream = streams['best'].open()


# AAI websocket endpoint
url = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"


async def send_receive():
    print(f'Connecting websocket to url ${url}')
    async with websockets.connect(
        url,
        extra_headers=(('Authorization', AAI_API_KEY),),
        ping_interval=5,
        ping_timeout=20
    ) as _ws:
        await asyncio.sleep(0.1)
        print("Receiving session started...")
        session_begins = await _ws.recv()
        print(session_begins)
        print("Sending messages...")

        async def send():
            while True:
                try:
                    data = stream.read(FRAMES_PER_BUFFER)
                    data = base64.b64encode(data).decode("latin-1")
                    json_data = json.dumps({'audio_data': str(data)})
                    await _ws.send(json_data)
                    print(f'Sent: {type(json_data)}')

                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break

                except Exception as e:
                    print(e)
                    assert False, "Not a websocket 4008 error."

                await asyncio.sleep(0.1)

            return True

        async def receive():
            while True:
                try:
                    result_str = await _ws.recv()
                    print(f"Received: {result_str}")
                    print(json.loads(result_str))
                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break
                except Exception as e:
                    print(e)
                    assert False, "Not a websocket 4008 error"

        send_result, receive_result = await asyncio.gather(send(), receive())

asyncio.run(send_receive())