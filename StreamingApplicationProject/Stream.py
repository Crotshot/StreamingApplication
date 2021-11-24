from PIL import ImageGrab, Image  # Used for screenshotting for screen streaming
import numpy as np  # Used after grabbing screen for image processing
from flask import Flask, render_template, Response #Python mini web framework
#from numba import jit, cuda #Used to put code on the GPU for faster processing (Disable as could not get functioning)
from nudenet import NudeDetector # Used to censor the images
import cv2  # Image processing
import os  # Changing working directory

app = Flask(__name__) # Flask application


webcamNumber = 0 #Index of webcam
refresh = 30 #Variable used to refresh motion capture background

sourceInput = "Screen" # Source input of stream, Webcam or Screen

webcamChanged = True # Used to update the current camera
playing = True #Toggle for pause/playing the stream
motionTracking = False # Toggle motion tracking
censoring = False # Toggle censoring
backgroundRefresh = True # Toggle motion background refreshing

cwd = os.path.dirname(os.path.abspath(__file__)) # Get path of current file
os.chdir(cwd) # Change working Directory to directory of this file


# <editor-fold desc="Frame generation">
def gen_frames():
    global sourceInput, refresh, motionTracking, webcamChanged, censoring, backgroundRefresh, webcamNumber
    background = None # Background

    cam = cv2.VideoCapture(webcamNumber) # Assign camera

    det = NudeDetector()  # NudeDetector constructor
    censorParts = det.detect("in/frame.jpg", "fast") # Generate first censored frame

    while True:
        if not playing:
            continue
        if webcamChanged: # Update webcam
            cam = cv2.VideoCapture(webcamNumber)
            webcamChanged = False

        refC = False
        if refresh == 30: #Refresh Censor everytime refresh is 30 (Every 60 frames)
            refC = True
        #preByte is frame before it is turned to bytes and frame is after it is turned to bytes
        preByte, frame, temp = frameCalc(sourceInput, cam, refresh, censoring, censorParts, refC, background, motionTracking, det)

        if type(temp) != bool:
            censorParts = temp
        if type(preByte) == bool: #If camera was not successfully read it frameCalc returns a boolean
            continue
        else:
            if refresh == 0:#Refresh motion capture background every 60 frames
                if backgroundRefresh and sourceInput == "Webcam":
                    background = refBackground(preByte) #Use frame before it is turned to bytes for background refreshing
                refresh = 60
            else:
                refresh -= 1

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Add byte frame, then show it

    os.remove("in/frame.jpg")

# @jit#(target = "cuda")
def refBackground(frame): # Motion censor background is a gray scaled image with a blur
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    backg = cv2.GaussianBlur(gray, (21, 21), 0)
    return backg

# @jit#(target = "cuda")
def frameCalc(source, camera, ref, censor, cParts, refCen, backg, motC, detector):
    if source == "Webcam":
        success, frame = camera.read()
        if success: # If Webcam try to read active camera and flip result , if fails returns false
            frame = cv2.flip(frame, 1)
        else:
            return False, False, False
    elif source == "Screen": # Grab screen and change colour to rgb from bgr (A little slow as it is done currently on the CPU)
        screenGrab = np.array(ImageGrab.grab(bbox=(0, 0, 1920, 1080)))  # x, y, width, height
        frame = cv2.cvtColor(screenGrab, cv2.COLOR_BGR2RGB)  # Convert PIL screen grab to cv2 colours


    if motC and source == "Webcam": # Motion capture for webcam
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) # Grayscale frame
        gray = cv2.GaussianBlur(gray, (21, 21), 0) # Blur gray frame
        subtraction = cv2.absdiff(backg, gray) # Subtract background and gray frame
        threshold = cv2.threshold(subtraction, 55, 255, cv2.THRESH_BINARY)[1]
        contourimg = threshold.copy() # Compare differences and if an area is large enough get an outline for it
        outlines, hierarchy = cv2.findContours(contourimg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for c in outlines:
            if cv2.contourArea(c) < 6000:
                continue
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2) # Draw all the outlines over the frame

    if censor:
        print(ref) # Censoring is currently done on CPU and is very slow, printing refresh here for debugging purposes
        if refCen:
            cv2.imwrite("in/frame.jpg", frame)  # Write current frame to folder
            cParts = detector.detect("in/frame.jpg", mode="fast") # Read in folder and detect what needs to be censored (This is the really heavy part)
        if len(cParts) > 0:
            for i in range(len(cParts)):
                box = cParts[i]["box"]
                print(str(box[0]) + ", " + str(box[1]) + ", " + str(box[2]) + ", " + str(box[3]) + ", ")
                cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 0, 0), -1)

    ret, buffer = cv2.imencode('.jpg', frame) # Encode frame into memory buffer
    bufferedFrame = buffer.tobytes() # Convert buffered frame to byte string
    return frame, bufferedFrame, cParts
# </editor-fold>

# <editor-fold desc="app routes">
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


@app.route('/autoRemakeBackground')
def autoRemakeBackground():
    global backgroundRefresh
    if backgroundRefresh:
        backgroundRefresh = False
    else:
        backgroundRefresh = True
    return ('nothing')


@app.route('/')
def index():
    return render_template('index.html')
# </editor-fold>