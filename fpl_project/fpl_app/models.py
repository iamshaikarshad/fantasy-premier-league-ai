from django.db import models
from django.utils import timezone

class Team(models.Model):
    team_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=10)
    strength = models.IntegerField(default=3)
    strength_overall_home = models.IntegerField(default=1000)
    strength_overall_away = models.IntegerField(default=1000)
    strength_attack_home = models.IntegerField(default=1000)
    strength_attack_away = models.IntegerField(default=1000)
    strength_defence_home = models.IntegerField(default=1000)
    strength_defence_away = models.IntegerField(default=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Player(models.Model):
    POSITION_CHOICES = [
        ('GKP', 'Goalkeeper'),
        ('DEF', 'Defender'),
        ('MID', 'Midfielder'),
        ('FWD', 'Forward'),
    ]

    player_id = models.IntegerField(unique=True)
    web_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    second_name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    position = models.CharField(max_length=3, choices=POSITION_CHOICES)
    
    # Current stats
    now_cost = models.DecimalField(max_digits=4, decimal_places=1)
    total_points = models.IntegerField(default=0)
    form = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    points_per_game = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    selected_by_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    
    # Performance stats
    minutes = models.IntegerField(default=0)
    goals_scored = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    clean_sheets = models.IntegerField(default=0)
    goals_conceded = models.IntegerField(default=0)
    own_goals = models.IntegerField(default=0)
    penalties_saved = models.IntegerField(default=0)
    penalties_missed = models.IntegerField(default=0)
    yellow_cards = models.IntegerField(default=0)
    red_cards = models.IntegerField(default=0)
    saves = models.IntegerField(default=0)
    bonus = models.IntegerField(default=0)
    bps = models.IntegerField(default=0)
    
    # Advanced stats
    influence = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    creativity = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    threat = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    ict_index = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    expected_goals = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    expected_assists = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    expected_goal_involvements = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    expected_goals_conceded = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    
    # Status
    status = models.CharField(max_length=1, default='a')  # a=available, d=doubtful, i=injured, u=unavailable
    chance_of_playing_next_round = models.IntegerField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-total_points']

    def __str__(self):
        return f"{self.web_name} ({self.team.short_name})"


class GameWeek(models.Model):
    gameweek_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)
    deadline_time = models.DateTimeField()
    is_current = models.BooleanField(default=False)
    is_next = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['gameweek_id']

    def __str__(self):
        return self.name


class PlayerGameWeekStats(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='gameweek_stats')
    gameweek = models.ForeignKey(GameWeek, on_delete=models.CASCADE)
    
    minutes = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    goals_scored = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    clean_sheets = models.IntegerField(default=0)
    goals_conceded = models.IntegerField(default=0)
    own_goals = models.IntegerField(default=0)
    penalties_saved = models.IntegerField(default=0)
    penalties_missed = models.IntegerField(default=0)
    yellow_cards = models.IntegerField(default=0)
    red_cards = models.IntegerField(default=0)
    saves = models.IntegerField(default=0)
    bonus = models.IntegerField(default=0)
    bps = models.IntegerField(default=0)
    
    influence = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    creativity = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    threat = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    ict_index = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    
    expected_goals = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    expected_assists = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    expected_goal_involvements = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    expected_goals_conceded = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    
    value = models.DecimalField(max_digits=4, decimal_places=1)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['player', 'gameweek']
        ordering = ['-gameweek__gameweek_id', '-total_points']

    def __str__(self):
        return f"{self.player.web_name} - GW{self.gameweek.gameweek_id}"


class Fixture(models.Model):
    fixture_id = models.IntegerField(unique=True)
    gameweek = models.ForeignKey(GameWeek, on_delete=models.CASCADE, related_name='fixtures')
    team_h = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_fixtures')
    team_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_fixtures')
    
    kickoff_time = models.DateTimeField()
    is_finished = models.BooleanField(default=False)
    
    team_h_score = models.IntegerField(null=True)
    team_a_score = models.IntegerField(null=True)
    team_h_difficulty = models.IntegerField()
    team_a_difficulty = models.IntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['kickoff_time']

    def __str__(self):
        return f"{self.team_h.short_name} vs {self.team_a.short_name}"


class MLModel(models.Model):
    MODEL_TYPES = [
        ('points_predictor', 'Points Predictor'),
        ('team_optimizer', 'Team Optimizer'),
        ('captain_selector', 'Captain Selector'),
    ]

    name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPES)
    version = models.CharField(max_length=20)
    
    mlflow_run_id = models.CharField(max_length=100, unique=True)
    mlflow_experiment_id = models.CharField(max_length=100)
    
    accuracy_score = models.DecimalField(max_digits=5, decimal_places=4, null=True)
    rmse = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    mae = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    
    is_active = models.BooleanField(default=False)
    trained_at = models.DateTimeField(auto_now_add=True)
    
    training_params = models.JSONField(default=dict)
    feature_importance = models.JSONField(default=dict)

    class Meta:
        ordering = ['-trained_at']

    def __str__(self):
        return f"{self.name} v{self.version}"


class OptimalTeam(models.Model):
    gameweek = models.ForeignKey(GameWeek, on_delete=models.CASCADE)
    model = models.ForeignKey(MLModel, on_delete=models.SET_NULL, null=True)
    
    players = models.ManyToManyField(Player, through='OptimalTeamPlayer')
    
    total_cost = models.DecimalField(max_digits=5, decimal_places=1)
    predicted_points = models.DecimalField(max_digits=6, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-gameweek__gameweek_id', '-predicted_points']

    def __str__(self):
        return f"Optimal Team for GW{self.gameweek.gameweek_id}"


class OptimalTeamPlayer(models.Model):
    team = models.ForeignKey(OptimalTeam, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    
    is_captain = models.BooleanField(default=False)
    is_vice_captain = models.BooleanField(default=False)
    is_starting = models.BooleanField(default=True)
    position_order = models.IntegerField()
    
    predicted_points = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ['team', '-is_starting', 'position_order']

    def __str__(self):
        return f"{self.player.web_name} in {self.team}"

print("Django models created successfully!")
print("\nNext steps:")
print("1. Create migrations: python manage.py makemigrations")
print("2. Apply migrations: python manage.py migrate")
print("3. Check the artifact for the complete project structure")
