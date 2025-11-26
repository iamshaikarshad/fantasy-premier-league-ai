"""
API Views for FPL Optimizer.
"""
import logging
import joblib
from pathlib import Path
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from fpl_app.models import Player, Team, GameWeek, MLModel, OptimalTeam
from fpl_app.serializers import (
    PlayerSerializer, GameWeekSerializer, MLModelSerializer,
    OptimalTeamSerializer, PredictionRequestSerializer,
    OptimizeTeamRequestSerializer
)
from fpl_app.ml.data_fetcher import fetch_bootstrap_data, fetch_player_history
from fpl_app.ml.features import extract_player_features_from_history, get_feature_columns_for_model
from fpl_app.ml.optimizer import optimize_team

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).parent.parent / 'models'


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    filterset_fields = ['team', 'position', 'status']
    search_fields = ['web_name', 'first_name', 'second_name']
    ordering_fields = ['total_points', 'now_cost', 'form']
    ordering = ['-total_points']
    
    @action(detail=True, methods=['get'])
    def predictions(self, request, pk=None):
        """Get predictions for a specific player."""
        player = self.get_object()
        gw = request.query_params.get('gw', 1)
        
        try:
            # Load model
            model_path = MODELS_DIR / 'points_predictor_model.joblib'
            if not model_path.exists():
                return Response(
                    {'error': 'Model not trained yet'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            model = joblib.load(str(model_path))
            
            # Get player features
            history_data = fetch_player_history(player.player_id)
            features = extract_player_features_from_history({
                'id': player.player_id,
                'web_name': player.web_name,
                'team': player.team_id,
                'element_type': player.position,
                'now_cost': int(player.now_cost * 10),
                'total_points': player.total_points,
                'minutes': player.minutes,
                'form': player.form,
                'points_per_game': player.points_per_game,
                'selected_by_percent': player.selected_by_percent,
            }, history_data)
            
            # Prepare features for model
            feature_cols = get_feature_columns_for_model()
            feature_values = [features.get(col, 0.0) for col in feature_cols]
            
            # Make prediction
            pred = model.predict([feature_values])[0]
            pred = max(0, min(pred, 20))  # Clip to 0-20
            
            return Response({
                'player_id': player.player_id,
                'player_name': player.web_name,
                'predicted_points': float(pred),
                'confidence': 0.75  # Placeholder
            })
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GameWeekViewSet(viewsets.ModelViewSet):
    queryset = GameWeek.objects.all()
    serializer_class = GameWeekSerializer
    ordering = ['-gameweek_id']
    
    @action(detail=True, methods=['get'])
    def current(self, request):
        """Get current gameweek."""
        current = GameWeek.objects.filter(is_current=True).first()
        if not current:
            return Response({'error': 'No current gameweek'}, status=404)
        return Response(GameWeekSerializer(current).data)


class MLModelViewSet(viewsets.ModelViewSet):
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer
    filterset_fields = ['model_type', 'is_active']
    ordering = ['-trained_at']
    
    @action(detail=False, methods=['post'])
    def retrain(self, request):
        """Trigger model retraining."""
        from fpl_app.tasks import retrain_model_task
        
        model_type = request.data.get('model_type', 'points_predictor')
        task = retrain_model_task.delay(model_type)
        
        return Response({
            'task_id': task.id,
            'status': 'retraining_started',
            'model_type': model_type
        })
    
    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """Get active model metrics."""
        active_model = MLModel.objects.filter(is_active=True).first()
        if not active_model:
            return Response({'error': 'No active model'}, status=404)
        
        return Response({
            'model_id': active_model.id,
            'rmse': float(active_model.rmse or 0),
            'mae': float(active_model.mae or 0),
            'accuracy': float(active_model.accuracy_score or 0)
        })


class OptimalTeamViewSet(viewsets.ModelViewSet):
    queryset = OptimalTeam.objects.all()
    serializer_class = OptimalTeamSerializer
    filterset_fields = ['gameweek']
    ordering = ['-gameweek__gameweek_id']
    
    @action(detail=False, methods=['post'])
    def optimize(self, request):
        """Optimize team for a gameweek."""
        from fpl_app.tasks import optimize_team_task
        
        serializer = OptimizeTeamRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        gw_id = serializer.validated_data['gw_id']
        task = optimize_team_task.delay(gw_id)
        
        return Response({
            'task_id': task.id,
            'status': 'optimization_started',
            'gameweek_id': gw_id
        })
