from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room, disconnect, emit
import requests, config, pydash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'socketapp'
app.config['PORT'] = 8000
socketio = SocketIO(app)

messages = {}

@socketio.on('test')
def test_socket(mesg):
    emit('test_back', { 'data': 'test run' })

@socketio.on('join')
def join(message):
    mentee = message['mentee']
    mentor = message['mentor']
    room = mentee + mentor
    join_room(room)
    emit('joined', {'data': ['chat history']})


@socketio.on('leave')
def leave(message):
    room = message['room']
    leave_room(room)
    del messages[room]
    emit('left', {'data': 'leaving room'})


@socketio.on('send_msg')
def send_room_message(message):
    _id = message['_id']
    data = message['data']
    mentor = message['mentor']
    mentee = message['mentee']
    if isMentor:
        headers = {'Ocp-Apim-Subscription-Key': config.mskey}
        resp = requests.post('https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/languages', headers=headers, json={ 'documents': [{'id': 1, 'text': data }]})
        json_resp = resp.json()
        print(json_resp)
        language = pydash.get(json_resp, '0.detectedLanguages.name', 'en')[:2].lower()
        print(language)
        sentiment = requests.post('https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment', headers=headers, json={ 'documents': [{'id': 1, 'text': data, 'language': language }]})
        score = pydash.get(sentiment.json(), 'documents.0.score')
        if int(score) < 70:
            emit('msg_sent', {   } )
        print(sentiment.json())
    

    emit('msg_sent', {'data':data, '_id': _id }, room=room)


@socketio.on('disconnect')
def disconnect():
    emit('disconneted',
         {'data': 'disconnected' })
    disconnect()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, use_reloader=True)
