"""
Celery Tasks for background job processing.
"""
import logging
from celery import shared_task
from django.db import transaction
from fpl_app.models import MLModel, GameWeek, OptimalTeam
from fpl_app.ml.data_fetcher import fetch_bootstrap_data, fetch_player_history
from fpl_app.ml.features import create_player_features_dataframe, get_feature_columns_for_model
from fpl_app.ml.train import train_and_save_model, create_synthetic_training_data
from fpl_app.ml.optimizer import optimize_team
from sklearn.model_selection import train_test_split
import pandas as pd

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def fetch_fpl_data_task(self):
    """Fetch and update FPL data from API."""
    try:
        logger.info("Starting FPL data fetch...")
        
        # Fetch bootstrap data
        bootstrap = fetch_bootstrap_data()
        if not bootstrap:
            return {'status': 'failed', 'error': 'Could not fetch bootstrap'}
        
        # Update teams, players, gameweeks from bootstrap
        from fpl_app.models import Team, Player, GameWeek as GW
        from django.utils import timezone
        from datetime import datetime
        
        # Process teams
        for team_data in bootstrap.get('teams', []):
            Team.objects.update_or_create(
                team_id=team_data['id'],
                defaults={
                    'name': team_data['name'],
                    'short_name': team_data['short_name'],
                    'strength': team_data.get('strength', 3),
                }
            )
        
        # Process players
        for player_data in bootstrap.get('elements', [])[:10]:  # Limit for testing
            team_id = player_data.get('team')
            if team_id:
                team = Team.objects.filter(team_id=team_id).first()
                Player.objects.update_or_create(
                    player_id=player_data['id'],
                    defaults={
                        'web_name': player_data.get('web_name', ''),
                        'first_name': player_data.get('first_name', ''),
                        'second_name': player_data.get('second_name', ''),
                        'team': team,
                        'position': player_data.get('element_type'),
                        'now_cost': player_data.get('now_cost', 0) / 10.0,
                        'total_points': player_data.get('total_points', 0),
                        'minutes': player_data.get('minutes', 0),
                    }
                )
        
        # Process gameweeks
        for event_data in bootstrap.get('events', []):
            GW.objects.update_or_create(
                gameweek_id=event_data['id'],
                defaults={
                    'name': event_data['name'],
                    'deadline_time': event_data['deadline_time'],
                    'is_current': event_data.get('is_current', False),
                    'is_finished': event_data.get('is_finished', False),
                }
            )
        
        logger.info("FPL data fetch completed")
        return {'status': 'success', 'data_updated': True}
    
    except Exception as e:
        logger.error(f"Data fetch error: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(bind=True)
def retrain_model_task(self, model_type='points_predictor'):
    """Retrain ML model."""
    try:
        logger.info(f"Starting retraining for model: {model_type}")
        
        # Create synthetic data for MVP
        X, y = create_synthetic_training_data(n_samples=200)
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        result = train_and_save_model(
            X_train, y_train, X_val, y_val,
            model_name=model_type, tune=False
        )
        
        # Save model record
        with transaction.atomic():
            MLModel.objects.filter(model_type=model_type, is_active=True).update(is_active=False)
            MLModel.objects.create(
                name=f"{model_type}_v1",
                model_type=model_type,
                version='1.0.0',
                mlflow_run_id='run_123',
                mlflow_experiment_id='exp_1',
                accuracy_score=result['metrics'].get('r2'),
                rmse=result['metrics'].get('rmse'),
                mae=result['metrics'].get('mae'),
                is_active=True,
                feature_importance=result.get('feature_importance', {})
            )
        
        logger.info(f"Retraining completed: {result}")
        return {'status': 'success', 'metrics': result['metrics']}
    
    except Exception as e:
        logger.error(f"Retraining error: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(bind=True)
def optimize_team_task(self, gameweek_id):
    """Optimize team for a gameweek."""
    try:
        logger.info(f"Starting team optimization for GW{gameweek_id}")
        
        from fpl_app.models import Player, GameWeek
        
        # Get gameweek
        gw = GameWeek.objects.filter(gameweek_id=gameweek_id).first()
        if not gw:
            return {'status': 'failed', 'error': f'Gameweek {gameweek_id} not found'}
        
        # Get all players with predictions
        players = Player.objects.all().values(
            'player_id', 'web_name', 'position', 'now_cost',
            'team_id', 'total_points'
        )
        
        players_df = pd.DataFrame(list(players))
        if players_df.empty:
            return {'status': 'failed', 'error': 'No players available'}
        
        # Add predicted points (placeholder: use form or random)
        players_df['predicted_points'] = players_df['total_points'].fillna(0) / 10 + 3
        players_df['price'] = players_df['now_cost'] / 10
        
        # Run optimizer
        result = optimize_team(players_df)
        
        # Save result
        if result['status'] == 'Optimal':
            optimal_team = OptimalTeam.objects.create(
                gameweek=gw,
                total_cost=result['total_cost'],
                predicted_points=result['total_predicted_points']
            )
            
            # Add players to team
            for idx, player_data in enumerate(result['selected_players']):
                from fpl_app.models import OptimalTeamPlayer
                player_obj = Player.objects.get(player_id=player_data['player_id'])
                OptimalTeamPlayer.objects.create(
                    team=optimal_team,
                    player=player_obj,
                    is_starting=(idx < 11),
                    position_order=idx,
                    predicted_points=player_data['predicted_points']
                )
        
        logger.info(f"Team optimization completed: {result}")
        return {'status': 'success', 'result': result}
    
    except Exception as e:
        logger.error(f"Team optimization error: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def calculate_metrics_task():
    """Calculate post-gameweek metrics."""
    try:
        logger.info("Calculating metrics...")
        # Post-gameweek processing
        return {'status': 'success'}
    except Exception as e:
        logger.error(f"Metrics calculation error: {e}")
        return {'status': 'failed', 'error': str(e)}
