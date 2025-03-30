        document.addEventListener('DOMContentLoaded', () => {
            const attendanceStatuses = {}; // Track attendance status
            const registeredStudents = new Set(); // Store registered student
            const attendanceResult = document.getElementById('attendanceTable');
            let attendanceData = [];

            // Fetch student data dynamically
            fetch('/get-data/', { method: 'GET' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const studentsTableBody = document.getElementById('studentsTableBody');
                        if (data.data.length === 0) {
                            studentsTableBody.innerHTML = '<tr><td colspan="3">No data available</td></tr>';
                        } else {
                            data.data.forEach((item, index) => {

                                // Add student ID to registeredStudents set
                                registeredStudents.add(item.content);
                                attendanceStatuses[item.content] = 'Absent';
                                const row = document.createElement('tr');
                                row.innerHTML = `
                                    <td>${index + 1}</td>
                                    <td>${item.content}</td>
                                    <td>
                                        <div class="form-check form-switch">
                                            <input class="form-check-input toggle-attendance" type="checkbox" id="toggle-${item.content}">
                                            <label class="form-check-label" for="toggle-${item.content}">Absent</label>
                                        </div>
                                    </td>
                                `;
                                studentsTableBody.appendChild(row);

                                // Add event listener for toggle
                                const toggleSwitch = document.getElementById(`toggle-${item.content}`);
                                toggleSwitch.addEventListener('change', (e) => {
                                    const label = e.target.nextElementSibling;
                                    if (e.target.checked) {
                                        label.textContent = 'Present';
                                        attendanceStatuses[item.content] = 'Present';
                                    } else {
                                        label.textContent = 'Absent';
                                        attendanceStatuses[item.content] = 'Absent';
                                    }
                                });
                            });
                        }
                    } else {
                        alert('Error fetching data: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                });

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

const csrfToken = getCookie('csrftoken');

function fetchAndDisplayBigTable() {
    const unitName = document.getElementById('unit_name').value;
    const year = document.getElementById('year').value;
    const semester = document.getElementById('semester').value;
    const year_record = document.getElementById('year_record').value;

    if (!unitName){
        alert('Please select a unit. ');
        return;
    }
    fetch(`/fetch-saved-attendance/?unit_name=${encodeURIComponent(unitName)}&year_record=${year_record}&semester=${semester}`, { method: 'GET' })


        .then(response => response.json())
        .then(data => {
            console.log('Fetched Data:', data);
            if (data.success) {
                const table = document.getElementById('bigAttendanceTable');
                const thead = table.querySelector('thead tr');
                const tbody = table.querySelector('tbody');

                // Clear existing rows
                tbody.innerHTML = '';
                while (thead.children.length > 3) {
                    thead.removeChild(thead.lastChild);
                }
                const uniqueLectures = [...new Set(data.lectures)].slice(0, 14);

                // Add lecture columns to the header
                uniqueLectures.forEach(lecture => {
                    const th = document.createElement('th');
                    th.textContent = lecture;
                    thead.appendChild(th);
                });


                // Populate rows with student data
                data.students.forEach((student, index) => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${index + 1}</td>
                        <td>${student.student_id}</td>
                        <td>${student.student_name}</td>
                    `;

                    // Add attendance for each lecture
                    uniqueLectures.forEach(lecture => {
                        const td = document.createElement('td');
                        td.textContent = student.lectures[lecture] || ''; // Empty if no data
                        row.appendChild(td);
                    });

                    tbody.appendChild(row);
                });
            } else {
                alert('Error fetching attendance records: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error fetching attendance records:', error);
        });
}

            // Save attendance for the current lecture
            document.getElementById('saveAttendanceBtn').addEventListener('click', () => {
                const unitName = document.getElementById('unit_name').value;
                const lectureId = document.getElementById('lecture_id').value;
                const semester = document.getElementById('semester').value;
                const year_record = document.getElementById('year_record').value;
                const attendancePayload = Array.from(document.querySelectorAll('#studentsTableBody tr')).map(row => {
                    const studentId = row.querySelector('td:nth-child(2)').textContent.trim();
                    const toggleSwitch = row.querySelector('.toggle-attendance');
                    return {
                        student_id: studentId,
                        is_present: toggleSwitch.checked
                    };
                });
                console.log('Attendance Payload: ', attendancePayload)
                console.log(lectureId)

                if (!unitName || !lectureId) {
                    alert('Please enter both Unit Name and Lecture Number.');
                    return;
                }

                fetch('/save-attendance/', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        unitName,
                        lecture_id: lectureId,
                        year_record: year_record,
                        attendance_entries: attendancePayload
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to save attendance');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        //alert('Attendance saved successfully!');
                        fetchAndDisplayBigTable(); // Fetch and display updated records
                        // Auto-select the next lecture
                        if (data.next_lecture) {
                            document.getElementById("lecture_id").value = data.next_lecture;
                        }
                    } else {
                        alert('Error saving attendance 2: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error saving attendance 3:', error);
                });
            });
 // Fetch saved attendance on page load
document.addEventListener('DOMContentLoaded', fetchAndDisplayBigTable);

            // QR Code Scanner
            const qrScanner = new Html5QrcodeScanner('qrScanner', { fps: 10, qrbox: 250 });
            qrScanner.render((decodedText) => {
                if (attendanceStatuses[decodedText] !== undefined) {
                    const toggleSwitch = document.getElementById(`toggle-${decodedText}`);
                    const label = toggleSwitch.nextElementSibling;

                    toggleSwitch.checked = true;
                    label.textContent = 'Present';
                    attendanceStatuses[decodedText] = 'Present';
                } else {
                    alert(`Student ID ${decodedText} is not in the list.`);
                }
            });
        });