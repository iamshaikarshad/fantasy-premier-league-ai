"""
FPL Data Fetcher - Fetch and validate data from FPL API.
"""
import httpx
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

FPL_API_BASE = 'https://fantasy.premierleague.com/api/'


def fetch_bootstrap_data():
    """Fetch bootstrap-static data from FPL API."""
    try:
        url = f"{FPL_API_BASE}bootstrap-static/"
        response = httpx.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch bootstrap data: {e}")
        return None


def fetch_player_history(player_id: int):
    """Fetch historical data for a specific player."""
    try:
        url = f"{FPL_API_BASE}element-summary/{player_id}/"
        response = httpx.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch history for player {player_id}: {e}")
        return None


def fetch_fixtures():
    """Fetch all fixtures data."""
    try:
        url = f"{FPL_API_BASE}fixtures/"
        response = httpx.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch fixtures: {e}")
        return None


def validate_player_data(player_data):
    """Validate player data for completeness."""
    required_fields = [
        'id', 'web_name', 'element_type', 'team', 
        'now_cost', 'total_points', 'minutes'
    ]
    for field in required_fields:
        if field not in player_data:
            return False
    return True


def validate_gameweek_data(gw_data):
    """Validate gameweek data."""
    required_fields = ['id', 'name', 'deadline_time', 'is_current', 'is_finished']
    for field in required_fields:
        if field not in gw_data:
            return False
    return True
