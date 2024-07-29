# Hand-Tracking-Volume-Control
Python computer vision hand tracking. Created using a Google mediapipe hand-tracking task which reads frames passed by OpenCV.

https://github.com/user-attachments/assets/379333dd-400b-4e00-9b64-612f8b347a21


Requirements:
- `opencv-python` (Setup here: https://docs.opencv.org/4.x/da/df6/tutorial_py_table_of_contents_setup.html)
- `mediapipe` (Download hand-landmarker task here and make it available in your directory: https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/index#:~:text=Learn%20more.-,Model%20name,-Input%20shape)
- `numpy`
- `matplotlib`

"tracking.py" is a barebones example of how to process video frames from openCV into a mediapipe hand-tracking task. Some things to note:
- The current implementation mirrors the frames, since this program was executed using a front-facing camera, which mirrors by default. For rear-facing cameras, `text_x = int((1 - min(x_coordinates)) * width)` can be changed to `text_x = int((min(x_coordinates)) * width)` to write the hand labels starting from the right instead of the left. You will also need to remove `text_image = cv.flip(text_image, 1)`, which flips the hand labels once they are drawn.
- This implementation does not retrieve the actual timestamp of the edited frame, but instead layers the openCV frame with the drawn hand landmarks. The program expects that your computer is powerful enough. If it is not, there will be some noticeable delay with the landmarks compared to the displayed frame.
    - A good place to start to change this would be reading the landmark timestamp from the result output for the tracking instead of manually getting the current frame from openCV.
- The implementation uses a global `RESULT` variable to access the result outside of the callback function. This is not a great implementation. `volume_control_tracking` has a much more structured implementation.

Some things are customizable. In the code, you can change:
- The colors of the tracking. In `draw_landmarks_on_image`, there is commented code which allows you to set custom colors. It is just an example; you can fine tune each hand landmark and find references online. To use it, uncomment the code and change both functions accordingly.
- The minimum hand tracking detection confidence (`min_hand_detection_confidence`) and minimum hand presence confidence (`min_hand_presence_confidence`) are important. They range from 0.1 to 1, and increasing towards 1 gives you more accurate tracking at the cost of frames not being read if the task does not see your hands. Decreasing towards 0.1 gives you a smoother tracking at the expense of some accuracy.
- The default print output prints out all of the landmarks, for each frame. An example of this is shown in the VSCode terminal in the video. You could edit the output to give you certain landmarks, among other things. To see the names of landmarks, check out the labels [here](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/index#:~:text=Learn%20more.-,Model%20name,-Input%20shape). There is also more information on the hand tracking task.

### Volume Control [WIP]
This program (`volume_control_tracking.py`) is an example of how to control volume with fingers. By retrieving and then calculating the distance between the index and thumb, we can use this distance to increase or decrease the volume given how far apart the fingers are. Some things to note:
- The currently read fingers are read within the main function (`thumb_tip` and `index_tip`). You can easily change which hand landmarks you would like to read by changing which landmark values are accessed. Currently, 4 and 8 are accessed, which map to the thumb and index tip, respectively. The image below shows the landmark mappings.
- The implementation works by incrementally increasing the volume when the fingers are far apart, not changing it when the fingers are a medium/resting distance apart, and decreasing when the fingers are close together.
- ![image](https://github.com/user-attachments/assets/9ccc9f1c-707b-41a0-93b6-c6a0b19ecda0)
