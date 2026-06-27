# -*- coding: utf-8 -*-
'''
任务21：摄像头画面实时显示

启动 Flask 视频流服务，浏览器访问 http://0.0.0.0:5001/ 可看到实时画面。

用法：python3 tasks/task_21/startingcameraservice.py
      python3 tasks/task_21/startingcameraservice.py --location yard
'''

import os
import sys
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

from flask import Flask, render_template, Response, request
from oldcare.camera import VideoCamera

ap = argparse.ArgumentParser()
ap.add_argument("-l", "--location", default='room',
                choices=['room', 'yard', 'corridor', 'desk'])
args = vars(ap.parse_args())
location = args['location']

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'))

video_camera = None
global_frame = None

@app.route('/')
def index():
    return render_template(location + '_camera.html')

@app.route('/record_status', methods=['POST'])
def record_status():
    global video_camera
    if video_camera is None:
        video_camera = VideoCamera()
    status = request.form.get('status')
    save_path = request.form.get('save_video_path', 'recording.avi')
    if status == 'true':
        video_camera.start_record(save_path)
        return 'start record'
    else:
        video_camera.stop_record()
        return 'stop record'

def video_stream():
    global video_camera, global_frame
    if video_camera is None:
        video_camera = VideoCamera()
    while True:
        frame = video_camera.get_frame()
        if frame is not None:
            global_frame = frame
        if global_frame is not None:
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')

@app.route('/video_viewer')
def video_viewer():
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print('[INFO] 摄像头服务启动: http://0.0.0.0:5001/')
    print('[INFO] 摄像头位置: %s' % location)
    app.run(host='0.0.0.0', threaded=True, port=5001)
