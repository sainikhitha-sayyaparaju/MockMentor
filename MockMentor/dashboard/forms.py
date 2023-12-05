from socket import fromshare
from django import forms
from django.forms import widgets
from . models import Interview
from django.contrib.auth.forms import UserCreationForm


class InterviewForm(forms.ModelForm):
    EXPERTISE_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )


    # expertise = forms.ChoiceField(
    #     choices=EXPERTISE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    expertise = forms.ChoiceField(
        choices=EXPERTISE_CHOICES, widget=forms.RadioSelect())

    class Meta:
        model = Interview
        fields = ['topic', 'subtopic', 'expertise', 'number']



