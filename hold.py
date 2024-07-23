# # Image Capture
# image = cv.imread("image.png")
# cv.imshow("Image", image)
# cv.waitKey(0)
# cv.destroyAllWindows()


import cv2 as cv

# Live Camera Video Capture
cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    # Our operations on the frame come here
    # Display the resulting frame
    cv.flip(frame, 1, frame)
    cv.imshow("frame", frame)
    if cv.waitKey(1) == ord("q"):
        break

cap.release()
cv.destroyAllWindows()
