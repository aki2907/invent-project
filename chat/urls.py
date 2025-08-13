from django.urls import path
from . import views

app_name = 'chat'
urlpatterns = [
    path('<int:conversation_id>/', views.chat_room_view, name='room'),
]
