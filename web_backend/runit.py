from app import app,socketio

socketio.run(app,host='127.0.0.1',debug=False,port=5000)



