import asyncio
from environment import SmartHomeEnergyEnv
from models import Action, ApplianceAction, BatteryAction
from graders import grade_easy_task, grade_medium_task, grade_hard_task

async def test_task(difficulty: str):
    print(f"\n{'='*50}")
    print(f"Testing {difficulty.upper()} task")
    print('='*50)
    
    env = SmartHomeEnergyEnv(difficulty=difficulty)
    obs = await env.reset()
    
    print(f"✓ Environment created")
    print(f"  Appliances: {len(obs.appliances)}")
    print(f"  Battery enabled: {obs.battery.capacity_kwh > 0}")
    print(f"  Solar enabled: {obs.solar.current_generation_kw >= 0}")
    
    # Run a few steps
    for i in range(5):
        action = Action(
            appliance_actions=[],
            battery_action=BatteryAction(command="IDLE")
        )
        obs, reward, done, info = await env.step(action)
        print(f"  Step {i+1}: Cost ${obs.total_cost_so_far:.3f}, Reward {reward.total:.4f}")
    
    # Get final state and grade
    state = await env.state()
    
    if difficulty == "easy":
        score = grade_easy_task(state)
    elif difficulty == "medium":
        score = grade_medium_task(state)
    else:
        score = grade_hard_task(state)
    
    print(f"\n✓ Grader score: {score:.4f}")
    return score

async def main():
    scores = {}
    
    for difficulty in ["easy", "medium", "hard"]:
        try:
            score = await test_task(difficulty)
            scores[difficulty] = score
        except Exception as e:
            print(f"\n❌ Error in {difficulty}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*50}")
    print("SUMMARY")
    print('='*50)
    for task, score in scores.items():
        print(f"{task.capitalize():10s}: {score:.4f}")
    print("\n✅ All task tests completed!")

if __name__ == "__main__":
    asyncio.run(main())