from environment import SmartHomeEnergyEnv
import inspect

env = SmartHomeEnergyEnv()

print("Checking SmartHomeEnergyEnv methods:")
print("=" * 50)

methods = [name for name, method in inspect.getmembers(env, predicate=inspect.ismethod)]

required_methods = [
    'reset', 'step', 'state', 
    '_get_observation', '_get_current_time', 
    '_get_appliance', '_update_comfort', '_calculate_reward'
]

for method in required_methods:
    if method in methods:
        print(f"✓ {method}")
    else:
        print(f"✗ {method} MISSING!")

print("=" * 50)
print(f"Total methods found: {len(methods)}")