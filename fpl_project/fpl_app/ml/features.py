"""
Feature Engineering - Extract and transform features for ML models.
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def rolling_average(arr, window: int, fill_value: float = 0.0):
    """Calculate rolling average for a list/array."""
    if not arr or len(arr) == 0:
        return fill_value
    series = pd.Series(arr)
    return float(series.rolling(window=min(window, len(series))).mean().iloc[-1])


def extract_player_features_from_history(player_data, history_data):
    """Extract features from player data and match history."""
    features = {
        'player_id': player_data.get('id'),
        'player_name': player_data.get('web_name', ''),
        'team': player_data.get('team'),
        'position': player_data.get('element_type'),
        'price': player_data.get('now_cost', 0) / 10.0,
        'total_points': player_data.get('total_points', 0),
        'minutes': player_data.get('minutes', 0),
        'form': float(player_data.get('form', 0.0) or 0.0),
        'points_per_game': float(player_data.get('points_per_game', 0.0) or 0.0),
        'selected_by_percent': float(player_data.get('selected_by_percent', 0.0) or 0.0),
    }
    
    if history_data and 'history' in history_data:
        hist = history_data['history']
        if hist:
            # Extract last 3, 5, 10 gameweeks
            last_10 = hist[-10:] if len(hist) >= 10 else hist
            last_5 = hist[-5:] if len(hist) >= 5 else hist
            last_3 = hist[-3:] if len(hist) >= 3 else hist
            
            features['points_last3_avg'] = rolling_average([h.get('total_points', 0) for h in last_3], 3)
            features['points_last5_avg'] = rolling_average([h.get('total_points', 0) for h in last_5], 5)
            features['points_last10_avg'] = rolling_average([h.get('total_points', 0) for h in last_10], 10)
            
            features['minutes_last3_avg'] = rolling_average([h.get('minutes', 0) for h in last_3], 3)
            features['goals_last5'] = sum([h.get('goals_scored', 0) for h in last_5])
            features['assists_last5'] = sum([h.get('assists', 0) for h in last_5])
            features['clean_sheets_last5'] = sum([h.get('clean_sheets', 0) for h in last_5])
        else:
            features['points_last3_avg'] = 0.0
            features['points_last5_avg'] = 0.0
            features['points_last10_avg'] = 0.0
            features['minutes_last3_avg'] = 0.0
            features['goals_last5'] = 0
            features['assists_last5'] = 0
            features['clean_sheets_last5'] = 0
    
    # Advanced stats
    features['influence'] = float(player_data.get('influence', 0.0) or 0.0)
    features['creativity'] = float(player_data.get('creativity', 0.0) or 0.0)
    features['threat'] = float(player_data.get('threat', 0.0) or 0.0)
    features['ict_index'] = float(player_data.get('ict_index', 0.0) or 0.0)
    features['expected_goals'] = float(player_data.get('expected_goals', 0.0) or 0.0)
    features['expected_assists'] = float(player_data.get('expected_assists', 0.0) or 0.0)
    
    return features


def fixture_difficulty_score(fixtures_list):
    """Calculate fixture difficulty score from fixtures list."""
    if not fixtures_list:
        return 0.0
    difficulties = [f.get('difficulty', 3) for f in fixtures_list if f]
    return float(np.mean(difficulties)) if difficulties else 0.0


def create_player_features_dataframe(players_list, histories_dict=None):
    """Create a DataFrame of player features.
    
    Args:
        players_list: List of player dicts from bootstrap
        histories_dict: Dict mapping player_id to history data
    
    Returns:
        DataFrame with player features
    """
    features_list = []
    histories_dict = histories_dict or {}
    
    for player in players_list:
        player_id = player.get('id')
        history = histories_dict.get(player_id)
        features = extract_player_features_from_history(player, history)
        features_list.append(features)
    
    df = pd.DataFrame(features_list)
    return df


def get_feature_columns_for_model():
    """Return list of feature column names for training."""
    return [
        'price', 'form', 'points_per_game', 'selected_by_percent',
        'points_last3_avg', 'points_last5_avg', 'points_last10_avg',
        'minutes_last3_avg', 'goals_last5', 'assists_last5', 'clean_sheets_last5',
        'influence', 'creativity', 'threat', 'ict_index',
        'expected_goals', 'expected_assists', 'minutes'
    ]
