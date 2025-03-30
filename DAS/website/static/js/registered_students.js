    function loadRegisteredStudents() {
        fetch('/get-registered-students/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const tbody = document.querySelector('#registered-students-table');
                    tbody.innerHTML = ''; 
                    data.students.forEach((student, index) => {
                        const row = document.createElement("tr");
                        row.innerHTML = `
                            <td>${index + 1}</td>
                            <td>${student.student_id}</td>
                            <td><button class="btn btn-danger btn-sm" onclick="deleteStudent('${student.student_id}')">Delete</button></td>
                        `;
                        tbody.appendChild(row);
                    });
                }
            })
            .catch(error => console.error('Error loading students:', error));
    }

    function deleteStudent(studentId) {
        const encodedStudentId = encodeURIComponent(studentId).replace(/\//g, "%2F");

        if (confirm(`Are you sure you want to delete student ID: ${studentId}?`)) {
            fetch(`/delete-student/${encodedStudentId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`Student ID: ${studentId} deleted successfully!`);
                    loadRegisteredStudents();  // Refresh student list
                } else {
                    alert(`Failed to delete student ID: ${studentId}. Error: ` + data.error);
                }
            })
            .catch(error => console.error('Error deleting student:', error));
        }
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    document.addEventListener('DOMContentLoaded', loadRegisteredStudents);