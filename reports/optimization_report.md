# Microgrid Energy Management Optimization Report

**Data Source**: Real NSW NEM Data (OpenElectricity API)
**Period**: 2024-12-06 to 2024-12-13 (7 days)
**Resolution**: 1-hour intervals (169 time steps)
**Region**: NSW National Electricity Market (NEM)

---

## 1. Executive Summary

This report presents results from a linear programming-based battery dispatch optimization using **real NSW NEM wholesale market data**. The optimizer successfully exploits extreme price volatility in the NEM to transform a net electricity cost into net revenue.

**Key Results**:
- Baseline cost of **$9.28** converted to net revenue of **$11.18**
- Total value captured: **$20.46 (220.5% improvement)**
- Extreme price spike of **$5,548/MWh** successfully mitigated through battery arbitrage

---

## 2. Market Data Analysis

### 2.1 Price Volatility

The real NEM data exhibits significant price volatility, validating the core thesis of this project:

| Metric | Value |
|--------|-------|
| Mean Price | $179/MWh ($0.179/kWh) |
| Min Price | **-$24/MWh** (negative pricing) |
| Max Price | **$5,548/MWh** (extreme spike) |
| Std Dev | $460/MWh |
| Price Ratio | >200x |

**Key Observation**: The presence of both negative prices (oversupply) and extreme spikes (scarcity events) creates substantial arbitrage opportunity for battery storage.

### 2.2 Load and Solar Profiles

| Metric | Load | Solar |
|--------|------|-------|
| Mean | 1.01 kW | 1.75 kW |
| Min | 0.54 kW | 0 kW |
| Max | 1.94 kW | 6.6 kW |

---

## 3. System Configuration

| Parameter | Value |
|-----------|-------|
| Battery Capacity | 13.5 kWh |
| Max Charge/Discharge Power | 5.0 kW |
| Round-trip Efficiency | ~90% |
| SOC Limits | 10% – 90% |
| Solar PV Capacity | 6.6 kW |
| Feed-in Tariff | $0.05/kWh |

---

## 4. Optimization Results

### 4.1 Cost Analysis

| Scenario | Net Cost | Interpretation |
|----------|----------|----------------|
| **Baseline** (No Battery) | +$9.28 | Net cost (paying for electricity) |
| **Optimized** (With Battery) | **-$11.18** | Net revenue (earning from arbitrage) |
| **Value Captured** | **$20.46** | 220.5% improvement |

### 4.2 Energy Flows

| Metric | Baseline | Optimized |
|--------|----------|-----------|
| Grid Import | 84.3 kWh | Variable (price-responsive) |
| Grid Export | 208.2 kWh | Variable (price-responsive) |
| Self-Consumption | 29.4% | Increased via battery storage |
| Battery Throughput | — | 102.4 kWh (7.6 cycles) |

### 4.3 Price Spike Mitigation

The most significant value came from avoiding grid imports during the **$5,548/MWh price spike** event:

- Without battery: Forced to import at extreme prices
- With battery: Pre-charged during low-price periods, discharged during spike
- **Single-event value**: Estimated $15+ in avoided cost

---

## 5. Dispatch Behavior Analysis

The optimizer exhibits economically rational behavior:

1. **Negative Price Periods**: Imports from grid to charge battery (paid to consume)
2. **Low Price Periods**: Charges battery from grid and solar
3. **High Price Periods**: Discharges battery to meet load, avoids grid import
4. **Extreme Spikes**: Fully utilizes stored energy, may export at premium prices

### Observed Pattern (from real data):
- Battery charges during overnight/early morning (low prices)
- Maintains charge during midday solar surplus
- Discharges during evening peak demand/price periods
- Responds aggressively to price spikes

---

## 6. Visualizations

### 6.1 Dispatch Schedule
![Dispatch Schedule](figures/dispatch_schedule.png)

*Top*: Solar generation and load demand profiles
*Middle*: Battery charge/discharge and grid import/export flows
*Bottom*: Real NEM spot price (note $5.5/kWh spike on left)

### 6.2 Cost Comparison
![Cost Comparison](figures/cost_comparison.png)

The optimization transforms a $9.28 cost into $11.18 revenue—a complete reversal of energy economics through strategic dispatch.

### 6.3 State of Charge
![SOC Trajectory](figures/soc_trajectory.png)

---

## 7. Conclusions

### 7.1 Key Findings

1. **Real Market Validation**: Using actual NSW NEM data confirms that wholesale price volatility creates substantial value for optimized battery storage.

2. **Extreme Event Value**: A single price spike event ($5,548/MWh) dominated the value capture, demonstrating the importance of being prepared for tail events.

3. **Negative Pricing Opportunity**: The optimizer exploits negative price periods—a feature unique to real wholesale markets—to charge batteries while being paid.

4. **Computational Feasibility**: The LP formulation solves in 0.28 seconds, enabling real-time dispatch decisions.

### 7.2 Implications for Industry

- **Retailers**: Battery-backed customers can transform from cost centers to revenue sources during price spikes
- **Networks**: Optimized DER dispatch reduces peak demand and grid stress
- **Market Operators**: Price-responsive storage provides valuable demand flexibility

---

## 8. Technical Details

### Solver Statistics

| Metric | Value |
|--------|-------|
| Solver | CVXPY + HiGHS |
| Problem Type | Linear Program (LP) |
| Solve Time | 0.280 s |
| Status | Optimal |

### Data Source

- **API**: OpenElectricity (data.openelectricity.org.au)
- **Price Data**: NSW Regional Reference Price (RRP)
- **Demand Data**: NSW region demand (scaled to residential)
- **Solar Data**: NSW rooftop solar aggregate (scaled to 6.6 kW system)

---

## Appendix: Commands to Reproduce

```bash
# Fetch real NEM data
python scripts/ingest_data.py --period 7d

# Run baseline
python scripts/run_baseline.py

# Run optimization
python scripts/run_optimization.py

# Run sensitivity analysis
python scripts/run_sensitivity.py
```

---

*Report generated using real NSW NEM wholesale market data*
*Microgrid Energy Management Optimization Framework v1.1*
