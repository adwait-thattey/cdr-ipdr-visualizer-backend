from tensorflow.keras.models import load_model
import glob
import numpy as np
# import random
import librosa

saved_classifier_model = load_model(
    '/run/media/coderdude/Adwait/Projects/sih2020/repos/cdr-ipdr-visualizer-backend/backend/detect_person/detect_person_model/')
# saved_classifier_model._make_predict_function()
reverse_label_dict = {0: "jackson", 1: 'nicolas', 2: 'theo'}
max_length = 80


def pre_process(filename):
    wave, sr = librosa.load(filename, mono=True)
    mfcc = librosa.feature.mfcc(wave, sr)
    to_ret = None
    try:
        mfcc = np.pad(mfcc, ((0, 0), (0, max_length -
                                      len(mfcc[0]))), mode='constant', constant_values=0)
        to_ret = np.array(mfcc)
    except:
        print('wrong file')
        to_ret = 'error'
    return to_ret


def get_name(filepath):
    file = filepath
    x = pre_process(file)
    name = ''
    if type(x) != str:
        y = saved_classifier_model.predict_classes(np.array([x]))[0]
        probability = saved_classifier_model.predict(np.array([x]))[0][y]
        # print(probability[y])
        name = reverse_label_dict[y]
    else:
        name = 'something is wrong !!'
        probability = -1
    context = {'person_name': name, 'confidence': probability}

    return context


if __name__ == "__main__":
    get_name(
        '/run/media/coderdude/Adwait/Projects/sih2020/repos/cdr-ipdr-visualizer-backend/backend/media/0_jackson_19.wav')
