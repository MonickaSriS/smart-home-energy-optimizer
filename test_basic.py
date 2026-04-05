import asyncio
from environment import SmartHomeEnergyEnv

async def test_environment():
    print("Testing environment creation...")
    
    # Test Easy
    env = SmartHomeEnergyEnv(difficulty="easy")
    print("✓ Easy environment created")
    
    # Test reset
    obs = await env.reset()
    print(f"✓ Reset successful - {len(obs.appliances)} appliances loaded")
    print(f"  Time: {obs.timestamp}")
    print(f"  Initial cost: ${obs.total_cost_so_far:.2f}")
    
    # Test one step
    from models import Action, ApplianceAction, BatteryAction
    action = Action(
        appliance_actions=[
            ApplianceAction(appliance_id="dishwasher", command="ON")
        ],
        battery_action=BatteryAction(command="IDLE")
    )
    
    obs, reward, done, info = await env.step(action)
    print(f"✓ Step successful - Reward: {reward.total:.4f}")
    print(f"  Feedback: {obs.last_action_feedback}")
    
    # Test state
    state = await env.state()
    print(f"✓ State retrieved - Step {state['time_step']}, Cost ${state['total_cost']:.2f}")
    
    print("\n✅ All basic tests passed!")

if __name__ == "__main__":
    asyncio.run(test_environment())