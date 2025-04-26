document.addEventListener('DOMContentLoaded', function() {
    // Add click event listeners to all task status buttons
    document.querySelectorAll('[data-task-id]').forEach(button => {
        button.addEventListener('click', function() {
            const taskId = this.dataset.taskId;
            const status = this.dataset.status;
            updateTaskProgress(taskId, status);
        });
    });
});

function updateTaskProgress(taskId, status) {
    fetch(`/tasks/${taskId}/update-progress/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Reload the page to show updated status
            window.location.reload();
        } else {
            alert('Failed to update task status: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the task status.');
    });
}
