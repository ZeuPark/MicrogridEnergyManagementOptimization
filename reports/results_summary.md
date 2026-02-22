# Optimization Results Summary

**Project**: Microgrid Energy Management Optimization
**Data**: Real NSW NEM wholesale market data
**Period**: December 6–13, 2024 (7 days, 169 hourly intervals)

---

## Market Conditions

| Metric | Value |
|--------|-------|
| Price Range | **-$24 to $5,548/MWh** |
| Mean Price | $179/MWh |
| Volatility (Std Dev) | $460/MWh |
| Negative Price Intervals | Present (oversupply periods) |
| Extreme Spike Events | 1 event >$5,000/MWh |

---

## System Configuration

| Component | Specification |
|-----------|---------------|
| Battery | 13.5 kWh / 5.0 kW (Tesla Powerwall 2 equivalent) |
| Solar PV | 6.6 kW rooftop system |
| Efficiency | 90% round-trip |
| SOC Range | 10–90% |

---

## Optimization Performance

### Cost Analysis

| Scenario | Net Cost | Notes |
|----------|----------|-------|
| Baseline (No Battery) | **+$9.28** | Net cost (import > export revenue) |
| Optimized (With Battery) | **-$11.18** | Net revenue (arbitrage profit) |
| Absolute Delta | **$20.46** | Value captured over 7 days |

### Value Attribution

The economic value is driven by two primary mechanisms:

1. **Extreme Spike Avoidance**
   - Avoided grid imports during $5,548/MWh price spike
   - The majority of weekly economic value was captured during a single extreme price event exceeding $5,000/MWh

2. **Negative Price Exploitation**
   - Charged battery during negative pricing periods
   - Effectively paid to consume electricity during oversupply

---

## Dispatch Behavior

The optimizer exhibits economically rational behavior aligned with NEM market signals:

| Period | Price Condition | Optimizer Action |
|--------|-----------------|------------------|
| Overnight | Low/negative prices | Grid import → Battery charge |
| Morning | Rising prices | Hold charge, solar self-consumption |
| Midday | Moderate prices | Solar export, opportunistic charging |
| Evening Peak | High prices | Battery discharge → Load supply |
| Price Spike | Extreme prices (>$1,000/MWh) | Full discharge, zero grid import |

---

## Key Metrics

| KPI | Result |
|-----|--------|
| Grid Import (Baseline) | 84.3 kWh |
| Grid Import (Optimized) | Price-responsive (minimized during spikes) |
| Battery Throughput | 102.4 kWh (7.6 equivalent cycles) |
| Self-Consumption | Improved from 29% to ~45% |
| Solve Time | 0.28 seconds |

---

## Technical Validation

| Aspect | Status |
|--------|--------|
| Solver Status | Optimal |
| Constraint Satisfaction | All constraints met |
| SOC Bounds | Respected (10–90%) |
| Energy Balance | Verified |
| Unit Tests | 10/10 passed |

---

## Key Insights

### 1. Tail Events Dominate Value

A single extreme price spike ($5,548/MWh) accounted for the majority of captured value. This demonstrates the importance of:
- Maintaining battery charge for unexpected events
- Real-time price signal integration
- Conservative SOC management

### 2. Negative Pricing Creates Opportunity

The NEM exhibits negative pricing during solar oversupply. The optimizer correctly:
- Imports from grid during negative prices (paid to consume)
- Stores energy for later high-price discharge
- Monetizes conditions that penalize passive consumers

### 3. Mechanism Over Magnitude

The absolute dollar savings ($20.46/week) scale with:
- System size (13.5 kWh battery)
- Price volatility (extreme in test period)
- Solar/load profile alignment

Percentage claims are avoided as they depend heavily on baseline conditions.

---

## Reproducibility

```bash
# Fetch real NEM data
python scripts/ingest_data.py --period 7d

# Run optimization
python scripts/run_baseline.py
python scripts/run_optimization.py

# View results
cat reports/optimization_report.md
```

---

## Files Generated

| File | Description |
|------|-------------|
| `data/processed/microgrid_data.csv` | Input data (price, load, solar) |
| `data/processed/optimization_results.csv` | Dispatch schedule output |
| `reports/figures/dispatch_schedule.png` | Visualization of dispatch |
| `reports/figures/cost_comparison.png` | Baseline vs optimized cost |
| `reports/figures/soc_trajectory.png` | Battery state of charge |
| `reports/optimization_report.md` | Detailed analysis report |

---

## Interview Talking Points

1. **"What problem does this solve?"**
   > Reduces electricity procurement cost by minimizing grid imports during extreme wholesale price intervals.

2. **"How does it create value?"**
   > Two mechanisms: avoiding grid imports during extreme price spikes (>$5,000/MWh) and exploiting negative pricing during oversupply by charging the battery.

3. **"Why LP optimization?"**
   > Convex formulation guarantees global optimum, solves in <0.3s, supporting potential rolling-horizon implementations.

4. **"What makes this different from a typical ML project?"**
   > This is operational strategy design, not prediction. It integrates market understanding (NEM price dynamics), optimization theory (LP formulation), and engineering constraints (battery physics).

---

*Summary generated from real NSW NEM market data analysis*
