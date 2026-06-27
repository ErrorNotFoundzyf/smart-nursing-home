# -*- coding: utf-8 -*-
'''
文字转换为声音
声音转换为文字

注：网络需要能访问Google
'''

import speech_recognition as sr
from gtts import gTTS

# text to speech
def text_to_speech(audio_string, file_name = 'voices/audio.mp3'):
    tts = gTTS(text = audio_string, lang = 'zh-tw')# en-us or  zh-cn
    tts.save(file_name)

# speech to text
def speech_to_text():
    print('begin to record audio')
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Say something!')
        audio = r.listen(source)
    print('finish recording')
    # Speech recognition using Google Speech Recognition
    data = ''
    try:
        # Uses the default API key
        data = r.recognize_google(audio)
        print('You said: %s' %(data))
    except sr.UnknownValueError:
        print('Google Speech Recognition cannot understand audio.')
    except sr.RequestError as e:
        print('Cannot request results from Google. {0}'.format(e))

    return data

if __name__ == '__main__':
    audio_string = '采集完毕'
    file_name = 'end_capturing.mp3'
    text_to_speech(audio_string, file_name)
    
    