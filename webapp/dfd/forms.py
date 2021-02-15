from django import forms

class VideoForm(forms.Form):
    video = forms.FileField(label="Select Video", required=True,widget=forms.FileInput(attrs={"accept": "video/*"}))