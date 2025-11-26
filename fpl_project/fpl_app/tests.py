"""
Unit tests for feature engineering and models.
"""
import pytest
from django.test import TestCase
from fpl_app.ml.features import rolling_average, extract_player_features_from_history
from fpl_app.models import Team, Player


def test_rolling_average_empty():
    assert rolling_average([], 3) == 0.0


def test_rolling_average_with_values():
    arr = [1, 2, 3, 4, 5]
    result = rolling_average(arr, 3)
    assert result == pytest.approx(4.0)  # (3+4+5)/3


def test_rolling_average_window_larger_than_array():
    arr = [1, 2]
    result = rolling_average(arr, 5)
    assert result == pytest.approx(1.5)  # (1+2)/2


def test_extract_player_features_basic():
    player_data = {
        'id': 1,
        'web_name': 'Test Player',
        'team': 1,
        'element_type': 2,
        'now_cost': 50,
        'total_points': 100,
        'minutes': 900,
        'form': '8.5',
        'points_per_game': '5.0',
        'selected_by_percent': '50.0'
    }
    history_data = None
    
    features = extract_player_features_from_history(player_data, history_data)
    
    assert features['player_id'] == 1
    assert features['player_name'] == 'Test Player'
    assert features['price'] == 5.0
    assert features['total_points'] == 100
    assert features['minutes'] == 900


def test_extract_player_features_with_history():
    player_data = {
        'id': 1,
        'web_name': 'Test Player',
        'team': 1,
        'element_type': 2,
        'now_cost': 50,
        'total_points': 100,
        'minutes': 900,
        'form': '8.5',
        'points_per_game': '5.0',
        'selected_by_percent': '50.0'
    }
    
    history_data = {
        'history': [
            {'total_points': 5, 'minutes': 90, 'goals_scored': 1, 'assists': 0},
            {'total_points': 6, 'minutes': 90, 'goals_scored': 0, 'assists': 1},
            {'total_points': 7, 'minutes': 90, 'goals_scored': 1, 'assists': 0},
        ]
    }
    
    features = extract_player_features_from_history(player_data, history_data)
    
    assert features['points_last3_avg'] == pytest.approx(6.0)
    assert features['minutes_last3_avg'] == pytest.approx(90.0)
    assert features['goals_last5'] == 2
    assert features['assists_last5'] == 1


class PlayerModelTest(TestCase):
    def setUp(self):
        self.team = Team.objects.create(
            team_id=1,
            name='Test Team',
            short_name='TST'
        )
    
    def test_create_player(self):
        player = Player.objects.create(
            player_id=1,
            web_name='Test Player',
            first_name='Test',
            second_name='Player',
            team=self.team,
            position='MID',
            now_cost=9.5,
            total_points=100
        )
        assert player.web_name == 'Test Player'
        assert player.position == 'MID'

