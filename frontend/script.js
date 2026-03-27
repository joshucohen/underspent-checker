async function upload() {
    const file = document.getElementById("fileInput").files[0];
    const threshold = document.getElementById("threshold").value;
    const includeRevenue = document.getElementById("includeRevenue").checked;
  
    const formData = new FormData();
    formData.append("file", file);
    formData.append("threshold", threshold);
    formData.append("include_revenue", includeRevenue);
  
    const res = await fetch("https://underspent-checker.onrender.com/analyze", {
      method: "POST",
      body: formData
    });
  
    const data = await res.json();
  
    if (data.length === 0) {
      document.getElementById("output").textContent = "No underspent funds found.";
    } else {
      document.getElementById("output").textContent =
        JSON.stringify(data, null, 2);
    }
  }

  function copyResults() {
    const text = document.getElementById("output").textContent;
    navigator.clipboard.writeText(text);
    alert("Copied to clipboard");
  }