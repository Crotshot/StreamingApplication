from PIL import ImageGrab #Used for getting the the screen
import numpy as np #Used after grabbing screen
from flask import Flask, render_template, Response
import cv2
import asyncio

app = Flask(__name__)

webcamNumber = 0
sourceInput = "Screen"
source = False
loop = True
# class EchoServerProtocol:
#     def connection_made(self, transport):
#         self.transport = transport
#
#     def datagram_received(self, data, addr):
#         message = data.decode()
#         print('Received %r from %s' % (message, addr))
#         print('Send %r to %s' % (message, addr))
#         self.transport.sendto(data, addr)

# async def server():
#     print("Starting UDP server")
#     # Get a reference to the event loop as we plan to use low-level APIs.
#     loop = asyncio.get_running_loop()
#
#     # One protocol instance will be created to serve all client requests.
#     transport, protocol = await loop.create_datagram_endpoint(
#         lambda: EchoServerProtocol(),
#         local_addr=('127.0.0.1', 9999))
#
#     try:
#         await asyncio.sleep(3600)  # Serve for 1 hour.
#     finally:
#         transport.close()

def gen_frames():
    global loop
    #asyncio.run(server())
    if sourceInput == "Webcam":
        camera = cv2.VideoCapture(webcamNumber)
        while loop:
            success, frame = camera.read()
            if not success:
                break
            else:
                frame = cv2.flip(frame, 1)
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
    else:
        while loop:
            screenGrab = np.array(ImageGrab.grab(bbox=(0, 0, 1920, 1080)))  # x, y, w, h
            frame = cv2.cvtColor(screenGrab, cv2.COLOR_BGR2RGB)  # Convert PIL screen grab to cv2 colours
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
    if not loop:
        loop = True
        gen_frames()

# class EchoClientProtocol(asyncio.Protocol):
#     def __init__(self, message, on_con_lost):
#         self.message = message
#         self.on_con_lost = on_con_lost
#
#     def connection_made(self, transport):
#         transport.write(self.message.encode())
#         print('Data sent: {!r}'.format(self.message))
#
#     def data_received(self, data):
#         print('Data received: {!r}'.format(data.decode()))
#
#     def connection_lost(self, exc):
#         print('The server closed the connection')
#         self.on_con_lost.set_result(True)
#
# async def client():
#     # Get a reference to the event loop as we plan to use low-level APIs.
#     loop = asyncio.get_running_loop()
#     on_con_lost = loop.create_future()
#     message = 'Hello World!'
#
#     transport, protocol = await loop.create_connection(
#         lambda: EchoClientProtocol(message, on_con_lost),
#         '127.0.0.1', 8888)
#     # Wait until the protocol signals that the connection is lost and close the transport.
#     try:
#         await on_con_lost
#     finally:
#         transport.close()

def get_frames():
    # Loop and receive bytes to make frames with from the server
    #asyncio.run(client())
    print("Waiting. . . ")
    # frame = adwnikoawdonijadwnoja;
    # ret, buffer = cv2.imencode('.jpg', frame)
    # frame = buffer.tobytes()
    # yield (b'--frame\r\n'
    #        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    if source:
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return Response(get_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/changeSource')
def changeSource():
    global sourceInput, loop
    if sourceInput == 'Screen':
        sourceInput = 'Webcam'
    else:
        sourceInput = 'Screen'
    loop = False
    return ('nothing')

@app.route('/')
def index():
    return render_template('index.html')