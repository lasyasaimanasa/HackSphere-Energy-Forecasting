
from transition_controller import determine_grid_state

test_cases = [
    ("2026-10-24 10:00:00", 150, "Main Grid Mode", False),
    ("2026-10-24 10:00:00", 170, "Renewable Storage Mode", False),
    ("2026-10-24 19:00:00", 140, "Renewable Storage Mode", False),
    ("2026-10-24 12:00:00", 210, "Renewable Storage Mode", True),
    ("2026-10-24 22:00:00", 200, "Renewable Storage Mode", True),
    ("2026-10-24 23:00:00", 160, "Main Grid Mode", False),
]

for timestamp, demand, expected_mode, expected_alert in test_cases:
    result = determine_grid_state(timestamp, demand)

    assert result["grid_mode"] == expected_mode, result
    assert result["overload_alert"] == expected_alert, result

    print(
        f"{timestamp} | {demand} kW | "
        f"{result['grid_mode']} | "
        f"Alert: {result['alert_message']}"
    )

print("\nAll transition controller tests passed!")
