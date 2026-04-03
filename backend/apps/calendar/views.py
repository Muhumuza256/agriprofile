from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from shared.permissions import IsFieldAgentOrAbove
from .models import FarmActivity
from .services import FarmCalendarService


class FarmActivitySerializer(serializers.ModelSerializer):
    crop_name = serializers.CharField(source='farmer_crop.crop_name', read_only=True)
    farmer_name = serializers.CharField(source='farmer_crop.farmer.full_name', read_only=True)

    class Meta:
        model = FarmActivity
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'calendar_activity_id', 'synced_at']


class FarmerCalendarView(generics.ListAPIView):
    """All scheduled activities for a specific farmer's crops."""
    serializer_class = FarmActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FarmActivity.objects.filter(
            farmer_crop__farmer_id=self.kwargs['farmer_pk']
        )


class GroupCalendarView(APIView):
    """Aggregated activity calendar for a group."""
    permission_classes = [IsAuthenticated]

    def get(self, request, group_pk):
        activities = FarmActivity.objects.filter(
            farmer_crop__farmer__group_id=group_pk
        ).order_by('scheduled_date')

        serializer = FarmActivitySerializer(activities, many=True)
        return Response({
            'group_id': str(group_pk),
            'activity_count': activities.count(),
            'activities': serializer.data,
        })


class GenerateSeasonCalendarView(APIView):
    """Generate a full season calendar for all crops of a farmer."""
    permission_classes = [IsFieldAgentOrAbove]

    def post(self, request, farmer_pk):
        from apps.farmers.models import FarmerProfile
        try:
            farmer = FarmerProfile.objects.get(pk=farmer_pk)
        except FarmerProfile.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

        service = FarmCalendarService()
        created_count = 0
        for crop in farmer.crops.all():
            activities = service.generate_season_calendar(crop)
            created_count += len(activities)

        return Response({
            'detail': f'Generated {created_count} activities across {farmer.crops.count()} crops.'
        })
