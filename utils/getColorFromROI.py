import numpy as np
import cv2
import functions

if functions.isRaspberry():
    from picamera.array import PiRGBArray
    from picamera import PiCamera
    import time
    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 90
    camera.brightness = 60
    camera.rotation = 180
    rawCapture = PiRGBArray(camera, size=camera.resolution)
    # allow the camera to warmup
    time.sleep(2)
else:
    camera = cv2.VideoCapture(0)


x_start, y_start, x_end, y_end = 0, 0, 0, 0
cropping = False
getROI = False
refPt = []
lower = np.array([])
upper = np.array([])


def click_and_crop(event, x, y, flags, param):
    '''
    MouseCallback function
    '''
    # grab references to the global variables
    global x_start, y_start, x_end, y_end, cropping, getROI

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
        x_start, y_start, x_end, y_end = x, y, x, y
        cropping = True

    elif event == cv2.EVENT_MOUSEMOVE:
        if cropping == True:
            x_end, y_end = x, y

    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates and indicate that
        # the cropping operation is finished
        x_end, y_end = x, y
        cropping = False
        getROI = True


def getColorFromCrop():
    lower = np.array([])
    upper = np.array([])
    global getROI
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", click_and_crop)
        
    while True:

        if functions.isRaspberry():
            # grab the current frame
            camera.capture(rawCapture, use_video_port=True, format='bgr')
            frame = rawCapture.array
        else:
            ret, frame = camera.read()
        
        if not getROI:

            if not cropping:
                cv2.imshow("image", frame)

            elif cropping:
                cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)
                cv2.imshow("image", frame)

        else:
            cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)
            cv2.imshow("image", frame)


            # if there are two reference points, then crop the region of interest
            # from teh image and display it
            refPt = [(x_start, y_start), (x_end, y_end)]

            roi = frame[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]

            hsvRoi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            #print('min H = {}, min S = {}, min V = {}; max H = {}, max S = {}, max V = {}'.format(hsvRoi[:,:,0].min(), hsvRoi[:,:,1].min(), hsvRoi[:,:,2].min(), hsvRoi[:,:,0].max(), hsvRoi[:,:,1].max(), hsvRoi[:,:,2].max()))
         
            lower = np.array([hsvRoi[:,:,0].min(), hsvRoi[:,:,1].min(), hsvRoi[:,:,2].min()])
            upper = np.array([hsvRoi[:,:,0].max(), hsvRoi[:,:,1].max(), hsvRoi[:,:,2].max()])
            if functions.isRaspberry():
                cv2.destroyAllWindows()
            else:
                camera.release()
            return lower, upper

        
        if functions.isRaspberry():
            # clear the stream in preparation for the next frame
            rawCapture.truncate(0)

        #cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            if functions.isRaspberry():
                cv2.destroyAllWindows()
            else:
                camera.release()
            break


if __name__ == '__main__':
    lower, upper = getColorFromCrop()
    print(lower, upper)

'''
        if done:

            blurred = cv2.GaussianBlur(frame, (11, 11), 0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

            # construct a mask for the color from dictionary`1, then perform
            # a series of dilations and erosions to remove any small
            # blobs left in the mask
            kernel = np.ones((9,9),np.uint8)
            mask = cv2.inRange(hsv, lower, upper)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                    
            # find contours in the mask and initialize the current
            # (x, y) center of the ball
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)[-2]
            center = None
            
            # only proceed if at least one contour was found
            if len(cnts) > 0:
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
                # centroid
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            
                # only proceed if the radius meets a minimum size. Correct this value for your obect's size
                if radius > 0.5:
                    # draw the circle and centroid on the frame,
                    # then update the list of tracked points
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 0), 2)
                    cv2.putText(frame, 'center: {}, {}'.format(int(x), int(y)), (int(x-radius),int(y-radius)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

                 
            # show the frame to our screen
            cv2.imshow("image", frame)

        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)
        
        key = cv2.waitKey(1) & 0xFF
        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            cv2.destroyAllWindows()
            break
        elif key == ord("r"):
            getROI = False
'''
