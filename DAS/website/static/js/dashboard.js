function viewStudentProgress(studentId, studentName, selectedYear, selectedSemester) { 
    fetch(`/student-progress/${studentId}/?year_semester=${selectedYear}-${selectedSemester}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("student-name-title").innerText = studentName;

            const chartsContainer = document.querySelector(".charts-container");
            chartsContainer.innerHTML = ""; // Clear previous charts

            if (data.units.length > 0) {
                document.getElementById("close-button").style.display = "block"; // Show close button
            } else {
                document.getElementById("close-button").style.display = "none"; // Hide close button if no charts
            }

            data.units.forEach(unit => {
                // Create a div for each chart
                const chartWrapper = document.createElement("div");
                chartWrapper.classList.add("chart-wrapper");

                // Create a canvas for the chart
                const canvas = document.createElement("canvas");
                canvas.id = `chart-${unit.id}`;
                chartWrapper.appendChild(canvas);

                // Add label below the chart
                const label = document.createElement("div");
                label.classList.add("chart-label");
                label.innerText = unit.name;
                chartWrapper.appendChild(label);

                chartsContainer.appendChild(chartWrapper);

                // Chart data
                const chartData = {
                    labels: ["Attended", "Missed"],
                    datasets: [{
                        data: [unit.attended, unit.missed],
                        backgroundColor: ["#4CAF50", "#E0E0E0"]
                    }]
                };

                // Create the chart
                const ctx = canvas.getContext("2d");
                new Chart(ctx, {
                    type: "doughnut",
                    data: chartData
                });
            });

            document.getElementById("student-progress-card").style.display = "block"; // Show card
        })
        .catch(error => console.error("Error fetching student progress:", error));
}

function closeProgressCard() {
    document.getElementById("student-progress-card").style.display = "none";
    document.getElementById("close-button").style.display = "none"; // Hide close button when card is closed
}


