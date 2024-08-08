import numpy as np
import cv2 as cv
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from mediapipe.python.solutions import drawing_utils, drawing_styles, hands
from dll_control import AudioController

# Hand Label Text Parameters
MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)  # vibrant green
# Volume object from dll_control.py
volume = AudioController()


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
                    landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z)
                    for landmark in hand_landmarks
                ]
            )

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
        """
        Initializes the VolumeControlTracking object.

        Args:
            model_path (str, optional): The path to the hand landmarker model asset. Defaults to "hand_landmarker.task".
        """
        self.RESULT = None
        self.options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
            running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
            num_hands=2,
            result_callback=self.print_result,
            min_hand_detection_confidence=0.3,
            min_hand_presence_confidence=0.3,
        )
        self.landmarker = mp.tasks.vision.HandLandmarker.create_from_options(self.options)

    def print_result(
        self,
        result: mp.tasks.vision.HandLandmarkerResult,  # type: ignore
        output_image: mp.Image,
        timestamp_ms: int,
    ):
        """
        Prints the result of hand landmark detection.

        Args:
            result (mp.tasks.vision.HandLandmarkerResult): The result of hand landmark detection.
            output_image (mp.Image): The output image with hand landmarks drawn.
            timestamp_ms (int): The timestamp in milliseconds.

        Returns:
            None
        """
        self.RESULT = result

    def detect(self, frame, frame_timestamp_ms):
        """
        Detects hand landmarks in the given frame.

        Args:
            frame: The input frame to detect hand landmarks in.
            frame_timestamp_ms: The timestamp of the frame in milliseconds.

        Returns:
            The result of the detection process.
        """
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
            if len(detection_result.hand_landmarks) > 0:
                thumb_tip = detection_result.hand_landmarks[0][4]
                index_tip = detection_result.hand_landmarks[0][8]
                # Pythagorean
                distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
                current_volume = volume.get_volume()
                if distance <= 0.10:
                    # Multiplier for scaling dynamic volume change
                    smallMulti = (1 / distance) / 9
                    volume.set_volume(-0.01 * smallMulti)
                elif distance >= 0.15:
                    # Multiplier for scaling dynamic volume change
                    bigMulti = distance * 6
                    volume.set_volume(0.01 * bigMulti)
            cv.flip(annotated_image, 1, annotated_image)
            cv.imshow("Hand Tracking", annotated_image)
            detector.RESULT = None
            if cv.waitKey(1) == ord("q"):
                break

    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
