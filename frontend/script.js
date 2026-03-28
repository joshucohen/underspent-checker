// =========================
// MAIN ANALYSIS FUNCTION
// =========================
async function upload() {
    const output = document.getElementById("output");
  
    try {
      const fileInput = document.getElementById("fileInput");
      const file = fileInput.files[0];
      const threshold = Number(document.getElementById("threshold").value);
      const includeRevenue = document.getElementById("includeRevenue").checked;
  
      // =========================
      // VALIDATION
      // =========================
  
      if (!file) {
        throw new Error("Please upload an Excel (.xlsx) file before analyzing.");
      }
  
      if (!file.name.toLowerCase().endsWith(".xlsx")) {
        throw new Error("Invalid file type. Please upload a valid Excel (.xlsx) file.");
      }
  
      if (isNaN(threshold) || threshold < 0 || threshold > 100) {
        throw new Error("Threshold must be a number between 0 and 100.");
      }
  
      // Clear previous results
      output.innerHTML = "";
  
      // =========================
      // API CALL
      // =========================
  
      const formData = new FormData();
      formData.append("file", file);
      formData.append("threshold", threshold);
      formData.append("include_revenue", includeRevenue);
  
      const res = await fetch("https://underspent-checker.onrender.com/analyze", {
        method: "POST",
        body: formData
      });
  
      const text = await res.text();
  
      if (!res.ok) {
        throw new Error(text || "Server error occurred.");
      }
  
      let data;
      try {
        data = JSON.parse(text);
      } catch {
        throw new Error("Unexpected response from server. Please try again.");
      }
  
      // =========================
      // NO RESULTS
      // =========================
      if (!data || data.length === 0) {
        output.innerHTML = `
          <div style="padding:16px; color:#555;">
            No underspent funds found based on your selected threshold.
          </div>
        `;
        scrollToResults();
        return;
      }
  
      // =========================
      // SORT DATA (lowest first)
      // =========================
      data.sort((a, b) => a.spend_rate - b.spend_rate);
  
      // =========================
      // BUILD TABLE
      // =========================
      let table = `
        <table style="
          width:100%;
          table-layout: fixed;
          border-collapse: collapse;
          margin-top: 20px;
          font-size: 16px;
          background: white;
          border-radius: 8px;
          overflow: hidden;
        ">
          <thead>
            <tr style="background-color:#f4f6f8; border-bottom:2px solid #ddd;">
              <th style="padding:14px; text-align:left;">Fund ID</th>
              <th style="padding:14px; text-align:left;">Spend Rate</th>
              <th style="padding:14px; text-align:left;">Avg Balance</th>
              <th style="padding:14px; text-align:left;">Avg Spend</th>
            </tr>
          </thead>
          <tbody>
      `;
  
      data.forEach(fund => {
        const spendRate = Number(fund.spend_rate) || 0;
        const avgBalance = Number(fund.avg_balance) || 0;
        const avgSpend = Number(fund.avg_spend) || 0;
  
        const isLow = spendRate < 0.05;
  
        table += `
          <tr style="border-bottom:1px solid #eee;">
            <td style="padding:14px;">${fund.fund_id}</td>
            <td style="
              padding:14px;
              font-weight:${isLow ? '600' : '400'};
              color:${isLow ? '#d32f2f' : '#333'};
            ">
              ${(spendRate * 100).toFixed(2)}%
            </td>
            <td style="padding:14px;">${avgBalance.toFixed(2)}</td>
            <td style="padding:14px;">${avgSpend.toFixed(2)}</td>
          </tr>
        `;
      });
  
      table += `
          </tbody>
        </table>
      `;
  
      output.innerHTML = table;
  
      scrollToResults();
  
    } catch (err) {
      console.error(err);
      showError(err.message || "Something went wrong. Please try again.");
    }
  }
  
  
  // =========================
  // SCROLL HELPER
  // =========================
  function scrollToResults() {
    const section = document.getElementById("resultsSection");
    if (section) {
      setTimeout(() => {
        section.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
    }
  }
  
  
  // =========================
  // ERROR HANDLING
  // =========================
  function showError(message) {
    const output = document.getElementById("output");
  
    output.innerHTML = `
      <div style="
        padding:16px;
        color:#b91c1c;
        background:#fee2e2;
        border:1px solid #fecaca;
        border-radius:8px;
      ">
        ${message}
      </div>
    `;
  }
  
  
  // =========================
  // COPY RESULTS (EXCEL READY)
  // =========================
  function copyResults() {
    const table = document.querySelector("#output table");
  
    if (!table) {
      alert("No results to copy.");
      return;
    }
  
    let text = "";
  
    for (let row of table.rows) {
      let rowData = [];
      for (let cell of row.cells) {
        rowData.push(cell.innerText.trim());
      }
      text += rowData.join("\t") + "\n";
    }
  
    navigator.clipboard.writeText(text);
    alert("Copied in Excel-ready format!");
  }
  
  
  // =========================
  // TEMPLATE DOWNLOAD
  // =========================
  function downloadTemplate() {
    const wb = XLSX.utils.book_new();
  
    const headers = [["fund_id", "balance", "spend", "revenue"]];
    const sheets = ["Year1", "Year2", "Year3"];
  
    sheets.forEach(name => {
      const ws = XLSX.utils.aoa_to_sheet(headers);
      XLSX.utils.book_append_sheet(wb, ws, name);
    });
  
    XLSX.writeFile(wb, "underspent_template.xlsx");
  }