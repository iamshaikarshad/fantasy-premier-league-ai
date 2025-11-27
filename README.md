# FPL Optimizer - Django Implementation

A production-ready Fantasy Premier League team optimization application with ML predictions, automated retraining, and team optimization.

## Project Structure

```
fpl_optimizer/
├── fpl_project/               # Django project root
│   ├── fpl_project/           # Project settings
│   │   ├── settings.py        # Django configuration
│   │   ├── urls.py            # URL routing
│   │   ├── wsgi.py            # WSGI entry
│   │   └── celery.py          # Celery configuration
│   ├── fpl_app/               # Main Django app
│   │   ├── ml/
│   │   │   ├── data_fetcher.py      # FPL API data fetching
│   │   │   ├── features.py          # Feature engineering
│   │   │   ├── train.py             # Model training (LightGBM + Optuna)
│   │   │   └── optimizer.py         # Team optimization (Linear Programming)
│   │   ├── models.py          # Django models
│   │   ├── views.py           # DRF viewsets
│   │   ├── serializers.py     # DRF serializers
│   │   ├── tasks.py           # Celery tasks
│   │   ├── urls.py            # App URL routing
│   │   ├── admin.py           # Django admin config
│   │   └── tests.py           # Unit tests
│   ├── manage.py
│   └── requirements.txt
```

## Features

### 1. Data Pipeline
- **Data Fetcher** (`ml/data_fetcher.py`):
  - Fetch FPL bootstrap data (teams, players, gameweeks)
  - Fetch player historical data
  - Data validation and error handling

### 2. Feature Engineering (`ml/features.py`)
- Rolling averages (3, 5, 10 games)
- Historical performance metrics
- Advanced stats (influence, creativity, threat, ICT index)
- Expected goals/assists
- Fixture difficulty calculations

### 3. Machine Learning (`ml/train.py`)
- **LightGBM** model for points prediction
- **Optuna** hyperparameter optimization
- MLflow experiment tracking
- Model serialization and versioning
- Synthetic data generation for testing

### 4. Team Optimization (`ml/optimizer.py`)
- **Linear Programming** using PuLP
- FPL constraint satisfaction:
  - £100M budget
  - 1 GK, 3-5 DEF, 2-5 MID, 1-3 FWD
  - Max 3 players per team
  - 15 total players
- Transfer suggestion engine
- Team value optimization

### 5. API Endpoints

#### Players
```
GET  /api/players/                    # List all players
GET  /api/players/{id}/               # Get player details
GET  /api/players/{id}/predictions/   # Get predictions for player
```

#### Gameweeks
```
GET  /api/gameweeks/                  # List gameweeks
GET  /api/gameweeks/current/          # Get current gameweek
```

#### Models
```
GET    /api/models/                   # List ML models
POST   /api/models/retrain/           # Trigger retraining
GET    /api/models/metrics/           # Get active model metrics
```

#### Team Optimization
```
GET    /api/teams/                    # List optimal teams
POST   /api/teams/optimize/           # Optimize new team
```

### 6. Background Jobs (Celery)

**Scheduled Tasks:**
- **fetch-fpl-data-hourly**: Update FPL data every hour
- **retrain-models-weekly**: Retrain models every Sunday at 2 AM
- **calculate-metrics-daily**: Post-gameweek metrics at 11 PM

## Setup & Installation

### Prerequisites
- Python 3.9+
- Redis (for Celery)
- PostgreSQL (optional, SQLite for dev)

### Installation Steps

1. **Clone and navigate:**
```bash
cd fpl_optimizer/fpl_project
```

2. **Create virtual environment:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Setup database:**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser:**
```bash
python manage.py createsuperuser
```

6. **Start development server:**
```bash
python manage.py runserver
```

7. **In separate terminal, start Celery:**
```bash
celery -A fpl_project worker -l info
```

8. **In another terminal, start Celery Beat (scheduler):**
```bash
celery -A fpl_project beat -l info
```

## API Usage Examples

### Get Player Predictions
```bash
curl http://localhost:8000/api/players/1/predictions/
```

Response:
```json
{
  "player_id": 1,
  "player_name": "Mohamed Salah",
  "predicted_points": 8.5,
  "confidence": 0.75
}
```

### Trigger Model Retraining
```bash
curl -X POST http://localhost:8000/api/models/retrain/ \
  -H "Content-Type: application/json" \
  -d '{"model_type": "points_predictor"}'
```

Response:
```json
{
  "task_id": "abc123xyz",
  "status": "retraining_started",
  "model_type": "points_predictor"
}
```

### Optimize Team
```bash
curl -X POST http://localhost:8000/api/teams/optimize/ \
  -H "Content-Type: application/json" \
  -d '{"gameweek_id": 1, "budget": 100.0}'
```

Response:
```json
{
  "task_id": "def456abc",
  "status": "optimization_started",
  "gameweek_id": 1
}
```

## Model Details

### Points Predictor Model
- **Algorithm**: LightGBM (Gradient Boosting)
- **Target**: Expected points for next gameweek
- **Features**: 18 engineered features
  - Price, form, PPG, ownership
  - Rolling averages
  - Advanced stats (ICT index, xG, xA)
  - Minutes consistency
- **Hyperparameters**: Optimized via Optuna
- **Evaluation**: RMSE, MAE, R²

### Performance Targets
- RMSE < 2.5 points
- API response time < 200ms (p95)
- Model accuracy calibration

## Database Models

### Core Models
- **Team**: Premier League teams
- **Player**: Player data and statistics
- **GameWeek**: Fixture schedule and deadlines
- **Fixture**: Match data
- **PlayerGameWeekStats**: Weekly performance

### ML Models
- **MLModel**: Trained model metadata (version, metrics, artifacts)
- **OptimalTeam**: Optimized teams (cost, predicted points)
- **OptimalTeamPlayer**: Team squad (captain, starting XI)

## Configuration

### Environment Variables
```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost/fpl_db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
MLFLOW_TRACKING_URI=file:///mlruns
FPL_API_BASE_URL=https://fantasy.premierleague.com/api/
DEBUG=True
SECRET_KEY=your-secret-key
```

### Django Settings
Update `fpl_project/settings.py`:
- `DATABASES`: Configure PostgreSQL for production
- `ALLOWED_HOSTS`: Add your domain
- `CELERY_BROKER_URL`: Redis connection
- `MLFLOW_TRACKING_URI`: MLflow server (optional)

## Testing

### Run Unit Tests
```bash
python manage.py test fpl_app
```

### Run with Coverage
```bash
coverage run --source='.' manage.py test fpl_app
coverage report
```

### Test Specific Module
```bash
python -m pytest fpl_app/tests.py::test_rolling_average -v
```

## Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Gunicorn Production Server
```bash
gunicorn fpl_project.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Nginx Configuration
```nginx
upstream fpl_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://fpl_app;
    }
}
```

## Monitoring & Logging

### Logs
- Celery task logs: `celery.log`
- Application logs: Configured in `settings.py`
- API access: Django logging

### Metrics
- Model performance: MLflow UI (`http://localhost:5000` if using MLflow server)
- Task status: Celery Flower (`celery -A fpl_project events --port 5555`)
- API metrics: Django Debug Toolbar (dev only)

## Performance Optimization

### Caching
```python
# Redis caching for predictions
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache for 5 minutes
def player_predictions(request, player_id):
    ...
```

### Database Optimization
- Indexing on frequently queried fields
- Connection pooling with django-db-pool
- Query optimization with `select_related` and `prefetch_related`

### Async Task Processing
- Long-running tasks via Celery
- Model retraining scheduled weekly
- Data fetching hourly

## Troubleshooting

### Redis Connection Error
```bash
# Start Redis (if not running)
redis-server
```

### Celery Tasks Not Running
```bash
# Check Celery worker status
celery -A fpl_project inspect active

# Clear task queue
celery -A fpl_project purge
```

### Model Not Found Error
```bash
# Trigger retraining to create initial model
POST /api/models/retrain/
```

### Database Migration Issues
```bash
python manage.py migrate --fake-initial
python manage.py migrate
```

## Development Roadmap

### Phase 1 (Complete)
- ✅ Data fetching and validation
- ✅ Feature engineering
- ✅ ML model training
- ✅ Team optimization
- ✅ API endpoints
- ✅ Celery background jobs

### Phase 2 (In Progress)
- Transfer recommendations
- Captain selector model
- Advanced analytics dashboard

### Phase 3 (Planned)
- Real-time updates (WebSockets)
- Mobile app
- User authentication & authorization
- League-specific insights

## Security

- JWT authentication (add djangorestframework-simplejwt)
- Rate limiting (add django-ratelimit)
- Input validation & sanitization
- CORS configuration
- Secret key management via environment variables

## Contributing

1. Create feature branch
2. Make changes with tests
3. Run `python manage.py test`
4. Submit pull request

## License

MIT License - See LICENSE file

## Support

For issues or questions:
- Create GitHub issue
- Check documentation
- Review API examples
