from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Todo


def todo_list(request):
    """Display all todos with optional filtering."""
    filter_status = request.GET.get('filter', 'all')
    
    if filter_status == 'completed':
        todos = Todo.objects.filter(completed=True)
    elif filter_status == 'active':
        todos = Todo.objects.filter(completed=False)
    else:
        todos = Todo.objects.all()
    
    context = {
        'todos': todos,
        'filter_status': filter_status,
        'total_count': Todo.objects.count(),
        'completed_count': Todo.objects.filter(completed=True).count(),
        'active_count': Todo.objects.filter(completed=False).count(),
    }
    return render(request, 'app/todo_list.html', context)


def todo_create(request):
    """Create a new todo."""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        
        if title:  # Basic validation
            Todo.objects.create(title=title, description=description)
            return redirect('todo_list')
    
    return render(request, 'app/todo_form.html', {'action': 'Create'})


def todo_update(request, pk):
    """Update an existing todo."""
    todo = get_object_or_404(Todo, pk=pk)
    
    if request.method == 'POST':
        todo.title = request.POST.get('title', todo.title)
        todo.description = request.POST.get('description', todo.description)
        todo.completed = request.POST.get('completed') == 'on'
        todo.save()
        return redirect('todo_list')
    
    context = {
        'todo': todo,
        'action': 'Update'
    }
    return render(request, 'app/todo_form.html', context)


def todo_delete(request, pk):
    """Delete a todo."""
    todo = get_object_or_404(Todo, pk=pk)
    
    if request.method == 'POST':
        todo.delete()
        return redirect('todo_list')
    
    return render(request, 'app/todo_confirm_delete.html', {'todo': todo})


def toggle_complete(request, pk):
    """Toggle the completion status of a todo."""
    todo = get_object_or_404(Todo, pk=pk)
    todo.completed = not todo.completed
    todo.save()
    return redirect('todo_list')
