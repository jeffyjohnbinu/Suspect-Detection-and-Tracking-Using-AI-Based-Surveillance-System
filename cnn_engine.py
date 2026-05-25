import cv2
import face_recognition
import os

SUSPECT_FOLDER = "suspects"

known_encodings = []
known_names = []

print("[INFO] Loading suspects...")

for file in os.listdir(SUSPECT_FOLDER):
    if file.endswith(".jpg") or file.endswith(".png"):
        img = face_recognition.load_image_file(f"{SUSPECT_FOLDER}/{file}")
        enc = face_recognition.face_encodings(img)

        if enc:
            known_encodings.append(enc[0])
            known_names.append(file)
            print("Loaded:", file)

print("Total suspects:", len(known_names))

camera = cv2.VideoCapture(0)

def generate_frames():

    while True:
        success, frame = camera.read()
        if not success:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        locations = face_recognition.face_locations(rgb, model="cnn")
        encodings = face_recognition.face_encodings(rgb, locations)

        for (top,right,bottom,left), face in zip(locations, encodings):

            matches = face_recognition.compare_faces(known_encodings, face, tolerance=0.45)
            name = "Unknown"

            if True in matches:
                name = known_names[matches.index(True)]

            cv2.rectangle(frame,(left,top),(right,bottom),(0,255,0),2)
            cv2.putText(frame,name,(left,top-10),
                        cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
