from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import time
import os
from functools import lru_cache
from config import get_config

app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
config = get_config(env)
app.config.from_object(config)

# Global variables for cached data
hadith_df = None
faiss_index = None
model = None

def load_data():
    """Load hadith data, embeddings, and FAISS index"""
    global hadith_df, faiss_index, model
    
    if hadith_df is not None:
        return  # Already loaded
    
    try:
        # Load hadith dataframe
        if os.path.exists(app.config['HADITH_DATA_PATH']):
            hadith_df = pd.read_csv(app.config['HADITH_DATA_PATH'])
            print(f"✓ Loaded {len(hadith_df)} hadiths from {app.config['HADITH_DATA_PATH']}")
        else:
            print(f"⚠ Warning: {app.config['HADITH_DATA_PATH']} not found")
            hadith_df = pd.DataFrame()
        
        # Load FAISS index
        if os.path.exists(app.config['FAISS_INDEX_PATH']):
            faiss_index = faiss.read_index(app.config['FAISS_INDEX_PATH'])
            print(f"✓ FAISS index loaded from {app.config['FAISS_INDEX_PATH']}")
        else:
            print(f"⚠ Warning: {app.config['FAISS_INDEX_PATH']} not found")
        
        # Load sentence transformer model
        model = SentenceTransformer(app.config['SENTENCE_TRANSFORMER_MODEL'])
        print(f"✓ Sentence Transformer model loaded: {app.config['SENTENCE_TRANSFORMER_MODEL']}")
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        hadith_df = pd.DataFrame()

def highlight_keywords(text, keywords):
    """Highlight keywords in text"""
    if not text or not keywords:
        return text
    
    highlighted = str(text)
    for keyword in keywords:
        # Case-insensitive highlight
        highlighted = highlighted.replace(
            keyword,
            f'<mark>{keyword}</mark>'
        )
    return highlighted

def get_unique_values(column):
    """Get unique values from a column"""
    try:
        if hadith_df is not None and column in hadith_df.columns:
            return sorted(hadith_df[column].dropna().unique().tolist())
        return []
    except Exception as e:
        print(f"Error getting unique values for {column}: {e}")
        return []

@app.route('/')
def index():
    """Homepage"""
    load_data()
    books = get_unique_values('Chapter_English')
    chapters = get_unique_values('Section_English')
    
    stats = {
        'total_hadiths': len(hadith_df) if hadith_df is not None else 0,
        'books': len(books),
        'chapters': len(chapters)
    }
    
    return render_template('index.html', stats=stats, books=books, chapters=chapters)

@app.route('/search', methods=['POST'])
def search():
    """Search for similar hadiths"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        limit = min(data.get('limit', app.config['DEFAULT_SEARCH_LIMIT']), 
                   app.config['MAX_SEARCH_LIMIT'])
        book_filter = data.get('book', None)
        chapter_filter = data.get('chapter', None)
        sort_by = data.get('sort_by', 'relevance')
        
        if not query:
            return jsonify({'error': 'Query cannot be empty', 'results': []}), 400
        
        if hadith_df is None or faiss_index is None or model is None:
            return jsonify({'error': 'System not initialized', 'results': []}), 500
        
        # Encode query
        query_embedding = model.encode([query])
        query_embedding = query_embedding.astype('float32')
        
        # Search FAISS index
        k = min(limit * 2, len(hadith_df))  # Get more results for filtering
        distances, indices = faiss_index.search(query_embedding, k)
        
        # Get results
        results_data = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(hadith_df):
                row = hadith_df.iloc[idx]
                
                # Apply filters
                if book_filter and row['Chapter_English'] != book_filter:
                    continue
                if chapter_filter and row['Section_English'] != chapter_filter:
                    continue
                
                result_item = {
                    'id': idx,
                    'english_hadith': str(row.get('English_Hadith', '')),
                    'arabic_hadith': str(row.get('Arabic_Hadith', '')),
                    'english_math': str(row.get('English_Math', '')),
                    'arabic_math': str(row.get('Arabic_Math', '')),
                    'book': str(row.get('Chapter_English', 'N/A')),
                    'chapter': str(row.get('Section_English', 'N/A')),
                    'chapter_number': str(row.get('Chapter_Number', 'N/A')),
                    'section_number': str(row.get('Section_Number', 'N/A')),
                    'english_grade': str(row.get('English_Grade', 'N/A')),
                    'arabic_grade': str(row.get('Arabic_Grade', 'N/A')),
                    'relevance_score': float(distance)
                }
                results_data.append(result_item)
        
        # Sort results
        if sort_by == 'latest':
            results_data.sort(key=lambda x: x['section_number'], reverse=True)
        else:  # relevance (default)
            results_data.sort(key=lambda x: x['relevance_score'])
        
        # Limit results
        results_data = results_data[:limit]
        
        # Highlight keywords
        keywords = query.lower().split()
        for result in results_data:
            result['english_hadith_highlighted'] = highlight_keywords(
                result['english_hadith'],
                keywords
            )
        
        processing_time = time.time() - start_time
        
        return jsonify({
            'query': query,
            'results': results_data,
            'total_results': len(results_data),
            'processing_time': round(processing_time, 3),
            'success': True
        })
    
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({
            'error': str(e),
            'results': [],
            'success': False
        }), 500

@app.route('/api/filters')
def get_filters():
    """Get available filters"""
    load_data()
    return jsonify({
        'books': get_unique_values('Chapter_English'),
        'chapters': get_unique_values('Section_English')
    })

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    """500 error handler"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    load_data()
    app.run(debug=True, port=5000)
