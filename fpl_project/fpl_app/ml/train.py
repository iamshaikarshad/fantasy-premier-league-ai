"""
Training Module - Train ML models with LightGBM and Optuna.
"""
import logging
import joblib
import mlflow
import pandas as pd
import numpy as np
import lightgbm as lgb
import optuna
from optuna.integration import LightGBMPruningCallback
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from pathlib import Path
from fpl_app.ml.features import (
    create_player_features_dataframe, 
    get_feature_columns_for_model
)

logger = logging.getLogger(__name__)

# Model storage
MODELS_DIR = Path(__file__).parent.parent.parent / 'models'
MODELS_DIR.mkdir(exist_ok=True)


def train_lightgbm_model(X_train, y_train, X_val, y_val, trial=None):
    """Train a LightGBM model with optional Optuna trial."""
    params = {
        'objective': 'regression',
        'metric': 'rmse',
        'verbosity': -1,
        'seed': 42,
    }
    
    # If trial provided, use for hyperparameter tuning
    if trial:
        params['num_leaves'] = trial.suggest_int('num_leaves', 20, 150)
        params['max_depth'] = trial.suggest_int('max_depth', 3, 12)
        params['learning_rate'] = trial.suggest_float('learning_rate', 0.01, 0.3)
        params['lambda_l1'] = trial.suggest_float('lambda_l1', 0.0, 10.0)
        params['lambda_l2'] = trial.suggest_float('lambda_l2', 0.0, 10.0)
    
    train_data = lgb.Dataset(X_train, label=y_train)
    valid_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
    
    callbacks = [lgb.early_stopping(20)]
    if trial:
        callbacks.append(LightGBMPruningCallback(trial, 'rmse'))
    
    model = lgb.train(
        params,
        train_data,
        valid_sets=[valid_data],
        num_boost_round=200,
        callbacks=callbacks
    )
    
    return model


def evaluate_model(model, X_val, y_val):
    """Evaluate model performance."""
    preds = model.predict(X_val)
    mse = mean_squared_error(y_val, preds)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_val, preds)
    r2 = r2_score(y_val, preds)
    
    return {
        'rmse': float(rmse),
        'mae': float(mae),
        'r2': float(r2)
    }


def optimize_hyperparameters(X_train, y_train, X_val, y_val, n_trials=20):
    """Optimize hyperparameters using Optuna."""
    def objective(trial):
        model = train_lightgbm_model(X_train, y_train, X_val, y_val, trial)
        preds = model.predict(X_val)
        mse = mean_squared_error(y_val, preds)
        rmse = np.sqrt(mse)
        return rmse
    
    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    
    return study.best_params


def train_and_save_model(X_train, y_train, X_val, y_val, model_name='points_predictor', tune=False):
    """Train and save a model."""
    mlflow.set_experiment('fpl_optimizer')
    
    with mlflow.start_run():
        # Hyperparameter tuning
        best_params = {}
        if tune:
            logger.info("Starting hyperparameter optimization...")
            best_params = optimize_hyperparameters(X_train, y_train, X_val, y_val, n_trials=10)
            mlflow.log_params(best_params)
        
        # Train final model
        logger.info("Training final model...")
        model = train_lightgbm_model(X_train, y_train, X_val, y_val)
        
        # Evaluate
        metrics = evaluate_model(model, X_val, y_val)
        for metric_name, metric_value in metrics.items():
            mlflow.log_metric(metric_name, metric_value)
        
        # Feature importance
        feature_importance = model.feature_importance(importance_type='gain')
        feature_names = X_train.columns.tolist()
        importance_dict = {name: int(imp) for name, imp in zip(feature_names, feature_importance)}
        mlflow.log_dict(importance_dict, 'feature_importance.json')
        
        # Save model
        model_path = MODELS_DIR / f'{model_name}_model.joblib'
        joblib.dump(model, str(model_path))
        mlflow.log_artifact(str(model_path))
        
        logger.info(f"Model saved to {model_path}")
        logger.info(f"Metrics: {metrics}")
        
        return {
            'model_path': str(model_path),
            'metrics': metrics,
            'feature_importance': importance_dict
        }


def create_synthetic_training_data(n_samples=100):
    """Create synthetic data for testing."""
    feature_cols = get_feature_columns_for_model()
    X = pd.DataFrame(
        np.random.randn(n_samples, len(feature_cols)),
        columns=feature_cols
    )
    # Synthetic target: weighted combination of features
    y = (
        X['points_last3_avg'] * 0.3 +
        X['form'] * 0.2 +
        X['influence'] * 0.1 +
        X['threat'] * 0.15 +
        np.random.randn(n_samples) * 0.5
    ).clip(0, 20)
    
    return X, y
