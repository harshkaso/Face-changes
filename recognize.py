# USAGE
# python recognize_video.py --detector face_detection_model \
#   --embedding-model openface_nn4.small2.v1.t7 \
#   --recognizer output/recognizer.pickle \
#   --le output/le.pickle

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import pickle
import time
import cv2
import os

# Setup for writing records in a file
import csv
import datetime
from os.path import dirname, abspath


class face:

    def __init__(self, company, vs):
        self.company = company
        self.detected = False
        self.date = None
        self.vs = vs
    
    def recognize(self):
        try:

            DETECTOR = "face_detection_model"
            EMBEDDING_MODEL = "openface_nn4.small2.v1.t7"
            RECOGNIZER = f"Clients/{self.company}/recognizer.pickle"
            LE = f"Clients/{self.company}/le.pickle"
            CONFIDENCE = 0.55
            PROBABILITY = 0.35

            print("[INFO] loading face detector...")
            protoPath = os.path.sep.join([DETECTOR, "deploy.prototxt"])
            modelPath = os.path.sep.join([DETECTOR, "res10_300x300_ssd_iter_140000.caffemodel"])
            detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath)

            # load our serialized face embedding model from disk
            print("[INFO] loading face recognizer...")
            embedder = cv2.dnn.readNetFromTorch(EMBEDDING_MODEL)

            # load the actual face recognition model along with the label encoder
            recognizer = pickle.loads(open(RECOGNIZER, "rb").read())
            le = pickle.loads(open(LE, "rb").read())

            # initialize the video stream, then allow the camera sensor to warm up
            print("[INFO] starting video stream...")
            # vs = VideoStream(src=-1).start()
            #######################################
            # self.vs = VideoStream(usePiCamera=True).start()
        
            # time.sleep(2.0)
            #######################################
            # start the FPS throughput estimator
            fps = FPS().start()
            counter = 0
            # loop over frames from the video file stream
            while not self.detected:
                # grab the frame from the threaded video stream
                frame = self.vs.read()
                lastframe = frame
                # resize the frame to have a width of 600 pixels (while
                # maintaining the aspect ratio), and then grab the image
                # dimensions
            
                frame = imutils.resize(frame, width=600)
            
                (h, w) = frame.shape[:2]
            

                # construct a blob from the image
                imageBlob = cv2.dnn.blobFromImage(
                    cv2.resize(frame, (300, 300)), 1.0, (300, 300),
                    (104.0, 177.0, 123.0), swapRB=False, crop=False)

                # apply OpenCV's deep learning-based face detector to localize
                # faces in the input image
                detector.setInput(imageBlob)
                detections = detector.forward()

                # loop over the detections
                for i in range(0, detections.shape[2]):
                    # extract the confidence (i.e., probability) associated with
                    # the prediction
                    confidence = detections[0, 0, i, 2]

                    # filter out weak detections
                    if confidence > CONFIDENCE:
                        # compute the (x, y)-coordinates of the bounding box for
                        # the face
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (startX, startY, endX, endY) = box.astype("int")

                        # extract the face ROI
                        face = frame[startY:endY, startX:endX]
                        (fH, fW) = face.shape[:2]

                        # ensure the face width and height are sufficiently large
                        if fW < 20 or fH < 20:
                            continue

                        # construct a blob for the face ROI, then pass the blob
                        # through our face embedding model to obtain the 128-d
                        # quantification of the face
                        faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,
                            (96, 96), (0, 0, 0), swapRB=True, crop=False)
                        embedder.setInput(faceBlob)
                        vec = embedder.forward()

                        # perform classification to recognize the face
                        preds = recognizer.predict_proba(vec)[0]
                        j = np.argmax(preds)
                        proba = preds[j]
                        name = le.classes_[j]
                        print("[INFO] Face recognized by model as : ", name)



                        # draw the bounding box of the face along with the
                        # associated probability
                        text = "{}: {:.2f}%".format(name, proba * 100)
                        y = startY - 10 if startY - 10 > 10 else startY + 10
                        cv2.rectangle(frame, (startX, startY), (endX, endY),
                            (0, 0, 255), 2)
                        cv2.putText(frame, text, (startX, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

                        # if mode == "entry" and proba > 0.7:
                        #   self.detected = True
                            # self.message = self.entry(self, name)
                        print("Probability is ", proba)
                        if proba > PROBABILITY:
                            self.detected = True
                            self.date = datetime.datetime.now()
                        
                            # self.message = self.exit(self, name)
                    
                # update the FPS counter
                fps.update()

                # show the output frame
                #cv2.imshow("Frame", frame)
                #cv2.waitKey(1)
            
                if self.detected == True: 
                    self.detected = False
                    break
                elif counter > 3:
                    name = "unknown"
                    self.date = None
                
                    break
                # key = cv2.waitKey(1) & 0xFF
                counter+=1
                # if the `q` key was pressed, break from the loop
                # if key == ord("q"):
                #   break

            # stop the timer and display FPS information
            fps.stop()
            print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
            print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
            #vs.stream.release()
            cv2.destroyAllWindows()
            self.vs.stop()
            # lastframe = imutils.resize(lastframe, width=400)
            cv2.imwrite(dirname(abspath(__file__)) + "/icons/display.png",lastframe)
            return name, self.date
        except Exception as e:
            return "unknown", None