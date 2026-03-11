from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, RegisterView
from django.urls import path, include
from .views import home
from .views import register_page
from .views import login_page
from .views import dashboard
from .views import create_task
from .views import edit_task
from .views import delete_task
from .views import logout_user
from . import views

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('', home, name='home'),
    path('register/', register_page, name='register_page'),
    path('login/', login_page, name='login_page'),
    path('dashboard/', dashboard, name='dashboard'),
    path('create-task/', create_task, name='create_task'),
    path('edit-task/<int:task_id>/', edit_task, name='edit_task'),
    path('delete-task/<int:task_id>/', delete_task, name='delete_task'),
    path('logout/', logout_user, name='logout'),
    path("task/<int:task_id>/", views.task_detail, name="task_detail"),
    path("toggle-task/<int:task_id>/", views.toggle_task_status, name="toggle_task_status"),
    path("admin-insights/", views.admin_insights, name="admin_insights"),
    path("delete-user/<int:user_id>/", views.delete_user, name="delete_user"),
]