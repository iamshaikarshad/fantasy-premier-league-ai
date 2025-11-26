# FPL Optimizer - API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication
Currently using session authentication (development). Add JWT tokens for production.

---

## Players Endpoints

### List Players
```
GET /api/players/
```

**Query Parameters:**
- `position`: Filter by position (GKP, DEF, MID, FWD)
- `team`: Filter by team ID
- `status`: Filter by status (a=available, i=injured, d=doubtful, u=unavailable)
- `search`: Search by name
- `ordering`: Sort by field (-total_points, now_cost, form)
- `page`: Pagination

**Example:**
```bash
curl "http://localhost:8000/api/players/?position=MID&ordering=-form&page=1"
```

**Response:**
```json
{
  "count": 245,
  "next": "http://localhost:8000/api/players/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "player_id": 1,
      "web_name": "Mohamed Salah",
      "team": {
        "id": 14,
        "team_id": 14,
        "name": "Liverpool",
        "short_name": "LIV",
        "strength": 4
      },
      "position": "MID",
      "now_cost": 13.5,
      "total_points": 285,
      "form": "8.5",
      "points_per_game": "6.2",
      "selected_by_percent": "75.5",
      "minutes": 2700,
      "status": "a"
    }
  ]
}
```

---

### Get Player Details
```
GET /api/players/{id}/
```

**Example:**
```bash
curl http://localhost:8000/api/players/1/
```

---

### Get Player Predictions
```
GET /api/players/{id}/predictions/?gw=1
```

**Query Parameters:**
- `gw`: Gameweek number (optional, default=1)

**Response:**
```json
{
  "player_id": 1,
  "player_name": "Mohamed Salah",
  "predicted_points": 8.5,
  "confidence": 0.75
}
```

---

## Gameweek Endpoints

### List Gameweeks
```
GET /api/gameweeks/
```

**Response:**
```json
{
  "count": 38,
  "results": [
    {
      "id": 1,
      "gameweek_id": 1,
      "name": "Gameweek 1",
      "deadline_time": "2024-08-16T18:30:00Z",
      "is_current": true,
      "is_finished": false
    }
  ]
}
```

---

### Get Current Gameweek
```
GET /api/gameweeks/current/
```

**Response:**
```json
{
  "id": 1,
  "gameweek_id": 1,
  "name": "Gameweek 1",
  "deadline_time": "2024-08-16T18:30:00Z",
  "is_current": true,
  "is_finished": false
}
```

---

## ML Model Endpoints

### List Models
```
GET /api/models/
```

**Query Parameters:**
- `model_type`: Filter by type (points_predictor, team_optimizer, captain_selector)
- `is_active`: Filter by active status

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "points_predictor_v1.0",
      "model_type": "points_predictor",
      "version": "1.0.0",
      "accuracy_score": 0.8234,
      "rmse": 2.15,
      "mae": 1.67,
      "is_active": true,
      "trained_at": "2024-08-15T10:30:00Z"
    }
  ]
}
```

---

### Get Model Metrics
```
GET /api/models/metrics/
```

**Response:**
```json
{
  "model_id": 1,
  "rmse": 2.15,
  "mae": 1.67,
  "accuracy": 0.8234
}
```

---

### Trigger Model Retraining
```
POST /api/models/retrain/
```

**Request Body:**
```json
{
  "model_type": "points_predictor"
}
```

**Response:**
```json
{
  "task_id": "abc123xyz-def456",
  "status": "retraining_started",
  "model_type": "points_predictor"
}
```

**Task Status Check:**
```bash
curl http://localhost:8000/api/tasks/{task_id}/status/
```

---

## Team Optimization Endpoints

### List Optimal Teams
```
GET /api/teams/
```

**Query Parameters:**
- `gameweek`: Filter by gameweek ID

**Response:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "gameweek": {
        "id": 1,
        "gameweek_id": 1,
        "name": "Gameweek 1",
        "deadline_time": "2024-08-16T18:30:00Z",
        "is_current": true,
        "is_finished": false
      },
      "model": {
        "id": 1,
        "name": "points_predictor_v1.0",
        "model_type": "points_predictor",
        "version": "1.0.0"
      },
      "players": [
        {
          "player": {
            "id": 1,
            "player_id": 1,
            "web_name": "Alisson",
            "position": "GKP",
            "now_cost": 5.8
          },
          "is_captain": false,
          "is_vice_captain": false,
          "is_starting": true,
          "predicted_points": 5.2
        }
      ],
      "total_cost": 99.8,
      "predicted_points": 65.3,
      "created_at": "2024-08-15T10:30:00Z"
    }
  ]
}
```

---

### Optimize New Team
```
POST /api/teams/optimize/
```

**Request Body:**
```json
{
  "gameweek_id": 1,
  "budget": 100.0,
  "auto_captain": true
}
```

**Response:**
```json
{
  "task_id": "def456abc-ghi789",
  "status": "optimization_started",
  "gameweek_id": 1
}
```

**Poll for Results:**
```bash
curl http://localhost:8000/api/teams/{id}/
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid parameters",
  "errors": {
    "gameweek_id": ["This field is required."]
  }
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "detail": "An error occurred",
  "error_code": "MODEL_NOT_TRAINED"
}
```

---

## Rate Limiting

Endpoints are rate-limited to prevent abuse:
- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1629036000
```

---

## Caching

GET endpoints implement caching:
- `/api/players/`: Cached for 5 minutes
- `/api/gameweeks/`: Cached for 1 hour
- Predictions: Cached for 10 minutes

Clear cache:
```bash
curl -X POST http://localhost:8000/api/cache/clear/
```

---

## Pagination

Default page size: 100 results

```bash
# Get page 2
curl "http://localhost:8000/api/players/?page=2"

# Custom page size (max 100)
curl "http://localhost:8000/api/players/?page=1&page_size=50"
```

---

## Filtering & Searching

### Filter by Multiple Values
```bash
# Multiple teams
curl "http://localhost:8000/api/players/?team=1&team=2"

# Multiple positions
curl "http://localhost:8000/api/players/?position=MID&position=FWD"
```

### Search
```bash
curl "http://localhost:8000/api/players/?search=salah"
```

### Ordering
```bash
# Ascending
curl "http://localhost:8000/api/players/?ordering=now_cost"

# Descending
curl "http://localhost:8000/api/players/?ordering=-total_points"
```

---

## Useful Examples

### Get Best Value Midfielders
```bash
curl "http://localhost:8000/api/players/?position=MID&ordering=now_cost&page_size=10"
```

### Get Highest Scoring Forwards
```bash
curl "http://localhost:8000/api/players/?position=FWD&ordering=-total_points&page_size=5"
```

### Get Players in Good Form
```bash
curl "http://localhost:8000/api/players/?ordering=-form&page_size=20"
```

### Predict Points for Top 5 Players
```bash
curl http://localhost:8000/api/players/1/predictions/ \
curl http://localhost:8000/api/players/2/predictions/ \
curl http://localhost:8000/api/players/3/predictions/ \
curl http://localhost:8000/api/players/4/predictions/ \
curl http://localhost:8000/api/players/5/predictions/
```

---

## Webhooks & Events

Async tasks emit events:

### Model Retraining Complete
```json
{
  "event": "model_retrained",
  "model_type": "points_predictor",
  "version": "1.0.1",
  "metrics": {
    "rmse": 2.12,
    "mae": 1.65
  },
  "timestamp": "2024-08-15T12:00:00Z"
}
```

### Team Optimization Complete
```json
{
  "event": "team_optimized",
  "gameweek_id": 1,
  "total_predicted_points": 65.3,
  "total_cost": 99.8,
  "timestamp": "2024-08-15T12:00:00Z"
}
```

---

## API Client Examples

### Python
```python
import requests

# Get players
response = requests.get('http://localhost:8000/api/players/')
players = response.json()

# Get predictions for player
response = requests.get('http://localhost:8000/api/players/1/predictions/')
prediction = response.json()

# Optimize team
response = requests.post('http://localhost:8000/api/teams/optimize/', 
    json={'gameweek_id': 1, 'budget': 100.0})
task_id = response.json()['task_id']
```

### JavaScript (Fetch)
```javascript
// Get players
fetch('http://localhost:8000/api/players/')
  .then(r => r.json())
  .then(data => console.log(data));

// Get predictions
fetch('http://localhost:8000/api/players/1/predictions/')
  .then(r => r.json())
  .then(data => console.log(data));
```

### cURL
```bash
# Get players
curl http://localhost:8000/api/players/

# Get player predictions
curl http://localhost:8000/api/players/1/predictions/

# Optimize team
curl -X POST http://localhost:8000/api/teams/optimize/ \
  -H "Content-Type: application/json" \
  -d '{"gameweek_id": 1, "budget": 100.0}'
```

---

## Support

For API issues or documentation updates:
- Create GitHub issue
- Check Django logs: `tail -f logs/django.log`
- Check API server status: `GET /health/`
