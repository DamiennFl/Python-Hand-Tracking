import numpy as np
import cv2 as cv
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from mediapipe.python.solutions import drawing_utils, drawing_styles, hands

# Hand Label Text Parameters
MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)  # vibrant green


class HandLandmarkDrawer:
    def __init__(self):
        pass

    def draw_landmarks_on_image(self, rgb_image, detection_result):
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


class HandLandmarkDetector:
    def __init__(self, model_path="hand_landmarker.task"):
        self.RESULT = None
        self.options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
            running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
            num_hands=2,
            result_callback=self.print_result,
            min_hand_detection_confidence=0.3,
            min_hand_presence_confidence=0.3,
        )
        self.landmarker = mp.tasks.vision.HandLandmarker.create_from_options(
            self.options
        )

    def print_result(
        self,
        result: mp.tasks.vision.HandLandmarkerResult,
        output_image: mp.Image,
        timestamp_ms: int,
    ):
        # Check if there are any hand landmarks detected
        if result.hand_landmarks:
            # Access the first hand's landmarks
            hand_landmarks = result.hand_landmarks[0]
            # Check if landmark 1 exists
            if len(hand_landmarks) > 8:
                landmark1 = hand_landmarks[4]
                landmark2 = hand_landmarks[8]
                print(f"Landmark 4: x={landmark1.x}, y={landmark1.y}, z={landmark1.z}")
                print(f"Landmark 8: x={landmark2.x}, y={landmark2.y}, z={landmark2.z}")
            else:
                print("Landmarks not found.")
        else:
            print("No hand landmarks detected.")
        self.RESULT = result

    def detect(self, frame, frame_timestamp_ms):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(frame))
        self.landmarker.detect_async(mp_image, frame_timestamp_ms)
        return self.RESULT


def main():
    drawer = HandLandmarkDrawer()
    detector = HandLandmarkDetector()

    # Camera Initialization
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
        frame_timestamp_ms = int(cap.get(cv.CAP_PROP_POS_MSEC))
        detection_result = detector.detect(frame, frame_timestamp_ms)
        if detection_result is not None:
            annotated_image = drawer.draw_landmarks_on_image(frame, detection_result)
            cv.flip(annotated_image, 1, annotated_image)
            cv.imshow("Hand Tracking", annotated_image)
            detector.RESULT = None
            if cv.waitKey(1) == ord("q"):
                break

    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
