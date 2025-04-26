// Function to toggle the navbar menu
function toggleMenu() {
    const menu = document.querySelector('.navbar-menu');
    menu.classList.toggle('active');
}

$(document).ready(function() {
    // Initialize Select2
    $('#id_assigned_to').select2({
        placeholder: "Search and select students...",
        allowClear: true,
        width: '100%'
    });

    // Handle Select All button
    $('#selectAllBtn').click(function() {
        $('#id_assigned_to option').prop('selected', true);
        $('#id_assigned_to').trigger('change');
    });

    // Handle Clear All button
    $('#clearAllBtn').click(function() {
        $('#id_assigned_to').val(null).trigger('change');
    });
}); 