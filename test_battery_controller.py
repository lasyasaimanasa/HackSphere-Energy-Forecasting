
from battery_controller import BatteryController


def test_initial_state_of_charge():
    battery = BatteryController(initial_soc=80, capacity_kwh=100)
    assert battery.soc == 80


def test_battery_discharges_gradually():
    battery = BatteryController(initial_soc=80, capacity_kwh=100)
    soc = battery.update(demand_kw=180)
    assert soc == 78


def test_battery_recharges_below_threshold():
    battery = BatteryController(initial_soc=80, capacity_kwh=100)
    soc = battery.update(demand_kw=150)
    assert soc == 83


def test_battery_never_goes_below_zero():
    battery = BatteryController(initial_soc=2, capacity_kwh=100)
    soc = battery.update(demand_kw=500, duration_hours=5)
    assert soc == 0


def test_battery_never_exceeds_100():
    battery = BatteryController(initial_soc=99, capacity_kwh=100)
    soc = battery.update(demand_kw=100)
    assert soc == 100


def test_invalid_initial_soc():
    try:
        BatteryController(initial_soc=120)
        assert False, "Expected ValueError for invalid SOC"
    except ValueError:
        pass


if __name__ == "__main__":
    test_initial_state_of_charge()
    test_battery_discharges_gradually()
    test_battery_recharges_below_threshold()
    test_battery_never_goes_below_zero()
    test_battery_never_exceeds_100()
    test_invalid_initial_soc()
    print("All battery controller tests passed!")
