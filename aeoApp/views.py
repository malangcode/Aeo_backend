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
from django.db.models import Sum, F


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
    
    
    
    
    

class BrandWorkspaceAnalysisAPIView(APIView):
    """
    Returns:
      - Prompt history with brand mentions
      - Brand metrics (total mentions, percentage, trend)
      - Time series data for plotting
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            brand_profile = user.brand_profile
        except BrandProfile.DoesNotExist:
            return Response({"error": "Brand profile not found"}, status=404)

        # -------------------------------------------------
        # 1️⃣ Prompt history
        # -------------------------------------------------
        prompt_history_qs = PromptHistory.objects.filter(
            brand_profile=brand_profile
        ).order_by("-created_at")[:50]  # last 50 prompts

        prompt_history = []
        for ph in prompt_history_qs:
            prompt_history.append({
                "id": ph.id,
                "prompt": ph.prompt,
                "date": ph.created_at.strftime("%b %d, %Y"),
                "timestamp": ph.created_at.strftime("%I:%M %p"),
                "brandMentioned": ph.user_brand_mentioned or ph.competitor_mentioned,
                "brands": ph.mentioned_brands,
            })

        # -------------------------------------------------
        # 2️⃣ Brand metrics
        # -------------------------------------------------
        metrics_qs = BrandMentionMetric.objects.filter(
            brand_profile=brand_profile
        ).order_by("-total_mentions")

        total_mentions = metrics_qs.aggregate(total=Sum("total_mentions"))["total"] or 1

        brand_metrics = []
        for m in metrics_qs:
            percentage = round((m.total_mentions / total_mentions) * 100)
            # Calculate trend by comparing with previous day sum (optional: here we can assume 'up', 'down', 'stable')
            last_day = BrandMentionTimeseries.objects.filter(
                brand_profile=brand_profile,
                brand_name=m.brand_name
            ).order_by("-date").first()
            prev_day = BrandMentionTimeseries.objects.filter(
                brand_profile=brand_profile,
                brand_name=m.brand_name
            ).order_by("-date")[1:2].first() if BrandMentionTimeseries.objects.filter(
                brand_profile=brand_profile,
                brand_name=m.brand_name
            ).count() > 1 else None

            if last_day and prev_day:
                if last_day.mentions > prev_day.mentions:
                    trend = "up"
                elif last_day.mentions < prev_day.mentions:
                    trend = "down"
                else:
                    trend = "stable"
            else:
                trend = "stable"

            brand_metrics.append({
                "name": m.brand_name,
                "mentions": m.total_mentions,
                "percentage": percentage,
                "trend": trend,
            })

        # -------------------------------------------------
        # 3️⃣ Time series
        # -------------------------------------------------
        # Collect last 14 days
        ts_qs = BrandMentionTimeseries.objects.filter(
            brand_profile=brand_profile
        ).order_by("date")

        # Prepare data grouped by date
        time_series_dict = {}
        for ts in ts_qs:
            date_str = ts.date.strftime("%b %d")  # e.g., "Jan 12"
            if date_str not in time_series_dict:
                time_series_dict[date_str] = {}
            key = "yourBrand" if ts.brand_name == brand_profile.brand_name else ts.brand_name.replace(" ", "")
            time_series_dict[date_str][key] = ts.mentions

        # Convert to list
        time_series_data = []
        for date, data in time_series_dict.items():
            entry = {"date": date}
            entry.update(data)
            time_series_data.append(entry)

        return Response({
            "promptHistory": prompt_history,
            "brandMetrics": brand_metrics,
            "timeSeriesData": time_series_data,
        })    