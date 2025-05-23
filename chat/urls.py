    # """
    # Chat app URL patterns:
    # - Root path ('') -> chat view
    # - API endpoint ('api/chat/') -> groq_chat view
    # """


from django.urls import path
from .views import chat, groq_chat, user_chat_sessions, create_chat_session, delete_chat_session
from . import views



app_name = 'chat'

# urlpatterns = [
#     path('', chat, name='chat'),  # For home page view
#     path('api/chat/', groq_chat, name='groq_chat'),  # ✅ This is what React calls
#     path('api/sessions/', user_chat_sessions, name='chat_sessions'),
#     path('api/sessions/create/', create_chat_session, name='create_session'),
#     path('api/sessions/<uuid:session_id>/', delete_chat_session, name='delete_session'),
# ]

# In your urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/user-chat-sessions/', views.user_chat_sessions, name='user_chat_sessions'),
    path('api/create-chat-session/', views.create_chat_session, name='create_chat_session'),
    path('api/groq-chat/', views.groq_chat, name='groq_chat'),
    path('api/delete-chat-session/<uuid:session_id>/', views.delete_chat_session, name='delete_chat_session'),
]