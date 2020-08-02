import speech_recognition as sr

r = sr.Recognizer()


def speech2text(filepath):
    file = filepath
    harvard = sr.AudioFile(file)

    with harvard as source:
        audio = r.record(source, duration=10)
    try:
        transcript = r.recognize_google(audio)
    except sr.UnknownValueError:
        transcript = 'erorUnd1'
        # print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        transcript = 'erorRes2'
        # print("Could not request results from Google Speech Recognition service; {0}".format(e))
    except:
        transcript = 'erorUnk3'

    trigger_words = ['terrorist', 'bomb', 'assasainate', 'robbery', 'plan', 'terror', 'gun', 'within', 'kill',
                     'murder', ]
    found_trigger_words = list(set(transcript.split()).intersection(set(trigger_words)))
    twb = bool(len(found_trigger_words))

    context = {'transcript': transcript.lower(), 'trigger_word_exists': twb, 'trigger_words': found_trigger_words}

    return context
