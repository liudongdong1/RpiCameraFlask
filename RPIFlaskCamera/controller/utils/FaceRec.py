# 这是一个在树莓派上运行人脸识别的案例
# 本案例会在命令行控制面板上输出识别出的人脸数量和身份结果。

# 你需要一个2代以上的树莓派，并在树莓派上安装face_recognition，并连接上picamera摄像头
# 并确保picamera这个模块已经安装（树莓派一般会内置安装）
# 你可以参考这个教程配制你的树莓派：
# https://gist.github.com/ageitgey/1ac8dbe8572f3f533df6269dab35df65

import face_recognition
import numpy as np
import os
import cv2

# 你需要在sudo raspi-config中把camera功能打开
class FaceRec(object):
    def __init__(self,process=True):
        self.process_this_frame=process
        known_face_encodings,known_face_names=self.loadFaceDatabase()


    def loadFaceDatabase(self):
        # Load known people from the database/ folder as database
        known_faces = os.listdir('../img/database')
        root = os.path.realpath('../img/database')

        # Create arrays of known face encodings and their names
        known_face_encodings = []
        known_face_names = []

        for known_face in known_faces:
            name = known_face[:-4]
            path = os.path.join(root, known_face)
            face_image = face_recognition.load_image_file(path)
            face_encoding = face_recognition.face_encodings(face_image=face_image)[0]
            known_face_encodings.append(face_encoding)
            known_face_names.append(name)
        return known_face_encodings,known_face_names
    #input: a frame
    #return: a frame with face_bounding box && relative name
    def getFaceName(self,frame):
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
         # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]
        # Only process every other frame of video to save time
        if self.process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            if len(face_locations) == 0:
                pass
            else:
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = "Unknown"
                    # Or instead, use the known face with the smallest distance to the new face
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    # print(face_distances)
                    best_match_index = np.argmin(face_distances)
                    if face_distances[best_match_index] < 0.4 and matches[best_match_index]:
                        name = self.known_face_names[best_match_index]

                    face_names.append(name)
                    if name is not 'Unknown':
                        # Face recognized, Do something to open the door:
                        print('Hello, ' + name + '. Welcome home!')
                        pass
                    else:
                        print('Sorry, you are not welcomed. Please contact the host.')
                        # print(name)
                        pass

        self.process_this_frame = not self.process_this_frame
        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        return frame


if __name__ == "__main__":
    
