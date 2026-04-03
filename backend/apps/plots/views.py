from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from shared.permissions import IsFieldAgentOrAbove, IsSupervisorOrAbove
from .models import FarmPlot
from .serializers import PlotListSerializer, PlotCreateSerializer, PlotDetailSerializer


class PlotListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsFieldAgentOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['farmer', 'land_tenure', 'is_verified']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PlotCreateSerializer
        return PlotListSerializer

    def get_queryset(self):
        return FarmPlot.objects.select_related('farmer').all()

    def perform_create(self, serializer):
        serializer.save(mapped_by=self.request.user)


class PlotDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FarmPlot.objects.select_related('farmer').all()
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'delete']

    def get_serializer_class(self):
        return PlotDetailSerializer


class VerifyPlotView(APIView):
    permission_classes = [IsSupervisorOrAbove]

    def post(self, request, pk):
        try:
            plot = FarmPlot.objects.get(pk=pk)
        except FarmPlot.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        plot.is_verified = True
        plot.save()
        return Response({'detail': 'Plot verified.', 'area_acres': float(plot.area_acres or 0)})


class FarmerPlotsView(generics.ListAPIView):
    """All plots for a specific farmer."""
    serializer_class = PlotDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FarmPlot.objects.filter(farmer_id=self.kwargs['farmer_pk'])
