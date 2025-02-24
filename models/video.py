import cv2
from tensorflow.keras.models import load_model
import numpy as np
import os
import base64

class VideoCamera:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.modelPath = r"models/fer2013.h5"
        self.model = load_model(self.modelPath)
        self.faceCascadePath = r"models/haarcascade_frontalface_default.xml"
        self.face = cv2.CascadeClassifier(self.faceCascadePath)

    def __del__(self):
        self.camera.release()

    def predictEmotion(self, roi):
        label_dict = {0:'Angry',1:'Disgust',2:'Fear',3:'Happy',4:'Neutral',5:'Sad',6:'Surprise'}
        roi = np.array(roi)
        roi = cv2.resize(roi,(48,48))
        roi = np.expand_dims(roi,axis = 0)
        roi = roi.reshape(1,48,48,1)
        roi = roi/255.0
        result = self.model.predict(roi)
        result = list(result[0])
        return label_dict[result.index(max(result))]

    def get_frame(self):
        success, frame = self.camera.read()
        if not success:
            return None
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        face = self.face.detectMultiScale(gray, 1.1, 4)
        for (x,y,w,h) in face:
            roi = gray[y: y + h, x: x + w]
            pred = self.predictEmotion(roi)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0,255,0), 2)
            cv2.putText(frame, pred, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 5)
        ret, buffer = cv2.imencode('.jpg', frame)
        return buffer.tobytes()
    
    def process_file(self, file_path):
        # Load the image or video file
        if file_path.endswith('.jpg') or file_path.endswith('.png'):
            image = cv2.imread(file_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            face = self.face.detectMultiScale(gray, 1.1, 4)
            for (x,y,w,h) in face:
                roi = gray[y: y + h, x: x + w]
                pred = self.predictEmotion(roi)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0,255,0), 2)
                cv2.putText(image, pred, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 5)
            ret, buffer = cv2.imencode('.jpg', image)
            return base64.b64encode(buffer).decode('utf-8')
        elif file_path.endswith('.mp4') or file_path.endswith('.avi'):
            template_dir = 'templates'
            if not os.path.exists(template_dir):
                os.makedirs(template_dir)
            processed_video_path = os.path.join(template_dir, 'processed_video.mp4')
            cap = cv2.VideoCapture(file_path)
            frames = []
            while True:
                success, frame = cap.read()
                if not success:
                    break
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face = self.face.detectMultiScale(gray, 1.1, 4)
                for (x,y,w,h) in face:
                    roi = gray[y: y + h, x: x + w]
                    pred = self.predictEmotion(roi)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0,255,0), 2)
                    cv2.putText(frame, pred, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 5)
                frames.append(frame)
            cap.release()
            
            out = cv2.VideoWriter(processed_video_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (frames[0].shape[1], frames[0].shape[0]))
            for frame in frames:
                out.write(frame)
            out.release()
            return processed_video_path
        else:
            return None
