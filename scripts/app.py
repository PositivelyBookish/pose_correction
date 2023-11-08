from flask import Flask, request
from flask_cors import CORS, cross_origin
import time

import cv2
import mediapipe as mp
import csv 
import os

app = Flask(__name__)
CORS(app, support_credentials=True)

def imagePoints():

    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    pose = mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5)

    # create capture object
    cap = cv2.imread('S2.jpg')
    temp_file = open('temp.csv', 'w', newline='')
    writer = csv.writer(temp_file)
    # writer.writerow(['x', 'y', 'z', 'visibility'])

    # while cap.isOpened():
    #     # read cap from capture object
    # _, cap = cap.read()

    try:
        # convert the cap to RGB format
        RGB = cv2.cvtColor(cap, cv2.COLOR_BGR2RGB)

        # process the RGB cap to get the result
        results = pose.process(RGB)

        print(results.pose_landmarks)
        # draw detected skeleton on the cap
        mp_drawing.draw_landmarks(
            cap, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # show the final output
        cv2.imshow('Output', cap)

        for landmark in results.pose_landmarks.landmark:
            writer.writerow([landmark.x, landmark.y, landmark.z, landmark.visibility])

        # close the temporary CSV file
        
    except :
        print("Error")
    # if cv2.waitKey(1) == ord('q'):
    #     break
        
    temp_file.close()
    os.replace('temp.csv', 'landmarks.csv')
    # cap.release()
    # cap.release()
    cv2.destroyAllWindows()

def main():

    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    # Open a video capture object
    cap = cv2.VideoCapture(0)

    # Check if the webcam is opened correctly
    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    # Set up mediapipe drawing styles
    drawing_styles = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

    # Read stored landmarks from CSV
    with open('landmarks.csv', mode='r') as file:
        csv_reader = csv.reader(file)
        stored_landmarks = [list(map(float, row)) for row in csv_reader]

    # Initialize a list to store the Euclidean distance errors
    euclidean_distances = []

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()

            # If the frame is not read correctly or the video capture is not successful, break
            if not ret:
                break

            # Convert the BGR image to RGB before processing
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            # Make detection
            results = pose.process(image)

            # Draw the pose landmarks on the frame
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.pose_landmarks:
                # Compare the detected landmarks with stored landmarks
                detected_landmarks = [(landmark.x, landmark.y, landmark.z) for landmark in results.pose_landmarks.landmark]
                for i, (stored, detected) in enumerate(zip(stored_landmarks, detected_landmarks)):
                    # Perform your comparison here
                    # Example comparison (Euclidean distance)
                    euclidean_distance = ((stored[0] - detected[0]) ** 2 + (stored[1] - detected[1]) ** 2 + (stored[2] - detected[2]) ** 2) ** 0.5
                    euclidean_distances.append(euclidean_distance)

                    # Draw the point on the image
                    cv2.circle(image, (int(detected[0] * image.shape[1]), int(detected[1] * image.shape[0])), 5, (0, 0, 255), -1)
                    cv2.putText(image, f'{i}: {euclidean_distance:.2f}', (int(detected[0] * image.shape[1]) + 10, int(detected[1] * image.shape[0])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    drawing_styles,
                    mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                )

            # Show the frame
            cv2.imshow("Pose Detection", image)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    # Release the VideoCapture object and close the window
    cap.release()
    cv2.destroyAllWindows()

    # Print Euclidean distances at the end
    print("Euclidean distances:")
    for i, distance in enumerate(euclidean_distances):
        print(f'Point {i}: {distance}')


# Define a route for handling POST requests
@app.route('/post_example', methods=['POST','GET'])
@cross_origin(supports_credentials=True)
def post_example():
    if request.method == 'GET':
        # Access data sent with the POST request
        
        # Assuming 'data' contains a URL, you can extract it
        # url = data  # You may want to perform additional validation or parsing

        imagePoints()

        time.sleep(10)

        main()

        return ""
    else:
        return 'This route only accepts POST requests.'

if __name__ == '__main__':
    app.run()