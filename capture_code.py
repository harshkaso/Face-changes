# import the necessary packages
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import os

# construct the argument parser and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-c", "--cascade", required=True,
#   help = "path to where the face cascade resides")
# ap.add_argument("-o", "--output", required=True,
#   help="path to output directory")
# args = vars(ap.parse_args())
def capData(companyname, foldername):
    # foldername = 'Jeet_Patel'
    print(companyname, foldername)
    dirName = f'Clients/{companyname}/dataset/{foldername}'
    print(dirName)
    if not os.path.exists(dirName):
        os.makedirs(dirName)
        # print("Directory " , dirName ,  " Created ")

    CASCADE = "haarcascade.xml"
    OUTPUT = dirName

    # Set time interval between each frame captures [in seconds]
    INTERVAL = 1.5 
    NIMAGES = 20
    ########################################################
    # load OpenCV's Haar cascade for face detection from disk
    detector = cv2.CascadeClassifier(CASCADE)
    # initialize the video stream, allow the camera sensor to warm up,
    # and initialize the total number of example faces written to disk
    # thus far
    print("[INFO] starting video stream...")
    # vs = VideoStream(src=0).start()
    vs = VideoStream(usePiCamera=True).start()
    time.sleep(2.0)
    total = 0

    start_time = time.time()

    # loop over the frames from the video stream
    while True:
        # grab the frame from the threaded video stream, clone it, (just
        # in case we want to write it to disk), and then resize the frame
        # so we can apply face detection faster
        frame = vs.read()
        orig = frame.copy()
        frame = imutils.resize(frame, width=400)
        # detect faces in the grayscale frame
        rects = detector.detectMultiScale(
            cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), scaleFactor=1.1, 
            minNeighbors=5, minSize=(30, 30))
        # loop over the face detections and draw them on the frame
        for (x, y, w, h) in rects:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # show the output frame
            cv2.imshow("Frame", frame)
            cv2.waitKey(1)       
        # if the `k` key was pressed, write the *original* frame to disk
        # so we can later process it and use it for face recognition
        elapsed_time = time.time() - start_time

        if elapsed_time >= INTERVAL:
            p = os.path.sep.join([OUTPUT, "{}.png".format(str(total).zfill(5))])
            cv2.imwrite(p, orig)
            total += 1
            print("[INFO] Total frame captured: ", total)
            start_time = time.time()

        # if the `q` key was pressed, break from the loop
        if total == NIMAGES:
            break

    # print the total faces saved and do a bit of cleanup
    print("[INFO] {} face images stored".format(total))
    print("[INFO] cleaning up...")
    cv2.destroyAllWindows()
    vs.stop()
    return True