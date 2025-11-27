"""
Serializers for DRF API endpoints.
"""
from rest_framework import serializers
from fpl_app.models import (
    Player, Team, GameWeek, PlayerGameWeekStats, 
    MLModel, OptimalTeam, OptimalTeamPlayer
)


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'team_id', 'name', 'short_name', 'strength']


class PlayerSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    
    class Meta:
        model = Player
        fields = [
            'id', 'player_id', 'web_name', 'team', 'position',
            'now_cost', 'total_points', 'form', 'points_per_game',
            'selected_by_percent', 'minutes', 'status'
        ]


class GameWeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameWeek
        fields = ['id', 'gameweek_id', 'name', 'deadline_time', 'is_current', 'is_finished']


class PlayerGameWeekStatsSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)
    gameweek = GameWeekSerializer(read_only=True)
    
    class Meta:
        model = PlayerGameWeekStats
        fields = [
            'player', 'gameweek', 'minutes', 'total_points',
            'goals_scored', 'assists', 'clean_sheets', 'value'
        ]


class MLModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModel
        fields = [
            'id', 'name', 'model_type', 'version',
            'accuracy_score', 'rmse', 'mae', 'is_active', 'trained_at'
        ]


class OptimalTeamPlayerSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)
    
    class Meta:
        model = OptimalTeamPlayer
        fields = [
            'player', 'is_captain', 'is_vice_captain',
            'is_starting', 'predicted_points'
        ]


class OptimalTeamSerializer(serializers.ModelSerializer):
    players = OptimalTeamPlayerSerializer(
        source='optimaltemplayer_set', many=True, read_only=True
    )
    gameweek = GameWeekSerializer(read_only=True)
    model = MLModelSerializer(read_only=True)
    
    class Meta:
        model = OptimalTeam
        fields = [
            'id', 'gameweek', 'model', 'players',
            'total_cost', 'predicted_points', 'created_at'
        ]


class PredictionRequestSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()
    gameweek_id = serializers.IntegerField(required=False)


class OptimizeTeamRequestSerializer(serializers.Serializer):
    gameweek_id = serializers.IntegerField()
    budget = serializers.FloatField(default=100.0)
    auto_captain = serializers.BooleanField(default=True)


class TransferSuggestionSerializer(serializers.Serializer):
    out = serializers.CharField()
    in_player = serializers.CharField()
    points_gain = serializers.FloatField()
    cost_impact = serializers.FloatField()
    net_value = serializers.FloatField()
