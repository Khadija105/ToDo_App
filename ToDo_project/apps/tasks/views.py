from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from .models import Task
from .forms import TaskForm


@login_required(login_url='login')
def task_list(request):
    """Display all tasks for the current user"""
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/task_list.html', {'tasks': tasks})


@login_required(login_url='login')
def task_detail(request, pk):
    """Display specific task detail - only if user owns it"""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    return render(request, 'tasks/task_detail.html', {'task': task})


@login_required(login_url='login')
def task_create(request):
    """Create new task and assign to current user"""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Create'})


@login_required(login_url='login')
def task_edit(request, pk):
    """Edit existing task - only if user owns it"""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            messages.success(request, f'Task "{task.title}" updated successfully!')
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form, 'task': task, 'action': 'Edit'})


@login_required(login_url='login')
def task_delete(request, pk):
    """Delete task - only if user owns it"""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted successfully!')
        return redirect('task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@login_required(login_url='login')
def task_complete(request, pk):
    """Mark task as complete/incomplete - only if user owns it"""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = not task.completed
    task.save()
    status = 'completed' if task.completed else 'incomplete'
    messages.success(request, f'Task marked as {status}!')
    return redirect('task_detail', pk=task.pk)
