import numpy as np
import cv2 as cv
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)  # vibrant green


def draw_landmarks_on_image(rgb_image, detection_result):
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness
    annotated_image = np.copy(rgb_image)

    # Loop through the detected hands to visualize.
    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        handedness = handedness_list[idx]

        # Draw the hand landmarks.
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend(
            [
                landmark_pb2.NormalizedLandmark(
                    x=landmark.x, y=landmark.y, z=landmark.z
                )
                for landmark in hand_landmarks
            ]
        )
        solutions.drawing_utils.draw_landmarks(
            annotated_image,
            hand_landmarks_proto,
            solutions.hands.HAND_CONNECTIONS,
            solutions.drawing_styles.get_default_hand_landmarks_style(),
            solutions.drawing_styles.get_default_hand_connections_style(),
        )

        # Get the top left corner of the detected hand's bounding box.
        height, width, _ = annotated_image.shape
        x_coordinates = [landmark.x for landmark in hand_landmarks]
        y_coordinates = [landmark.y for landmark in hand_landmarks]
        text_x = int(min(x_coordinates) * width)
        text_y = int(min(y_coordinates) * height) - MARGIN

        # Draw handedness (left or right hand) on the image.
        cv.putText(
            annotated_image,
            f"{handedness[0].category_name}",
            (text_x, text_y),
            cv.FONT_HERSHEY_DUPLEX,
            FONT_SIZE,
            HANDEDNESS_TEXT_COLOR,
            FONT_THICKNESS,
            cv.LINE_AA,
        )

    return annotated_image


BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode


# Create a hand landmarker instance with the live stream mode:
def print_result(
    result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int
):
    print("hand landmarker result: {}".format(result))


options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="hand_landmarker.task"),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result,
)
with HandLandmarker.create_from_options(options) as landmarker:
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
        frame_timestamp_ms = int(cap.get(cv.CAP_PROP_POS_MSEC))
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(frame)
        )
        detection_result = landmarker.detect_async(mp_image, frame_timestamp_ms)
        if detection_result is not None:
            annotated_image = draw_landmarks_on_image(
                mp_image.numpy_view(), detection_result
            )
            annotated_image_bgr = cv.cvtColor(annotated_image, cv.COLOR_RGB2BGR)
            cv.imshow("Hand Tracking", annotated_image_bgr)
            if cv.waitKey(1) == ord("q"):
                break

    cap.release()
    cv.destroyAllWindows()

# Convert BGR to RGB
# rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

# Optionally flip the frame if needed
# rgb_frame = cv.flip(rgb_frame, 1)

# Prepare the frame for MediaPipe
# frame_timestamp_ms = int(cap.get(cv.CAP_PROP_POS_MSEC))
# mp_image = mp.Image(
#     image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(frame)
# )

# Perform asynchronous detection
# landmarker.detect_async(mp_image, frame_timestamp_ms)
