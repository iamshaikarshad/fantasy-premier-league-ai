# Quick Start Guide - FPL Optimizer

Get up and running with the FPL Optimizer in 5 minutes!

## Option 1: Local Development (Recommended for Development)

### Step 1: Setup Python Environment
```powershell
cd fpl_project
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 2: Initialize Database
```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Step 3: Bootstrap FPL Data & Train Model
```powershell
python manage.py bootstrap_fpl
```

This command will:
- Fetch FPL teams, players, and gameweeks
- Train an initial ML model
- Prepare the application for use

### Step 4: Start Redis (Required for Celery)
```powershell
# Make sure Redis is installed or use:
docker run -d -p 6379:6379 redis:7-alpine
```

### Step 5: Start Services (3 separate terminals)

**Terminal 1 - Django Dev Server:**
```powershell
python manage.py runserver
```
👉 Access at: http://localhost:8000

**Terminal 2 - Celery Worker:**
```powershell
celery -A fpl_project worker -l info
```

**Terminal 3 - Celery Beat (Scheduler):**
```powershell
celery -A fpl_project beat -l info
```

### Step 6: Access the Application

- **API**: http://localhost:8000/api/
- **Admin**: http://localhost:8000/admin/ (use superuser credentials)
- **API Docs**: http://localhost:8000/api/players/ (browse API)

---

## Option 2: Docker Deployment (Recommended for Production)

### Step 1: Build and Run
```powershell
cd fpl_project
docker-compose up -d
```

### Step 2: Initialize Database
```powershell
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py bootstrap_fpl
```

### Step 3: Access Services

- **API**: http://localhost:8000
- **Admin**: http://localhost:8000/admin/
- **Redis**: localhost:6379
- **Database**: postgresql://fpl_user:fpl_pass@localhost:5432/fpl_optimizer

### View Logs
```powershell
docker-compose logs -f web
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat
```

### Stop Services
```powershell
docker-compose down
```

---

## Testing the API

### 1. Get All Players
```bash
curl http://localhost:8000/api/players/
```

### 2. Get Player Predictions
```bash
curl http://localhost:8000/api/players/1/predictions/
```

### 3. Trigger Model Retraining
```bash
curl -X POST http://localhost:8000/api/models/retrain/ \
  -H "Content-Type: application/json" \
  -d '{"model_type":"points_predictor"}'
```

### 4. Optimize Team
```bash
curl -X POST http://localhost:8000/api/teams/optimize/ \
  -H "Content-Type: application/json" \
  -d '{"gameweek_id":1,"budget":100.0,"auto_captain":true}'
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError" or import errors
**Solution:**
```powershell
pip install -r requirements.txt
```

### Issue: "Connection refused" for Redis
**Solution:**
- Install and start Redis, or use Docker:
```powershell
docker run -d -p 6379:6379 redis:7-alpine
```

### Issue: Database migration errors
**Solution:**
```powershell
python manage.py migrate --fake-initial
python manage.py migrate
```

### Issue: Model not found error
**Solution:**
```powershell
python manage.py bootstrap_fpl
# or
curl -X POST http://localhost:8000/api/models/retrain/
```

### Issue: Celery tasks not running
**Solution:**
1. Check Redis is running: `redis-cli ping` (should return "PONG")
2. Restart Celery worker
3. Check logs: `celery -A fpl_project worker -l debug`

### Issue: Migrations conflict
**Solution:**
```powershell
python manage.py makemigrations --merge
python manage.py migrate
```

---

## Directory Structure

```
fpl_project/
├── fpl_project/           # Django project config
│   ├── settings.py        # Configuration
│   ├── urls.py            # URL routing
│   ├── celery.py          # Celery setup
│   └── wsgi.py            # WSGI app
├── fpl_app/               # Main app
│   ├── ml/
│   │   ├── data_fetcher.py    # FPL API interface
│   │   ├── features.py        # Feature engineering
│   │   ├── train.py           # Model training
│   │   └── optimizer.py       # Team optimizer
│   ├── models.py          # Database models
│   ├── views.py           # API views
│   ├── serializers.py     # DRF serializers
│   ├── tasks.py           # Celery tasks
│   ├── urls.py            # App URLs
│   └── tests.py           # Unit tests
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
├── API_DOCUMENTATION.md
└── QUICKSTART.md
```

---

## Key Features

### 🏆 Team Optimization
Automatically select 15 players that maximize predicted points while respecting FPL constraints:
- £100M budget
- 1 GK, 3-5 DEF, 2-5 MID, 1-3 FWD
- Max 3 players per team
- Captain & Vice-captain support

### 🤖 ML Predictions
LightGBM model predicts next gameweek points based on:
- Historical performance
- Form indicators
- Advanced stats (xG, xA, ICT index)
- Fixture difficulty
- Player ownership

### ⏰ Automated Jobs
Celery Beat scheduler runs:
- Hourly data fetches
- Weekly model retraining
- Daily performance calculations
- User notifications

### 📊 Admin Dashboard
Django admin panel provides:
- Player management
- Model version tracking
- Performance metrics
- Team optimization history

---

## Next Steps

1. **Explore the API**: Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed endpoints
2. **Configure Settings**: Update `settings.py` for production
3. **Add Authentication**: Install `djangorestframework-simplejwt`
4. **Deploy**: Use the Docker setup for production
5. **Monitor**: Setup MLflow or Prometheus for monitoring

---

## Useful Commands

### Django
```powershell
# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Run tests
python manage.py test

# Bootstrap data
python manage.py bootstrap_fpl

# Clear cache
python manage.py shell
# Then: from django.core.cache import cache; cache.clear()

# Database shell
python manage.py dbshell
```

### Celery
```powershell
# Check active tasks
celery -A fpl_project inspect active

# Purge all tasks
celery -A fpl_project purge

# Monitor tasks in real-time
celery -A fpl_project events --port 5555
# (Open http://localhost:5555 in browser)

# Flower (Web UI for Celery)
pip install flower
celery -A fpl_project flower
# (Open http://localhost:5555 in browser)
```

### Docker
```powershell
# View logs
docker-compose logs -f

# Access shell
docker-compose exec web python manage.py shell

# Run command in container
docker-compose exec web python manage.py bootstrap_fpl

# Rebuild images
docker-compose build

# Clean up
docker-compose down -v
```

---

## Development Tips

### 1. Use ipdb for Debugging
```python
# In any Python file
import ipdb; ipdb.set_trace()
```

### 2. Django Shell
```powershell
python manage.py shell
# Then:
from fpl_app.models import Player
Player.objects.count()
```

### 3. Test API Endpoints
```bash
# Using httpie (easier than curl)
pip install httpie
http GET localhost:8000/api/players/
http POST localhost:8000/api/models/retrain/ model_type=points_predictor
```

### 4. Check Database
```powershell
python manage.py dbshell
# Then SQL queries
SELECT * FROM fpl_app_player LIMIT 5;
```

---

## Performance Tips

1. **Enable Caching**: Redis caching for frequently accessed endpoints
2. **Database Indexing**: Already configured for common queries
3. **Async Tasks**: Long operations run in Celery background
4. **Pagination**: All list endpoints paginated (default 100 items)
5. **Select Related**: API uses `select_related` for foreign keys

---

## Production Checklist

- [ ] Set `DEBUG = False` in settings
- [ ] Set `SECRET_KEY` to random value
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Switch to PostgreSQL database
- [ ] Enable HTTPS (nginx + SSL)
- [ ] Setup error monitoring (Sentry)
- [ ] Configure MLflow for model tracking
- [ ] Setup automated backups
- [ ] Enable rate limiting
- [ ] Setup monitoring (Prometheus, Grafana)

---

## Support & Documentation

- **README.md**: Comprehensive project documentation
- **API_DOCUMENTATION.md**: Detailed API reference
- **Django Docs**: https://docs.djangoproject.com/
- **DRF Docs**: https://www.django-rest-framework.org/
- **LightGBM**: https://lightgbm.readthedocs.io/
- **Celery**: https://docs.celeryproject.io/

---

**🚀 You're all set! Start building amazing FPL insights!**
