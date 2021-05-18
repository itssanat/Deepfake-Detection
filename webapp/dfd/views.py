from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from .forms import VideoForm
import shutil
import time
import os

# ---------------------------------
import tensorflow as tf
import cv2
import os
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import dlib

# --------------------------------
model = load_model('/home/itssanat/Downloads/deepfake-detection-model-v3(lr_.0001).h5')
input_shape = (128, 128, 3)
detector = dlib.get_frontal_face_detector()

def predict(request):
    print('inside predict function')
    print(request.session['file_name'])
    cap = cv2.VideoCapture(request.session['file_name'])
    frameRate = cap.get(5)
    real = 0
    fake = 0
    count = 0
    pred_result = {}  # to store predition result 
    while cap.isOpened():
        frameId = cap.get(1)
        ret, frame = cap.read()
        if ret != True:
            break
        if frameId % ((int(frameRate)+1)*1) == 0:
            face_rects, scores, idx = detector.run(frame, 0)
            for i, d in enumerate(face_rects):
                x1 = d.left()
                y1 = d.top()
                x2 = d.right()
                y2 = d.bottom()
                crop_img = frame[y1:y2, x1:x2]

                img_name = 'img_'+str(int(time.time()))+'_'+str(count)+'.png'
                img_path = os.path.join(settings.BASE_DIR, 'temp_images', img_name)
                cv2.imwrite( img_path , cv2.resize(crop_img, (128, 128)))

                data = img_to_array(cv2.resize(crop_img, (128, 128))).flatten() / 255.0
                data = data.reshape(-1, 128, 128, 3)
                pred = np.sum(model.predict_classes(data)).item()
                print(pred)
                if pred == 1:
                    real = real + 1
                else :
                    fake = fake + 1
                pred_result.update({img_name : pred})
                count = count + 1
    print(real, fake, count)
    request.session['pred_result']=pred_result
    return pred_result , True if real > fake else False


def index(request):
    if request.method == 'GET':
        form = VideoForm()
        if 'file_name' in request.session:
            del request.session['file_name']
        if 'pred_result' in request.session:
            del request.session['pred_result']
        return render(request , 'dfd/index.html' , {'form': form})
        
    else :
        form = VideoForm(request.POST, request.FILES)
        # print(form.is_valid())
        if form.is_valid():
            video_file = form.cleaned_data['video']
            video_file_ext = video_file.name.split('.')[-1]
            # print(video_file_ext)
            # print('form is valid')
            video_content_type = video_file.content_type.split('/')[0]

            saved_video_file = 'uploaded_file_'+str(int(time.time()))+"."+video_file_ext
            print(saved_video_file)
            print(settings.BASE_DIR)
            with open(os.path.join(settings.BASE_DIR, 'temp_videos', saved_video_file), 'wb') as vFile:
                shutil.copyfileobj(video_file, vFile)
            request.session['file_name'] = os.path.join(settings.BASE_DIR, 'temp_videos', saved_video_file)
            print(request.session['file_name'])
            pred_result , isReal = predict(request)
            # pred_result = {'img_1613472231_0.png': 1, 'img_1613472235_1.png': 0, 'img_1613472236_2.png': 0, 
            #             'img_1613472236_3.png': 0, 'img_1613472237_4.png': 0, 'img_1613472238_5.png': 0, 
            #             'img_1613472238_6.png': 0, 'img_1613472239_7.png': 0, 'img_1613472239_8.png': 0, 
            #             'img_1613472240_9.png': 1}
            # isReal = True
            print(isReal)
            # print(pred_result)
            return render(request, 'dfd/index.html', {'form': form, 'pred_result': pred_result, 
                            'isReal': isReal, 'videoName': video_file.name, 'saved_video_file': saved_video_file})

        return render(request , 'dfd/index.html' , {'form': form, })
             
