import math

# 透明像素 alpha 达到该值才允许写入历史，低于它的（玻璃/粒子等）不写历史，
# 避免半透明物体在历史缓冲里留下鬼影。
HISTORY_ALPHA_THRESHOLD = 1.0

# 相对深度判定的小量，防止极近平面归一化时除零。
DEPTH_EPSILON = 1e-6


def reproject(uv, motion):
    """运动矢量重投影。

    旧实现只拿上一帧视图矩阵反投影，角色快速转身时历史全部错位。
    正确做法是用上一帧几何阶段生成的逐像素运动矢量：当前帧像素坐标
    减去运动矢量，即得到它在历史缓冲中的采样 UV。
    """
    u, v = uv
    mu, mv = motion
    return (u - mu, v - mv)


def depth_reject(prev, current, threshold):
    """深度拒绝（按视差分层）。

    固定阈值会把近处角色和远处背景一视同仁。这里把阈值解释为相对
    当前深度的比例：允许的深度差 = threshold * current，越近的平面
    允许的绝对偏差越小，远处背景则更宽容。返回 True 表示深度一致、
    历史可接受；False 表示视差异常，拒绝该历史像素。
    """
    return abs(prev - current) <= threshold * max(current, DEPTH_EPSILON)


def blend_linear(history, current, alpha):
    """历史混合（线性 HDR 域）。

    必须在 tonemap 之前的线性 HDR 空间做指数移动平均，否则亮部经过
    tonemap 压缩后残留在画面里形成白雾。alpha 是当前帧权重，
    历史权重为 (1 - alpha)。
    """
    return history * (1.0 - alpha) + current * alpha


def reset_on_cut(cut):
    """切镜重置。

    相机 cut 后两帧之间没有任何相关性，必须清空历史；否则切镜第一帧
    整屏都是上一镜头的残影。cut 为真时返回 True，由调用方丢弃历史。
    """
    return bool(cut)


def write_history(alpha):
    """透明写历史判定。

    透明物体（alpha < 1）不写入历史缓冲，玻璃后面的场景才不会被
    半透明颜色污染而拖出鬼影；只有完全不透明像素才回写历史。
    """
    return alpha >= HISTORY_ALPHA_THRESHOLD


def jitter(frame, count):
    """jitter 序列（连续 Halton 风格取模索引）。

    旧实现每帧把序列重置回第 0 项，静止画面也一直在闪。序列必须
    跨帧连续推进，用 frame 对周期 count 取模得到当前项索引，
    再归一化到 [0, 1) 抖动幅度；count 非正时退化为 0（无抖动）。
    """
    if count <= 0:
        return 0.0
    return (frame % count) / count


def clamp_history(value, low, high):
    """历史颜色钳制。

    把重投影后的历史颜色钳到当前帧邻域颜色的 [low, high] 包围盒内，
    HDR 高光就不会溢出到邻域像素，抑制亮边扩散。
    """
    return min(max(value, low), high)


def uv_after_scale(uv, old_scale, new_scale):
    """动态分辨率切换后的历史 UV 重算。

    分辨率按比例缩放后，历史纹理与当前缓冲的像素网格不再一一对应，
    需按 old_scale / new_scale 重算采样 UV，画面才不会整体偏移。
    """
    u, v = uv
    factor = old_scale / new_scale
    return (u * factor, v * factor)


def sharpen_order(order):
    """锐化顺序判定。

    锐化必须放在 TAA 之后：先锐化会把 TAA 的残影也锐化成硬边。
    接受管线名称字符串或管线阶段序列，只有顺序为
    TAA -> sharpen 时返回 True。
    """
    if isinstance(order, str):
        return order == "taa_then_sharpen"
    try:
        stages = list(order)
    except TypeError:
        return False
    return "taa" in stages and "sharpen" in stages and stages.index("taa") < stages.index("sharpen")


def camera_history_key(camera):
    """双眼独立历史的缓冲键。

    分屏/立体渲染时左右眼不能共用一份历史，否则左眼颜色污染右眼。
    以相机的 eye/视图标识作为历史缓冲键，保证每只眼拿到独立历史。
    """
    if isinstance(camera, dict):
        return camera.get("eye", camera.get("id", camera.get("view", "default")))
    return camera


def valid_motion(motion, max_len):
    """运动矢量合法性检查。

    长度超过 max_len 的运动矢量视为无效（重投影点落在合理范围外），
    调用方应丢弃该历史并回退到当前帧颜色，防止长矢量拉鬼影。
    """
    mx, my = motion
    return math.hypot(mx, my) <= max_len


def history_weight(frame, cap):
    """历史权重上限。

    历史权重随帧推进按 cap 几何衰减（frame 1 时为 1，之后每帧乘以
    cap），再老的历史也不会无限累积；cap 同时是单帧历史权重的上限。
    """
    if frame <= 1:
        return 1.0
    return cap ** (frame - 1)


def linear_depth(depth, near, far):
    """深度线性化。

    硬件深度是双曲线分布的非线性深度，直接比较会让近处分辨率过密、
    远处过疏。转回视图空间线性深度后再做视差分层判定。
    """
    return (near * far) / (far - depth * (far - near))


def reset_flag(cut, moved):
    """重置标记。

    两类情况必须重置历史：相机 cut（两帧无相关性），以及遮挡关系
    变化（被墙挡住的像素不能一直带着旧颜色）。任一条件成立即重置。
    """
    return bool(cut) or bool(moved)


def taa_id(seed, index):
    """TAA 实例标识。

    多视图（左右眼、分屏玩家）各自持有独立的 TAA 状态，用
    "seed:index" 组合成唯一 id，避免历史缓冲串用。
    """
    return f"{seed}:{index}"
