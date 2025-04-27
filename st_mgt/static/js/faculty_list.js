$(document).ready(function() {
    // Initialize Select2 for the courses field
    $('#id_courses').select2({
        placeholder: "Search and select courses...",
        allowClear: true,
        width: '100%',
        multiple: true
    });

    // Add event listener for user field change
    $('#id_user').change(function() {
        updateEmail();
    });
});

function toggleMenu() {
    const menu = document.querySelector('.navbar-menu');
    menu.classList.toggle('active');
}

function updateEmail() {
    const userId = $('#id_user').val();
    if (userId) {
        fetch(`/faculty/api/user-email/${userId}/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.email) {
                $('#id_email').val(data.email);
            }
        })
        .catch(error => console.error('Error:', error));
    }
} 