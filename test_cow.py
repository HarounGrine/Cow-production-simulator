from cow import Cow

def test_beef_cow():
    cow = Cow(1, "beef", 1.0, feed_type="premium", medicine_type="premium")
    while cow.is_alive:
        cow.advance_month()
        print(f"month: {cow.age}, weight: {cow.weight}, cost: {cow.cost}, revenue: {cow.cumulative_revenue}, feed_type: {cow.feed_type}")
    
    print(f"beef grade: {cow.beef_grade}, carcass weight: {cow.carcass_weight}, dressing percentage: {cow.dressing_percentage}, illness count: {cow.illness_count}, avg stress level: {cow.avg_stress_level}, illness count: {cow.illness_count},profit: {cow.profit}, roi: {cow.roi}%",)

def test_dairy_cow():
    cow = Cow(1, "dairy", 1.0, feed_type="premium", medicine_type="premium") 
    while cow.is_alive:
        cow.advance_month()
        print(f"month: {cow.age}, weight: {cow.weight}, cost: {cow.cost}, revenue: {cow.cumulative_revenue}, feed_type: {cow.feed_type}")
    
    print(f"peak milk yield: {cow.peak_milk_yield}, total milk liters: {cow.total_milk_liters}, illness count: {cow.illness_count}, avg stress level: {cow.avg_stress_level}, illness count: {cow.illness_count},profit: {cow.profit}, roi: {cow.roi}%",)
    print(f"monthly milk liters: {cow.monthly_milk_liters[-3:]}, monthly milk quality: {cow.monthly_milk_quality[-3:]}")

    
    
if __name__ == "__main__":
    print("=== BEEF COW TEST ===")
    test_beef_cow()
    print("\n=== DAIRY COW TEST ===")
    test_dairy_cow()