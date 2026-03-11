from rest_framework import viewsets, permissions
from .models import Task
from .serializers import TaskSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics
from .serializers import UserSerializer
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status
from datetime import date
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.utils import timezone

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user)

        status_param = self.request.query_params.get('status')
        priority_param = self.request.query_params.get('priority')

        if status_param:
            queryset = queryset.filter(status=status_param)

        if priority_param:
            queryset = queryset.filter(priority=priority_param)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        cache.delete(f"tasks_{self.request.user.id}")

    def list(self, request, *args, **kwargs):

        # ---------- RATE LIMITING ----------
        user = request.user
        rate_key = f"rate_limit_{user.id}"

        request_count = cache.get(rate_key, 0)

        if request_count >= 20:
            return Response(
                {"error": "Too many requests. Try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        cache.set(rate_key, request_count + 1, timeout=60)

        # ---------- REDIS CACHING ----------
        cache_key = f"tasks_{user.id}"

        cached_tasks = cache.get(cache_key)

        if cached_tasks:
            return Response(cached_tasks)

        response = super().list(request, *args, **kwargs)

        cache.set(cache_key, response.data, timeout=120)

        return response
    
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    return render(request, 'tasks/home.html')

def register_page(request):

    if request.user.is_authenticated:
        return redirect("/dashboard/")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # username cannot be empty
        if not username or not username.strip():
            return render(request, "tasks/register.html", {
                "error": "Username cannot be empty"
            })

        # password cannot be empty
        if not password:
            return render(request, "tasks/register.html", {
                "error": "Password cannot be empty"
            })

        # confirm password cannot be empty
        if not confirm_password:
            return render(request, "tasks/register.html", {
                "error": "Please confirm your password"
            })

        # passwords must match
        if password != confirm_password:
            return render(request, "tasks/register.html", {
                "error": "Passwords do not match"
            })

        # username already exists
        if User.objects.filter(username=username).exists():
            return render(request, "tasks/register.html", {
                "error": "Username already exists"
            })

        User.objects.create_user(username=username, password=password)

        messages.success(request, "Account created successfully. Please login.")
        return redirect("/login/")

    return render(request, "tasks/register.html")

def login_page(request):

    # if user is already logged in → go to dashboard
    if request.user.is_authenticated:
        return redirect("/dashboard/")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        # username cannot be empty
        if not username or not username.strip():
            return render(request, "tasks/login.html", {
                "error": "Username cannot be empty"
            })

        # password cannot be empty
        if not password:
            return render(request, "tasks/login.html", {
                "error": "Password cannot be empty"
            })

        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(request, "tasks/login.html", {
                "error": "Invalid username or password"
            })

        login(request, user)
        return redirect("/dashboard/")

    return render(request, "tasks/login.html")

@login_required
@never_cache
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, "tasks/dashboard.html", {"tasks": tasks})

@login_required
def create_task(request):

    if request.method == "POST":
        title = request.POST.get("title")
        status = request.POST.get("status")
        priority = request.POST.get("priority")
        deadline = request.POST.get("deadline")

        # validation: deadline cannot be in the past
        if deadline < str(date.today()):
            return render(request, "tasks/create_task.html", {
                "error": "Deadline cannot be in the past"
            })

        # validation: title cannot be empty
        if not title.strip():
            return render(request, "tasks/create_task.html", {
                "error": "Title cannot be empty"
            })

        # validation: minimum length
        if len(title) < 3:
            return render(request, "tasks/create_task.html", {
                "error": "Title must be at least 3 characters"
            })

        Task.objects.create(
            title=title,
            status=status,
            priority=priority,
            deadline=deadline,
            user=request.user
        )

        messages.success(request, "Task created successfully.")

        return redirect("/dashboard/")

    return render(request, "tasks/create_task.html", {"today": date.today()})

@login_required
def edit_task(request, task_id):

    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == "POST":

        title = request.POST.get("title")
        status = request.POST.get("status")
        priority = request.POST.get("priority")
        deadline = request.POST.get("deadline")

        # title cannot be empty
        if not title.strip():
            return render(request, "tasks/edit_task.html", {
                "task": task,
                "error": "Title cannot be empty"
            })

        # title minimum length
        if len(title) < 3:
            return render(request, "tasks/edit_task.html", {
                "task": task,
                "error": "Title must be at least 3 characters"
            })

        # deadline cannot be in the past
        if deadline < str(date.today()):
            return render(request, "tasks/edit_task.html", {
                "task": task,
                "error": "Deadline cannot be in the past"
            })

        task.title = title
        task.status = status
        task.priority = priority
        task.deadline = deadline
        task.save()
        messages.success(request, "Task updated successfully.")

        return redirect("/dashboard/")

    return render(request, "tasks/edit_task.html", {
    "task": task,
    "today": date.today()
    })

@login_required
def delete_task(request, task_id):

    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    messages.success(request, "Task deleted successfully.")

    return redirect("/dashboard/")

def logout_user(request):
    logout(request)
    return redirect("/login/")

def dashboard(request):
    tasks = Task.objects.filter(user=request.user)

    completed = tasks.filter(status="completed").count()
    pending = tasks.filter(status="pending").count()
    high_priority = tasks.filter(priority="high").count()

    context = {
        "tasks": tasks,
        "completed": completed,
        "pending": pending,
        "high_priority": high_priority,
    }

    return render(request, "tasks/dashboard.html", context)

@login_required
def task_detail(request, task_id):

    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == "POST":
        task.notes = request.POST.get("notes")
        task.save()
        messages.success(request, "Notes saved successfully.")

    return render(request, "tasks/task_detail.html", {"task": task})

@login_required
def toggle_task_status(request, task_id):

    task = get_object_or_404(Task, id=task_id, user=request.user)

    if task.status == "completed":
        task.status = "pending"
        messages.success(request, "Task marked as pending.")
    else:
        task.status = "completed"
        messages.success(request, "Task marked as completed.")

    task.save()

    return redirect("/dashboard/")

@login_required
@never_cache
def admin_insights(request):

    if not request.user.is_superuser:
        messages.error(request, "You are not authorized to access this page.")
        return redirect("/dashboard/")

    total_users = User.objects.count()
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status="completed").count()
    pending_tasks = Task.objects.filter(status="pending").count()
    high_priority_tasks = Task.objects.filter(priority="high").count()

    overdue_tasks = Task.objects.filter(
        deadline__lt=timezone.now().date(),
        status="pending"
    ).count()

    users = User.objects.filter(is_superuser=False).order_by("id")

    context = {
        "total_users": total_users,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "high_priority_tasks": high_priority_tasks,
        "overdue_tasks": overdue_tasks,
        "users": users,
    }

    return render(request, "tasks/admin_insights.html", context)

@login_required
@never_cache
def delete_user(request, user_id):

    if not request.user.is_superuser:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect("/dashboard/")

    user_to_delete = get_object_or_404(User, id=user_id)

    if user_to_delete == request.user:
        messages.error(request, "You cannot delete your own admin account.")
        return redirect("/admin-insights/")

    user_to_delete.delete()
    messages.success(request, "User deleted successfully.")

    return redirect("/admin-insights/")