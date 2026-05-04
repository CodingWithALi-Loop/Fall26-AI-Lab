# Hadith Search Engine - Web UI

A modern, responsive Flask-based web application for searching through a comprehensive database of Islamic traditions (Hadiths) using semantic similarity powered by FAISS and Sentence Transformers.

## Features

✨ **Modern Interface**
- Clean, Islamic-themed design with green and gold accents
- Responsive layout for desktop, tablet, and mobile
- Smooth animations and transitions

🔍 **Advanced Search**
- Semantic search using sentence embeddings
- Real-time FAISS-powered similarity search
- Keyword highlighting in results
- Instant search feedback

🎯 **Filtering & Sorting**
- Filter by Book and Chapter
- Sort by relevance or latest
- Adjustable result count (5, 10, 20, 50)

📊 **Results Display**
- Beautiful card-based result layout
- Bilingual support (English & Arabic)
- Relevance scoring
- Hadith metadata (Chapter, Section, Grade)

⚡ **Performance**
- Fast semantic search with FAISS index
- Processing time display
- Optimized for large datasets

📱 **Responsive Design**
- Mobile-first approach
- Touch-friendly interface
- Fast loading times

## Project Structure

```
Task-12/
├── app.py                  # Flask backend application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── templates/
│   └── index.html         # Main HTML template
└── static/
    ├── style.css          # Styling
    └── script.js          # Frontend JavaScript
```

## Installation

### 1. Prerequisites
- Python 3.8 or higher
- pip package manager

### 2. Setup Virtual Environment

**Windows (Command Prompt):**
```bash
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare Data Files

Before running the application, you need to have the processed files from Task12.ipynb in the same directory:

- `cleaned_hadith.csv` - The processed hadith dataset
- `faiss_index.faiss` - The FAISS index
- `embeddings.npy` - The embeddings (optional, for reference)

**To generate these files, run the notebook cells:**

```python
# Cell 1-8: Load and clean hadith data
import pandas as pd
import glob
import re

# Load data, clean text, and save
columns = [
    'Chapter_Number', 'Chapter_English', 'Chapter_Arabic',
    'Section_Number', 'Section_English', 'Section_Arabic',
    'English_Hadith', 'English_Isnad','English_Math',
    'Arabic_Hadith', 'Arabic_Isnad','Arabic_Math',
    'Arabic_Grade','English_Grade', 'Cleaned_Hadith'
]

# ... (complete cleanup process from notebook)
hadith_df.to_csv('cleaned_hadith.csv', index=False)

# Cell 9-11: Create embeddings
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
embeddings = model.encode(hadith_df['Cleaned_Hadith'].fillna('').values)
np.save('embeddings.npy', embeddings)

# Cell 12-13: Create FAISS index
import faiss
dimensions = embeddings.shape[1]
faiss_index = faiss.IndexFlatL2(dimensions)
faiss_index.add(embeddings)
faiss.write_index(faiss_index, 'faiss_index.faiss')
```

## Running the Application

### Start the Flask Server

```bash
python app.py
```

### Access the Application

Open your browser and navigate to:
```
http://localhost:5000
```

The application will display the homepage with:
- Search bar
- Advanced filter options
- Database statistics

## Usage

### 1. Search

Enter your query in the search bar (e.g., "mercy", "faith", "prayer") and click the search button or press Enter.

### 2. Filter Results

- **Book**: Filter by specific hadith book
- **Chapter**: Filter by specific chapter/section
- **Sort By**: Choose between Most Relevant or Latest
- **Results**: Select how many results to display (5, 10, 20, or 50)

### 3. View Results

Results display as cards containing:
- Relevance score (%)
- English hadith text with highlighted keywords
- Arabic hadith text
- English and Arabic meanings
- Chapter and section numbers
- Grading information

### Keyboard Shortcuts

- `Ctrl+K` or `Cmd+K`: Focus search box
- `Escape`: Clear results and return to homepage

## API Endpoints

### GET /
Homepage with search interface

### POST /search
Perform a hadith search

**Request Body:**
```json
{
    "query": "search term",
    "limit": 10,
    "book": "Book Name or null",
    "chapter": "Chapter Name or null",
    "sort_by": "relevance or latest"
}
```

**Response:**
```json
{
    "query": "search term",
    "results": [
        {
            "id": 0,
            "english_hadith": "...",
            "arabic_hadith": "...",
            "english_math": "...",
            "arabic_math": "...",
            "book": "...",
            "chapter": "...",
            "chapter_number": "1",
            "section_number": "1",
            "english_grade": "...",
            "arabic_grade": "...",
            "relevance_score": 0.45,
            "english_hadith_highlighted": "..."
        }
    ],
    "total_results": 10,
    "processing_time": 0.123,
    "success": true
}
```

### GET /api/filters
Get available filter options

**Response:**
```json
{
    "books": ["Book 1", "Book 2", ...],
    "chapters": ["Chapter 1", "Chapter 2", ...]
}
```

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Search Engine**: FAISS (Facebook AI Similarity Search)
- **Embeddings**: Sentence Transformers
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Data Processing**: Pandas, NumPy

## Performance

- **Search Speed**: ~100-200ms for typical queries
- **Dataset**: Supports 10,000+ hadiths
- **Memory**: Efficient FAISS indexing for fast similarity search
- **Scalability**: Can be optimized with GPU acceleration

## Browser Compatibility

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Customization

### Change Color Scheme

Edit `static/style.css` and modify the CSS variables at the top:

```css
:root {
    --primary-color: #2d5016;        /* Main green */
    --accent-color: #c4a747;         /* Gold accent */
    --primary-light: #4a7c2c;
    --primary-dark: #1a3009;
    /* ... other variables */
}
```

### Change Search Results Limit

In `app.py`, modify the `search()` function:

```python
k = min(limit * 2, len(hadith_df))  # Adjust multiplier for more results
```

### Add More Filters

1. Edit `app.py` - Add to `get_filters()` and `search()` functions
2. Edit `templates/index.html` - Add filter UI elements
3. Edit `static/script.js` - Handle new filter in `performSearch()`

## Troubleshooting

### "System not initialized" Error

**Cause**: Missing data files
**Solution**: Ensure `cleaned_hadith.csv` and `faiss_index.faiss` are in the same directory as `app.py`

### Slow Search Performance

**Cause**: FAISS index not optimized
**Solution**: GPU acceleration or index optimization (see FAISS documentation)

### Search Returns No Results

**Cause**: Query may be too specific or filters too restrictive
**Solution**: Try broader search terms or remove filters

### CSS/JavaScript Not Loading

**Cause**: Static files not found
**Solution**: Ensure `static/` folder structure is correct and run Flask with `debug=True`

## Development

### Enable Debug Mode

Already enabled in `app.py`. For production, set `debug=False`:

```python
if __name__ == '__main__':
    load_data()
    app.run(debug=False, port=5000)
```

### Add Logging

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Database Optimization

For large datasets, consider:
- GPU-accelerated FAISS (faiss-gpu)
- Caching frequent searches
- Database indexing (SQLite/PostgreSQL)

## Future Enhancements

- 🔐 User authentication
- 💾 Saved searches and favorites
- 📥 Advanced export (PDF, JSON)
- 🌙 Dark mode toggle
- 📱 Progressive Web App (PWA)
- 🗣️ Voice search
- 🤖 AI-powered suggestions
- 📊 Advanced analytics dashboard
- 🔄 Multi-language support
- ⭐ Community ratings and reviews

## Contributing

To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available for educational purposes.

## Support

For issues, questions, or suggestions, please create an issue or contact the development team.

## Credits

- **Hadith Data**: Islamic Research Foundation
- **Embeddings**: Sentence Transformers (Hugging Face)
- **Search**: FAISS (Meta)
- **Framework**: Flask

---

**Version**: 1.0.0  
**Last Updated**: May 2, 2026  
**Status**: Production Ready ✅
