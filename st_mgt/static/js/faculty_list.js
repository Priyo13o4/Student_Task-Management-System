$(document).ready(function() {
    // Initialize Select2 for the courses field
    $('#id_courses').select2({
        placeholder: "Search and select courses...",
        allowClear: true,
        width: '100%',
        multiple: true
    });
});

function toggleMenu() {
    const menu = document.querySelector('.navbar-menu');
    menu.classList.toggle('active');
} 