from django.http import HttpResponse
from rest_framework import status,  permissions, mixins, generics
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
    
    
    
    
class AddCompetitorView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            brand_profile = BrandProfile.objects.get(user=request.user)
        except BrandProfile.DoesNotExist:
            return Response(
                {"error": "Brand profile not found for this user"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CompetitorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(brand_profile=brand_profile)
            return Response(
                {
                    "message": "Competitor added successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    
class CompetitorView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # 🔹 helper: get user's brand profile
    def get_brand_profile(self, user):
        try:
            return BrandProfile.objects.get(user=user)
        except BrandProfile.DoesNotExist:
            return None

    # 🔹 helper: get competitor owned by user
    def get_competitor(self, brand_profile, competitor_id):
        try:
            return Competitors.objects.get(
                id=competitor_id,
                brand_profile=brand_profile
            )
        except Competitors.DoesNotExist:
            return None

    # 🟢 GET → list OR retrieve
    def get(self, request, competitor_id=None):
        brand_profile = self.get_brand_profile(request.user)
        if not brand_profile:
            return Response(
                {"error": "Brand profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if competitor_id:
            competitor = self.get_competitor(brand_profile, competitor_id)
            if not competitor:
                return Response(
                    {"error": "Competitor not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = CompetitorSerializer(competitor)
            return Response(serializer.data, status=status.HTTP_200_OK)

        competitors = Competitors.objects.filter(
            brand_profile=brand_profile
        ).order_by('-created_at')

        serializer = CompetitorSerializer(competitors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 🟢 POST → create
    def post(self, request):
        brand_profile = self.get_brand_profile(request.user)
        if not brand_profile:
            return Response(
                {"error": "Brand profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CompetitorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(brand_profile=brand_profile)
            return Response(
                {
                    "message": "Competitor added successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 🟢 PUT / PATCH → update
    def put(self, request, competitor_id):
        return self._update(request, competitor_id)

    def patch(self, request, competitor_id):
        return self._update(request, competitor_id)

    def _update(self, request, competitor_id):
        brand_profile = self.get_brand_profile(request.user)
        if not brand_profile:
            return Response(
                {"error": "Brand profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        competitor = self.get_competitor(brand_profile, competitor_id)
        if not competitor:
            return Response(
                {"error": "Competitor not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CompetitorSerializer(
            competitor,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Competitor updated successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 🟢 DELETE → delete
    def delete(self, request, competitor_id):
        brand_profile = self.get_brand_profile(request.user)
        if not brand_profile:
            return Response(
                {"error": "Brand profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        competitor = self.get_competitor(brand_profile, competitor_id)
        if not competitor:
            return Response(
                {"error": "Competitor not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        competitor.delete()
        return Response(
            {"message": "Competitor deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )    
        
        

class SecondaryBrandView(
    generics.GenericAPIView,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = SecondaryBrandSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SecondaryBrands.objects.filter(
            brand_profile__user=self.request.user
        )

    def get_brand_profile(self):
        try:
            return BrandProfile.objects.get(user=self.request.user)
        except BrandProfile.DoesNotExist:
            return None

    # CREATE
    def post(self, request, *args, **kwargs):
        brand_profile = self.get_brand_profile()
        if not brand_profile:
            return Response(
                {"error": "Brand profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(brand_profile=brand_profile)
        return Response(
            {"message": "Secondary brand added", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )

    # READ (list)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    # UPDATE
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    # DELETE
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)        