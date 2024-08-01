import cv2
import mediapipe as mp
import math
import numpy as np
import time
import os
import imageio

def process_video_cv(file_path):
    mpDraw = mp.solutions.drawing_utils
    mpPose = mp.solutions.pose
    pose = mpPose.Pose()
    cap = cv2.VideoCapture(file_path)

    if not cap.isOpened():
        raise Exception(f"Failed to open video file {file_path}")

    pTime = 0
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    project_root = os.path.dirname(os.path.abspath(__file__))  # Root directory of your project
    temp_dir = os.path.join(project_root, 'tmp')  # Temp directory inside the app folder
    os.makedirs(temp_dir, exist_ok=True)  # Create temp directory if it doesn't exist
    output_file_path = os.path.join(temp_dir, 'output_video.mp4')
    writer = imageio.get_writer(output_file_path, fps=30, codec='libx264')
    print("Frame width:", frame_width)
    print("Frame height:", frame_height)

    sit_stand_results = False
    start_writing = False

    while cap.isOpened():
        success, img = cap.read()
        if not success:
            print("No more frames or error reading frame.")
            break  # Exits the loop if no frames are left to read or if there's an error

        img = resize_image(img)  # Assuming resize_image function is defined elsewhere
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)

        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            key_points = {}
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
                if id == 28:
                    key_points["right Ankle"]= lm
                elif id == 26:
                    key_points["right Knee"]= lm
                elif id == 24:
                    key_points["right Hip"]= lm
                elif id == 27:
                    key_points["left Ankle"]= lm                
                elif id == 25:
                    key_points["left Knee"]= lm
                elif id == 23:
                    key_points["left Hip"]= lm

            if sit_stand_test(key_points):
                sit_stand_results = True

            text = "Test: Passed" if sit_stand_results else "Test: Failed"
            cv2.putText(img, text, (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
        start_writing = True

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        print(start_writing)

        if start_writing:
            try:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                writer.append_data(img_rgb)
            except Exception as e:
                print(f"Error writing frame: {e}")

    cap.release()
    writer.close()
    cv2.destroyAllWindows()
    print(f"Video written to {output_file_path}")
    return output_file_path, sit_stand_results, start_writing

def create_test_video(output_path):
    writer = imageio.get_writer(output_path, fps=30, codec='libx264')
    for _ in range(100):  # Write 100 frames
        frame = np.zeros((480, 640, 3), dtype=np.uint8)  # Black frame
        writer.append_data(frame)
    writer.close()

 
def getAngle(landmark1,landmark2,landmark3):
    x1,y1 = landmark1
    x2,y2 = landmark2 
    x3,y3 = landmark3
    
    angle = math.degrees(math.atan2(y3-y2,x3-x2)-math.atan2(y1-y2,x1-x2))
    if angle< 0:
        angle = -angle
    if angle > 180:
        angle = 360-angle

    return angle


def sit_stand_test(key_points):
    right_ankle = (key_points["right Ankle"].x, key_points["right Ankle"].y)
    right_knee = (key_points["right Knee"].x, key_points["right Knee"].y)
    right_hip= (key_points["right Hip"].x,key_points["right Hip"].y)
    left_ankle = (key_points["left Ankle"].x,key_points["left Ankle"].y)
    left_knee = (key_points["left Knee"].x, key_points["left Knee"].y)
    left_hip = (key_points["left Hip"].x, key_points["left Hip"].y)
    right_leg_angle = getAngle(right_ankle,right_knee,right_hip)
    left_leg_angle = getAngle(left_ankle,left_knee,left_hip)
    # print(right_leg_angle,left_leg_angle)
    if right_leg_angle>=120 or left_leg_angle>=120:
        return True
    else:
        return False
    

def resize_image(img, target_width=1280, target_height=720):
    original_height, original_width = img.shape[:2]
    ratio = min(target_width/original_width, target_height/original_height)
    
    # Compute new dimensions
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)

    # Resize the original image
    resized_image = cv2.resize(img, (new_width, new_height))

    # Create a black canvas of the target size
    canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)

    # Compute position to center the image on the canvas
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2

    # Place the resized image onto the center of the canvas
    canvas[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized_image

    return canvas

def file_exists(bucket, file_name):
    # List all blobs in the bucket
    blobs = bucket.list_blobs()

    # Check if the file_name exists in the list of blobs
    for blob in blobs:
        if blob.name == file_name:
            return True
    return False

