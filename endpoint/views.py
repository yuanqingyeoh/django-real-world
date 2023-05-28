from django.http import JsonResponse
from django.shortcuts import render
from endpoint.models import User
from endpoint.serializers import UserSerializer
# Create your views here.


def get_current_user(request):
    if request.method == 'GET':
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return JsonResponse(serializer.data, safe=False)
