from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room, disconnect, emit
import requests
import config
import pydash
import xml.etree.ElementTree as ET
from google.cloud import translate
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'socketapp'
app.config['PORT'] = 8000
socketio = SocketIO(app)

cached_id = {}

# translate_client = translate.Client(key=config.google_translation)

language_map = {
    'english': 'en',
    'spanish': 'es'
}

@socketio.on('test')
def test_socket(mesg):
    emit('test_back', {'data': 'test run'})


@socketio.on('join')
def join(message):
    mentee = message['mentee']
    mentor = message['mentor']
    room = mentee + mentor
    join_room(room)

    # history = requests.post(config.base_url + '/message',
    #                         json={'mentor': mentor, 'mentee': mentee})
    # mentor_obj = requests.get(config.base_url + '/user' + mentor).json()
    # mentee_obj = requests.get(config.base_url + '/user' + mentee).json()
    # cached_id[mentee] = mentee_obj
    # cached_id[mentor] = mentor_obj
    # emit('joined', {'data': history.json()})
    emit('joined', {'data': []})
    


@socketio.on('leave')
def leave(message):
    mentor = message['mentor']
    mentee = message['mentee']
    room = mentee + mentor
    leave_room(room)
    emit('left', {'data': 'leaving room'})


@socketio.on('send_msg')
def send_room_message(message):
    print(message)
    global cached_id
    _id = message['_id']
    data = message['data']
    language = message['lang']
    mentor = message['mentor']
    mentee = message['mentee']
    room = mentee + mentor
    mentee_lang = pydash.get(language_map, pydash.get(cached_id, mentee + '.language', 'english').lower(), 'es')
    mentor_lang = pydash.get(language_map, pydash.get(cached_id, mentor + '.language', 'spanish').lower(), 'en')
    requests.post(config.base_url + '/message', json={'mentor': mentor, 'mentee': mentee,
                                        'sent_by': _id, 'message': data })
    print(mentee_lang, mentor_lang)
    if _id == mentor:

        if mentee_lang != mentor_lang:
            # translation = requests.get('https://api.microsofttranslator.com/V2/Http.svc/Translate', 
            #                       headers={'Ocp-Apim-Subscription-Key': config.translation_key}, 
            #                       params={ 'text': data, 'from': mentor_lang, 'to': mentee_lang } ).text
            # data = ET.fromstring(translation).text
            translation = requests.post('https://translation.googleapis.com/language/translate/v2', 
                                  params={ 'key': config.google_translation, 'target': mentee_lang, 'q': data } ).json()
            print(translation)
            data = pydash.get(translation, 'data.translations.0.translatedText', data)

        sentiment = requests.post('https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment',
                                  headers={'Ocp-Apim-Subscription-Key': config.sentiment_key}, 
                                  json={'documents': [{'id': 1, 'text': data, 'language': language}]}).json()

        moderation = requests.post('https://westus.api.cognitive.microsoft.com/contentmoderator/moderate/v1.0/ProcessText/Screen/', 
                                headers={'Ocp-Apim-Subscription-Key': config.moderation_key, 'Content-Type': 'text/plain' }, 
                                params={ 'language': 'eng' }, data=data ).json()
        


        score = pydash.get(sentiment, 'documents.0.score', 0.5)
        prof_terms = pydash.get(moderation, 'Terms')

        print(score, prof_terms)    
                
       
        if language == 'en' and score < 0.4 or prof_terms is not None:
            emit('msg_sent', { '_id': mentee, 'data': 'we have not sent your message, we detected some negative intensions'}, room=room, broadcast=True)
        else:
            emit('msg_sent', {'_id': _id, 'data': data }, room=room)
    else:

        if mentee_lang != mentor_lang:
            # translation = requests.get('https://api.microsofttranslator.com/V2/Http.svc/Translate', 
            #                         headers={'Ocp-Apim-Subscription-Key': config.translation_key}, 
            #                         params={ 'text': data, 'from': mentee_lang, 'to': mentor_lang } ).text
            # data = ET.fromstring(translation).text

            translation = requests.post('https://translation.googleapis.com/language/translate/v2', 
                                  params={ 'key': config.google_translation, 'target': mentor_lang, 'q': data } ).json()
            data = pydash.get(translation, 'data.translations.0.translatedText', data)

        emit('msg_sent', { 'data': data, '_id': _id }, room=room)


@socketio.on('disconnect')
def disconnect():
    emit('disconneted',
         {'data': 'disconnected'})
    disconnect()


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, use_reloader=True)
