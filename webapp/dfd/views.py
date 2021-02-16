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
model = load_model('/home/itssanat/Downloads/deepfake-detection-model.h5')
input_shape = (128, 128, 3)
detector = dlib.get_frontal_face_detector()

def predict(request):
    print('inside predict function')
    print(request.session['file_name'])
    cap = cv2.VideoCapture(request.session['file_name'])
    frameRate = cap.get(5)
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
                data = img_to_array(cv2.resize(crop_img, (128, 128))).flatten() / 255.0
                data = data.reshape(-1, 128, 128, 3)
                print(model.predict_classes(data))


def index(request):
    if request.method == 'GET':
        form = VideoForm()
        if 'file_name' in request.session:
            del request.session['file_name']
        if 'faces_cropped_images' in request.session:
            del request.session['faces_cropped_images']
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
            predict(request)

        return render(request , 'dfd/index.html' , {'form': form})
             
