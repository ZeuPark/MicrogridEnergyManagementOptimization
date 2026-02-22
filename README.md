# Microgrid Energy Management Optimization

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A linear programming-based optimization framework for residential microgrid battery dispatch scheduling. This project minimizes electricity costs by optimally scheduling battery charging and discharging based on solar generation forecasts, load profiles, and time-varying electricity prices.

## Project Overview

This project addresses the energy management problem for a grid-connected microgrid with:
- Rooftop solar PV system
- Battery energy storage system (BESS)
- Residential load demand
- Connection to the NSW National Electricity Market (NEM)

The optimizer determines the optimal battery dispatch schedule to minimize total operating costs while respecting technical constraints.

## Key Features

- **LP-based Optimization**: Convex optimization using CVXPY with HiGHS solver
- **Configurable Parameters**: YAML-based configuration for battery specs, grid limits, and analysis settings
- **Modular Architecture**: Clean separation of data, optimization, evaluation, and visualization modules
- **Sensitivity Analysis**: Parametric sweeps for battery sizing and economic analysis
- **Reproducible Results**: Synthetic data generation for consistent benchmarking

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/MicrogridEnergyManagementOptimization.git
cd MicrogridEnergyManagementOptimization
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Optimization
```bash
# Generate synthetic data
python scripts/ingest_data.py --config config/config.yaml

# Compute baseline (no battery)
python scripts/run_baseline.py --synthetic

# Run optimization
python scripts/run_optimization.py --synthetic

# Run sensitivity analysis
python scripts/run_sensitivity.py
```

### 5. Explore Notebooks
```bash
jupyter notebook notebooks/
```

## Project Structure

```
MicrogridEnergyManagementOptimization/
├── config/
│   └── config.yaml              # Main configuration file
├── data/
│   ├── raw/                     # Original unprocessed data
│   └── processed/               # Cleaned and merged datasets
├── src/
│   ├── config/                  # Configuration loading
│   ├── data/                    # Data ingestion and API clients
│   ├── features/                # Solar and load forecasting
│   ├── optimization/            # Core LP solver and battery model
│   ├── evaluation/              # Baseline, metrics, sensitivity
│   ├── plots/                   # Visualization functions
│   └── utils/                   # Logging and time utilities
├── scripts/                     # CLI execution scripts
├── notebooks/                   # Jupyter notebooks for analysis
├── reports/                     # Generated figures and report
└── tests/                       # Unit and smoke tests
```

## Optimization Formulation

### Objective Function
Minimize total operating cost over the scheduling horizon:

$$\min \sum_{t=1}^{T} \left( \pi_t \cdot P_{import,t} - \pi_{FiT} \cdot P_{export,t} \right) \cdot \Delta t$$

### Constraints
- **Power Balance**: $P_{solar,t} + P_{discharge,t} + P_{import,t} = P_{load,t} + P_{charge,t} + P_{export,t}$
- **SOC Dynamics**: $SOC_{t+1} = SOC_t + \frac{\eta_c \cdot P_{charge,t} - P_{discharge,t}/\eta_d}{C_{bat}} \cdot \Delta t$
- **SOC Bounds**: $SOC_{min} \leq SOC_t \leq SOC_{max}$
- **Power Limits**: $0 \leq P_{charge,t}, P_{discharge,t} \leq P_{max}$

## Configuration

Edit `config/config.yaml` to customize:

```yaml
battery:
  capacity_kwh: 13.5        # Tesla Powerwall 2 equivalent
  max_power_kw: 5.0
  efficiency_charge: 0.95
  efficiency_discharge: 0.95
  soc_min: 0.1
  soc_max: 0.9

solar:
  capacity_kw: 6.6          # Typical residential system

optimization:
  solver: "CVXPY"
  backend: "HIGHS"
```

## Results

The optimization achieves cost savings through:
1. **Price Arbitrage**: Charging during low-price periods, discharging during peaks
2. **Solar Maximization**: Storing excess solar for evening use
3. **Peak Shaving**: Reducing maximum grid import power

Typical results show 15-25% cost reduction compared to the no-battery baseline.

## Running Tests

```bash
pytest tests/ -v
```

## Technical Stack

- **Optimization**: CVXPY, HiGHS, PuLP
- **Data Processing**: pandas, NumPy
- **Visualization**: Matplotlib
- **Configuration**: PyYAML
- **Testing**: pytest

## Future Extensions

- [ ] Integration with AEMO NEM API for real price data
- [ ] Model Predictive Control (MPC) with rolling horizon
- [ ] Multi-objective optimization (cost vs. degradation)
- [ ] 5-minute dispatch resolution
- [ ] Stochastic optimization for forecast uncertainty

## Author

**[Your Name]**
Electrical Engineering Student
[Your University]

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- NSW NEM data from AEMO
- Battery specifications referenced from Tesla Powerwall 2
- Optimization formulation based on standard microgrid EMS literature
