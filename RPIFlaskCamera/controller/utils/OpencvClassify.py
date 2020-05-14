import os
import time
import cv2    


class OpencvWrapper(object):
    def __init__(self):
        self.cascade_ped_src="controller/utils/data/cas_classify/haarcascade_fullbody.xml"    # 注意路径， 更目录是app.py 所在的目录
        self.facesrc="controller/utils/data/cas_classify/haarcascade_frontalface_default.xml"
        self.ped_cascade = cv2.CascadeClassifier(self.facesrc)


    def get_object(self, frame):
        found_objects = False
         # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        objects = self.get_objects(self.ped_cascade, gray)

        if len(objects) > 0:
            found_objects = True
        # Draw a rectangle around the objects
        for (x, y, w, h) in objects:
            x *= 4
            y *= 4
            w *= 4
            h *= 4
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        return frame, found_objects

    def get_objects(self, classifier, gray):
        objects = classifier.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=5,
            minSize=(30, 30)
        )
        return objects

if __name__ == "__main__":
    wrapper=OpencvWrapper()
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        frame,_=wrapper.get_object(frame)
        # ret, jpeg = cv2.imencode('.jpg', frame)
        cv2.imshow("result", frame)
        c = cv2.waitKey(10)
        if c == 27: # ESC
            break