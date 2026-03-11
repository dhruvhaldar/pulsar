# Pulsar ✨

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Vercel](https://img.shields.io/badge/vercel-%23000000.svg?style=flat&logo=vercel&logoColor=white)](https://vercel.com/)
[![Three.js](https://img.shields.io/badge/threejs-black?style=flat&logo=three.js&logoColor=white)](https://threejs.org/)
[![Chart.js](https://img.shields.io/badge/chart.js-F5788D.svg?style=flat&logo=chart.js&logoColor=white)](https://www.chartjs.org/)

**Pulsar** is an educational system identification and physical modeling workbench. Designed with a stunning Space-Themed Claymorphism UI, it provides an interactive platform to simulate physical models and perform data-driven system identification directly from your browser.

## Features

- ⚛️ **Physical Modeling**: Construct mechanical (Mass, Spring, Damper) or electrical (Resistor, Inductor, Capacitor) systems. Simulates the dynamics using a custom Differential-Algebraic Equation (DAE) solver.
- 📈 **Data-Driven Identification**: Upload CSV data containing time, input (u), and output (y) signals to perform ARX (AutoRegressive with eXogenous input) model estimation.
- 🌌 **Space-Themed Claymorphism UI**: A beautifully crafted frontend featuring a dark space background with a Three.js starfield and floating, matte 3D inflated UI elements.
- 📊 **Interactive Charts**: Visualize Time Series, Bode Plots (Magnitude & Phase), and Validation Residual Autocorrelation using Chart.js.
- 🚀 **Vercel Ready**: Architected for seamless deployment on Vercel with a serverless FastAPI Python backend and static frontend.

## Technology Stack

### Backend
- **Python 3.11+**
- **FastAPI**: High-performance serverless API framework.
- **NumPy & SciPy**: Powerful scientific computing for DAE solving and ARX estimation.
- **Pytest**: For robust unit testing.

### Frontend
- **Vanilla JavaScript (ES6+), HTML5, CSS3**
- **Three.js**: Renders the immersive 3D starfield background.
- **Chart.js**: Powers the interactive data visualization charts.
- **D3.js**: Data manipulation and visualization support.

## Project Structure

```text
pulsar/
├── api/
│   └── index.py            # FastAPI serverless entry point
├── public/                 # Static frontend assets
│   ├── index.html          # Main application UI
│   ├── style.css           # General layout & styling
│   ├── clay.css            # Claymorphism UI styles
│   ├── script.js           # Frontend logic and API integration
│   └── three_bg.js         # Three.js starfield animation
├── pulsar/                 # Core Python backend library
│   ├── dae_solver.py       # Differential-Algebraic Equation Solver
│   ├── identification.py   # ARX Model Estimation and Simulation
│   ├── physics.py          # Physical component definitions
│   └── validation.py       # Auto/Cross-correlation validation utilities
├── tests/                  # Pytest test suite
│   ├── test_identification.py
│   └── test_physics.py
├── requirements.txt        # Python dependencies
└── vercel.json             # Vercel deployment configuration
```

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dhruvhaldar/pulsar.git
   cd pulsar
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   ./venv/Scripts/activate  # On Windows: .\venv\Scripts\Activate.ps1
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

To start the local development server:

```bash
python -m uvicorn api.index:app --reload
```

The FastAPI backend will run on `http://127.0.0.1:8000`.
To view the frontend, you can simply open `public/index.html` in your web browser, or serve it using a simple HTTP server:

```bash
cd public
python -m http.server 3000
```
Then navigate to `http://localhost:3000`.

### Running Tests

The project includes a comprehensive test suite using `pytest`. To run the tests, execute:

```bash
python -m pytest tests/
```

## Deployment

Pulsar is optimized for deployment on Vercel.
Simply connect your repository to Vercel, and the provided `vercel.json` configuration will handle routing the `api/` requests to the serverless FastAPI functions and serving the `public/` folder as static assets.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
Copyright (c) 2026 Dhruv Haldar
