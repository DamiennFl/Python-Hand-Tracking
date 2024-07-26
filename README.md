# Hand-Tracking-Volume-Control
#### Python computer vision hand tracking. Created using a Google mediapipe hand-tracking task which reads frames passed by OpenCV.

Requirements:
- `opencv-python`
- `mediapipe`
- `numpy`

This is a currently a barebones example of how to process video frames from openCV into a mediapipe hand-tracking task. Some things to note:
- The current implementation mirrors the frames, since this program was executed using a front-facing camera, which mirrors by default. For rear-facing cameras, `text_x = int((1 - min(x_coordinates)) * width)` can be changed to `text_x = int((min(x_coordinates)) * width)` to write the hand labels starting from the right instead of the left. You will also need to remove `text_image = cv.flip(text_image, 1)`, which flips the hand labels once they are drawn.
- This implementation does not retrieve the actual timestamp of the edited frame, but instead layers the openCV frame with the drawn hand landmarks. The program expects that your computer is powerful enough. If it is not, there will be some noticeable delay with the landmarks compared to the displayed frame.
    - A good place to start to change this would be reading the landmark timestamp from the result output for the tracking instead of manually getting the current frame from openCV.
- The implementation uses a global `RESULT` variable to access the result outside of the callback function. This is unsafe (but I didn't want to spend time restructuring).

Some things are customizable. In this code, you can change:
- The colors of the tracking. In `draw_landmarks_on_image`, there is commented code which allows you to set custom colors. It is just an example; you can fine tune each hand landmark and find references online. To use it, uncomment the code and change both functions accordingly.
- The minimum hand tracking detection confidence (`min_hand_detection_confidence`) and minimum hand presence confidence (`min_hand_presence_confidence`) are important. They range from 0.1 to 1, and increasing towards 1 gives you more accurate tracking at the cost of frames not being read if the task does not see your hands. Decreasing towards 0.1 gives you a smoother tracking at the expense of some accuracy.
- The default print output prints out all of the landmarks, for each frame. You could edit the output to give you certain landmarks, among other things. To see the names of landmarks, check out the labels [here](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/index#:~:text=Learn%20more.-,Model%20name,-Input%20shape). There is also more information on the hand tracking task.
