$(document).ready(function() {
    // Dark mode functionality
    function setDarkMode(on) {
        if(on) {
            document.body.classList.add('dark-mode');
            document.getElementById('darkModeToggle').innerText = 'Light Mode';
        } else {
            document.body.classList.remove('dark-mode');
            document.getElementById('darkModeToggle').innerText = 'Dark Mode';
        }
    }

    // Initialize dark mode
    let dark = localStorage.getItem('darkMode');
    if(dark === null) dark = 'true';
    setDarkMode(dark === 'true');

    // Dark mode toggle event listener
    document.getElementById('darkModeToggle').onclick = function() {
        const isDark = !document.body.classList.contains('dark-mode');
        setDarkMode(isDark);
        localStorage.setItem('darkMode', isDark);
    };

    // Initialize Select2
    $('#id_assigned_to').select2({
        placeholder: "Select students...",
        allowClear: true,
        width: '100%'
    });

    // Select All button functionality
    $('#selectAllBtn').click(function() {
        $('#id_assigned_to option').prop('selected', true);
        $('#id_assigned_to').trigger('change');
    });

    // Clear All button functionality
    $('#clearAllBtn').click(function() {
        $('#id_assigned_to option').prop('selected', false);
        $('#id_assigned_to').trigger('change');
    });

    let currentGradeId = null;
    let currentStudentItem = null;

    // Initialize Select2
    $('#gradeSelect').select2({
        dropdownParent: $('#gradeModal')
    });

    // Handle search
    $('#searchInput').on('input', function() {
        const searchText = $(this).val().toLowerCase();
        filterStudents();
    });

    // Handle grade filter
    $('#gradeFilter').on('change', function() {
        filterStudents();
    });

    function filterStudents() {
        const searchText = $('#searchInput').val().toLowerCase();
        const gradeFilter = $('#gradeFilter').val();
        
        $('.student-item').each(function() {
            const studentName = $(this).find('h6').text().toLowerCase();
            const studentId = $(this).find('small').text().toLowerCase();
            const isPending = $(this).find('.status-badge').hasClass('pending');
            
            const matchesSearch = studentName.includes(searchText) || studentId.includes(searchText);
            const matchesFilter = gradeFilter === 'all' || 
                                (gradeFilter === 'pending' && isPending) ||
                                (gradeFilter === 'graded' && !isPending);
            
            $(this).toggle(matchesSearch && matchesFilter);
        });
    }

    // Handle grade assignment
    $('.assign-grade-btn').click(function() {
        currentStudentItem = $(this).closest('.student-item');
        currentGradeId = currentStudentItem.data('grade-id');
        const studentName = currentStudentItem.find('h6').text();
        const studentId = currentStudentItem.find('small').text();
        
        $('#studentInfo').html(`
            <h6>Student: ${studentName}</h6>
            <p class="text-muted">${studentId}</p>
        `);
        $('#gradeSelect').val('').trigger('change');
    });

    // Save grade
    $('#saveGradeBtn').click(function() {
        const grade = $('#gradeSelect').val();
        if (!grade) {
            alert('Please select a grade');
            return;
        }

        if (!confirm('Are you sure you want to assign this grade? This action cannot be undone.')) {
            return;
        }

        $.ajax({
            url: `/users/faculty/grades/${currentGradeId}/assign/`,
            method: 'POST',
            data: {
                grade: grade,
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function(response) {
                if (response.success) {
                    // Update the UI
                    currentStudentItem.find('.status-badge')
                        .removeClass('pending')
                        .addClass('graded')
                        .text('Grade: ' + grade);
                    currentStudentItem.find('.assign-grade-btn').remove();
                    
                    // Close modal
                    $('#gradeModal').modal('hide');
                    
                    // Show success message
                    alert('Grade assigned successfully!');
                } else {
                    alert('Error assigning grade: ' + response.error);
                }
            },
            error: function() {
                alert('Error assigning grade. Please try again.');
            }
        });
    });
}); 