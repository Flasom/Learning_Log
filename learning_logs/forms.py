from django import forms
from .models import Topic, Entry, History

class Topic_Form(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['text']
        labels = {'text': ''}

class Entry_Form(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['text']
        labels = {'text': ''}
        widgets = {'text': forms.Textarea(attrs={'cols':80})}

class History_Form(forms.ModelForm):
    class Meta:
        model = History
        fields  = ['title','text']
        labels = {'title': '', 'text': ''}