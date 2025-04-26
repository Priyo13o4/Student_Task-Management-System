// Handle course removal using event delegation
document.addEventListener('DOMContentLoaded', function() {
    const courseList = document.querySelector('.course-list');
    if (courseList) {
        courseList.addEventListener('click', function(event) {
            const removeButton = event.target.closest('.remove-course');
            if (removeButton) {
                const facultyId = removeButton.dataset.facultyId;
                const courseId = removeButton.dataset.courseId;
                removeCourse(facultyId, courseId);
            }
        });
    }
});

function removeCourse(facultyId, courseId) {
    if (confirm('Are you sure you want to remove this course?')) {
        fetch(`/faculty/remove-course/${facultyId}/${courseId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove the course element from the DOM
                const courseElement = document.querySelector(`[data-course-id="${courseId}"]`);
                if (courseElement) {
                    courseElement.remove();
                }
                
                // If no courses left, show the empty message
                const courseList = document.querySelector('.course-list');
                if (courseList && courseList.children.length === 0) {
                    const emptyMessage = document.createElement('li');
                    emptyMessage.textContent = 'No courses assigned yet.';
                    courseList.appendChild(emptyMessage);
                }

                // Show success message
                const messagesList = document.querySelector('.messages');
                if (!messagesList) {
                    // Create messages list if it doesn't exist
                    const messagesDiv = document.createElement('ul');
                    messagesDiv.className = 'messages';
                    document.body.insertBefore(messagesDiv, document.body.firstChild);
                }

                const messageElement = document.createElement('li');
                messageElement.className = 'success';
                messageElement.textContent = data.message;
                document.querySelector('.messages').appendChild(messageElement);

                // Remove the message after 3 seconds
                setTimeout(() => {
                    messageElement.remove();
                    // Remove the messages list if it's empty
                    const messagesList = document.querySelector('.messages');
                    if (messagesList && messagesList.children.length === 0) {
                        messagesList.remove();
                    }
                }, 3000);
            } else {
                alert('Failed to remove course: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while removing the course.');
        });
    }
}

// Helper function to get CSRF token
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
