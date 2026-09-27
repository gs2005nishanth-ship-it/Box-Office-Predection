import os
import json
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file
from ml_engine import get_ml_engine
from llm_engine import get_llm_engine

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'box-office-super-secret-key-2026'

# Initialize engines
ml_engine = get_ml_engine()
llm_engine = get_llm_engine()

# Load raw train data for dataset browser (cached in memory)
train_df_raw = None
def get_train_df():
    global train_df_raw
    if train_df_raw is None and os.path.exists('train.csv'):
        df = pd.read_csv('train.csv')
        df['budget'] = df['budget'].fillna(0)
        df['revenue'] = df['revenue'].fillna(0)
        df['popularity'] = df['popularity'].fillna(0)
        df['title'] = df['title'].fillna(df['original_title']).fillna('Untitled')
        train_df_raw = df
    return train_df_raw

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/movie-lookup', methods=['POST'])
def movie_lookup():
    data = request.get_json() or {}
    movie_name = data.get('query', '').strip()
    if not movie_name:
        return jsonify({'error': 'Please provide a movie name.'}), 400

    engine = get_llm_engine()
    print(f"Executing movie lookup for: {movie_name} (Provider: {engine.provider})")
    result = engine.query_movie(movie_name)
    if not result or 'movie' not in result:
        return jsonify({'error': 'Could not retrieve box office data for this movie.'}), 404

    return jsonify(result)

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.get_json() or {}
    try:
        prediction = ml_engine.predict_custom(data)
        return jsonify({'status': 'success', 'prediction': prediction})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        stats = ml_engine.dataset_stats
        return jsonify({'status': 'success', 'stats': stats})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/models-info', methods=['GET'])
def get_models_info():
    try:
        return jsonify({
            'status': 'success',
            'best_model': ml_engine.best_model_name,
            'metrics': ml_engine.metrics
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/movies', methods=['GET'])
def get_movies():
    df = get_train_df()
    if df is None:
        return jsonify({'movies': [], 'total': 0})

    query = request.args.get('q', '').lower().strip()
    genre_filter = request.args.get('genre', '').lower().strip()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 15))

    filtered = df.copy()
    if query:
        filtered = filtered[filtered['title'].str.lower().str.contains(query, na=False)]
    if genre_filter:
        filtered = filtered[filtered['genres'].str.lower().str.contains(genre_filter, na=False)]

    total = len(filtered)
    start = (page - 1) * limit
    end = start + limit
    subset = filtered.iloc[start:end]

    results = []
    for _, row in subset.iterrows():
        results.append({
            'id': int(row['id']),
            'title': str(row['title']),
            'budget': float(row['budget']),
            'revenue': float(row['revenue']),
            'popularity': round(float(row['popularity']), 2),
            'release_date': str(row.get('release_date', 'N/A')),
            'runtime': float(row.get('runtime', 0)) if pd.notnull(row.get('runtime')) else 0,
            'tagline': str(row.get('tagline', '')) if pd.notnull(row.get('tagline')) else ''
        })

    return jsonify({
        'movies': results,
        'total': total,
        'page': page,
        'limit': limit,
        'pages': (total + limit - 1) // limit
    })

@app.route('/api/submission-preview', methods=['GET'])
def submission_preview():
    sub_path = 'submission.csv'
    if not os.path.exists(sub_path):
        return jsonify({'status': 'error', 'message': 'submission.csv not generated yet.'}), 404

    df_sub = pd.read_csv(sub_path)
    preview = df_sub.head(10).to_dict(orient='records')
    return jsonify({
        'status': 'success',
        'total_rows': len(df_sub),
        'preview': preview
    })

@app.route('/download/submission', methods=['GET'])
def download_submission():
    sub_path = 'submission.csv'
    if os.path.exists(sub_path):
        return send_file(sub_path, as_attachment=True, download_name='submission.csv')
    return jsonify({'error': 'submission.csv file not found.'}), 404

@app.route('/api/set-api-key', methods=['POST'])
def set_api_key():
    data = request.get_json() or {}
    api_key = data.get('api_key', '')
    provider = data.get('provider', 'openai')
    model = data.get('model', '')

    res = llm_engine.set_api_key(api_key, provider, model)
    return jsonify({'status': 'success', 'config': res})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Box Office Web Dashboard on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
