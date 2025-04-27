document.addEventListener('DOMContentLoaded', function() {
    // Add click event listeners to all task status buttons
    document.querySelectorAll('[data-task-id]').forEach(button => {
        button.addEventListener('click', function() {
            const taskId = this.dataset.taskId;
            const status = this.dataset.status;
            updateTaskProgress(taskId, status, this);
        });
    });
});

function updateTaskProgress(taskId, status, button) {
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
            // Update the button styles in the DOM
            const btnGroup = button.closest('.btn-group');
            btnGroup.querySelectorAll('button').forEach(btn => {
                btn.classList.remove('btn-warning', 'btn-primary', 'btn-success', 'btn-outline-warning', 'btn-outline-primary', 'btn-outline-success');
                if (btn.dataset.status === status) {
                    if (status === 'Pending') btn.classList.add('btn-warning');
                    else if (status === 'In Progress') btn.classList.add('btn-primary');
                    else if (status === 'Completed') btn.classList.add('btn-success');
                } else {
                    if (btn.dataset.status === 'Pending') btn.classList.add('btn-outline-warning');
                    else if (btn.dataset.status === 'In Progress') btn.classList.add('btn-outline-primary');
                    else if (btn.dataset.status === 'Completed') btn.classList.add('btn-outline-success');
                }
            });
            // Update the status in the DOM for this task
            button.closest('.task-item').setAttribute('data-current-status', status);
            // Recalculate and update stats
            updateDashboardStats();
        } else {
            alert('Failed to update task status: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the task status.');
    });
}

function updateDashboardStats() {
    // Count tasks by status in the DOM
    let pending = 0, inprogress = 0, completed = 0, total = 0;
    document.querySelectorAll('.task-item').forEach(item => {
        let status = 'Pending';
        // Try to get status from the active button
        const btnGroup = item.querySelector('.btn-group');
        if (btnGroup) {
            btnGroup.querySelectorAll('button').forEach(btn => {
                if (btn.classList.contains('btn-warning')) status = 'Pending';
                if (btn.classList.contains('btn-primary')) status = 'In Progress';
                if (btn.classList.contains('btn-success')) status = 'Completed';
            });
        }
        if (status === 'Pending') pending++;
        if (status === 'In Progress') inprogress++;
        if (status === 'Completed') completed++;
        total++;
    });
    // Update the numbers in the stat cards
    document.querySelectorAll('.stat-label').forEach(label => {
        if (label.textContent.includes('Pending Tasks')) {
            label.previousElementSibling.textContent = pending;
        }
        if (label.textContent.includes('In Progress Tasks')) {
            label.previousElementSibling.textContent = inprogress;
        }
        if (label.textContent.includes('Completed Tasks')) {
            label.previousElementSibling.textContent = completed;
        }
        if (label.textContent.includes('Total Tasks')) {
            label.previousElementSibling.textContent = total;
        }
    });
}
