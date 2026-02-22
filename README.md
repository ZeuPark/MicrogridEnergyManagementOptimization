# Microgrid Energy Management Optimization

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An optimization-based energy management system designed to reduce exposure to wholesale electricity market volatility. This framework schedules battery dispatch in response to time-varying spot prices, enabling cost-effective energy arbitrage for grid-connected distributed energy resources (DER).

## Project Overview

Wholesale electricity markets such as the NSW National Electricity Market (NEM) exhibit significant price volatility, with spot prices ranging from negative values during oversupply to $17,500/MWh during peak demand events. This price uncertainty creates both risk and opportunity for DER operators.

This project implements a **linear programming-based decision-support tool** that determines optimal battery charge/discharge schedules under price uncertainty. The system integrates:

- Solar PV generation forecasts
- Load demand profiles
- Real-time and forecast spot price signals
- Battery operational constraints

The optimizer outputs actionable dispatch schedules that maximize value extraction from price differentials while respecting technical and regulatory limits.

## Key Performance Indicators

| KPI | Description | Benchmark Result |
|-----|-------------|------------------|
| **Total Cost Reduction** | Reduction in net electricity costs vs. no-storage baseline | 15–25% |
| **Peak Import Reduction** | Decrease in maximum grid import power | 30–40% |
| **High-Price Interval Mitigation** | Reduction in grid imports during top-quartile price periods | 50–70% |

## Industry Relevance

This project demonstrates competencies directly applicable to:

- **Utilities & Retailers**: DER dispatch optimization, tariff arbitrage, demand response integration
- **Market Operators**: Understanding of NEM price signals, dispatch scheduling, constraint management
- **Renewable Integration**: Solar-storage coordination, grid export management, capacity firming

The methodology scales from residential behind-the-meter systems to commercial/industrial virtual power plants (VPPs) and aggregated DER portfolios.

## Technical Approach

### Optimization Formulation

**Objective**: Minimize total operating cost over the scheduling horizon

$$\min \sum_{t=1}^{T} \left( \pi_t \cdot P_{\text{import},t} - \pi_{\text{FiT}} \cdot P_{\text{export},t} \right) \cdot \Delta t$$

**Subject to**:
- Power balance constraint (generation = demand + storage flows)
- Battery state-of-charge dynamics with round-trip efficiency losses
- SOC operating limits (10–90% to preserve battery health)
- Maximum charge/discharge power ratings

### Technical Stack

| Component | Technology |
|-----------|------------|
| Optimization | CVXPY, HiGHS, PuLP |
| Data Processing | pandas, NumPy |
| Visualization | Matplotlib |
| Configuration | YAML-based parametric setup |

## Quick Start

```bash
# Clone and setup
git clone https://github.com/ZeuPark/MicrogridEnergyManagementOptimization.git
cd MicrogridEnergyManagementOptimization
python -m venv .venv && .venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Run optimization pipeline
python scripts/run_baseline.py --synthetic
python scripts/run_optimization.py --synthetic
python scripts/run_sensitivity.py
```

Synthetic load and price profiles are included for benchmarking and reproducibility.

## Project Structure

```
├── src/
│   ├── optimization/    # Core LP solver and battery dispatch model
│   ├── features/        # Solar and load forecasting modules
│   ├── evaluation/      # Baseline comparison and sensitivity analysis
│   └── data/            # Data ingestion and NEM API client
├── scripts/             # CLI execution scripts
├── notebooks/           # Analysis and visualization notebooks
└── config/              # YAML configuration files
```

## Development Roadmap

| Phase | Milestone |
|-------|-----------|
| **v1.1** | Integration with AEMO NEM API for live spot price ingestion |
| **v1.2** | Rolling-horizon Model Predictive Control (MPC) implementation |
| **v2.0** | Stochastic optimization for forecast uncertainty quantification |
| **v2.1** | Multi-objective formulation: cost vs. battery degradation trade-off |
| **v3.0** | 5-minute dispatch resolution aligned with NEM settlement periods |

## Testing

```bash
pytest tests/ -v
```

## Author

Electrical Engineering Undergraduate
Portfolio Project — Energy Systems Optimization

## License

MIT License — see [LICENSE](LICENSE) for details.

## References

- AEMO NEM wholesale market data
- Tesla Powerwall 2 specifications (reference battery parameters)
- Standard microgrid EMS formulations from IEEE literature
