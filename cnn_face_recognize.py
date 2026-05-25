import cv2, os, time, csv
import numpy as np
import face_recognition
import tkinter as tk
import winsound
import requests
import threading

# ================= TELEGRAM =================

BOT_TOKEN = "8697242441:AAFltHk6ibXQocYiJwpd2VlzMiaKgMa9wUI"
CHAT_ID = "5759887919"

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

def send_telegram_photo(image_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(image_path, "rb") as photo:
        requests.post(url, data={"chat_id": CHAT_ID}, files={"photo": photo})

# 🔥 ASYNC ALERT (NO LAG)
def send_alert_async(name, img_path):
    def task():
        send_telegram_alert(f"🚨 Suspect detected: {name}")
        send_telegram_photo(img_path)
    threading.Thread(target=task, daemon=True).start()

# ================= SETTINGS =================

SUSPECT_FOLDER = "suspects"
CAPTURE_FOLDER = "captures"
LOG_FILE = "logs.csv"
THRESHOLD = 0.40   # slightly stricter

os.makedirs(CAPTURE_FOLDER, exist_ok=True)

# ================= LOAD SUSPECTS =================

print("[INFO] Loading faces...")

suspect_encodings = []
suspect_names = []

for file in os.listdir(SUSPECT_FOLDER):
    path = os.path.join(SUSPECT_FOLDER, file)

    try:
        img = face_recognition.load_image_file(path)
        enc = face_recognition.face_encodings(img)

        if enc:
            suspect_encodings.append(enc[0])
            suspect_names.append(file.split(".")[0])
            print("Loaded:", file)
        else:
            print("No face in:", file)

    except Exception as e:
        print("Error:", file, e)

print("Total suspects:", len(suspect_encodings))

# ================= CSV =================

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        csv.writer(f).writerow(["Time", "Name"])

# ================= UI =================

root = tk.Tk()
root.title("AI Suspect Tracker")
root.geometry("420x260")
root.configure(bg="#0d1117")
root.resizable(False, False)

alarm_enabled = tk.BooleanVar(value=True)

tk.Label(root, text="🛡 AI Suspect Tracker",
         font=("Segoe UI", 16, "bold"),
         fg="#00ffaa", bg="#0d1117").pack(pady=10)

panel = tk.Frame(root, bg="#161b22")
panel.pack(fill="both", expand=True, padx=10, pady=5)

sus_lbl = tk.Label(panel, text="Suspects : 0",
                  font=("Segoe UI", 12),
                  fg="red", bg="#161b22")
sus_lbl.pack(pady=5)

unk_lbl = tk.Label(panel, text="Unknown : 0",
                  font=("Segoe UI", 12),
                  fg="orange", bg="#161b22")
unk_lbl.pack(pady=5)

fps_lbl = tk.Label(panel, text="FPS : 0",
                  font=("Segoe UI", 11),
                  fg="#58a6ff", bg="#161b22")
fps_lbl.pack(pady=5)

tk.Checkbutton(panel, text=" Alarm",
               variable=alarm_enabled,
               fg="#00ffaa", bg="#161b22",
               selectcolor="#161b22").pack(pady=10)

tk.Button(panel, text="Exit",
          bg="#ff4444", fg="white",
          command=root.destroy).pack()

# ================= CAMERA =================

cap = cv2.VideoCapture(0)

suspects = 0
unknowns = 0
last_beep = 0
prev = time.time()

# 🔥 smart alert delay
last_alert_time = {}
ALERT_DELAY = 10

frame_count = 0

while True:

    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    # 🔥 Resize for speed
    small = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
    rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

    # 🔥 Faster detection
    locs = face_recognition.face_locations(rgb, model="hog")
    encs = face_recognition.face_encodings(rgb, locs)

    for (t, r, b, l), face in zip(locs, encs):

        # scale back
        t *= 2; r *= 2; b *= 2; l *= 2

        name = "Unknown"
        color = (0, 255, 255)

        if suspect_encodings:
            d = face_recognition.face_distance(suspect_encodings, face)
            best = np.argmin(d)

            if d[best] < THRESHOLD:
                name = suspect_names[best]
                color = (0, 0, 255)
                suspects += 1

                if alarm_enabled.get() and time.time() - last_beep > 2:
                    winsound.Beep(1500, 300)
                    last_beep = time.time()

                ts = time.strftime("%Y%m%d_%H%M%S")
                img_path = f"{CAPTURE_FOLDER}/{name}_{ts}.jpg"
                cv2.imwrite(img_path, frame)

                with open(LOG_FILE, "a", newline="") as f:
                    csv.writer(f).writerow([ts, name])

                # 🔥 SMART TELEGRAM ALERT
                now_time = time.time()
                if name not in last_alert_time or now_time - last_alert_time[name] > ALERT_DELAY:
                    send_alert_async(name, img_path)
                    last_alert_time[name] = now_time

            else:
                unknowns += 1

        cv2.rectangle(frame, (l, t), (r, b), color, 2)
        cv2.putText(frame, name, (l, t - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    now = time.time()
    fps = int(1 / (now - prev))
    prev = now

    sus_lbl.config(text=f"Suspects : {suspects}")
    unk_lbl.config(text=f"Unknown : {unknowns}")
    fps_lbl.config(text=f"FPS : {fps}")

    root.update()
    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
root.destroy()