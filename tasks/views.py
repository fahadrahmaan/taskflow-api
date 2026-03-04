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

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]  

    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user)

        status = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')

        if status:
            queryset = queryset.filter(status=status)

        if priority:
            queryset = queryset.filter(priority=priority)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    return render(request, 'tasks/home.html')

def register_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        User.objects.create_user(username=username, password=password)

        return redirect("/")

    return render(request, "tasks/register.html")

def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/dashboard/")

    return render(request, "tasks/login.html")

@login_required
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

        Task.objects.create(
            title=title,
            status=status,
            priority=priority,
            deadline=deadline,
            user=request.user
        )

        return redirect("/dashboard/")

    return render(request, "tasks/create_task.html")

@login_required
def edit_task(request, task_id):

    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == "POST":
        task.title = request.POST.get("title")
        task.status = request.POST.get("status")
        task.priority = request.POST.get("priority")
        task.deadline = request.POST.get("deadline")

        task.save()

        return redirect("/dashboard/")

    return render(request, "tasks/edit_task.html", {"task": task})

@login_required
def delete_task(request, task_id):

    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()

    return redirect("/dashboard/")

def logout_user(request):
    logout(request)
    return redirect("/")