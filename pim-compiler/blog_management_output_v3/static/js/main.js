
// Basic CRUD operations
async function fetchData(endpoint) {
    const response = await fetch(`/api/${endpoint}`);
    return await response.json();
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Load data based on current page
    const path = window.location.pathname.split('/')[1];
    if (path && path !== '') {
        loadPageData(path);
    }
});

async function loadPageData(page) {
    const data = await fetchData(page);
    const table = document.getElementById(`${page}-table`);
    // Populate table with data
    // ...
}
