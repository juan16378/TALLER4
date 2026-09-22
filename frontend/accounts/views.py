"""
Vistas de autenticacion: registro, login y logout.

Por ahora usa unicamente el sistema de usuarios integrado de Django
(sesion clasica username/password). La sincronizacion con el backend
FastAPI (JWT para los endpoints de reconocimiento facial) se anade mas
adelante, cuando se integre el cliente HTTP hacia esa API.
"""
from django.contrib import messages
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cuenta creada correctamente. Ahora inicia sesion.")
            return redirect("accounts:login")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            django_login(request, user)
            return redirect("/")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    django_logout(request)
    messages.info(request, "Sesion cerrada correctamente.")
    return redirect("accounts:login")
