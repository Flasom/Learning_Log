from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('topics/', views.topics, name='topics'),
    path('topics/<topic_id>/', views.topic, name='topic'),
    path('new_topic', views.new_topic, name='new_topic'),
    path('new_entry/<topic_id>/', views.new_entry, name='new_entry'),
    path('edit_entry/<entry_id>/', views.edit_entry, name='edit_entry'),
    path('edit_topic/<topic_id>/', views.edit_topic,  name='edit_topic'),
    path('delete_topic/<topic_id>', views.delete_topic, name='delete_topic'),
    path('delete_entry/<entry_id>', views.delete_entry, name='delete_entry'),
    path('delete_confirm_entry/<entry_id>', views.delete_confirm_entry, name='delete_confirm_entry'),
    path('delete_confirm_topic/<topic_id>', views.delete_confirm_topic, name='delete_confirm_topic'),
    path('history', views.history, name='history'),
]