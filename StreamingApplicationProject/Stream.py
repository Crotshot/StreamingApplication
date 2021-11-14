from PIL import ImageGrab #Used for getting the the screen
import numpy as np #Used after grabbing screen
from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

webcamNumber = 0
sourceInput = "Screen"


def gen_frames():
    camera = cv2.VideoCapture(webcamNumber)
    while True:
        if sourceInput == "Webcam":
            success, frame = camera.read()
            if success:
                frame = cv2.flip(frame, 1)
            else:
                break
        else:
            screenGrab = np.array(ImageGrab.grab(bbox=(0, 0, 1920, 1080)))  # x, y, w, h
            #screenGrab = np.array(ImageGrab.grab(bbox=(-1920, 0, 1920, 1080)))  # x, y, w, h
            frame = cv2.cvtColor(screenGrab, cv2.COLOR_BGR2RGB)  # Convert PIL screen grab to cv2 colours

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/changeSource')
def changeSource():
    global sourceInput
    if sourceInput == 'Screen':
        sourceInput = 'Webcam'
        print("Source: Webcam")
    else:
        sourceInput = 'Screen'
        print("Source: Screen")
    return ('nothing')

@app.route('/incCam')
def incCam():
    global webcamNumber
    webcamNumber = webcamNumber + 1
    print("Web cam number: " + str(webcamNumber))
    return ('nothing')

@app.route('/lowCam')
def lowCam():
    global webcamNumber
    if webcamNumber > 0:
        webcamNumber = webcamNumber -1
    print("Web cam number: " + str(webcamNumber))
    return ('nothing')

@app.route('/')
def index():
    return render_template('index.html')