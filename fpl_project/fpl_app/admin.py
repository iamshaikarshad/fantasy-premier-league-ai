from django.contrib import admin
from fpl_app.models import (
    Team, Player, GameWeek, PlayerGameWeekStats,
    Fixture, MLModel, OptimalTeam, OptimalTeamPlayer
)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'strength']
    search_fields = ['name', 'short_name']


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['web_name', 'team', 'position', 'now_cost', 'total_points', 'form']
    list_filter = ['position', 'team', 'status']
    search_fields = ['web_name', 'first_name', 'second_name']
    readonly_fields = ['player_id', 'created_at', 'updated_at']


@admin.register(GameWeek)
class GameWeekAdmin(admin.ModelAdmin):
    list_display = ['name', 'deadline_time', 'is_current', 'is_finished']
    list_filter = ['is_current', 'is_finished']
    readonly_fields = ['gameweek_id', 'created_at', 'updated_at']


@admin.register(PlayerGameWeekStats)
class PlayerGameWeekStatsAdmin(admin.ModelAdmin):
    list_display = ['player', 'gameweek', 'total_points', 'minutes']
    list_filter = ['gameweek', 'player__position']
    search_fields = ['player__web_name']


@admin.register(Fixture)
class FixtureAdmin(admin.ModelAdmin):
    list_display = ['team_h', 'team_a', 'kickoff_time', 'is_finished', 'team_h_score', 'team_a_score']
    list_filter = ['is_finished', 'gameweek']


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_type', 'version', 'trained_at', 'is_active', 'rmse']
    list_filter = ['model_type', 'is_active']
    readonly_fields = ['mlflow_run_id', 'trained_at']


@admin.register(OptimalTeam)
class OptimalTeamAdmin(admin.ModelAdmin):
    list_display = ['gameweek', 'total_cost', 'predicted_points', 'created_at']
    list_filter = ['gameweek', 'created_at']


@admin.register(OptimalTeamPlayer)
class OptimalTeamPlayerAdmin(admin.ModelAdmin):
    list_display = ['player', 'is_captain', 'is_vice_captain', 'is_starting', 'predicted_points']
    list_filter = ['is_captain', 'is_starting']
    search_fields = ['player__web_name']
