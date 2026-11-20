import pytest
from render import taa_history as mod

CASES = [
    ("reproj", 'm.reproject((0.5, 0.5), (0.1, 0.2)) == approx((0.4, 0.3))'),
    ("reject", 'm.depth_reject(0.5, 0.55, 0.1) is True'),
    ("reject2", 'm.depth_reject(0.5, 0.8, 0.1) is False'),
    ("blend", 'm.blend_linear(1, 3, 0.5) == approx(2.0)'),
    ("cut", 'm.reset_on_cut(True) is True'),
    ("write", 'm.write_history(0.5) is False'),
    ("jitter", 'm.jitter(5, 4) == approx(0.25)'),
    ("clamp", 'm.clamp_history(1.5, 0, 1) == 1.0'),
    ("scale", 'm.uv_after_scale((0.5, 0.5), 2, 1) == approx((1.0, 1.0))'),
    ("order", 'm.sharpen_order("taa_then_sharpen") is True'),
    ("motion", 'm.valid_motion((3, 4), 6) is True'),
    ("weight", 'm.history_weight(3, 0.5) == approx(0.25)'),
    ("depth", 'm.linear_depth(0.5, 1, 10) == approx(1.818182)'),
    ("reset", 'm.reset_flag(False, True) is True'),
    ("id", 'm.taa_id(3, 2) == "3:2"')
]

@pytest.mark.parametrize("name,expr", CASES, ids=[c[0] for c in CASES])
def test_contract(name, expr):
    assert eval(expr, {"m": mod, "approx": pytest.approx})
