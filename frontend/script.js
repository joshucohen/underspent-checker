async function upload() {
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
  
    const data = await res.json();
  
    const output = document.getElementById("output");
  
    if (data.length === 0) {
      output.innerHTML = "<p>No underspent funds found.</p>";
      return;
    }
  
    let table = `
      <table border="1" cellpadding="8" cellspacing="0">
        <tr>
          <th>Fund ID</th>
          <th>Spend Rate</th>
          <th>Avg Balance</th>
          <th>Avg Spend</th>
        </tr>
    `;
  
    data.forEach(fund => {
      table += `
        <tr>
          <td>${fund.fund_id}</td>
          <td>${(fund.spend_rate * 100).toFixed(2)}%</td>
          <td>${fund.avg_balance.toFixed(2)}</td>
          <td>${fund.avg_spend.toFixed(2)}</td>
        </tr>
      `;
    });
  
    table += "</table>";
  
    output.innerHTML = table;
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