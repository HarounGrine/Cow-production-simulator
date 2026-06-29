<<<<<<< HEAD
import statistics
from metrics import evaluate_herd

def monte_carlo(feed_type, medicine_type, n=1000):
    results = []

    for i in range(n):
        results.append(evaluate_herd(100, 0.5, 120, feed_type, medicine_type))
    
    
    profits = [r["total_profit"] for r in results]
    rois = [r["herd_roi"] for r in results]
    months = [r["avg_months"] for r in results]

    return {
        "avg_profit": statistics.mean(profits),
        "q1_profit": statistics.quantiles(profits, n=4)[0],
        "q3_profit": statistics.quantiles(profits, n=4)[2],
        "std_dev_profit": statistics.stdev(profits) if len(profits) > 1 else 0,
        "avg_roi": statistics.mean(rois),
        "std_dev_roi": statistics.stdev(rois) if len(rois) > 1 else 0,
        "avg_months": statistics.mean(months),
    }

budget = monte_carlo("budget", "basic", 1000)
premium = monte_carlo("premium", "premium", 1000)

print("BUDGET:", budget)
=======
import statistics
from metrics import evaluate_herd

def monte_carlo(feed_type, medicine_type, n=1000):
    results = []

    for i in range(n):
        results.append(evaluate_herd(100, 0.5, 120, feed_type, medicine_type))
    
    
    profits = [r["total_profit"] for r in results]
    rois = [r["herd_roi"] for r in results]
    months = [r["avg_months"] for r in results]

    return {
        "avg_profit": statistics.mean(profits),
        "q1_profit": statistics.quantiles(profits, n=4)[0],
        "q3_profit": statistics.quantiles(profits, n=4)[2],
        "std_dev_profit": statistics.stdev(profits) if len(profits) > 1 else 0,
        "avg_roi": statistics.mean(rois),
        "std_dev_roi": statistics.stdev(rois) if len(rois) > 1 else 0,
        "avg_months": statistics.mean(months),
    }

budget = monte_carlo("budget", "basic", 1000)
premium = monte_carlo("premium", "premium", 1000)

print("BUDGET:", budget)
>>>>>>> b51322418df800ac0489e6af571bac9f3f7645c3
print("PREMIUM:", premium)