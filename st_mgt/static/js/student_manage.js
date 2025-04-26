// Function to enable/disable update button
function enableUpdateButton() {
    const updateButton = document.getElementById('updateButton');
    updateButton.disabled = false;
}

// Initialize select2 for course dropdown
$(document).ready(function() {
    $('.select2').select2({
        placeholder: "Search and select a course...",
        allowClear: true,
        width: '100%'
    });
});

// Handle course removal
document.querySelectorAll('.remove-course').forEach(button => {
    button.addEventListener('click', function(e) {
        e.preventDefault();
        const courseId = this.dataset.courseId;
        const studentId = this.dataset.studentId;
        
        if (confirm('Are you sure you want to remove this course?')) {
            fetch(`/students/${studentId}/remove_course/${courseId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove the course element from the list
                    this.closest('li').remove();
                    // Refresh the course dropdown
                    location.reload();
                } else {
                    alert('Error removing course: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while removing the course');
            });
        }
    });
}); 