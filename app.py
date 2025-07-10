from flask import Flask, request,send_from_directory,render_template,Response
from ultralytics import YOLO
import os
import time
import uuid
import math 
import cv2

import numpy as np
import base64
from collections import Counter
import caption
from flask import Flask, jsonify
from PIL import Image


app = Flask(__name__)
RESULT_FOLDER= r'static/results/'
UPLOAD_FOLDER = 'static/uploads/'
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
model = YOLO(r'models/best.pt')
classNames = model.names

object_counts = {}
caption_frame = ""
should_stop = False




cap = cv2.VideoCapture(0)

@app.route('/')
def index():
    return render_template(r'yolo_BHH.html')


def gen_source_frames():
    
    
    try:
        while not should_stop:
            success, img = cap.read()
            if not success:
                print("Failed to read frame from webcam")
                break
            ret, buffer = cv2.imencode('.jpg', img)
            if not ret:
                continue
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        cap.release()
        print("Released webcam for source_feed")


def gen_frames():
    global object_counts
    global caption_frame
    global should_stop
    
    
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    unique_id = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"
    result_realtime_name = f"result_video_{unique_id}.mp4"
    result_realtime_path = os.path.join(app.config['RESULT_FOLDER'], result_realtime_name)
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(result_realtime_path, fourcc, fps, (frame_width, frame_height))
    
    
    try:
        while not should_stop:
            success, img = cap.read()
            if not success:
                print("Failed to read frame from webcam")
                break
            
            img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            caption_frame = caption.load_model_and_predict_2(img_pil)
            
            object_names = []
            processed_frame = img.copy()
            results = model(img, stream=True)
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    cv2.rectangle(processed_frame, (x1, y1), (x2, y2), (255, 0, 255), 3)
                    conf = math.ceil((box.conf[0] * 100)) / 100
                    cls = int(box.cls[0])
                    class_name = classNames[cls]
                    label = f'{class_name} {conf}'
                    t_size = cv2.getTextSize(label, 0, fontScale=1, thickness=2)[0]
                    c2 = x1 + t_size[0], y1 - t_size[1] - 3
                    cv2.rectangle(processed_frame, (x1, y1), c2, [255, 0, 255], -1, cv2.LINE_AA)
                    cv2.putText(processed_frame, label, (x1, y1-2), 0, 1, [255, 255, 255], thickness=1, lineType=cv2.LINE_AA)
                    
                    object_names.append(class_name)
            out.write(processed_frame)
            object_counts = dict(Counter(object_names))     
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            if not ret:
                continue
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        cap.release()
        out.release()
        should_stop = False
        print("Released webcam for video_feed")

@app.route('/source_feed')
def source_feed():
    return Response(gen_source_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/get_object_count_realtime')
def get_objects_count():
    global object_counts
    return jsonify(object_counts)
@app.route('/describe_topic')
def get_caption_frame():
    global caption_frame
    return jsonify(caption_frame)

@app.route('/stop', methods=['POST'])
def stop():
    global should_stop
    should_stop = True
    return {"message": "Stopping webcam and saving video"}



@app.route('/detect_image', methods= ['POST'])
def detect_image():
    if 'file' not in request.files:
        return {"error": "No file provided"},400
    file = request.files['file']
    if file.filename=='':
        return {"error": "No file selected"},400
    unique_id = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"
    temp_img_name = f"temp_image_{unique_id}.jpg"


    temp_img_path = os.path.join(app.config['UPLOAD_FOLDER'],temp_img_name)
    file.save(temp_img_path)
    
    results =  model(temp_img_path)
    
    
    result_img_name = f"result_img_{unique_id}.jpg"
    result_img_path = os.path.join(app.config['RESULT_FOLDER'],result_img_name)
    results[0].save(result_img_path)
    
    boxes = results[0].boxes
    class_ids = boxes.cls.tolist()
    names = model.names
    object_name = [names[int(i)]for i in class_ids]
    object_counts = dict(Counter(object_name))
    
    image_caption = caption.load_model_and_predict(temp_img_path)
    
    return {"result_image":f"/static/results/{result_img_name}","list_count": object_counts,"image_caption": image_caption},200


@app.route('/detect_video', methods=['POST'])
def detect_video():
    if 'file' not in request.files:
        return {"error": "No file provided"}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {"error": "No file selected"}, 400
    

    unique_id = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"
    temp_video_name = f"temp_video_{unique_id}.mp4"
    result_video_name = f"result_video_{unique_id}.mp4"
    

    temp_video_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_video_name)
    file.save(temp_video_path)
    

    cap  = cv2.VideoCapture(temp_video_path)
    if not cap.isOpened():
        return {"error": "Cannot open video"}, 500
    

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    

    result_video_path = os.path.join(app.config['RESULT_FOLDER'], result_video_name)
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(result_video_path, fourcc, fps, (frame_width, frame_height))
    while True:
        success, img = cap.read()
        if not success:
            break
        results = model(img)
        annotated_frame = results[0].plot() 
        out.write(annotated_frame)
    
    cap.release()
    out.release()
    
    return {"result_video":f"/static/results/{result_video_name}"}, 200

@app.route('/static/results/<filename>')
def serve_result(filename):
    return send_from_directory(app.config['RESULT_FOLDER'], filename,mimetype='video/mp4')


if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        cap.release()
        print("Webcam released on program exit")