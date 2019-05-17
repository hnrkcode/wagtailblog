from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.BlogPageView.as_view(), name='blogpage'),
    path('<slug:slug>/', views.BlogPostView.as_view(), name='blogpost'),
    path('tag/<str:tag>/', views.TagPageView.as_view(), name='tagpage'),
]
