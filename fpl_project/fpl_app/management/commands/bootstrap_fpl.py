"""
Management command to bootstrap initial FPL data and train initial model.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
import logging
from fpl_app.ml.data_fetcher import fetch_bootstrap_data
from fpl_app.ml.train import train_and_save_model, create_synthetic_training_data
from fpl_app.models import Team, Player, GameWeek, MLModel
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Bootstrap FPL data and train initial model'
    
    def handle(self, *args, **options):
        self.stdout.write("🚀 Starting FPL bootstrap...")
        
        # Fetch and load FPL data
        self.stdout.write("📥 Fetching FPL bootstrap data...")
        bootstrap = fetch_bootstrap_data()
        
        if bootstrap:
            # Load teams
            self.stdout.write("📋 Loading teams...")
            for team_data in bootstrap.get('teams', []):
                Team.objects.update_or_create(
                    team_id=team_data['id'],
                    defaults={
                        'name': team_data['name'],
                        'short_name': team_data['short_name'],
                        'strength': team_data.get('strength', 3),
                    }
                )
            self.stdout.write(self.style.SUCCESS(f"✅ Loaded {len(bootstrap['teams'])} teams"))
            
            # Load players (first 50 for bootstrap)
            self.stdout.write("👥 Loading players...")
            count = 0
            for player_data in bootstrap.get('elements', [])[:50]:
                team_id = player_data.get('team')
                if team_id:
                    try:
                        team = Team.objects.get(team_id=team_id)
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
                                'form': float(player_data.get('form', 0) or 0),
                            }
                        )
                        count += 1
                    except Team.DoesNotExist:
                        pass
            self.stdout.write(self.style.SUCCESS(f"✅ Loaded {count} players"))
            
            # Load gameweeks
            self.stdout.write("📅 Loading gameweeks...")
            for event_data in bootstrap.get('events', [])[:10]:
                GameWeek.objects.update_or_create(
                    gameweek_id=event_data['id'],
                    defaults={
                        'name': event_data['name'],
                        'deadline_time': event_data['deadline_time'],
                        'is_current': event_data.get('is_current', False),
                        'is_next': event_data.get('is_next', False),
                        'is_finished': event_data.get('is_finished', False),
                    }
                )
            self.stdout.write(self.style.SUCCESS(f"✅ Loaded gameweeks"))
        else:
            self.stdout.write(self.style.WARNING("⚠️  Could not fetch FPL data, skipping..."))
        
        # Train initial model
        self.stdout.write("🤖 Training initial model...")
        X, y = create_synthetic_training_data(n_samples=200)
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        
        result = train_and_save_model(X_train, y_train, X_val, y_val, model_name='points_predictor', tune=False)
        
        # Save model record
        MLModel.objects.create(
            name='points_predictor_v1.0',
            model_type='points_predictor',
            version='1.0.0',
            mlflow_run_id='initial_run',
            mlflow_experiment_id='initial_exp',
            accuracy_score=result['metrics'].get('r2'),
            rmse=result['metrics'].get('rmse'),
            mae=result['metrics'].get('mae'),
            is_active=True,
            feature_importance=result.get('feature_importance', {})
        )
        
        self.stdout.write(self.style.SUCCESS(f"✅ Model trained! RMSE: {result['metrics']['rmse']:.4f}"))
        self.stdout.write(self.style.SUCCESS("✨ Bootstrap complete! Application ready to use."))
