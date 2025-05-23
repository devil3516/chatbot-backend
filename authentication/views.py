from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer
from django.db.models import Q

@api_view(['POST'])
def login_view(request):
    if request.method == 'POST':
        identifier = request.data.get('username')
        password = request.data.get('password')

        try:
            #find user by email or username
            user = User.objects.get(Q(username = identifier) | Q(email = identifier))
        except User.DoesNotExist:
            return Response({'error':'User Not Found'}, status=status.HTTP_404_NOT_FOUND)
        #now authenticate user using username(not with email )
        user = authenticate(username = user.username, password = password)
        if user is not None:
            token, created = Token.objects.get_or_create(user = user)
            return Response({
                'token':token.key,
                'user': UserSerializer(user).data
            })
        else:
            return Response({'error':'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def register_view(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if User.objects.filter(username = username).exists():
        return Response({'error':'User already exists'},status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(username = username, email=email,password = password)
    token = Token.objects.create(user=user)
    return Response({
        'token': token.key,
        'user': UserSerializer(user).data
    },status=status.HTTP_201_CREATED)
        