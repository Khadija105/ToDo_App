from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy
from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm, 
    UserPasswordChangeForm
)
from apps.tasks.models import Task


def register(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('task_list')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f'Registration successful! Welcome {user.username}. Please log in.'
            )
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('task_list')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('task_list')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@require_http_methods(['POST'])
def user_logout(request):
    """Handle user logout with POST-only for security."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required(login_url='login')
def profile(request):
    """Display user profile with statistics."""
    user = request.user
    total_tasks = Task.objects.filter(user=user).count()
    completed_tasks = Task.objects.filter(user=user, completed=True).count()
    pending_tasks = total_tasks - completed_tasks

    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
    }

    return render(request, 'accounts/profile.html', context)


@login_required(login_url='login')
def profile_edit(request):
    """Handle user profile updates."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/profile_edit.html', {'form': form})


class CustomPasswordChangeView(PasswordChangeView):
    """Custom password change view with messages and Bootstrap form."""
    form_class = UserPasswordChangeForm
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('password_change_done')

    def form_valid(self, form):
        messages.success(self.request, 'Password changed successfully!')
        return super().form_valid(form)


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    """Custom password change done view."""
    template_name = 'accounts/password_change_done.html'
