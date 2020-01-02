from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Bird, Photo
from .forms import FeedingForm
from django.http import HttpResponse
import uuid
import boto3


S3_BASE_URL = 'https://s3-us-east-1.amazonaws.com/'
BUCKET = 'shredward'

# Create your views here.


class BirdCreate(LoginRequiredMixin, CreateView):
    model = Bird
    fields = ['name', 'species', 'description', 'age']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class BirdUpdate(LoginRequiredMixin, UpdateView):
    model = Bird
    fields = ['species', 'description', 'age']

class BirdDelete(LoginRequiredMixin, DeleteView):
    model = Bird
    success_url = '/birds/'

@login_required
def add_feeding(request, bird_id):
    form = FeedingForm(request.POST)
    if form.is_valid():
        new_feeding = form.save(commit=False)
        new_feeding.bird_id = bird_id
        new_feeding.save()
    return redirect('detail', bird_id=bird_id)

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

@login_required
def birds_index(request):
    birds = Bird.objects.filter(user=request.user)
    return render(request, 'birds/index.html', {
        'birds': birds
    })
@login_required
def birds_detail(request, bird_id):
    bird = Bird.objects.get(id=bird_id)
    feeding_form = FeedingForm()
    return render(request, 'birds/detail.html', {
        'bird': bird, 
        'feeding_form': feeding_form
    })
@login_required
def add_photo(request, bird_id):
    S3_BASE_URL = 'https://s3.us-east-2.amazonaws.com/'
    BUCKET = 'shredward'
    photo_file = request.FILES.get('photo-file', None)
    if photo_file:
        s3 = boto3.client('s3')
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        try:
            s3.upload_fileobj(photo_file, BUCKET, key)
            url = f"{S3_BASE_URL}{BUCKET}/{key}"
            photo = Photo(url=url, bird_id=bird_id)
            photo.save()
        except:
            print('an error occured uploading file to S3')
    return redirect('detail', bird_id=bird_id)

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message }
    return render(request, 'registration/signup.html', context)