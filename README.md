# Smart Home Energy Optimizer

An OpenEnv environment for training AI agents to optimize residential energy consumption through intelligent appliance scheduling, battery management, and solar integration.

## 🎯 Overview

This environment simulates a smart home where an AI agent must minimize electricity costs while maintaining user comfort and completing necessary appliance cycles. The agent operates over a 24-hour period with 15-minute decision intervals.

## 🏠 Environment Description

The agent controls:
- **Appliances**: Dishwasher, washing machine, EV charger, HVAC, pool pump, etc.
- **Battery Storage**: Charge/discharge decisions (hard mode)
- **Solar Integration**: Leverage solar generation to reduce grid dependence

Key challenges:
- Time-of-use electricity pricing (peak vs off-peak)
- Appliance time windows and dependencies
- User comfort requirements (temperature, timing preferences)
- Battery state management
- Solar generation variability

## 📊 Tasks

### Easy Task
**Objective**: Schedule 3 appliances to minimize cost

- **Appliances**: Dishwasher, Washing Machine, EV Charger
- **Duration**: 24 hours (96 steps)
- **Success**: Score ≥ 0.75
- **Baseline**: ~0.82

### Medium Task
**Objective**: Manage 10 devices with solar integration

- **Appliances**: 10 devices including HVAC, pool pump, irrigation
- **Features**: Solar panels, comfort optimization
- **Success**: Score ≥ 0.65
- **Baseline**: ~0.71

### Hard Task
**Objective**: Full home optimization with battery

- **Appliances**: 20 devices across all home systems
- **Features**: Battery storage, dynamic pricing, load prediction
- **Success**: Score ≥ 0.55
- **Baseline**: ~0.62

## 🎮 Action Space
```python
Action(
    appliance_actions=[
        ApplianceAction(appliance_id="dishwasher", command="ON"),
        ApplianceAction(appliance_id="ev_charger", command="OFF"),
    ],
    battery_action=BatteryAction(command="CHARGE", power_kw=2.5)
)
```

**Appliance Commands**: `ON`, `OFF`, `MAINTAIN`
**Battery Commands**: `CHARGE`, `DISCHARGE`, `IDLE`

## 👁️ Observation Space
```python
Observation(
    timestamp="14:30",
    time_step=58,
    appliances=[...],  # Current state of all devices
    battery=BatteryState(current_charge_kwh=7.2, ...),
    solar=SolarState(current_generation_kw=3.5, ...),
    grid=GridState(current_price_per_kwh=0.25, ...),
    indoor_temperature=71.0,
    total_cost_so_far=5.67
)
```

## 🎁 Reward Structure

- **Cost Component**: Negative reward proportional to electricity cost
- **Comfort Component**: Penalty for temperature outside 68-72°F
- **Efficiency Component**: Bonus for utilizing solar generation
- **Constraint Penalty**: Penalty for missing deadlines or dependencies

## 📈 Grading

Scores range from 0.0 to 1.0:

**Easy**: 
- 50% completion (all appliances finish cycles)
- 50% cost efficiency (vs optimal schedule)

**Medium**:
- 40% cost minimization
- 30% comfort maintenance
- 20% solar utilization
- 10% constraint satisfaction

**Hard**:
- 35% cost optimization (including battery)
- 25% multi-zone comfort
- 20% battery efficiency
- 10% grid independence
- 10% equipment longevity

## 🚀 Quick Start

### Local Setup
```bash
# Clone repository
git clone https://github.com/yourusername/smart-home-energy-optimizer
cd smart-home-energy-optimizer

# Install dependencies
pip install -r requirements.txt

# Validate environment
openenv validate

# Run baseline inference
export OPENAI_API_KEY="your-key"
export MODEL_NAME="gpt-4"
export TASK="easy"
python inference.py
```

### Docker
```bash
# Build image
docker build -t smart-home-energy .

# Run container
docker run -p 7860:7860 smart-home-energy

# Test endpoint
curl -X POST http://localhost:7860/reset
```

## 📊 Baseline Scores

| Task | Model | Score | Cost Savings |
|------|-------|-------|--------------|
| Easy | GPT-4 | 0.82 | 45% vs peak |
| Medium | GPT-4 | 0.71 | 38% + solar |
| Hard | GPT-4 | 0.62 | 52% + battery |

## 🏗️ Project Structure