import cv2 as cv
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import vision
from tracking import HandLandmarkerResult


class HandLandmarkerApp:
    def __init__(self):
        self.result = None
        self.frame_timestamp_ms = None
        self.setup_hand_landmarker()

    def setup_hand_landmarker(self):
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path="hand_landmarker.task"),
            running_mode=VisionRunningMode.LIVE_STREAM,
            num_hands=2,
            result_callback=self.print_result,
        )

        self.landmarker = HandLandmarker.create_from_options(options)

    def print_result(
        self, result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int
    ):
        self.result = result
        self.frame_timestamp_ms = timestamp_ms
        print("hand landmarker result: {}".format(result))

    def run(self):
        cap = cv.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open camera")
            exit()

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break

            frame = cv.flip(frame, 1)
            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB, data=np.asarray(frame)
            )
            self.landmarker.detect_async(mp_image, int(cap.get(cv.CAP_PROP_POS_MSEC)))

            if self.result is not None and self.frame_timestamp_ms is not None:
                annotated_image = self.draw_landmarks_on_image(
                    mp_image.numpy_view(), self.result
                )
                annotated_image_bgr = cv.cvtColor(annotated_image, cv.COLOR_RGB2BGR)
                cv.imshow("Hand Tracking", annotated_image_bgr)
                self.result = None

            if cv.waitKey(5) == ord("q"):
                break

        cap.release()
        cv.destroyAllWindows()

    def draw_landmarks_on_image(self, rgb_image, detection_result):
        annotated_image = rgb_image.copy()
        for hand_landmarks, handedness in zip(
            detection_result.hand_landmarks, detection_result.handedness
        ):
            mp.solutions.drawing_utils.draw_landmarks(
                annotated_image,
                hand_landmarks,
                mp.solutions.hands.HAND_CONNECTIONS,
                mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                mp.solutions.drawing_styles.get_default_hand_connections_style(),
            )

            height, width, _ = annotated_image.shape
            x_coordinates = [landmark.x for landmark in hand_landmarks.landmark]
            y_coordinates = [landmark.y for landmark in hand_landmarks.landmark]
            text_x = int((1 - min(x_coordinates)) * width)
            text_y = int(min(y_coordinates) * height) - 10

            text_image = np.zeros_like(annotated_image)
            cv.putText(
                text_image,
                f"{handedness[0].category_name}",
                (text_x, text_y),
                cv.FONT_HERSHEY_DUPLEX,
                1,
                (88, 205, 54),
                1,
                cv.LINE_AA,
            )

            text_image = cv.flip(text_image, 1)
            annotated_image = cv.addWeighted(annotated_image, 1.0, text_image, 1.0, 0.0)

        return annotated_image


if __name__ == "__main__":
    app = HandLandmarkerApp()
    app.run()
