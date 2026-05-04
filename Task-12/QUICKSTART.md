# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Prepare Data Files

Make sure you have generated the required files from Task12.ipynb:
- `cleaned_hadith.csv`
- `faiss_index.faiss`

If you haven't run the notebook yet, execute all cells in `Task12.ipynb` first.

### Step 3: Run the Application

```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

---

## 🎯 What You'll See

### Homepage
- Clean, modern interface with search bar
- Advanced filters (Book, Chapter, Sort)
- Database statistics

### Search Results
- Beautiful card-based layout
- English and Arabic text
- Relevance scoring
- Processing time display

---

## 🔍 How to Search

1. **Enter a query**: Type any hadith-related term (e.g., "mercy", "faith", "prayer")
2. **Set filters** (optional):
   - Filter by specific book
   - Filter by chapter
   - Sort by relevance or latest
3. **Click Search** or press **Enter**
4. **View Results** in card format with all relevant information

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` / `Cmd+K` | Focus search box |
| `Enter` | Perform search |
| `Escape` | Clear results |

---

## 📁 File Structure

```
Task-12/
├── app.py                      # Flask backend
├── requirements.txt            # Dependencies
├── README.md                   # Full documentation
├── QUICKSTART.md              # This file
├── Task12.ipynb               # Data processing notebook
├── cleaned_hadith.csv         # Processed hadith data
├── faiss_index.faiss          # Search index
├── templates/
│   └── index.html             # Web interface
└── static/
    ├── style.css              # Styling
    └── script.js              # Frontend logic
```

---

## 🎨 Features

✅ **Semantic Search** - Find similar hadiths using AI  
✅ **Bilingual** - English and Arabic support  
✅ **Fast** - FAISS-powered instant search  
✅ **Responsive** - Works on desktop and mobile  
✅ **Beautiful** - Islamic-themed modern UI  
✅ **Filters** - Book, Chapter, and sorting options  

---

## 🛠️ Troubleshooting

### Port 5000 Already in Use

Change port in `app.py`:
```python
app.run(debug=True, port=8000)  # Use 8000 or any available port
```

### Missing Data Files

Run the Jupyter notebook first:
```bash
jupyter notebook Task12.ipynb
```
Execute all cells to generate required files.

### Module Not Found Error

Make sure virtual environment is activated and dependencies installed:
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## 📱 Accessing from Other Devices

To access from mobile/tablet on the same network:

1. Find your computer's IP address:
   - **Windows**: `ipconfig` → IPv4 Address
   - **macOS/Linux**: `ifconfig` → inet

2. On mobile device, visit: `http://<YOUR_IP>:5000`

---

## 💡 Tips

- **Better Results**: Use specific terms (e.g., "Prophet Muhammad wisdom" instead of just "hadith")
- **Performance**: Start with fewer results (5-10) for faster loading
- **Mobile**: Use portrait mode for best experience
- **Search Time**: Processing takes ~100-200ms; be patient

---

## 📚 Next Steps

1. ✅ Run the application
2. 📝 Perform some test searches
3. 🎨 Customize colors in `static/style.css`
4. 🔧 Add more features (authentication, database, etc.)
5. 🚀 Deploy to production

---

## 📞 Support

For detailed information, see [README.md](README.md)

Happy searching! 🕌✨
