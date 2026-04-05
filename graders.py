from typing import Dict, Any

def grade_easy_task(final_state: Dict[str, Any]) -> float:
    """
    Grade Easy Task: 3 appliances, minimize cost
    Perfect score: all complete + optimal cost
    """
    # Check completion (50% of score)
    appliances = final_state.get("appliances", [])
    completed = sum(1 for a in appliances if a.get("completed", False))
    total_required = len([a for a in appliances if a.get("completed") is not None])
    
    completion_score = completed / total_required if total_required > 0 else 0.0
    
    # Check cost efficiency (50% of score)
    actual_cost = final_state.get("total_cost", 999.0)
    
    # Optimal: dishwasher (1.5kWh) + washer (2kWh) + EV (7kWh) = 10.5kWh at $0.12 = $1.26
    optimal_cost = 1.26
    worst_cost = 10.5 * 0.30  # All at peak = $3.15
    
    if actual_cost <= optimal_cost * 1.1:  # Within 10% of optimal
        cost_score = 1.0
    elif actual_cost >= worst_cost:
        cost_score = 0.0
    else:
        # Linear interpolation
        cost_score = (worst_cost - actual_cost) / (worst_cost - optimal_cost)
    
    final_score = 0.5 * completion_score + 0.5 * cost_score
    return round(max(0.0, min(1.0, final_score)), 4)


def grade_medium_task(final_state: Dict[str, Any]) -> float:
    """
    Grade Medium Task: 10 appliances + solar
    Scoring: cost (40%), comfort (30%), solar (20%), constraints (10%)
    """
    # 1. Cost efficiency (40%)
    actual_cost = final_state.get("total_cost", 999.0)
    baseline_cost = 15.0  # Reasonable baseline
    optimal_cost = 8.0    # With good solar usage
    
    if actual_cost <= optimal_cost:
        cost_score = 1.0
    elif actual_cost >= baseline_cost:
        cost_score = 0.0
    else:
        cost_score = (baseline_cost - actual_cost) / (baseline_cost - optimal_cost)
    
    # 2. Comfort (30%)
    total_steps = final_state.get("time_step", 96)
    violations = final_state.get("comfort_violations", 0)
    comfort_score = max(0.0, 1.0 - (violations / total_steps))
    
    # 3. Solar utilization (20%)
    solar_generated = final_state.get("solar_energy_generated", 0.0)
    solar_used = final_state.get("solar_energy_used", 0.0)
    solar_score = (solar_used / solar_generated) if solar_generated > 0 else 0.0
    
    # 4. Constraint satisfaction (10%)
    constraints_met = final_state.get("constraints_met", 0)
    total_constraints = final_state.get("total_constraints", 1)
    constraint_score = constraints_met / total_constraints if total_constraints > 0 else 1.0
    
    final_score = (
        0.40 * cost_score +
        0.30 * comfort_score +
        0.20 * solar_score +
        0.10 * constraint_score
    )
    
    return round(max(0.0, min(1.0, final_score)), 4)


def grade_hard_task(final_state: Dict[str, Any]) -> float:
    """
    Grade Hard Task: 20 appliances + battery + prediction
    Scoring: cost (35%), comfort (25%), battery (20%), independence (10%), longevity (10%)
    """
    # 1. Cost optimization (35%)
    actual_cost = final_state.get("total_cost", 999.0)
    grid_revenue = final_state.get("grid_export_revenue", 0.0)
    net_cost = actual_cost - grid_revenue
    
    baseline_cost = 25.0
    optimal_cost = 10.0
    
    if net_cost <= optimal_cost:
        cost_score = 1.0
    elif net_cost >= baseline_cost:
        cost_score = 0.0
    else:
        cost_score = (baseline_cost - net_cost) / (baseline_cost - optimal_cost)
    
    # 2. Comfort across zones (25%)
    total_steps = final_state.get("time_step", 96)
    violations = final_state.get("comfort_violations", 0)
    comfort_score = max(0.0, 1.0 - (violations / (total_steps * 0.5)))  # Allow some violations
    
    # 3. Battery efficiency (20%)
    battery_soc = final_state.get("battery_soc", 50.0)
    # Good battery usage: end with 40-60% charge (ready for next day)
    if 40 <= battery_soc <= 60:
        battery_score = 1.0
    else:
        battery_score = max(0.0, 1.0 - abs(battery_soc - 50) / 50)
    
    # 4. Grid independence (10%)
    total_energy = final_state.get("total_energy_consumed", 1.0)
    solar_energy = final_state.get("solar_energy_generated", 0.0)
    independence_score = min(1.0, solar_energy / total_energy) if total_energy > 0 else 0.0
    
    # 5. Equipment longevity (10%) - check excessive cycling
    # This would require tracking on/off cycles - simplified here
    longevity_score = 0.8  # Default reasonable score
    
    final_score = (
        0.35 * cost_score +
        0.25 * comfort_score +
        0.20 * battery_score +
        0.10 * independence_score +
        0.10 * longevity_score
    )
    
    return round(max(0.0, min(1.0, final_score)), 4)