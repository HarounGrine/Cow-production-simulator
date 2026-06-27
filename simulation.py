
import random
from cow import Cow

def run_simulation(herd_size, dairy_ratio, max_months=120, feed_type="standard", medicine_type="basic"):
    cows = []
    for i in range(herd_size):
        cow_type = "dairy" if random.random() < dairy_ratio else "beef"
        cows.append(Cow(i, cow_type, 0.85 + random.random() * 0.3, feed_type, medicine_type))
    for cow in cows:
        while cow.is_alive and cow.age < max_months:
            cow.advance_month()
    return cows
        
