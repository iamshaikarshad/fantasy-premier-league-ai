"""
URL Router for FPL API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from fpl_app import views

router = DefaultRouter()
router.register(r'players', views.PlayerViewSet)
router.register(r'gameweeks', views.GameWeekViewSet)
router.register(r'models', views.MLModelViewSet)
router.register(r'teams', views.OptimalTeamViewSet, basename='team')

urlpatterns = [
    path('', include(router.urls)),
]
