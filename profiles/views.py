from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from .models import Profile, ProfileImage
from .forms import ProfileForm

@login_required
def profile_setup(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            p = form.save(commit=False)
            p.is_complete = True
            p.save()

            # save photo to media_db if uploaded
            photo = request.FILES.get('photo')
            if photo:
                data         = photo.read()
                content_type = photo.content_type
                obj, _       = ProfileImage.objects.using('media_db').get_or_create(user_id=request.user.id)
                obj.data         = data
                obj.content_type = content_type
                obj.save(using='media_db')

            messages.success(request, 'Profile saved!')
            return redirect('swipe')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'profiles/setup.html', {'form': form})

@login_required
def my_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'profiles/my_profile.html', {'profile': profile})

def serve_photo(request, user_id):
    try:
        img = ProfileImage.objects.using('media_db').get(user_id=user_id)
        return HttpResponse(bytes(img.data), content_type=img.content_type)
    except ProfileImage.DoesNotExist:
        raise Http404
