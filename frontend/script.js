async function upload() {
    const output = document.getElementById("output");
    const button = document.querySelector("button[onclick='upload()']");
  
    try {
      const file = document.getElementById("fileInput").files[0];
      const threshold = document.getElementById("threshold").value;
      const includeRevenue = document.getElementById("includeRevenue").checked;
  
      if (!file) {
        alert("Please upload an Excel (.xlsx) file.");
        return;
      }
  
      // ✅ Enforce Excel only (frontend validation)
      if (!file.name.toLowerCase().endsWith(".xlsx")) {
        alert("Only Excel (.xlsx) files are supported. File must contain 3 sheets: Year1, Year2, Year3.");
        return;
      }
  
      // ✅ Loading state
      output.innerHTML = `
        <div style="padding:16px; color:#555;">
          Analyzing...
        </div>
      `;
      button.disabled = true;
  
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
        throw new Error(text || "Server error");
      }
  
      let data;
      try {
        data = JSON.parse(text);
      } catch {
        throw new Error("Invalid response from server");
      }
  
      if (!data || data.length === 0) {
        output.innerHTML = `
          <div style="padding:16px; color:#555;">
            No underspent funds found.
          </div>
        `;
        return;
      }
  
      let table = `
        <table style="
          width:100%;
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
  
    } catch (err) {
      console.error(err);
      document.getElementById("output").innerHTML = `
        <div style="padding:16px; color:red;">
          ${err.message || "Something went wrong. Please try again."}
        </div>
      `;
    } finally {
      const button = document.querySelector("button[onclick='upload()']");
      if (button) button.disabled = false;
    }
  }
  
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
        rowData.push(cell.innerText);
      }
      text += rowData.join("\t") + "\n";
    }
  
    navigator.clipboard.writeText(text);
    alert("Copied as table (paste into Excel)");
  }
  
  // ✅ CORRECT TEMPLATE: 3-sheet Excel (NO DATA, headers only)
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