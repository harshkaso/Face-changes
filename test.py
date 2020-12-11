from imutils.video import VideoStream
import imutils
import cv2
import time
vs = VideoStream(usePiCamera=True).start()
time.sleep(0.1)
while True:
    frame = vs.read()
    frame = imutils.resize(frame, width=500) 
    cv2.imshow('Test',frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('k'):
        break
cv2.destroyAllWindows()
vs.stop()
     

 