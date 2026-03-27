async function upload() {
    try {
      const file = document.getElementById("fileInput").files[0];
      const threshold = document.getElementById("threshold").value;
      const includeRevenue = document.getElementById("includeRevenue").checked;
  
      if (!file) {
        alert("Please upload a file first.");
        return;
      }
  
      const formData = new FormData();
      formData.append("file", file);
      formData.append("threshold", threshold);
      formData.append("include_revenue", includeRevenue);
  
      const res = await fetch("https://underspent-checker.onrender.com/analyze", {
        method: "POST",
        body: formData
      });
  
      if (!res.ok) {
        throw new Error("Server error");
      }
  
      const data = await res.json();
      const output = document.getElementById("output");
  
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
        const isLow = fund.spend_rate < 0.05;
  
        table += `
          <tr style="border-bottom:1px solid #eee;">
            <td style="padding:14px;">${fund.fund_id}</td>
            <td style="
              padding:14px;
              font-weight:${isLow ? '600' : '400'};
              color:${isLow ? '#d32f2f' : '#333'};
            ">
              ${(fund.spend_rate * 100).toFixed(2)}%
            </td>
            <td style="padding:14px;">${fund.avg_balance.toFixed(2)}</td>
            <td style="padding:14px;">${fund.avg_spend.toFixed(2)}</td>
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
          Something went wrong. Please try again.
        </div>
      `;
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