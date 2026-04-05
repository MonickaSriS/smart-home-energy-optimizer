---
title: Smart Home Energy Optimizer
emoji: 🏠⚡
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
tags:
  - openenv
  - reinforcement-learning
  - energy-optimization
  - smart-home
  - sustainability
---

# Smart Home Energy Optimizer 🏠⚡

An OpenEnv environment for training AI agents to optimize residential energy consumption.

## 🎯 Quick Start

This Space provides a REST API for the Smart Home Energy Optimizer environment.

### API Endpoints

**Base URL**: `https://Monickasri-smart-home-energy-optimizer.hf.space`

- `GET /health` - Health check
- `POST /reset` - Start new episode
- `POST /step` - Take action
- `GET /state` - Get current state

### Example Usage
```bash
# Reset environment
curl -X POST https://Monickasri-smart-home-energy-optimizer.hf.space/reset

# Take a step
curl -X POST https://Monickasri-smart-home-energy-optimizer.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{
    "action": {
      "appliance_actions": [
        {"appliance_id": "dishwasher", "command": "ON"}
      ],
      "battery_action": {"command": "IDLE", "power_kw": 0.0}
    }
  }'
```

## 📊 Tasks

- **Easy**: 3 appliances, basic scheduling
- **Medium**: 10 devices + solar panels
- **Hard**: 20 devices + battery storage

## 📖 Documentation

Full documentation: [GitHub Repository](https://github.com/MonickaSriS/smart-home-energy-optimizer)



