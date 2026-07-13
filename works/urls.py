from django.urls import path

from . import views

urlpatterns = [
    path('', views.works_list, name='works'),
    path('<slug:slug>/comment/', views.post_comment, name='post_comment'),
    path('<slug:slug>/', views.project_detail, name='project_detail'),
]
