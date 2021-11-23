import ctypes.wintypes

from PIL import ImageGrab, Image #Used for getting the the screen
import numpy as np #Used after grabbing screen
from flask import Flask, render_template, Response
import cv2
import os

from nudenet import NudeDetector
detector = NudeDetector()

from numba import jit, cuda
app = Flask(__name__)

webcamNumber = 0
sourceInput = "Webcam"
webcamChanged = True
playing = True
background = None
motionTracking = False
refresh = 30
censoring = False
cwd = os.path.dirname(os.path.abspath(__file__))
os.chdir(cwd)


def gen_frames():
    global sourceInput, refresh, motionTracking, webcamChanged, background, censoring
    censorParts = detector.detect("in/frame.jpg", "fast")
    webcamChanged = True
    cam = cv2.VideoCapture(webcamNumber)
    while True:
        if not playing:
            continue
        if webcamChanged:
            cam = cv2.VideoCapture(webcamNumber)
            webcamChanged = False

        refC = False
        if refresh == 30:
            refC = True

        preByte, frame = frameCalc(sourceInput, cam, refresh, censoring, censorParts, refC, background, motionTracking)

        if type(preByte) == bool:
            continue
        else:
            if refresh == 0:
                background = refBackground(preByte)
                refresh = 60
            else:
                refresh = refresh - 1

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

    #os.remove("in/frame.jpg")
    os.remove("out/frame.jpg")

@jit
def refBackground(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    backg = cv2.GaussianBlur(gray, (21, 21), 0)
    return backg

@jit
def frameCalc(source, camera, ref, censor, cParts, refCen, backg, motC):
    if source == "Webcam":
        success, frame = camera.read()
        if success:
            frame = cv2.flip(frame, 1)
        else:
            return False, False
    else:
        screenGrab = np.array(ImageGrab.grab(bbox=(0, 0, 1920, 1080)))  # x, y, w, h
        # screenGrab = np.array(ImageGrab.grab(bbox=(-1920, 0, 1920, 1080)))  # x, y, w, h
        frame = cv2.cvtColor(screenGrab, cv2.COLOR_BGR2RGB)  # Convert PIL screen grab to cv2 colours
    # if stop:
    #     return

    if motC:
        countK = 0
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        subtraction = cv2.absdiff(backg, gray)
        threshold = cv2.threshold(subtraction, 55, 255, cv2.THRESH_BINARY)[1]
        contourimg = threshold.copy()
        outlines, hierarchy = cv2.findContours(contourimg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for c in outlines:
            if cv2.contourArea(c) < 6000:
                continue
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    if censor:
        print(ref)
        cv2.imwrite("in/frame.jpg", frame)

        if refCen:
            cParts = detector.detect("in/frame.jpg", "fast")
        detector.censor("in/frame.jpg", "out/frame.jpg", cParts)
        frame = cv2.imread("out/frame.jpg")

    ret, buffer = cv2.imencode('.jpg', frame)
    bufferedFrame = buffer.tobytes()
    return frame, bufferedFrame


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
    global webcamChanged
    webcamChanged = True
    webcamNumber = webcamNumber + 1
    print("Web cam number: " + str(webcamNumber))
    return ('nothing')


@app.route('/lowCam')
def lowCam():
    global webcamNumber
    global webcamChanged
    if webcamNumber > 0:
        webcamNumber = webcamNumber -1
        webcamChanged = True
    print("Web cam number: " + str(webcamNumber))
    return ('nothing')


@app.route('/togglePlay')
def togglePlay():
    global playing
    if playing:
        playing = False
    else:
        playing = True
    return ('nothing')


@app.route('/toggleCensoring')
def stopStream():
    global censoring
    if censoring:
        censoring = False
    else:
        censoring = True
    return ('nothing')


@app.route('/toggleMotion')
def toggleMotion():
    global motionTracking
    if motionTracking:
        motionTracking = False
    else:
        motionTracking = True
    return ('nothing')


@app.route('/remakeBackground')
def remakeBackground():
    global refresh
    refresh = 0
    return ('nothing')


@app.route('/')
def index():
    return render_template('index.html')