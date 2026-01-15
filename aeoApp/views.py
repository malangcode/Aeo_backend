from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import *
from .serializers import *
from rest_framework.views import APIView
from .models import BrandProfile
from .serializers import BrandProfileSerializer


User = get_user_model()

def home(request):
    return HttpResponse("<h1>This is Backend for Dev Rumble made in Django!</h1>")


class BrandProfileUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            brand_profile = request.user.brand_profile
        except BrandProfile.DoesNotExist:
            return Response(
                {"detail": "Brand profile does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = BrandProfileSerializer(
            brand_profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Brand profile updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)