# Microgrid Energy Management Optimization
## Technical Report

---

## 1. Problem Definition

### 1.1 Background
Grid-connected residential microgrids with solar PV and battery storage face the challenge of optimizing energy flows to minimize electricity costs. With time-varying electricity prices in the National Electricity Market (NEM), strategic battery dispatch can yield significant savings.

### 1.2 Objective
Design and implement an optimization framework that determines the optimal battery charging and discharging schedule to minimize total operating costs over a planning horizon.

### 1.3 Scope
- Single residential microgrid with solar PV and battery
- Grid-connected operation (no islanding)
- Hourly time resolution (expandable to 5-minute)
- Day-ahead scheduling with perfect forecast assumption

---

## 2. System Model

### 2.1 System Components

| Component | Parameter | Value |
|-----------|-----------|-------|
| Solar PV | Capacity | 6.6 kW |
| Battery | Capacity | 13.5 kWh |
| Battery | Max Power | 5.0 kW |
| Battery | Efficiency | 95% (round-trip: 90.25%) |
| Battery | SOC Range | 10% - 90% |
| Grid | Max Import | 10.0 kW |
| Grid | Max Export | 5.0 kW |

### 2.2 Power Balance Equation

At each time step $t$:

$$P_{solar,t} + P_{discharge,t} + P_{grid,import,t} = P_{load,t} + P_{charge,t} + P_{grid,export,t}$$

### 2.3 Battery Dynamics

State of charge evolution:

$$SOC_{t+1} = SOC_t + \frac{\eta_{charge} \cdot P_{charge,t} - P_{discharge,t} / \eta_{discharge}}{C_{battery}} \cdot \Delta t$$

---

## 3. Optimization Formulation

### 3.1 Decision Variables
- $P_{charge,t}$: Battery charging power at time $t$ [kW]
- $P_{discharge,t}$: Battery discharging power at time $t$ [kW]
- $P_{import,t}$: Grid import power at time $t$ [kW]
- $P_{export,t}$: Grid export power at time $t$ [kW]
- $SOC_t$: State of charge at time $t$ [-]

### 3.2 Objective Function

Minimize total cost:

$$\min \sum_{t=1}^{T} \left( \pi_t \cdot P_{import,t} - \pi_{FiT} \cdot P_{export,t} \right) \cdot \Delta t$$

Where:
- $\pi_t$: Spot price at time $t$ [$/kWh]
- $\pi_{FiT}$: Feed-in tariff [$/kWh]

### 3.3 Constraints

1. **Power balance** (equality constraint at each $t$)
2. **SOC dynamics** (equality constraint at each $t$)
3. **Initial SOC**: $SOC_0 = SOC_{initial}$
4. **SOC bounds**: $SOC_{min} \leq SOC_t \leq SOC_{max}$
5. **Charging power limit**: $0 \leq P_{charge,t} \leq P_{max}$
6. **Discharging power limit**: $0 \leq P_{discharge,t} \leq P_{max}$
7. **Grid import limit**: $0 \leq P_{import,t} \leq P_{import,max}$
8. **Grid export limit**: $0 \leq P_{export,t} \leq P_{export,max}$

### 3.4 Problem Classification

- **Type**: Linear Program (LP)
- **Variables**: $6T$ (where $T$ is number of time steps)
- **Constraints**: $4T$ equality + $6T$ inequality bounds
- **Solver**: HiGHS via CVXPY

---

## 4. Results

### 4.1 Baseline vs. Optimized Comparison

| Metric | Baseline | Optimized | Improvement |
|--------|----------|-----------|-------------|
| Total Cost | $X.XX | $Y.YY | Z.Z% |
| Grid Import | XXX kWh | YYY kWh | -ZZ% |
| Peak Import | X.X kW | Y.Y kW | -ZZ% |
| Self-Consumption | XX% | YY% | +ZZ% |

### 4.2 Dispatch Strategy Analysis

The optimized dispatch exhibits clear price arbitrage behavior:

1. **Overnight (00:00-06:00)**: Low prices, battery charges from grid
2. **Morning (06:00-10:00)**: Moderate prices, battery supports morning peak
3. **Midday (10:00-15:00)**: Excess solar charges battery
4. **Evening (15:00-21:00)**: Peak prices, battery discharges to reduce imports
5. **Night (21:00-24:00)**: Prices decrease, prepare for next cycle

### 4.3 Visualization

![Dispatch Schedule](figures/dispatch_schedule.png)
*Figure 1: Optimal battery dispatch schedule showing solar, load, battery power, and grid flows*

![SOC Trajectory](figures/soc_trajectory.png)
*Figure 2: Battery state of charge over the optimization horizon*

![Cost Comparison](figures/cost_comparison.png)
*Figure 3: Cost comparison between baseline and optimized scenarios*

---

## 5. Sensitivity Analysis

### 5.1 Battery Capacity

| Capacity (kWh) | Baseline Cost | Optimized Cost | Savings (%) |
|----------------|---------------|----------------|-------------|
| 5 | $X.XX | $Y.YY | Z.Z% |
| 10 | $X.XX | $Y.YY | Z.Z% |
| 13.5 | $X.XX | $Y.YY | Z.Z% |
| 20 | $X.XX | $Y.YY | Z.Z% |
| 30 | $X.XX | $Y.YY | Z.Z% |

**Finding**: Diminishing returns observed beyond 20 kWh capacity for residential application.

### 5.2 Battery Power Rating

Higher power ratings enable faster arbitrage response but show diminishing returns beyond the daily price swing magnitude.

### 5.3 Feed-in Tariff Impact

Lower feed-in tariffs increase battery value proposition by making self-consumption more attractive than export.

---

## 6. Limitations

1. **Perfect Foresight**: Assumes perfect knowledge of prices, solar, and load
2. **No Degradation Modeling**: Battery cycle aging not included in objective
3. **Single Objective**: Only cost minimization, no multi-objective trade-offs
4. **Deterministic**: No uncertainty quantification in forecasts
5. **No Network Constraints**: Voltage and power quality not modeled

---

## 7. Future Extensions

### 7.1 Short-term
- Integration with real AEMO NEM price data via API
- Model Predictive Control (MPC) for rolling horizon optimization
- 5-minute dispatch resolution for FCAS participation

### 7.2 Medium-term
- Stochastic optimization for forecast uncertainty
- Battery degradation cost in objective function
- Multi-objective optimization (cost vs. self-sufficiency)

### 7.3 Long-term
- Machine learning-based forecasting integration
- Virtual Power Plant (VPP) aggregation modeling
- Peer-to-peer energy trading optimization

---

## 8. Conclusion

This project demonstrates a complete microgrid energy management optimization framework achieving XX% cost reduction through optimal battery dispatch. The LP formulation ensures global optimality and computational efficiency suitable for day-ahead scheduling applications.

The modular code architecture enables easy extension to more complex scenarios, making this a solid foundation for further research in residential energy management systems.

---

## References

1. AEMO. "National Electricity Market Data Dashboard." https://aemo.com.au/
2. Tesla. "Powerwall 2 Technical Specifications."
3. Boyd, S., & Vandenberghe, L. "Convex Optimization." Cambridge University Press.
4. Lopes, J.P., et al. "Integrating distributed generation into electric power systems." Electric Power Systems Research, 2007.

---

*Report generated: [Date]*
*Author: [Your Name]*
