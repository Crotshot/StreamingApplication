from PIL import ImageGrab
import numpy as np
from flask import Flask, render_template, Response
import cv2
app = Flask(__name__)

#https://pypi.org/project/pyrtmp/ ->Just Browsing

webcamNumber = 0
sourceInput = ""

def gen_frames():
    if sourceInput == "Webcam":
        camera = cv2.VideoCapture(webcamNumber)
        while True:
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
        while True:
            screenGrab = np.array(ImageGrab.grab(bbox=(0, 0, 1920, 1080)))  # x, y, w, h
            frame = cv2.cvtColor(screenGrab, cv2.COLOR_BGR2RGB)  # Convert PIL screen grab to cv2 colours
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

def get_frames():
    # Wait for frames to ,come from the network
    print("Waiting. . . ")


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')