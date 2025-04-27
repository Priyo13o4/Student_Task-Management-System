$(document).ready(function() {
    // Function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Function to handle deletion with confirmation
    function handleDelete(url, successMessage, errorMessage, redirectUrl = null) {
        if (confirm('Are you sure you want to delete this item?')) {
            $.ajax({
                url: url,
                type: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                success: function(response) {
                    // Check if response is a string (parse it) or already an object
                    const responseData = typeof response === 'string' ? JSON.parse(response) : response;
                    
                    if (responseData.success) {
                        // Show success message
                        alert(successMessage);
                        // Redirect if URL is provided
                        if (redirectUrl) {
                            window.location.replace(redirectUrl);
                        } else {
                            window.location.reload();
                        }
                    } else {
                        alert(errorMessage);
                    }
                },
                error: function(xhr, status, error) {
                    alert('An error occurred while deleting the item.');
                }
            });
        }
    }

    // Handle course deletion
    $('.delete-button[data-course-id]').click(function(e) {
        e.preventDefault();
        const courseId = $(this).data('course-id');
        handleDelete(
            `/courses/${courseId}/delete/`,
            'Course deleted successfully!',
            'Failed to delete course.',
            '/courses/'  // Redirect to course list
        );
    });

    // Handle student deletion
    $('.delete-button[data-student-id]').click(function(e) {
        e.preventDefault();
        const studentId = $(this).data('student-id');
        handleDelete(
            `/students/${studentId}/delete/`,
            'Student deleted successfully!',
            'Failed to delete student.',
            '/students/'  // Redirect to student list
        );
    });

    // Handle faculty deletion
    $('.delete-button[data-faculty-id]').click(function(e) {
        e.preventDefault();
        const facultyId = $(this).data('faculty-id');
        handleDelete(
            `/faculty/delete/${facultyId}/`,
            'Faculty member deleted successfully!',
            'Failed to delete faculty member.',
            '/faculty/faculty_list/'  // Redirect to faculty list
        );
    });

    // Handle task deletion
    $('.delete-button[data-task-id]').click(function(e) {
        e.preventDefault();
        const taskId = $(this).data('task-id');
        handleDelete(
            `/tasks/${taskId}/delete/`,
            'Task deleted successfully!',
            'Failed to delete task.',
            '/tasks/'  // Redirect to task list
        );
    });
}); 