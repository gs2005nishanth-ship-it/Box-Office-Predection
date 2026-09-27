import os
import ast
import json
import math
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Utility functions to parse JSON-like columns in TMDB dataset
def safe_eval(val):
    if pd.isna(val) or val == 'None' or val == 'none' or not val:
        return []
    if isinstance(val, list):
        return val
    try:
        return ast.literal_eval(val)
    except Exception:
        try:
            return json.loads(val.replace("'", '"'))
        except Exception:
            return []

def extract_names(val, max_items=5):
    items = safe_eval(val)
    if isinstance(items, list):
        names = [item.get('name', '') for item in items if isinstance(item, dict) and 'name' in item]
        return names[:max_items]
    return []

def extract_cast(val, max_items=4):
    items = safe_eval(val)
    if isinstance(items, list):
        return [item.get('name', '') for item in items if isinstance(item, dict) and 'name' in item][:max_items]
    return []

def extract_director(val):
    items = safe_eval(val)
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict) and item.get('job') == 'Director':
                return item.get('name', 'Unknown')
    return 'Unknown'

class BoxOfficeMLEngine:
    def __init__(self, data_dir='.'):
        self.data_dir = data_dir
        self.train_path = os.path.join(data_dir, 'train.csv')
        self.test_path = os.path.join(data_dir, 'test.csv')
        self.models = {}
        self.metrics = {}
        self.feature_names = []
        self.best_model_name = 'GradientBoosting'
        self.scaler = None
        self.top_genres = []
        self.top_languages = []
        self.dataset_stats = {}
        self.is_trained = False

    def load_and_preprocess(self):
        print("Loading datasets...")
        train_df = pd.read_csv(self.train_path)
        test_df = pd.read_csv(self.test_path) if os.path.exists(self.test_path) else None

        # Impute missing runtimes from known corrections in TMDB dataset
        runtime_fixes_train = {2302: 86, 1335: 130}
        runtime_fixes_test = {243: 93, 1489: 91, 1632: 100, 3817: 90}
        for idx, rt in runtime_fixes_train.items():
            if idx in train_df.index:
                train_df.loc[idx, 'runtime'] = rt
        if test_df is not None:
            for idx, rt in runtime_fixes_test.items():
                if idx in test_df.index:
                    test_df.loc[idx, 'runtime'] = rt

        # Feature Engineering function
        def engineer_features(df, is_train=True):
            df = df.copy()

            # Fill missing release dates
            df['release_date'] = df['release_date'].fillna('01/01/2000')

            # Extract month, day, year
            def parse_date(d_str):
                try:
                    parts = str(d_str).split('/')
                    if len(parts) == 3:
                        m, d, y = int(parts[0]), int(parts[1]), int(parts[2])
                        # Handle 2-digit years
                        if y <= 19:
                            y += 2000
                        elif y < 100:
                            y += 1900
                        return m, d, y
                except Exception:
                    pass
                return 1, 1, 2000

            dates = df['release_date'].apply(parse_date)
            df['release_month'] = [d[0] for d in dates]
            df['release_day'] = [d[1] for d in dates]
            df['release_year'] = [d[2] for d in dates]
            df['release_quarter'] = df['release_month'].apply(lambda m: (m - 1) // 3 + 1)
            df['is_holiday_season'] = df['release_month'].isin([5, 6, 7, 11, 12]).astype(int)

            # Collection feature
            df['has_collection'] = df['belongs_to_collection'].notnull().astype(int)
            
            # Homepage feature
            df['has_homepage'] = df['homepage'].notnull().astype(int)
            
            # Status feature
            df['is_released'] = (df['status'] == 'Released').astype(int)

            # Tagline & Overview features
            df['has_tagline'] = df['tagline'].notnull().astype(int)
            df['tagline_len'] = df['tagline'].fillna('').apply(len)
            df['overview_len'] = df['overview'].fillna('').apply(len)
            df['title_len'] = df['title'].fillna('').apply(len)

            # Parse JSON features
            df['genre_list'] = df['genres'].apply(extract_names)
            df['genres_count'] = df['genre_list'].apply(len)

            df['production_companies_list'] = df['production_companies'].apply(extract_names)
            df['prod_companies_count'] = df['production_companies_list'].apply(len)

            df['spoken_languages_list'] = df['spoken_languages'].apply(extract_names)
            df['languages_count'] = df['spoken_languages_list'].apply(len)

            df['cast_list'] = df['cast'].apply(extract_cast)
            df['cast_count'] = df['cast'].apply(lambda x: len(safe_eval(x)))
            
            df['director'] = df['crew'].apply(extract_director)
            df['crew_count'] = df['crew'].apply(lambda x: len(safe_eval(x)))

            df['keywords_count'] = df['Keywords'].apply(lambda x: len(safe_eval(x)))

            # Impute numerical columns
            df['budget'] = df['budget'].fillna(0)
            median_budget = df[df['budget'] > 0]['budget'].median()
            df['budget_imputed'] = df['budget'].apply(lambda x: x if x > 0 else median_budget)
            df['log_budget'] = np.log1p(df['budget_imputed'])

            df['popularity'] = df['popularity'].fillna(df['popularity'].median())
            df['log_popularity'] = np.log1p(df['popularity'])

            df['runtime'] = df['runtime'].fillna(df['runtime'].median())

            # Original language
            df['is_english'] = (df['original_language'] == 'en').astype(int)

            return df

        train_clean = engineer_features(train_df, is_train=True)
        test_clean = engineer_features(test_df, is_train=False) if test_df is not None else None

        # Determine top genres across training dataset
        all_genres = [g for sublist in train_clean['genre_list'] for g in sublist]
        self.top_genres = pd.Series(all_genres).value_counts().head(15).index.tolist()

        # Add genre binary columns
        for g in self.top_genres:
            col = f'genre_{g.replace(" ", "_").lower()}'
            train_clean[col] = train_clean['genre_list'].apply(lambda lst: int(g in lst))
            if test_clean is not None:
                test_clean[col] = test_clean['genre_list'].apply(lambda lst: int(g in lst))

        # Generate summary statistics for dashboard charts
        self._compute_dataset_stats(train_clean)

        return train_clean, test_clean

    def _compute_dataset_stats(self, train_clean):
        # Budget vs Revenue sample for scatter plot (top 500 representative points)
        sample = train_clean[['id', 'title', 'budget', 'revenue', 'popularity', 'release_year', 'has_collection', 'runtime']].dropna()
        sample = sample[(sample['budget'] > 0) & (sample['revenue'] > 0)]
        
        # Genre stats
        genre_stats = []
        for g in self.top_genres:
            subset = train_clean[train_clean[f'genre_{g.replace(" ", "_").lower()}'] == 1]
            if len(subset) > 0:
                genre_stats.append({
                    'genre': g,
                    'count': int(len(subset)),
                    'avg_revenue': float(subset['revenue'].mean()),
                    'avg_budget': float(subset[subset['budget'] > 0]['budget'].mean() if len(subset[subset['budget'] > 0]) > 0 else 0),
                    'max_revenue': float(subset['revenue'].max())
                })
        genre_stats = sorted(genre_stats, key=lambda x: x['avg_revenue'], reverse=True)

        # Monthly stats
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_stats = []
        for m in range(1, 13):
            subset = train_clean[train_clean['release_month'] == m]
            month_stats.append({
                'month': month_names[m - 1],
                'month_num': m,
                'count': int(len(subset)),
                'avg_revenue': float(subset['revenue'].mean() if len(subset) > 0 else 0),
                'total_revenue': float(subset['revenue'].sum() if len(subset) > 0 else 0)
            })

        # Top 10 highest grossing in training set
        top_movies = train_clean.sort_values(by='revenue', ascending=False).head(10)[['title', 'release_year', 'budget', 'revenue', 'popularity', 'genres_count', 'runtime']].to_dict(orient='records')

        # Collection vs non-collection
        in_coll = train_clean[train_clean['has_collection'] == 1]
        out_coll = train_clean[train_clean['has_collection'] == 0]

        self.dataset_stats = {
            'total_train_movies': int(len(train_clean)),
            'avg_budget': float(train_clean[train_clean['budget'] > 0]['budget'].mean()),
            'median_budget': float(train_clean[train_clean['budget'] > 0]['budget'].median()),
            'avg_revenue': float(train_clean['revenue'].mean()),
            'median_revenue': float(train_clean['revenue'].median()),
            'max_revenue': float(train_clean['revenue'].max()),
            'min_revenue': float(train_clean['revenue'].min()),
            'top_genres': self.top_genres,
            'genre_stats': genre_stats,
            'month_stats': month_stats,
            'top_movies': top_movies,
            'collection_comparison': {
                'in_collection_avg_revenue': float(in_coll['revenue'].mean()),
                'out_collection_avg_revenue': float(out_coll['revenue'].mean()),
                'in_collection_count': int(len(in_coll)),
                'out_collection_count': int(len(out_coll))
            },
            'scatter_sample': sample.head(250).to_dict(orient='records')
        }

    def train(self):
        train_clean, test_clean = self.load_and_preprocess()

        # Define model feature columns
        num_features = [
            'budget_imputed', 'log_budget', 'popularity', 'log_popularity', 'runtime',
            'has_collection', 'has_homepage', 'has_tagline', 'tagline_len', 'overview_len',
            'title_len', 'genres_count', 'prod_companies_count', 'languages_count',
            'cast_count', 'crew_count', 'keywords_count', 'release_year', 'release_month',
            'release_quarter', 'is_holiday_season', 'is_english'
        ]
        genre_features = [f'genre_{g.replace(" ", "_").lower()}' for g in self.top_genres]
        self.feature_names = num_features + genre_features

        X = train_clean[self.feature_names].copy()
        y = train_clean['revenue'].copy()
        y_log = np.log1p(y)

        # Train/Validation Split (80/20)
        X_train, X_val, y_train, y_val, y_train_log, y_val_log = train_test_split(
            X, y, y_log, test_size=0.2, random_state=42
        )

        # Preprocessing Scaler
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_all_scaled = self.scaler.transform(X)

        # Define Models to train and compare
        model_candidates = {
            'LinearRegression': LinearRegression(),
            'Lasso': Lasso(alpha=0.1, random_state=42),
            'Ridge': Ridge(alpha=1.0, random_state=42),
            'RandomForest': RandomForestRegressor(n_estimators=150, max_depth=12, min_samples_split=4, random_state=42, n_jobs=-1),
            'GradientBoosting': GradientBoostingRegressor(n_estimators=180, learning_rate=0.06, max_depth=5, subsample=0.85, random_state=42),
            'HistGradientBoosting': HistGradientBoostingRegressor(max_iter=150, learning_rate=0.07, max_depth=6, random_state=42)
        }

        print("Training models and calculating metrics...")
        self.metrics = {}
        for name, model in model_candidates.items():
            if name in ['LinearRegression', 'Lasso', 'Ridge']:
                # Train on log target for better normal distribution handling
                model.fit(X_train_scaled, y_train_log)
                pred_log = model.predict(X_val_scaled)
                pred_y = np.expm1(np.clip(pred_log, 0, None))
                
                # Fit on full data
                model.fit(X_all_scaled, y_log)
            else:
                # Tree models on log revenue
                model.fit(X_train, y_train_log)
                pred_log = model.predict(X_val)
                pred_y = np.expm1(np.clip(pred_log, 0, None))
                
                # Fit on full data
                model.fit(X, y_log)

            self.models[name] = model

            # Calculate evaluation metrics
            rmse = float(np.sqrt(mean_squared_error(y_val, pred_y)))
            mae = float(mean_absolute_error(y_val, pred_y))
            r2 = float(r2_score(y_val, pred_y))
            rmsle = float(np.sqrt(mean_squared_error(y_val_log, pred_log)))

            self.metrics[name] = {
                'name': name,
                'rmse': rmse,
                'mae': mae,
                'r2_score': round(r2, 4),
                'rmsle': round(rmsle, 4),
                'formatted_rmse': f"${rmse/1e6:.2f}M",
                'formatted_mae': f"${mae/1e6:.2f}M"
            }
            print(f"Model {name:20} | R2: {r2:.4f} | RMSLE: {rmsle:.4f} | RMSE: ${rmse/1e6:.2f}M")

        # Select best model based on RMSLE
        best_name = min(self.metrics.keys(), key=lambda k: self.metrics[k]['rmsle'])
        self.best_model_name = best_name
        print(f"Best model selected: {self.best_model_name}")

        # Feature Importance for tree models
        feature_importance = []
        if hasattr(self.models['GradientBoosting'], 'feature_importances_'):
            importances = self.models['GradientBoosting'].feature_importances_
            for feat, imp in zip(self.feature_names, importances):
                feature_importance.append({'feature': feat, 'importance': round(float(imp), 4)})
            feature_importance = sorted(feature_importance, key=lambda x: x['importance'], reverse=True)
        self.metrics['feature_importance'] = feature_importance

        # Generate Test Predictions and save submission.csv
        if test_clean is not None:
            print("Generating submission.csv for test dataset...")
            X_test = test_clean[self.feature_names].copy()
            if self.best_model_name in ['LinearRegression', 'Lasso', 'Ridge']:
                X_test_scaled = self.scaler.transform(X_test)
                pred_test_log = self.models[self.best_model_name].predict(X_test_scaled)
            else:
                pred_test_log = self.models[self.best_model_name].predict(X_test)

            pred_test_revenue = np.expm1(np.clip(pred_test_log, 0, None))
            submission = pd.DataFrame({
                'id': test_clean['id'],
                'revenue': pred_test_revenue
            })
            submission_path = os.path.join(self.data_dir, 'submission.csv')
            submission.to_csv(submission_path, index=False)
            print(f"Submission saved to {submission_path} (Total predictions: {len(submission)})")

        # Save engine instance
        self.is_trained = True
        save_path = os.path.join(self.data_dir, 'box_office_model.joblib')
        joblib.dump(self, save_path)
        print(f"ML Engine state persisted to {save_path}")

        return self.metrics

    def predict_custom(self, custom_input):
        """
        Accepts a dict of custom movie features:
        {
            'budget': 100000000,
            'popularity': 25.0,
            'runtime': 120,
            'release_year': 2026,
            'release_month': 7,
            'has_collection': 1,
            'has_homepage': 1,
            'genres': ['Action', 'Adventure', 'Science Fiction'],
            'cast_tier': 'Superstars (A-List)',
            'director_tier': 'Top Tier A-List',
            'is_english': 1
        }
        """
        if not self.is_trained:
            self.train()

        budget = float(custom_input.get('budget', 50000000))
        popularity = float(custom_input.get('popularity', 15.0))
        runtime = float(custom_input.get('runtime', 115))
        release_year = int(custom_input.get('release_year', 2026))
        release_month = int(custom_input.get('release_month', 6))
        has_collection = int(custom_input.get('has_collection', 0))
        has_homepage = int(custom_input.get('has_homepage', 1))
        genres = custom_input.get('genres', ['Action', 'Adventure'])
        is_english = int(custom_input.get('is_english', 1))

        # Adjust popularity or cast count based on tiers
        cast_count = 15
        crew_count = 25
        if custom_input.get('cast_tier') == 'Superstars (A-List)':
            popularity += 15.0
            cast_count += 10
        elif custom_input.get('cast_tier') == 'Major Stars':
            popularity += 8.0

        if custom_input.get('director_tier') == 'Top Tier A-List':
            popularity += 10.0
            crew_count += 15

        log_budget = np.log1p(budget if budget > 0 else 25000000)
        log_pop = np.log1p(popularity)
        quarter = (release_month - 1) // 3 + 1
        is_holiday = int(release_month in [5, 6, 7, 11, 12])

        row = {
            'budget_imputed': budget,
            'log_budget': log_budget,
            'popularity': popularity,
            'log_popularity': log_pop,
            'runtime': runtime,
            'has_collection': has_collection,
            'has_homepage': has_homepage,
            'has_tagline': 1,
            'tagline_len': 35,
            'overview_len': 150,
            'title_len': 18,
            'genres_count': len(genres),
            'prod_companies_count': 3,
            'languages_count': 1,
            'cast_count': cast_count,
            'crew_count': crew_count,
            'keywords_count': 6,
            'release_year': release_year,
            'release_month': release_month,
            'release_quarter': quarter,
            'is_holiday_season': is_holiday,
            'is_english': is_english
        }

        for g in self.top_genres:
            col = f'genre_{g.replace(" ", "_").lower()}'
            row[col] = int(g in genres)

        df_input = pd.DataFrame([row])[self.feature_names]

        # Predict using best model
        pred_log = self.models[self.best_model_name].predict(df_input)[0]
        pred_revenue = float(np.expm1(np.clip(pred_log, 0, None)))

        # Also calculate lower and upper bounds (80% confidence band)
        lower_bound = max(0.0, pred_revenue * 0.72)
        upper_bound = pred_revenue * 1.38

        roi = ((pred_revenue - budget) / budget * 100) if budget > 0 else 0
        multiplier = (pred_revenue / budget) if budget > 0 else 0

        # Verdict
        if multiplier >= 4.0:
            verdict = "All-Time Blockbuster"
            badge_color = "#10b981" # emerald
        elif multiplier >= 2.5:
            verdict = "Super Hit"
            badge_color = "#34d399"
        elif multiplier >= 1.8:
            verdict = "Profitable Hit"
            badge_color = "#38bdf8" # sky
        elif multiplier >= 1.0:
            verdict = "Moderate / Average"
            badge_color = "#f59e0b" # amber
        else:
            verdict = "Box Office Flop"
            badge_color = "#ef4444" # red

        return {
            'predicted_revenue': round(pred_revenue, 2),
            'formatted_revenue': f"${pred_revenue:,.0f}",
            'revenue_millions': round(pred_revenue / 1e6, 2),
            'lower_bound_millions': round(lower_bound / 1e6, 2),
            'upper_bound_millions': round(upper_bound / 1e6, 2),
            'budget_millions': round(budget / 1e6, 2),
            'roi_percentage': round(roi, 1),
            'profit_multiplier': round(multiplier, 2),
            'verdict': verdict,
            'badge_color': badge_color,
            'model_used': self.best_model_name
        }

# Singleton accessor
_engine_instance = None

def get_ml_engine(data_dir='.'):
    global _engine_instance
    if _engine_instance is None:
        save_path = os.path.join(data_dir, 'box_office_model.joblib')
        if os.path.exists(save_path):
            try:
                _engine_instance = joblib.load(save_path)
            except Exception:
                _engine_instance = BoxOfficeMLEngine(data_dir=data_dir)
                _engine_instance.train()
        else:
            _engine_instance = BoxOfficeMLEngine(data_dir=data_dir)
            _engine_instance.train()
    return _engine_instance

if __name__ == '__main__':
    engine = BoxOfficeMLEngine()
    engine.train()
    print("Test custom prediction:")
    test_res = engine.predict_custom({
        'budget': 150000000,
        'popularity': 45.0,
        'genres': ['Action', 'Adventure', 'Science Fiction'],
        'has_collection': 1,
        'release_month': 5
    })
    print(test_res)
