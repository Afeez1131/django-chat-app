from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

from account.forms import RegistrationForm
from account.models import Profile


def login_user(request):
    next = request.GET.get('next')
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            if next:
                return HttpResponseRedirect(next)
            return HttpResponse('login success')
        else:
            messages.warning(request, 'This User is not Active')
    else:
        messages.warning(request, 'Not a Valid User')

    return render(request, 'account/login.html', {})


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('account:login'))


def register_user(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, state="Nigeria",
                                   age=24)
            return HttpResponseRedirect(reverse('account:login'))
    return render(request, 'account/signup.html', {'form': form})

