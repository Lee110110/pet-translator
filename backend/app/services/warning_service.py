from app.models.checkin import Checkin
from app.models.baseline import Baseline


def determine_warning_level(checkin: Checkin, deviations: dict | None = None) -> tuple[str, str]:
    """根据打卡数据和基线偏差判定预警等级
    返回 (warning_level, message)
    """
    scores = {
        "diet": checkin.diet_score,
        "water": checkin.water_score,
        "stool": checkin.stool_score,
        "spirit": checkin.spirit_score,
    }

    low_count = sum(1 for s in scores.values() if s <= 2)
    very_low_count = sum(1 for s in scores.values() if s == 1)

    high_water = scores["water"] >= 4

    details = []

    if very_low_count >= 1:
        for metric, score in scores.items():
            if score == 1:
                details.append(f"{_metric_label(metric)}极低")

    if low_count >= 3:
        level = "red"
        details.append("多个指标同时偏低")
    elif very_low_count >= 1 and low_count >= 2:
        level = "red"
    elif low_count >= 2:
        level = "orange"
        details.append("多个指标偏低")
    elif very_low_count >= 1:
        level = "orange"
    elif low_count >= 1:
        level = "yellow"
        details.append(f"个别指标偏低")
    elif high_water:
        level = "yellow"
        details.append("饮水量偏高，需关注")
    else:
        level = "green"

    if deviations:
        for metric, dev in deviations.items():
            if dev.get("sigma", 0) >= 2:
                if level in ("green", "yellow"):
                    level = "orange"
                details.append(f"{_metric_label(metric)}偏离基线{dev['sigma']:.1f}个标准差")
            elif dev.get("sigma", 0) >= 1:
                if level == "green":
                    level = "yellow"
                details.append(f"{_metric_label(metric)}轻微偏离基线")

    message = "；".join(details) if details else "各项指标正常"
    return level, message


def _metric_label(metric: str) -> str:
    return {"diet": "饮食量", "water": "饮水量", "stool": "排便", "spirit": "精神状态"}.get(metric, metric)