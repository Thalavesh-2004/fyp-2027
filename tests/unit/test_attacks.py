import pytest
from attacks.value_corruption import ValueCorruptionAttack
from attacks.wrong_aggregation import WrongAggregationAttack
from attacks.drop_computation import DropComputationAttack
from attacks.delay_attack import DelayAttack
from attacks.controller import AttackController

def test_value_corruption_additive():
    attack = ValueCorruptionAttack(strategy="additive", value=50.0, target_field="temperature")
    record = {"temperature": 30.0, "sensor_id": "S001"}
    result = attack.apply(record)

    assert result["temperature"] == 80.0
    assert result["attack_applied"] is True
    assert result["original_value"] == "30.0"

def test_wrong_aggregation_offset():
    attack = WrongAggregationAttack(strategy="offset", offset=25.0)
    record = {"avg_temperature": 31.5, "sensor_id": "S001"}
    result = attack.apply(record)

    assert result["avg_temperature"] == 56.5
    assert result["attack_applied"] is True

def test_drop_computation():
    attack = DropComputationAttack()
    record = {"event_id": 1001, "temperature": 30.0}
    result = attack.apply(record)

    assert result["dropped"] is True
    assert result["attack_applied"] is True

def test_attack_controller_disabled():
    cfg = {"attack": {"enabled": False, "type": "VALUE_CORRUPTION", "probability": 1.0}}
    ctrl = AttackController(cfg)
    record = {"temperature": 30.0, "sensor_id": "S001"}
    res = ctrl.process_record(record, hostname="host-1")

    assert res["attack_applied"] is False
    assert res["temperature"] == 30.0

def test_attack_controller_prob_one():
    cfg = {
        "attack": {
            "enabled": True,
            "type": "VALUE_CORRUPTION",
            "probability": 1.0,
            "corruption": {"strategy": "additive", "value": 50.0}
        }
    }
    ctrl = AttackController(cfg)
    record = {"temperature": 30.0, "sensor_id": "S001"}
    res = ctrl.process_record(record, hostname="host-1")

    assert res["attack_applied"] is True
    assert res["temperature"] == 80.0
