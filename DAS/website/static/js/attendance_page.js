function saveAsPDF(tableId, unitName) {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    let table = document.getElementById(tableId);
    if (!table) {
        alert("Error: Table not found. Please check the table ID.");
        return;
    }

    let rows = table.rows;
    let data = [];

    for (let i = 0; i < rows.length; i++) {
        let row = [];
        let cols = rows[i].cells;
        for (let j = 0; j < cols.length; j++) {
            row.push(cols[j].innerText);
        }
        data.push(row);
    }

    doc.text(unitName + " Attendance", 20, 10);

    doc.autoTable({
        head: [data[0]],  
        body: data.slice(1),  
        startY: 20,
        didParseCell: function (data) {
            if (data.row.index >= 0) {  
                let cellText = data.cell.text[0];
                if (cellText === "Present") {
                    data.cell.styles.textColor = [0, 128, 0];  
                    data.cell.styles.fontStyle = "bold";
                } else if (cellText === "Absent") {
                    data.cell.styles.textColor = [255, 0, 0];  
                    data.cell.styles.fontStyle = "bold";
                }
            }
        }
    });

    doc.save(unitName.replace(/\s+/g, '_') + "_Attendance.pdf");
}

        function saveAsCSV(tableId, unitName) {
            let table = document.getElementById(tableId);
            let rows = table.rows;
            let csvContent = "";

            for (let i = 0; i < rows.length; i++) {
                let row = [];
                let cols = rows[i].cells;
                for (let j = 0; j < cols.length; j++) {
                    row.push('"' + cols[j].innerText + '"');
                }
                csvContent += row.join(",") + "\n";
            }

            let blob = new Blob([csvContent], { type: "text/csv" });
            let link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = unitName.replace(/\s+/g, '_') + "_Attendance.csv";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }