/* ==================== Global Variables ==================== */
let searchQuery = '';
let currentResults = [];

/* ==================== DOM Elements ==================== */
const searchForm = document.getElementById('search-form');
const searchInput = document.getElementById('search-query');
const resultsSection = document.getElementById('results-section');
const resultsInfo = document.getElementById('results-info');
const resultsContainer = document.getElementById('results-container');
const loadingSpinner = document.getElementById('loading-spinner');
const noResultsDiv = document.getElementById('no-results');
const errorMessageDiv = document.getElementById('error-message');
const statsSection = document.getElementById('stats-section');

/* ==================== Search Handler ==================== */
function handleSearch(e) {
    e.preventDefault();
    
    const query = searchInput.value.trim();
    if (!query) {
        showError('Please enter a search query');
        return;
    }
    
    performSearch(query);
}

/* ==================== Perform Search ==================== */
async function performSearch(query) {
    try {
        // Show loading state
        resultsSection.style.display = 'block';
        statsSection.style.display = 'none';
        loadingSpinner.style.display = 'flex';
        resultsInfo.style.display = 'none';
        resultsContainer.innerHTML = '';
        noResultsDiv.style.display = 'none';
        errorMessageDiv.style.display = 'none';
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
        
        // Get filter values
        const bookFilter = document.getElementById('book-filter').value;
        const chapterFilter = document.getElementById('chapter-filter').value;
        const sortBy = document.getElementById('sort-by').value;
        const limit = parseInt(document.getElementById('limit-results').value);
        
        // Prepare request
        const payload = {
            query: query,
            book: bookFilter || null,
            chapter: chapterFilter || null,
            sort_by: sortBy,
            limit: limit
        };
        
        // Fetch results
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        loadingSpinner.style.display = 'none';
        
        if (!response.ok || !data.success) {
            showError(data.error || 'An error occurred during search');
            return;
        }
        
        if (data.results.length === 0) {
            noResultsDiv.style.display = 'block';
            return;
        }
        
        // Display results
        displayResults(data);
        
    } catch (error) {
        loadingSpinner.style.display = 'none';
        console.error('Search error:', error);
        showError('Failed to perform search. Please try again.');
    }
}

/* ==================== Display Results ==================== */
function displayResults(data) {
    // Update results info
    document.getElementById('results-count').textContent = data.total_results;
    document.getElementById('processing-time').textContent = 
        `Processing time: ${(data.processing_time * 1000).toFixed(0)}ms`;
    
    resultsInfo.style.display = 'block';
    
    // Clear previous results
    resultsContainer.innerHTML = '';
    
    // Create result cards
    data.results.forEach((result, index) => {
        const card = createResultCard(result, index);
        resultsContainer.appendChild(card);
    });
    
    // Hide no results message
    noResultsDiv.style.display = 'none';
    errorMessageDiv.style.display = 'none';
}

/* ==================== Create Result Card ==================== */
function createResultCard(result, index) {
    const card = document.createElement('div');
    card.className = 'result-card';
    card.style.animation = `slideUp 0.5s ease ${index * 0.05}s`;
    
    // Format relevance score (lower is better in L2 distance)
    const relevanceScore = Math.max(0, 100 - Math.min(result.relevance_score * 10, 100));
    
    // Create card HTML
    card.innerHTML = `
        <div class="result-card-header">
            <div style="flex: 1;">
                <div class="result-card-title">
                    <i class="fas fa-book-open" style="color: var(--primary-color); margin-right: 8px;"></i>
                    ${result.book}
                </div>
            </div>
            <div class="result-relevance">
                <i class="fas fa-star" style="color: var(--accent-color);"></i>
                ${relevanceScore.toFixed(0)}%
            </div>
        </div>
        
        <div class="result-card-content">
            ${result.english_hadith_highlighted ? `
                <div class="hadith-text-container">
                    <div class="hadith-text-label">English Text</div>
                    <div class="hadith-text">
                        ${result.english_hadith_highlighted}
                    </div>
                </div>
            ` : ''}
            
            ${result.arabic_hadith ? `
                <div class="hadith-text-container">
                    <div class="hadith-text-label">Arabic Text</div>
                    <div class="hadith-text arabic-text">
                        ${result.arabic_hadith}
                    </div>
                </div>
            ` : ''}
            
            ${result.english_math ? `
                <div class="hadith-text-container">
                    <div class="hadith-text-label">Meaning (English)</div>
                    <div class="hadith-text">
                        ${result.english_math}
                    </div>
                </div>
            ` : ''}
            
            ${result.arabic_math ? `
                <div class="hadith-text-container">
                    <div class="hadith-text-label">Meaning (Arabic)</div>
                    <div class="hadith-text arabic-text">
                        ${result.arabic_math}
                    </div>
                </div>
            ` : ''}
        </div>
        
        <div class="result-card-footer">
            <div class="footer-info">
                <strong>Chapter</strong>
                ${result.chapter_number}
            </div>
            <div class="footer-info">
                <strong>Section</strong>
                ${result.section_number}
            </div>
            <div class="footer-info">
                <strong>Grade (EN)</strong>
                ${result.english_grade}
            </div>
            <div class="footer-info">
                <strong>Grade (AR)</strong>
                ${result.arabic_grade}
            </div>
        </div>
    `;
    
    return card;
}

/* ==================== Show Error ==================== */
function showError(message) {
    resultsSection.style.display = 'block';
    statsSection.style.display = 'none';
    loadingSpinner.style.display = 'none';
    resultsInfo.style.display = 'none';
    noResultsDiv.style.display = 'none';
    errorMessageDiv.style.display = 'block';
    
    document.getElementById('error-text').textContent = message;
    resultsContainer.innerHTML = '';
    
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

/* ==================== Reset Search ==================== */
function resetSearch() {
    searchInput.value = '';
    resultsSection.style.display = 'none';
    statsSection.style.display = 'block';
    loadingSpinner.style.display = 'none';
    resultsInfo.style.display = 'none';
    resultsContainer.innerHTML = '';
    noResultsDiv.style.display = 'none';
    errorMessageDiv.style.display = 'none';
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
    searchInput.focus();
}

/* ==================== Event Listeners ==================== */
document.addEventListener('DOMContentLoaded', function() {
    // Auto-focus search input
    searchInput.focus();
    
    // Search on Enter
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSearch(e);
        }
    });
    
    // Handle filter changes - optionally re-search if already searched
    const filters = document.querySelectorAll('.filter-select');
    filters.forEach(filter => {
        filter.addEventListener('change', function() {
            if (resultsSection.style.display === 'block' && searchInput.value.trim()) {
                performSearch(searchInput.value.trim());
            }
        });
    });
});

/* ==================== Utility Functions ==================== */

// Smooth scroll to top
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Format date
function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
    } catch (e) {
        return dateString;
    }
}

// Truncate text
function truncateText(text, length) {
    if (text.length <= length) return text;
    return text.substring(0, length) + '...';
}

// Debounce search for autocomplete (if implemented)
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/* ==================== Accessibility ==================== */

// Add keyboard navigation
document.addEventListener('keydown', function(e) {
    // Ctrl+K or Cmd+K for search focus
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        searchInput.focus();
    }
    
    // Escape to clear results
    if (e.key === 'Escape' && resultsSection.style.display === 'block') {
        resetSearch();
    }
});

/* ==================== Load More / Pagination (Optional Enhancement) ==================== */
function loadMoreResults() {
    const currentLimit = parseInt(document.getElementById('limit-results').value);
    document.getElementById('limit-results').value = currentLimit + 10;
    performSearch(searchInput.value.trim());
}

/* ==================== Share Result (Optional Enhancement) ==================== */
function shareResult(resultIndex) {
    const result = currentResults[resultIndex];
    if (result) {
        const shareText = `Check out this Hadith: ${result.english_hadith.substring(0, 100)}...`;
        
        if (navigator.share) {
            navigator.share({
                title: 'Hadith Search Engine',
                text: shareText,
                url: window.location.href
            });
        } else {
            // Fallback: copy to clipboard
            navigator.clipboard.writeText(shareText);
            alert('Result copied to clipboard!');
        }
    }
}

console.log('✓ Script loaded successfully');
