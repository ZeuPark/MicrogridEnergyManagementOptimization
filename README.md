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

| KPI | Description |
|-----|-------------|
| **Net Cost Reduction** | Reduction in electricity procurement cost vs. no-storage baseline |
| **Peak Import Mitigation** | Avoidance of grid imports during extreme price intervals (>$1,000/MWh) |
| **Negative Price Capture** | Value extracted from grid charging during oversupply (negative pricing) |
| **Self-Consumption Rate** | Proportion of solar generation consumed on-site via storage |

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

# Run with real NEM data
python scripts/ingest_data.py --period 7d
python scripts/run_baseline.py
python scripts/run_optimization.py

# Or use synthetic data for benchmarking
python scripts/ingest_data.py --synthetic
```

Real-time NEM price data is fetched via OpenElectricity API. Synthetic profiles available for reproducible benchmarking.

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

| Phase | Milestone | Status |
|-------|-----------|--------|
| **v1.0** | Core LP optimization with synthetic data | Done |
| **v1.1** | Real NEM price data integration (OpenElectricity API) | Done |
| **v1.2** | Rolling-horizon Model Predictive Control (MPC) | Planned |
| **v2.0** | Stochastic optimization for forecast uncertainty | Planned |
| **v2.1** | Multi-objective: cost vs. battery degradation | Planned |
| **v3.0** | 5-minute dispatch aligned with NEM settlement | Planned |

## Testing

```bash
pytest tests/ -v
```

## Conclusion

This project demonstrates that optimization-based battery dispatch can materially reduce electricity procurement cost under volatile wholesale market conditions.

**Validation with Real NEM Data**

Using real NSW NEM price data (Dec 2024), the optimization model reduced net electricity cost by strategically avoiding extreme price spikes exceeding $5,000/MWh and exploiting negative pricing intervals during oversupply conditions.

Key outcomes:

1. **Extreme Event Mitigation**
   The economic value is driven primarily by avoidance of extreme price spike intervals. The optimizer pre-charges batteries during low-price periods to avoid forced imports during scarcity events.

2. **Negative Price Exploitation**
   The optimizer exploits negative pricing periods by charging from the grid, effectively monetizing oversupply conditions—a behavior unique to real wholesale market dynamics.

3. **Operational Interpretability**
   The resulting dispatch pattern aligns with expected economic behavior—charging during periods of solar surplus or low prices and discharging during evening peak demand—confirming model consistency with market incentives.

4. **Computational Efficiency**
   The convex formulation solves in under 0.3 seconds, supporting real-time deployment in rolling-horizon MPC architectures.

See [`reports/optimization_report.md`](reports/optimization_report.md) for detailed analysis with real market data.

## Author

Electrical Engineering Undergraduate
Portfolio Project — Energy Systems Optimization

## License

MIT License — see [LICENSE](LICENSE) for details.

## References

- AEMO NEM wholesale market data
- Tesla Powerwall 2 specifications (reference battery parameters)
- Standard microgrid EMS formulations from IEEE literature
