from django.test import TestCase, Client
from django.urls import reverse
from .models import Todo


class TodoModelTest(TestCase):
    """Test cases for the Todo model."""
    
    def setUp(self):
        """Set up test data."""
        self.todo = Todo.objects.create(
            title="Test Todo",
            description="Test description"
        )
    
    def test_todo_creation(self):
        """Test that a todo can be created successfully."""
        self.assertEqual(self.todo.title, "Test Todo")
        self.assertEqual(self.todo.description, "Test description")
        self.assertFalse(self.todo.completed)
    
    def test_todo_str_method(self):
        """Test the string representation of a todo."""
        self.assertEqual(str(self.todo), "Test Todo")
    
    def test_todo_default_completed_status(self):
        """Test that completed defaults to False."""
        new_todo = Todo.objects.create(title="Another Todo")
        self.assertFalse(new_todo.completed)
    
    def test_todo_timestamps(self):
        """Test that timestamps are set automatically."""
        self.assertIsNotNone(self.todo.created_at)
        self.assertIsNotNone(self.todo.updated_at)


class TodoViewsTest(TestCase):
    """Test cases for Todo views."""
    
    def setUp(self):
        """Set up test client and test data."""
        self.client = Client()
        self.todo = Todo.objects.create(
            title="Test Todo",
            description="Test description"
        )
    
    def test_todo_list_view_status_code(self):
        """Test that the list view returns 200."""
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_todo_list_view_template(self):
        """Test that the list view uses the correct template."""
        response = self.client.get(reverse('todo_list'))
        self.assertTemplateUsed(response, 'app/todo_list.html')
    
    def test_todo_list_view_contains_todo(self):
        """Test that todos are displayed in the list."""
        response = self.client.get(reverse('todo_list'))
        self.assertContains(response, "Test Todo")
    
    def test_todo_list_filter_completed(self):
        """Test filtering completed todos."""
        completed_todo = Todo.objects.create(title="Completed", completed=True)
        response = self.client.get(reverse('todo_list') + '?filter=completed')
        self.assertContains(response, "Completed")
    
    def test_todo_list_filter_active(self):
        """Test filtering active todos."""
        response = self.client.get(reverse('todo_list') + '?filter=active')
        self.assertContains(response, "Test Todo")
    
    def test_todo_create_get(self):
        """Test GET request to create view."""
        response = self.client.get(reverse('todo_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/todo_form.html')
    
    def test_todo_create_post(self):
        """Test POST request to create a new todo."""
        response = self.client.post(reverse('todo_create'), {
            'title': 'New Todo',
            'description': 'New description'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Todo.objects.filter(title='New Todo').exists())
    
    def test_todo_update_get(self):
        """Test GET request to update view."""
        response = self.client.get(reverse('todo_update', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/todo_form.html')
        self.assertContains(response, "Test Todo")
    
    def test_todo_update_post(self):
        """Test POST request to update a todo."""
        response = self.client.post(reverse('todo_update', args=[self.todo.pk]), {
            'title': 'Updated Todo',
            'description': 'Updated description',
            'completed': 'on'
        })
        self.assertEqual(response.status_code, 302)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated Todo')
        self.assertTrue(self.todo.completed)
    
    def test_todo_delete_get(self):
        """Test GET request to delete view shows confirmation."""
        response = self.client.get(reverse('todo_delete', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/todo_confirm_delete.html')
    
    def test_todo_delete_post(self):
        """Test POST request to delete a todo."""
        todo_id = self.todo.pk
        response = self.client.post(reverse('todo_delete', args=[todo_id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Todo.objects.filter(pk=todo_id).exists())
    
    def test_toggle_complete(self):
        """Test toggling completion status."""
        initial_status = self.todo.completed
        response = self.client.get(reverse('toggle_complete', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 302)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.completed, not initial_status)
    
    def test_todo_not_found(self):
        """Test that non-existent todo returns 404."""
        response = self.client.get(reverse('todo_update', args=[9999]))
        self.assertEqual(response.status_code, 404)
