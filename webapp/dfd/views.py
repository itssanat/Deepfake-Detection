from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from .forms import VideoForm
import shutil
import time
import os

def index(request):
    if request.method == 'POST':
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
        
    else:
        form = VideoForm()
    return render(request , 'dfd/index.html' , {'form': form})
