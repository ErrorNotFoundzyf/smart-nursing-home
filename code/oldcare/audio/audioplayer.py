'''
audio player
'''

# import library
from subprocess import call

# global variables
os_name = 'linux'

# play audio
def play_audio(audio_name):
    try:
        if os_name == 'linux':
            call('mpg321 ' + audio_name, shell=True) # use mpg321
        
        elif os_name == 'windows':
            from playsound import playsound
            playsound(audio_name) # pip install playsound
        
        else:
            print('Opearating System name is misspelled')
    except KeyboardInterrupt as e:
        print(e)
    finally:
        pass

if __name__ == '__main__':
    play_audio('voices/bibi.mp3')
    
    
    