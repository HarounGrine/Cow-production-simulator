

from simulation import run_simulation


def evaluate_herd(herd_size, dairy_ratio, max_months=120, feed_type="standard", medicine_type="basic"):
    cows = run_simulation(herd_size, dairy_ratio, max_months, feed_type, medicine_type)
    total_profit = sum(cow.profit for cow in cows)
    total_cost = sum(cow.cost for cow in cows)
    herd_roi = total_profit / total_cost * 100 if total_cost != 0 else 0
    avg_months = sum(cow.age for cow in cows) / len(cows) if cows else 0
    
    return {
        "total_profit": total_profit,
        "herd_roi": herd_roi,
        "avg_months": avg_months,
    }

