#Import necessary libraries
from flask import Flask, render_template, Response
import cv2
app = Flask(__name__)

webcamNumber = 0
source = ""

def gen_frames():
    camera = cv2.VideoCapture(webcamNumber)  # 0 is local web cam
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            frame = cv2.flip(frame, 1)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


def get_frames():
    # Wait for frames to ,come from the network
    print("Waiting. . . ")


@app.route('/video_feed')
def video_feed():
    if source == "Webcam":
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif source == "Screen":
        return Response(get_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    return render_template('index.html')

# Determine whether we are receiving or sending
# If Sending -> Send over network
# If receiving -> Wait