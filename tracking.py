import numpy as np
import cv2 as cv
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from mediapipe.framework.formats import landmark_pb2
from mediapipe.python.solutions import drawing_utils, drawing_styles, hands

# Hand Label Text Parameters
MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)  # vibrant green


def draw_landmarks_on_image(rgb_image, detection_result):
    """
    Draws hand landmarks on an RGB image.

    Args:
        rgb_image (numpy.ndarray): The RGB image on which to draw the landmarks.
        detection_result (mediapipe.python.solutions.hands.HandLandmarkList): The detection result containing hand landmarks.

    Returns:
        numpy.ndarray: The annotated image with hand landmarks and handedness information.

    """
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

        # # Custom landmark style
        # custom_landmark_style = drawing_utils.DrawingSpec(
        #     color=(0, 255, 0), thickness=2, circle_radius=2  # Green color
        # )

        # # Custom connection style
        # custom_connection_style = drawing_utils.DrawingSpec(
        #     color=(255, 0, 0), thickness=2  # Red color
        # )

        solutions.drawing_utils.draw_landmarks(
            annotated_image,
            hand_landmarks_proto,
            solutions.hands.HAND_CONNECTIONS,
            solutions.drawing_styles.get_default_hand_landmarks_style(),  # Replace these for custom colors
            solutions.drawing_styles.get_default_hand_connections_style(),  # Replace these for custom colors
        )

        # Get the top left corner of the detected hand's bounding box.
        height, width, _ = annotated_image.shape
        x_coordinates = [landmark.x for landmark in hand_landmarks]
        y_coordinates = [landmark.y for landmark in hand_landmarks]
        text_x = int((1 - min(x_coordinates)) * width)
        text_y = int(min(y_coordinates) * height) - MARGIN

        # Draw handedness (left or right hand) on the image.
        text_image = np.zeros_like(annotated_image)
        cv.putText(
            text_image,
            f"{handedness[0].category_name}",
            (text_x, text_y),
            cv.FONT_HERSHEY_DUPLEX,
            FONT_SIZE,
            HANDEDNESS_TEXT_COLOR,
            FONT_THICKNESS,
            cv.LINE_AA,
        )

        # Flip the text layer for front-facing cameras.
        text_image = cv.flip(text_image, 1)

        # Annotate frame
        annotated_image = cv.addWeighted(annotated_image, 1.0, text_image, 1.0, 0.0)
    return annotated_image


# MediaPipe Hand Landmark Task Initialization and Parameters
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Global variable for result, so that we can access it outside the callback function. UNSAFE
RESULT = None


# Result function which is necessary for live-streaming camera frames.
def print_result(
    result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int
):

    print("hand landmarker result: {}".format(result))
    global RESULT
    RESULT = result  # UNSAFE


# Hand Landmarker Options and Initialization
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="hand_landmarker.task"),
    running_mode=VisionRunningMode.LIVE_STREAM,
    num_hands=2,
    result_callback=print_result,
    min_hand_detection_confidence=0.1,
    min_hand_presence_confidence=0.1,
)
with HandLandmarker.create_from_options(options) as landmarker:

    # Camera Initialization
    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        cv.flip(frame, 1)

        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        # Our operations on the frame come here
        # Display the resulting frame
        frame_timestamp_ms = int(cap.get(cv.CAP_PROP_POS_MSEC))
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(frame))
        # Call to detect hand landmarks
        detection_result = landmarker.detect_async(mp_image, frame_timestamp_ms)
        if RESULT is not None:
            annotated_image = draw_landmarks_on_image(mp_image.numpy_view(), RESULT)
            cv.flip(annotated_image, 1, annotated_image)
            cv.imshow("Hand Tracking", annotated_image)
            RESULT = None  # Reset the RESULT variable (UNSAFE)
            if cv.waitKey(5) == ord("q"):
                break
    cap.release()
    cv.destroyAllWindows()
