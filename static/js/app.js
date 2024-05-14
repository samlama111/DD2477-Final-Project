// app.js might handle AJAX-based searches
function searchBooks() {
    const query = document.getElementById('searchQuery').value;
    fetch(`/search?query=${query}`)
        .then(response => response.json())
        .then(data => {
            console.log(data);  // Update the DOM with search results
        });
}
