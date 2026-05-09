import statistics
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.checkin import Checkin
from app.models.baseline import Baseline


async def calculate_baseline(pet_id: int, metric_type: str, db: AsyncSession) -> Baseline | None:
    """计算某只宠物某项指标的个体基线"""
    result = await db.execute(
        select(Checkin)
        .where(Checkin.pet_id == pet_id)
        .order_by(Checkin.checkin_date.desc())
        .limit(14)
    )
    checkins = result.scalars().all()

    if len(checkins) < 3:
        return None

    scores = [getattr(c, f"{metric_type}_score") for c in checkins]
    scores.reverse()

    window = scores[-7:] if len(scores) >= 7 else scores
    baseline_value = statistics.mean(window)
    std_deviation = statistics.stdev(window) if len(window) >= 2 else 0.5

    start_date = checkins[-1].checkin_date
    end_date = checkins[0].checkin_date

    baseline = Baseline(
        pet_id=pet_id,
        metric_type=metric_type,
        baseline_value=round(baseline_value, 2),
        std_deviation=round(std_deviation, 2),
        start_date=start_date,
        end_date=end_date,
        data_points=len(window),
        is_established=len(window) >= 7,
    )

    existing = await db.execute(
        select(Baseline).where(
            Baseline.pet_id == pet_id,
            Baseline.metric_type == metric_type,
        ).order_by(Baseline.end_date.desc()).limit(1)
    )
    existing_baseline = existing.scalar_one_or_none()
    if existing_baseline:
        existing_baseline.baseline_value = baseline.baseline_value
        existing_baseline.std_deviation = baseline.std_deviation
        existing_baseline.start_date = baseline.start_date
        existing_baseline.end_date = baseline.end_date
        existing_baseline.data_points = baseline.data_points
        existing_baseline.is_established = baseline.is_established
        await db.flush()
        return existing_baseline
    else:
        db.add(baseline)
        await db.flush()
        return baseline


async def check_deviations(pet_id: int, checkin: Checkin, db: AsyncSession) -> dict:
    """检查打卡数据与基线的偏差"""
    result = await db.execute(
        select(Baseline).where(Baseline.pet_id == pet_id)
    )
    baselines = {b.metric_type: b for b in result.scalars().all()}

    deviations = {}
    for metric in ["diet", "water", "stool", "spirit"]:
        baseline = baselines.get(metric)
        if not baseline or not baseline.is_established:
            continue

        actual = getattr(checkin, f"{metric}_score")
        diff = actual - baseline.baseline_value
        sigma = abs(diff) / baseline.std_deviation if baseline.std_deviation > 0 else 0

        if sigma >= 1:
            deviations[metric] = {
                "actual": actual,
                "baseline": baseline.baseline_value,
                "diff": round(diff, 2),
                "sigma": round(sigma, 2),
            }

    return deviations


async def get_chart_data(pet_id: int, db: AsyncSession) -> dict:
    """获取基线对比图表数据"""
    result = await db.execute(
        select(Checkin)
        .where(Checkin.pet_id == pet_id)
        .order_by(Checkin.checkin_date.asc())
        .limit(30)
    )
    checkins = result.scalars().all()

    result2 = await db.execute(
        select(Baseline).where(Baseline.pet_id == pet_id)
    )
    baselines = {b.metric_type: b for b in result2.scalars().all()}

    chart_data = {}
    for metric in ["diet", "water", "stool", "spirit"]:
        bl = baselines.get(metric)
        chart_data[metric] = {
            "dates": [c.checkin_date.isoformat() for c in checkins],
            "actual": [getattr(c, f"{metric}_score") for c in checkins],
            "baseline_value": bl.baseline_value if bl else None,
            "baseline_upper": (bl.baseline_value + bl.std_deviation) if bl else None,
            "baseline_lower": (bl.baseline_value - bl.std_deviation) if bl else None,
            "is_established": bl.is_established if bl else False,
        }

    return chart_data