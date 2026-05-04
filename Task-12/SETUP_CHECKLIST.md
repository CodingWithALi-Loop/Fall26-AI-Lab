# Setup & Testing Checklist

Complete this checklist to ensure your Hadith Search Engine is properly set up and working.

## ✅ Pre-Setup Requirements

- [ ] Python 3.8 or higher installed (`python --version`)
- [ ] pip package manager available (`pip --version`)
- [ ] Git installed (optional but recommended)
- [ ] Sufficient disk space (~1GB for dependencies)
- [ ] Internet connection (for downloading packages)

## ✅ File Structure Verification

Verify all files are in place:

```
Task-12/
├── app.py                      ✓
├── config.py                   ✓
├── run.py                      ✓
├── requirements.txt            ✓
├── README.md                   ✓
├── QUICKSTART.md               ✓
├── PROJECT_SUMMARY.md          ✓
├── DEPLOYMENT.md               ✓
├── .env.example                ✓
├── .gitignore                  ✓
├── Task12.ipynb                ✓
├── templates/
│   └── index.html              ✓
└── static/
    ├── style.css               ✓
    └── script.js               ✓
```

- [ ] All files exist
- [ ] Directory structure matches above
- [ ] No files missing

## ✅ Environment Setup

### Windows
```cmd
cd c:\Users\Hackerali\Desktop\AI-Lab\Fall26-AI-Lab\Task-12
python -m venv venv
venv\Scripts\activate
```
- [ ] Virtual environment created
- [ ] Virtual environment activated (see `(venv)` prefix in terminal)

### macOS/Linux
```bash
cd ~/Desktop/AI-Lab/Fall26-AI-Lab/Task-12
python3 -m venv venv
source venv/bin/activate
```
- [ ] Virtual environment created
- [ ] Virtual environment activated

## ✅ Dependencies Installation

```bash
pip install -r requirements.txt
```

Check installation:
```bash
pip list
```

Verify these are installed:
- [ ] Flask (≥3.0.0)
- [ ] pandas (≥2.0.0)
- [ ] numpy (≥1.24.0)
- [ ] faiss-cpu (≥1.7.0)
- [ ] sentence-transformers (≥2.2.0)
- [ ] torch (≥2.0.0)

## ✅ Data Files Generation

Run the Jupyter notebook to generate data files:

```bash
jupyter notebook Task12.ipynb
```

Or use Anaconda Navigator if preferred.

**Execute all cells in the notebook** to generate:

- [ ] `cleaned_hadith.csv` - Should be created in Task-12/
- [ ] `faiss_index.faiss` - Should be created in Task-12/
- [ ] `embeddings.npy` - Should be created (optional)

**Verify files exist:**
```bash
ls -la cleaned_hadith.csv faiss_index.faiss
```

- [ ] Both files present
- [ ] Files have non-zero size
- [ ] Files are readable

## ✅ Application Startup

### Option 1: Run with run.py (Recommended)
```bash
python run.py
```

You should see:
```
============================================================
🕌 HADITH SEARCH ENGINE - Starting Up
============================================================
Environment: development
Debug Mode: True
Server: http://127.0.0.1:5000
...
```

- [ ] No startup errors
- [ ] "Loading data..." message appears
- [ ] FAISS index loads successfully
- [ ] Server starts without errors

### Option 2: Run with Flask directly
```bash
python app.py
```

- [ ] Application starts
- [ ] Shows port (usually 5000)

### Option 3: Run on different port
```bash
python run.py --port 8000
```

- [ ] Application accessible on specified port

## ✅ Browser Access

### Access the Application
1. Open your browser
2. Navigate to: **http://localhost:5000**
3. You should see the Hadith Search Engine homepage

- [ ] Homepage loads without errors
- [ ] Search bar is visible
- [ ] Filters are visible
- [ ] Statistics are displayed
- [ ] Layout is responsive (try resizing)

## ✅ UI Elements Verification

### Navigation Bar
- [ ] Title "Hadith Search Engine" visible
- [ ] Book icon displayed
- [ ] Statistics displayed

### Hero Section
- [ ] Title displays clearly
- [ ] Subtitle displays clearly
- [ ] Background color is green

### Search Interface
- [ ] Search input field visible
- [ ] Search button visible
- [ ] Button has magnifying glass icon
- [ ] All 4 filters visible:
  - [ ] Book filter
  - [ ] Chapter filter
  - [ ] Sort By filter
  - [ ] Results count filter

### Statistics Section
- [ ] Shows "Database Statistics" header
- [ ] Displays 4 stat cards:
  - [ ] Total Hadiths count
  - [ ] Books count
  - [ ] Chapters count
  - [ ] Search Speed

### Footer
- [ ] Footer visible at bottom
- [ ] Contains copyright text
- [ ] Has footer links

## ✅ Functional Testing

### Test 1: Basic Search
1. Enter "mercy" in search box
2. Click Search button
3. Expected: Results appear in cards

- [ ] Search processes without error
- [ ] Results display in card format
- [ ] Loading spinner appeared then disappeared
- [ ] Processing time is shown
- [ ] Result count is displayed

### Test 2: Filter by Book
1. Perform a search
2. Open Book filter dropdown
3. Select a book
4. Results should filter

- [ ] Book dropdown has options
- [ ] Can select a book
- [ ] Results update when book selected
- [ ] Only results from selected book shown

### Test 3: Filter by Chapter
1. Perform a search
2. Open Chapter filter dropdown
3. Select a chapter
4. Results should filter

- [ ] Chapter dropdown has options
- [ ] Can select a chapter
- [ ] Results update when chapter selected

### Test 4: Sort Results
1. Perform a search
2. Change "Sort By" dropdown
3. Results should re-sort

- [ ] Sort dropdown works
- [ ] Results order changes
- [ ] Both "Most Relevant" and "Latest" work

### Test 5: Change Result Count
1. Perform a search
2. Change result count (5, 10, 20, 50)
3. Results should limit to selected count

- [ ] Count dropdown works
- [ ] Different counts display correctly
- [ ] Count matches what selected

### Test 6: Result Cards
1. Look at any result card
2. Should display:

- [ ] Relevance score with star icon
- [ ] English hadith text
- [ ] Arabic hadith text
- [ ] English meaning
- [ ] Arabic meaning
- [ ] Chapter number
- [ ] Section number
- [ ] Grade information

### Test 7: Keyboard Shortcuts
1. Press `Ctrl+K` (or `Cmd+K` on Mac)
   - [ ] Focus moves to search box
2. Press `Escape`
   - [ ] Results clear
3. Focus on search and press `Enter`
   - [ ] Search executes

### Test 8: Responsive Design
1. Open Developer Tools: F12
2. Toggle device toolbar
3. Test at different sizes:
   - [ ] Desktop (1200px+) - Layout correct
   - [ ] Tablet (768px) - Single/double column
   - [ ] Mobile (480px) - Single column, touch-friendly

## ✅ Error Handling Tests

### Test Empty Search
1. Click search with empty field
2. Expected: Error message or prompt to enter text

- [ ] Appropriate message shown
- [ ] Application doesn't crash

### Test with Missing Data Files
1. Rename `cleaned_hadith.csv` temporarily
2. Try to search
3. Expected: Error message

- [ ] Error message displayed
- [ ] Application handles gracefully

### Test Network Error (Simulate)
1. Search offline (if possible)
2. Expected: Appropriate error

- [ ] Error handled gracefully
- [ ] User can try again

## ✅ Performance Checks

### Response Time
1. Perform search
2. Note processing time displayed

- [ ] Processing time < 500ms (should be 100-200ms)
- [ ] UI remains responsive
- [ ] No browser freezing

### Page Load Time
1. Hard refresh page (Ctrl+Shift+R)
2. Monitor Network tab in DevTools

- [ ] Page loads < 3 seconds
- [ ] All assets load
- [ ] No 404 errors

## ✅ Browser Compatibility

Test in multiple browsers:

- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (if available)

For each:
- [ ] Page displays correctly
- [ ] Search works
- [ ] Filters work
- [ ] No JavaScript errors (F12 → Console)

## ✅ Data File Validation

### Check CSV File
```bash
python -c "import pandas as pd; df = pd.read_csv('cleaned_hadith.csv'); print(f'Rows: {len(df)}'); print(df.columns.tolist())"
```

- [ ] CSV loads without error
- [ ] Shows number of rows
- [ ] Shows all expected columns

### Check FAISS Index
```bash
python -c "import faiss; idx = faiss.read_index('faiss_index.faiss'); print(f'Index loaded, size: {idx.ntotal}')"
```

- [ ] Index loads without error
- [ ] Shows index size
- [ ] Size matches number of hadiths

## ✅ Configuration Verification

### Check config.py
- [ ] No syntax errors in config.py
- [ ] All required variables present
- [ ] Paths are correct
- [ ] Default values are reasonable

### Check app.py
- [ ] No syntax errors
- [ ] All routes defined
- [ ] Error handlers present
- [ ] Comments are clear

### Check templates & static
- [ ] HTML valid (no major errors)
- [ ] CSS loads correctly
- [ ] JavaScript loads correctly
- [ ] No 404 errors for assets

## ✅ Production Readiness

- [ ] DEBUG set to False in production
- [ ] SECRET_KEY configured
- [ ] Error handling comprehensive
- [ ] Logging configured
- [ ] Security headers set
- [ ] CORS configured (if needed)
- [ ] Rate limiting ready (optional)
- [ ] Database ready (optional)

## ✅ Documentation Review

Read through:
- [ ] README.md - Full features
- [ ] QUICKSTART.md - Fast setup
- [ ] DEPLOYMENT.md - Production guide
- [ ] PROJECT_SUMMARY.md - Overview
- [ ] config.py docstrings
- [ ] app.py docstrings

## ✅ Code Quality

Run checks:

### Python Syntax
```bash
python -m py_compile app.py config.py run.py
```
- [ ] No syntax errors

### Static Files
```bash
# Check CSS validity (visual inspection)
# Check JS syntax with browser console
```
- [ ] No CSS errors in console
- [ ] No JS errors in console

## ✅ Final Verification

### Full Workflow
1. [ ] Start fresh: `python run.py`
2. [ ] Open browser: `http://localhost:5000`
3. [ ] Search for "faith"
4. [ ] Filter by a book
5. [ ] Sort by latest
6. [ ] Change result count to 20
7. [ ] View multiple cards
8. [ ] Try keyboard shortcuts
9. [ ] Test responsive design
10. [ ] Clear and start new search

### Everything Works?
- [ ] YES - Application is ready to use!
- [ ] NO - Review errors and troubleshoot

## 🐛 Troubleshooting

If any test fails:

1. **Check logs**: Look at terminal/console output
2. **Check browser console**: F12 → Console tab
3. **Check network**: F12 → Network tab
4. **Review README.md**: Troubleshooting section
5. **Verify file paths**: Ensure all files exist
6. **Check dependencies**: `pip list`
7. **Restart terminal**: Clear any cached state

## 📞 Common Issues & Solutions

### Issue: "Module not found"
```bash
# Solution:
pip install -r requirements.txt
```

### Issue: "Address already in use"
```bash
# Solution:
python run.py --port 8000
```

### Issue: "No such file or directory"
```bash
# Solution: Run from correct directory
cd Task-12
python run.py
```

### Issue: "FAISS index not found"
```bash
# Solution: Run notebook to generate index
jupyter notebook Task12.ipynb
# Execute all cells
```

## ✨ Success Criteria

Your setup is successful when:

✅ Virtual environment created and activated  
✅ All dependencies installed  
✅ Data files generated from notebook  
✅ Application starts without errors  
✅ Homepage loads in browser  
✅ Search functionality works  
✅ Filters work correctly  
✅ Results display properly  
✅ Responsive design works  
✅ No errors in console  
✅ Performance is acceptable  

---

## 🎉 Next Steps

Once all checks pass:

1. **Explore the code**: Understand how it works
2. **Customize**: Change colors, branding, etc.
3. **Deploy**: Use DEPLOYMENT.md for production
4. **Extend**: Add features (auth, database, etc.)
5. **Optimize**: Profile and improve performance

---

**Last Updated**: May 2, 2026  
**Status**: Setup & Testing Guide ✅
