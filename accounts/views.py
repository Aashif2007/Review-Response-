from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("account_dashboard")

    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def user_login(request):
    error = None

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request, user)
            return redirect("account_dashboard")

        error = "Invalid username or password."

    return render(request, "accounts/login.html", {"error": error})


def user_logout(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    has_business = hasattr(request.user, "business")
    business = getattr(request.user, "business", None)
    return render(
        request,
        "accounts/dashboard.html",
        {"has_business": has_business, "business": business},
    )

