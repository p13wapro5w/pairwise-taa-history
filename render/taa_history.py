import math

def reproject(uv, motion):
    """运动矢量重投影。"""
    raise NotImplementedError("TODO: reproject")

def depth_reject(prev, current, threshold):
    """深度拒绝。"""
    raise NotImplementedError("TODO: depth_reject")

def blend_linear(history, current, alpha):
    """历史混合。"""
    raise NotImplementedError("TODO: blend_linear")

def reset_on_cut(cut):
    """切镜重置。"""
    raise NotImplementedError("TODO: reset_on_cut")

def write_history(alpha):
    """透明写历史。"""
    raise NotImplementedError("TODO: write_history")

def jitter(frame, count):
    """jitter 序列。"""
    raise NotImplementedError("TODO: jitter")

def clamp_history(value, low, high):
    """历史钳制。"""
    raise NotImplementedError("TODO: clamp_history")

def uv_after_scale(uv, old_scale, new_scale):
    """分辨率缩放 UV。"""
    raise NotImplementedError("TODO: uv_after_scale")

def sharpen_order(order):
    """锐化顺序。"""
    raise NotImplementedError("TODO: sharpen_order")

def camera_history_key(camera):
    """双眼历史键。"""
    raise NotImplementedError("TODO: camera_history_key")

def valid_motion(motion, max_len):
    """运动矢量合法性。"""
    raise NotImplementedError("TODO: valid_motion")

def history_weight(frame, cap):
    """历史权重上限。"""
    raise NotImplementedError("TODO: history_weight")

def linear_depth(depth, near, far):
    """深度线性化。"""
    raise NotImplementedError("TODO: linear_depth")

def reset_flag(cut, moved):
    """重置标记。"""
    raise NotImplementedError("TODO: reset_flag")

def taa_id(seed, index):
    """TAA id。"""
    raise NotImplementedError("TODO: taa_id")
