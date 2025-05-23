"""
View functions:
- chat(): Renders chat interface template
- groq_chat(): Handles API requests to Groq
"""

from django.shortcuts import render
from chat.utils.ai_chat import chat_with_groq
import json
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .models import ChatSession, ChatMessage
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
# Create your views here.
def chat(request):
    """Render the chat interface."""
    return render(request, 'chat/chat.html')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def groq_chat(request):
    try:
        message = request.data.get('message')
        session_id = request.data.get('session_id')
        if not message or not session_id:
            return Response({'error': 'Missing message or session_id'}, status=400)

        session = ChatSession.objects.get(id=session_id, user=request.user)
        ai_reply = chat_with_groq(message)

        # Save user and AI messages
        ChatMessage.objects.create(session=session, sender='user', message=message)
        ChatMessage.objects.create(session=session, sender='ai', message=ai_reply)

        return Response({
            'response': ai_reply,
            'session_id': session.id
        })

    except ChatSession.DoesNotExist:
        return Response({'error': 'Chat session not found'}, status=404)
    except Exception as e:
        return Response({'error': 'Internal server error', 'details': str(e)}, status=500)


    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_chat_sessions(request):
    sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
    data = []
    for session in sessions:
        messages = session.messages.all().order_by('timestamp')
        data.append({
            'id': session.id,
            'title': session.title,
            'createdAt': session.created_at,
            'messages': [
                {
                    'id': msg.id,
                    'content': msg.message,
                    'role': msg.sender,
                    'timestamp': msg.timestamp
                } for msg in messages
            ]
        })
    return JsonResponse(data, safe=False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_chat_session(request):
    chat = ChatSession.objects.create(user=request.user, title="New Chat")
    return Response({
        'id': str(chat.id),  # Convert to string for frontend compatibility
        'title': chat.title,
        'createdAt': int(chat.created_at.timestamp() * 1000),
        'messages': []
    }, status=201)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_chat_session(request, session_id):
    try:
        chat = ChatSession.objects.get(id=session_id, user=request.user)
        chat.delete()
        return Response({"detail": "Chat deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except ChatSession.DoesNotExist:
        return Response({"error": "Chat session not found"}, status=status.HTTP_404_NOT_FOUND)
