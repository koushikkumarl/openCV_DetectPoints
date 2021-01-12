import cv2
import numpy as np
from flask import Flask, render_template, Response

app = Flask(__name__)

def getContours(img, imgContour):
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        #minArea = cv2.getTrackbarPos("Area", "Parameters")
        if area > 10000:
            cv2.drawContours(imgContour, contours, -1, (255, 0, 255), 3)
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02*peri, True)
            x, y, w, h = cv2.boundingRect(approx)
            cv2.rectangle(imgContour, (x, y), (x+w, y+h), (0,255,0), 5)
            cv2.putText(imgContour, "Points: " + str(len(approx)), (x+w+20, y+20), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,255,0), 1)
            cv2.putText(imgContour, "Area: " + str(int(area)), (x+w+20, y+50), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0), 1)


def empytFunction(arg1):
    pass

framewidth = 640
frameheight = 480
# cv2.namedWindow("Parameters")
# cv2.resizeWindow("Parameters", 640, 240)
# cv2.createTrackbar("Threshold1", "Parameters", 110, 255, empytFunction)
# cv2.createTrackbar("Threshold2", "Parameters", 60, 255, empytFunction)
#cv2.createTrackbar("Area", "Parameters", 10000, 30000, empytFunction)

### Use this code for Webcam / external video source
capDevice = cv2.VideoCapture(0)

### Use this code to use recorded video
#capDevice = cv2.VideoCapture('./Resources/Shapes_all.mp4')
capDevice.set(3, framewidth)
capDevice.set(4, frameheight)

def getShape():
    while True:
        threshold1 = 110 #cv2.getTrackbarPos("Threshold1", "Parameters")
        threshold2 = 60 #cv2.getTrackbarPos("Threshold2", "Parameters")

        success, img = capDevice.read()
        try:
            imgContour = img.copy()
        except:
            print("End of Video Sequence - Terminating program")
            exit()
        imgBlur = cv2.GaussianBlur(img, (5,5), 1)
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        imgCanny = cv2.Canny(imgGray, threshold1, threshold2)
        imgDil = cv2.dilate(imgCanny, np.ones((5,5)), iterations=1)
        getContours(imgDil, imgContour)

        ret, buffer = cv2.imencode('.jpg', imgContour)
        imgContour = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + imgContour + b'\r\n')
        # cv2.imshow("Input Feed", imgContour)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

@app.route('/video_feed')
def video_feed():
    return Response(getShape(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False)