    let scannedData = [];
    let registeredStudents = new Set();

    function domReady(fn) {
        if (document.readyState === "complete" || document.readyState === "interactive") {
            setTimeout(fn, 1);
        } else {
            document.addEventListener('DOMContentLoaded', fn);
        }
    }

    function loadRegisteredStudents() {
        fetch('/get-registered-students/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const tbody = document.querySelector('#registered-students-table');
                    tbody.innerHTML = '';
                    data.students.forEach((student, index) => {
                        const row = `<tr><td>${index + 1}</td><td>${student.student_id}</td></tr>`;
                        tbody.innerHTML += row;
                        registeredStudents.add(student.student_id);
                    });
                }
            })
            .catch(error => console.error('Error loading students:', error));
    }

    domReady(function() {
        var lastResult;
        var countResults = 0;
        var tableBody = document.querySelector("#scanned-data-table");

        loadRegisteredStudents();

        function onScanSuccess(decodeText) {
            if (decodeText !== lastResult && !registeredStudents.has(decodeText)) {
                countResults++;
                lastResult = decodeText;
                scannedData.push({ content: decodeText });

                const row = `<tr><td>${countResults}</td><td>${decodeText}</td></tr>`;
                tableBody.innerHTML += row;
            } else {
                alert(`Duplicate or already registered: ${decodeText}`);
            }
        }

        var htmlscanner = new Html5QrcodeScanner('my-qr-reader', { fps: 10, qrbox: 250 });
        htmlscanner.render(onScanSuccess);

        document.getElementById('save-data-button').addEventListener('click', () => {
            if (scannedData.length === 0) {
                alert('No data to save.');
                return;
            }

            fetch('/save-data/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify({ scannedData })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Data saved successfully!');
                    scannedData = [];
                    tableBody.innerHTML = '';
                    countResults = 0;
                    loadRegisteredStudents();
                } else {
                    alert('Failed to save data: ' + data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        });

        function getCsrfToken() {
            const name = 'csrftoken';
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const trimmed = cookie.trim();
                if (trimmed.startsWith(name + '=')) {
                    return trimmed.substring(name.length + 1);
                }
            }
            return '';
        }
    });