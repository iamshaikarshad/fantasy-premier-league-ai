"""
Team Optimizer - Optimize team selection using Linear Programming.
"""
import logging
from pulp import *
import pandas as pd

logger = logging.getLogger(__name__)

# FPL Constraints
TOTAL_BUDGET = 100.0  # £100M
TOTAL_PLAYERS = 15
STARTING_PLAYERS = 11
MIN_GOALKEEPERS = 1
MAX_GOALKEEPERS = 1
MIN_DEFENDERS = 3
MAX_DEFENDERS = 5
MIN_MIDFIELDERS = 2
MAX_MIDFIELDERS = 5
MIN_FORWARDS = 1
MAX_FORWARDS = 3
MAX_PER_TEAM = 3


def optimize_team(players_df, predicted_points_col='predicted_points'):
    """
    Optimize team selection using Linear Programming.
    
    Args:
        players_df: DataFrame with columns [player_id, position, price, predicted_points, team_id]
        predicted_points_col: Column name for predicted points
    
    Returns:
        Dict with optimal team, total cost, and predicted points
    """
    
    # Create LP problem
    prob = LpProblem("FPL_Team_Optimizer", LpMaximize)
    
    # Decision variables
    player_vars = {}
    for idx, row in players_df.iterrows():
        player_id = row['player_id']
        player_vars[player_id] = LpVariable(f"player_{player_id}", cat='Binary')
    
    # Objective: maximize predicted points
    prob += lpSum([
        player_vars[row['player_id']] * row[predicted_points_col]
        for idx, row in players_df.iterrows()
    ]), "Total_Points"
    
    # Constraint 1: Total budget
    prob += lpSum([
        player_vars[row['player_id']] * row['price']
        for idx, row in players_df.iterrows()
    ]) <= TOTAL_BUDGET, "Budget"
    
    # Constraint 2: Total players
    prob += lpSum([player_vars[pid] for pid in player_vars]) == TOTAL_PLAYERS, "Total_Players"
    
    # Constraint 3: Position constraints
    gk_players = players_df[players_df['position'] == 1]['player_id'].tolist()
    prob += lpSum([player_vars[pid] for pid in gk_players]) == MIN_GOALKEEPERS, "Goalkeepers"
    
    def_players = players_df[players_df['position'] == 2]['player_id'].tolist()
    prob += lpSum([player_vars[pid] for pid in def_players]) >= MIN_DEFENDERS, "Min_Defenders"
    prob += lpSum([player_vars[pid] for pid in def_players]) <= MAX_DEFENDERS, "Max_Defenders"
    
    mid_players = players_df[players_df['position'] == 3]['player_id'].tolist()
    prob += lpSum([player_vars[pid] for pid in mid_players]) >= MIN_MIDFIELDERS, "Min_Midfielders"
    prob += lpSum([player_vars[pid] for pid in mid_players]) <= MAX_MIDFIELDERS, "Max_Midfielders"
    
    fwd_players = players_df[players_df['position'] == 4]['player_id'].tolist()
    prob += lpSum([player_vars[pid] for pid in fwd_players]) >= MIN_FORWARDS, "Min_Forwards"
    prob += lpSum([player_vars[pid] for pid in fwd_players]) <= MAX_FORWARDS, "Max_Forwards"
    
    # Constraint 4: Max 3 players per team
    teams = players_df['team_id'].unique()
    for team_id in teams:
        team_players = players_df[players_df['team_id'] == team_id]['player_id'].tolist()
        prob += lpSum([player_vars[pid] for pid in team_players]) <= MAX_PER_TEAM, f"Team_{team_id}"
    
    # Solve
    prob.solve(PULP_CBC_CMD(msg=0))
    
    # Extract solution
    selected_players = []
    total_cost = 0
    total_points = 0
    
    for idx, row in players_df.iterrows():
        player_id = row['player_id']
        if player_vars[player_id].varValue == 1:
            selected_players.append({
                'player_id': player_id,
                'player_name': row.get('player_name', ''),
                'position': row['position'],
                'price': row['price'],
                'predicted_points': row[predicted_points_col]
            })
            total_cost += row['price']
            total_points += row[predicted_points_col]
    
    return {
        'status': LpStatus[prob.status],
        'selected_players': selected_players,
        'total_cost': total_cost,
        'total_predicted_points': total_points,
        'num_players': len(selected_players)
    }


def get_transfer_suggestions(current_team_df, all_players_df, max_suggestions=5):
    """Get transfer suggestions to improve team."""
    current_ids = set(current_team_df['player_id'].tolist())
    
    # Players not in current team but available
    available = all_players_df[~all_players_df['player_id'].isin(current_ids)].copy()
    
    suggestions = []
    for idx, current_player in current_team_df.iterrows():
        # Find best replacement in same position
        same_pos = available[available['position'] == current_player['position']].copy()
        same_pos['points_diff'] = same_pos['predicted_points'] - current_player['predicted_points']
        same_pos['cost_diff'] = same_pos['price'] - current_player['price']
        same_pos['value'] = same_pos['points_diff'] - (same_pos['cost_diff'] * 0.1)
        
        if not same_pos.empty:
            best = same_pos.nlargest(1, 'value').iloc[0]
            if best['value'] > 0.5:  # Only suggest if significant improvement
                suggestions.append({
                    'out': current_player['player_name'],
                    'in': best['player_name'],
                    'points_gain': float(best['points_diff']),
                    'cost_impact': float(best['cost_diff']),
                    'net_value': float(best['value'])
                })
    
    return sorted(suggestions, key=lambda x: x['net_value'], reverse=True)[:max_suggestions]
