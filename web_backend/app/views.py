from flask_login import login_required
from flask import render_template, send_from_directory, Response
from app import app
import os, cv2
import eventlet
from eventlet import tpool

_VIDEO_FILES = {
    'room':     '/root/Desktop/old_care_system/images/tests/videos/room_01.mp4',
    'yard':     '/root/Desktop/old_care_system/images/tests/videos/yard_01.mp4',
    'corridor': '/root/Desktop/old_care_system/images/tests/videos/corridor_01.avi',
    'desk':     '/root/Desktop/old_care_system/images/tests/videos/desk_01.mp4',
}

_frame_caches = {}

def _start_readers():
    for loc, path in _VIDEO_FILES.items():
        def _reader(location=loc, fpath=path):
            while True:
                cap = cv2.VideoCapture(fpath)
                while True:
                    ret, frame = tpool.execute(cap.read)
                    if not ret:
                        break
                    _, buf = cv2.imencode('.jpg', frame)
                    _frame_caches[location] = buf.tobytes()
                    eventlet.sleep(0.04)
                cap.release()
        eventlet.spawn(_reader)

_start_readers()



@app.route('/css/<path:path>')
def send_css(path):
    #return send_from_directory(os.path.join(app.root_path, 'static/css'), path)
    return send_from_directory(app.static_folder+'/css', path)

@app.route('/js/<path:path>')
def send_js(path):
    #return send_from_directory(os.path.join(app.root_path, 'static/js'), path)
    return send_from_directory(app.static_folder + '/js', path)

@app.route('/font-awesome/<path:path>')
def send_font_awesome(path):
    #return send_from_directory(os.path.join(app.root_path, 'static/font-awesome'), path)
    return send_from_directory(app.static_folder + '/font-awesome', path)

@app.route('/bootstrap-dist/<path:path>')
def send_bootstrap_dist(path):
   # return send_from_directory(os.path.join(app.root_path, 'static/bootstrap-dist'), path)
   return send_from_directory(app.static_folder + '/bootstrap-dist', path)

@app.route('/img/<path:path>')
def send_img(path):
    #return send_from_directory(os.path.join(app.root_path, 'static/img'), path)
    return send_from_directory(app.static_folder + '/img', path)



@app.route('/index.html')
@app.route('/index')
@login_required
def index():
    return render_template("index.html")


@app.route('/camera')
@login_required
def camera_monitor():
    return render_template('camera.html')


def _gen_frames(location):
    while True:
        frame = _frame_caches.get(location)
        if frame:
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
        eventlet.sleep(0.04)

@app.route('/camera/stream/<location>')
@login_required
def camera_stream(location):
    if location not in _VIDEO_FILES:
        return '', 404
    return Response(_gen_frames(location), mimetype='multipart/x-mixed-replace; boundary=frame')




# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('error_404.html'), 404
