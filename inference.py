"""
Baseline inference script for Smart Home Energy Optimizer
Must follow exact logging format for evaluation
"""

import os
import asyncio
from openai import OpenAI
from typing import List
from environment import SmartHomeEnergyEnv
from models import Action, ApplianceAction, BatteryAction

# ============================================================================
# REQUIRED ENVIRONMENT VARIABLES
# ============================================================================
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")

# ============================================================================
# CONFIGURATION
# ============================================================================
TASK_NAME = os.getenv("TASK", "easy")  # easy, medium, or hard
BENCHMARK = "smart-home-energy-optimizer"
MAX_STEPS = 96  # 24 hours in 15-min intervals

# Scoring thresholds
MAX_TOTAL_REWARD = 0.0  # We accumulate negative costs, so max is 0
SUCCESS_SCORE_THRESHOLD = 0.70  # Target score from grader


# ============================================================================
# REQUIRED LOGGING FUNCTIONS - DO NOT MODIFY FORMAT
# ============================================================================
def log_start(task: str, env: str, model: str):
    """Log episode start - EXACT FORMAT REQUIRED"""
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error):
    """Log each step - EXACT FORMAT REQUIRED"""
    print(f"[STEP] step={step} action={action!r} reward={reward} done={done} error={error}", flush=True)


def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    """Log episode end - EXACT FORMAT REQUIRED"""
    print(f"[END] success={success} steps={steps} score={score:.4f} rewards={rewards}", flush=True)


# ============================================================================
# AGENT LOGIC
# ============================================================================
def get_model_decision(client: OpenAI, observation: dict, step: int) -> Action:
    """
    Simple greedy agent: run appliances during cheapest hours
    You can replace this with smarter logic
    """
    try:
        # Build prompt
        prompt = f"""You are managing a smart home energy system. Current state:

Time: {observation['timestamp']} (step {observation['time_step']}/96)
Electricity Price: ${observation['grid']['current_price_per_kwh']:.3f}/kWh
Solar Generation: {observation['solar']['current_generation_kw']:.2f} kW
Indoor Temperature: {observation['indoor_temperature']:.1f}°F

Appliances:
"""
        for app in observation['appliances']:
            status = "ON" if app['is_on'] else "OFF"
            completed = "✓" if app.get('completed', False) else "⏳"
            prompt += f"- {app['name']}: {status} {completed} ({app['power_rating']:.2f}kW)\n"

        prompt += f"""
Price Forecast (next 4 hours): {observation['grid']['price_forecast'][:4]}

Your goal: Minimize cost while completing all appliance cycles and maintaining comfort (68-72°F).

Respond with a JSON object:
{{
  "appliance_actions": [
    {{"appliance_id": "dishwasher", "command": "ON"}},
    {{"appliance_id": "ev_charger", "command": "OFF"}}
  ],
  "battery_action": {{"command": "IDLE", "power_kw": 0.0}},
  "reasoning": "Start dishwasher during cheap period"
}}
"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a smart home energy optimization agent. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500,
        )
        
        text = (response.choices[0].message.content or "").strip()
        
        # Parse JSON response
        import json
        # Remove markdown code fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        
        data = json.loads(text)
        
        # Build Action object
        appliance_actions = [
            ApplianceAction(**a) for a in data.get("appliance_actions", [])
        ]
        
        battery_action = BatteryAction(**data.get("battery_action", {"command": "IDLE"}))
        
        return Action(
            appliance_actions=appliance_actions,
            battery_action=battery_action,
            reasoning=data.get("reasoning", "")
        )
        
    except Exception as e:
        print(f"[DEBUG] Model decision failed: {e}", flush=True)
        # Fallback: do nothing
        return Action(
            appliance_actions=[],
            battery_action=BatteryAction(command="IDLE"),
        )


# ============================================================================
# MAIN INFERENCE LOOP
# ============================================================================
async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    # Initialize environment
    env = SmartHomeEnergyEnv(difficulty=TASK_NAME)
    
    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False
    
    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)
    
    try:
        # Reset environment
        observation = await env.reset()
        
        # Run episode
        for step in range(1, MAX_STEPS + 1):
            # Get current state
            current_state = await env.state()
            
            # Check if done
            if current_state.get('time_step', 0) >= 96:
                break
            
            # Get action from model
            action = get_model_decision(
                client,
                observation.dict(),
                step
            )
            
            # Take step
            result = await env.step(action)
            observation, reward_obj, done, info = result
            
            # Extract reward value
            reward = reward_obj.total if hasattr(reward_obj, 'total') else 0.0
            rewards.append(reward)
            steps_taken = step
            
            # Log step
            action_summary = f"{len(action.appliance_actions)} actions"
            log_step(
                step=step,
                action=action_summary,
                reward=reward,
                done=done,
                error=None
            )
            
            if done:
                break
        
        # Get final state for grading
        final_state = await env.state()
        
        # Calculate score using appropriate grader
        if TASK_NAME == "easy":
            from graders import grade_easy_task
            score = grade_easy_task(final_state)
        elif TASK_NAME == "medium":
            from graders import grade_medium_task
            score = grade_medium_task(final_state)
        else:
            from graders import grade_hard_task
            score = grade_hard_task(final_state)
        
        success = score >= SUCCESS_SCORE_THRESHOLD
        
        print(f"[DEBUG] Final cost: ${final_state['total_cost']:.2f}", flush=True)
        print(f"[DEBUG] Grader score: {score:.4f}", flush=True)
        
    except Exception as e:
        print(f"[DEBUG] Episode error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        
    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())