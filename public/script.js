// Globals for Charts
let bodeMagChartInstance = null;
let bodePhaseChartInstance = null;
let validationChartInstance = null;
let timeSeriesChartInstance = null;

// D3.js Workbench Setup
const workbenchArea = d3.select("#workbench-area");
const width = 300;
const height = 100;

const svg = workbenchArea.append("svg")
    .attr("width", "100%")
    .attr("height", "100%")
    .attr("viewBox", `0 0 ${width} ${height}`);

// Simulated Physical Blocks Data
const blocks = [
    { id: "m1", type: "Mass", value: 2.0, x: 50, y: 50 },
    { id: "k1", type: "Spring", value: 10.0, x: 150, y: 50 },
    { id: "c1", type: "Damper", value: 1.5, x: 250, y: 50 }
];

// Define drop shadow filter for D3 elements to match Claymorphism vaguely
const defs = svg.append("defs");
const filter = defs.append("filter")
    .attr("id", "clay-shadow")
    .attr("x", "-20%")
    .attr("y", "-20%")
    .attr("width", "140%")
    .attr("height", "140%");

filter.append("feDropShadow")
    .attr("dx", "4")
    .attr("dy", "4")
    .attr("stdDeviation", "4")
    .attr("flood-color", "rgba(0,0,0,0.5)");

// Create Blocks
const node = svg.selectAll(".node")
    .data(blocks)
    .enter().append("g")
    .attr("class", "node")
    .attr("transform", d => `translate(${d.x},${d.y})`)
    .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

// Pill Shape
node.append("rect")
    .attr("width", 80)
    .attr("height", 40)
    .attr("rx", 20)
    .attr("ry", 20)
    .attr("x", -40)
    .attr("y", -20)
    .style("fill", "#ffffff")
    .style("stroke", "#7ed321")
    .style("stroke-width", "2px")
    .attr("filter", "url(#clay-shadow)");

// Text
node.append("text")
    .attr("dy", 5)
    .attr("text-anchor", "middle")
    .style("fill", "#2c3e50")
    .style("font-family", "sans-serif")
    .style("font-size", "12px")
    .style("pointer-events", "none")
    .text(d => `${d.type}\n${d.value}`);

function dragstarted(event, d) {
    d3.select(this).raise().classed("active", true);
}

function dragged(event, d) {
    d.x = event.x;
    d.y = event.y;
    d3.select(this).attr("transform", `translate(${d.x},${d.y})`);
}

function dragended(event, d) {
    d3.select(this).classed("active", false);
}

// ---------------------------------------------------------
// Chart.js Default Config overrides
Chart.defaults.color = '#2c3e50';
Chart.defaults.borderColor = 'rgba(0, 0, 0, 0.1)';

// Generic Chart setup function
function createChart(ctxId, type, data, options) {
    const ctx = document.getElementById(ctxId).getContext('2d');
    return new Chart(ctx, {
        type: type,
        data: data,
        options: options
    });
}

// ---------------------------------------------------------
// API Calls

async function simulateSystem() {
    // Send standard mechanical blocks payload to backend
    const payload = {
        domain: "mechanical",
        components: blocks.map(b => ({ type: b.type, name: b.id, value: b.value })),
        t_end: 10.0,
        u_type: "step"
    };

    try {
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error("Simulation failed");

        const data = await response.json();
        plotTimeSeries(data.t, data.y, "Simulated Displacement", data.u, "Input Force");

    } catch (err) {
        console.error(err);
        alert("Simulation error: " + err.message);
    }
}

let sampleFileObj = null;

function useSampleData() {
    // Generate a simple step response of a 2nd order system
    let csvContent = "";
    let dt = 0.1;
    let t = 0;
    // Difference equation: y[k] = 1.5 y[k-1] - 0.7 y[k-2] + 0.1 u[k-1] + 0.05 u[k-2]
    let y1 = 0, y2 = 0;
    let u1 = 0, u2 = 0;
    
    for (let i = 0; i < 100; i++) {
        let u = t >= 1.0 ? 1.0 : 0.0;
        let y = 1.5 * y1 - 0.7 * y2 + 0.1 * u1 + 0.05 * u2;
        // add some noise
        y += (Math.random() - 0.5) * 0.05;
        
        csvContent += `${t.toFixed(2)},${u.toFixed(2)},${y.toFixed(4)}\n`;
        
        y2 = y1;
        y1 = y;
        u2 = u1;
        u1 = u;
        t += dt;
    }
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    sampleFileObj = new File([blob], "sample_data.csv", { type: "text/csv" });
    
    document.querySelector('label[for="csv-upload"]').innerText = "Sample Data Generated & Selected ✅";
    document.getElementById('csv-upload').value = ""; // Clear file input
}

// Attach event listener so manual uploads clear out the sample data
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById('csv-upload').addEventListener('change', function() {
        if(this.files.length > 0) {
            sampleFileObj = null;
            document.querySelector('label[for="csv-upload"]').innerText = `Selected: ${this.files[0].name}`;
        } else {
            document.querySelector('label[for="csv-upload"]').innerText = "Upload CSV (time, u, y)";
        }
    });
});

async function identifySystem() {
    const fileInput = document.getElementById('csv-upload');
    const na = document.getElementById('na').value;
    const nb = document.getElementById('nb').value;
    const nk = document.getElementById('nk').value;

    let fileToUpload = null;
    if (fileInput.files.length > 0) {
        fileToUpload = fileInput.files[0];
    } else if (sampleFileObj) {
        fileToUpload = sampleFileObj;
    }

    if (!fileToUpload) {
        alert("Please upload a CSV file or click 'Use Sample Data' first.");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileToUpload);
    formData.append("na", na);
    formData.append("nb", nb);
    formData.append("nk", nk);

    try {
        const response = await fetch('/api/identify', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errBody = await response.json();
            throw new Error(errBody.detail || "Identification failed");
        }

        const data = await response.json();

        plotBode(data.bode.w, data.bode.mag, data.bode.phase);
        plotValidation(data.validation.lags, data.validation.r_ee);
        plotTimeSeries(data.simulation.t, data.simulation.y, "Original Output", data.simulation.y_sim, "ARX Simulation", true);

    } catch (err) {
        console.error(err);
        alert("Identification error: " + err.message);
    }
}

// ---------------------------------------------------------
// Plotting Functions

function plotTimeSeries(t, y1, label1, y2, label2, isComparison = false) {
    if (timeSeriesChartInstance) timeSeriesChartInstance.destroy();

    const datasets = [{
        label: label1,
        data: y1,
        borderColor: '#7ed321',
        backgroundColor: 'transparent',
        borderWidth: 2,
        pointRadius: 0
    }];

    if (y2) {
        datasets.push({
            label: label2,
            data: y2,
            borderColor: '#f5a623',
            borderDash: isComparison ? [5, 5] : [],
            backgroundColor: 'transparent',
            borderWidth: 2,
            pointRadius: 0
        });
    }

    timeSeriesChartInstance = createChart('timeSeriesChart', 'line', {
        labels: t.map(v => v.toFixed(2)),
        datasets: datasets
    }, {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: { title: { display: true, text: 'Time (s)' } },
            y: { title: { display: true, text: 'Value' } }
        }
    });
}

function plotBode(w, mag, phase) {
    if (bodeMagChartInstance) bodeMagChartInstance.destroy();
    if (bodePhaseChartInstance) bodePhaseChartInstance.destroy();

    // Mag
    bodeMagChartInstance = createChart('bodeMagChart', 'line', {
        labels: w.map(v => v.toFixed(3)),
        datasets: [{
            label: 'Magnitude |H(e^jw)|',
            data: mag.map(m => 20 * Math.log10(m)), // dB
            borderColor: '#7ed321',
            borderWidth: 2,
            pointRadius: 0
        }]
    }, {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: { type: 'logarithmic', title: { display: true, text: 'Frequency (rad/s)' } },
            y: { title: { display: true, text: 'Magnitude (dB)' } }
        }
    });

    // Phase
    bodePhaseChartInstance = createChart('bodePhaseChart', 'line', {
        labels: w.map(v => v.toFixed(3)),
        datasets: [{
            label: 'Phase (deg)',
            data: phase,
            borderColor: '#f5a623',
            borderWidth: 2,
            pointRadius: 0
        }]
    }, {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: { type: 'logarithmic', title: { display: true, text: 'Frequency (rad/s)' } },
            y: { title: { display: true, text: 'Phase (deg)' } }
        }
    });
}

function plotValidation(lags, r_ee) {
    if (validationChartInstance) validationChartInstance.destroy();

    // 99% confidence interval approx: +/- 2.58 / sqrt(N)
    // Assume N is roughly constant, set a dummy boundary for visual
    const confInt = 0.1; // Hardcoded purely for visual reference in this demo

    validationChartInstance = createChart('validationChart', 'bar', {
        labels: lags,
        datasets: [
            {
                label: 'Auto-correlation',
                data: r_ee,
                backgroundColor: '#7ed321'
            },
            {
                type: 'line',
                label: '99% Confidence Boundary',
                data: Array(lags.length).fill(confInt),
                borderColor: 'rgba(255, 0, 0, 0.5)',
                borderWidth: 1,
                borderDash: [5, 5],
                pointRadius: 0,
                fill: false
            },
            {
                type: 'line',
                label: '-99% Confidence Boundary',
                data: Array(lags.length).fill(-confInt),
                borderColor: 'rgba(255, 0, 0, 0.5)',
                borderWidth: 1,
                borderDash: [5, 5],
                pointRadius: 0,
                fill: false
            }
        ]
    }, {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: { title: { display: true, text: 'Lag' } },
            y: {
                title: { display: true, text: 'Correlation' },
                min: -1,
                max: 1
            }
        }
    });
}
