from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404, JsonResponse
from .models import Profile, ProfileImage, ProfilePhoto, Prompt, UserPrompt, INTEREST_TAGS, PROMPT_QUESTIONS
from .forms import ProfileForm
import json


def _ensure_prompts():
    """Create predefined prompts if they don't exist."""
    for i, q in enumerate(PROMPT_QUESTIONS):
        Prompt.objects.get_or_create(question=q, defaults={'order': i})


@login_required
def profile_setup(request):
    _ensure_prompts()
    profile, _ = Profile.objects.get_or_create(user=request.user)
    prompts    = list(Prompt.objects.all())
    user_prompts = {up.prompt_id: up.answer for up in UserPrompt.objects.filter(user_id=request.user.id)}
    existing_photos = ProfilePhoto.objects.using('media_db').filter(user_id=request.user.id).order_by('order')

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            p = form.save(commit=False)

            # Interest tags from checkboxes
            p.interest_tags = request.POST.getlist('interest_tags')

            # Location coords from hidden inputs
            lat = request.POST.get('latitude', '').strip()
            lng = request.POST.get('longitude', '').strip()
            if lat and lng:
                try:
                    p.latitude  = float(lat)
                    p.longitude = float(lng)
                except ValueError:
                    pass

            p.is_complete = True
            p.save()

            # Save multiple photos
            photos = request.FILES.getlist('photos')
            current_count = ProfilePhoto.objects.using('media_db').filter(user_id=request.user.id).count()
            for i, photo in enumerate(photos):
                if current_count + i >= 6:  # max 6 photos
                    break
                obj = ProfilePhoto(
                    user_id      = request.user.id,
                    data         = photo.read(),
                    content_type = photo.content_type,
                    order        = current_count + i,
                )
                obj.save(using='media_db')

            # Save prompt answers
            for key, value in request.POST.items():
                if key.startswith('prompt_') and value.strip():
                    try:
                        prompt_id = int(key.split('_')[1])
                        prompt    = Prompt.objects.get(id=prompt_id)
                        UserPrompt.objects.update_or_create(
                            user_id=request.user.id, prompt=prompt,
                            defaults={'answer': value.strip()}
                        )
                    except (ValueError, Prompt.DoesNotExist):
                        pass

            messages.success(request, 'Profile saved!')
            return redirect('swipe')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profiles/setup.html', {
        'form':            form,
        'interest_tags':   INTEREST_TAGS,
        'selected_tags':   profile.interest_tags or [],
        'prompts':         prompts,
        'user_prompts':    user_prompts,
        'existing_photos': existing_photos,
        'max_photos':      6,
    })


@login_required
def delete_photo(request, photo_id):
    if request.method == 'POST':
        try:
            photo = ProfilePhoto.objects.using('media_db').get(id=photo_id, user_id=request.user.id)
            photo.delete(using='media_db')
            # Re-order remaining photos
            for i, p in enumerate(ProfilePhoto.objects.using('media_db').filter(user_id=request.user.id).order_by('order')):
                p.order = i
                p.save(using='media_db')
        except ProfilePhoto.DoesNotExist:
            pass
    return redirect('profile_setup')


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
