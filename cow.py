
import random
import re

FEED_TYPES = {
    "budget":   {"cost_mult": 0.75, "growth_mult": 0.88, 
                 "illness_prob": 0.06, "stress_drift": 0.02,"revenue_mult": 0.90},
    "standard": {"cost_mult": 1.0,  "growth_mult": 1.0,  
                 "illness_prob": 0.03, "stress_drift": 0.0, "revenue_mult": 1.0},
    "premium":  {"cost_mult": 1.25, "growth_mult": 1.12, 
                 "illness_prob": 0.015, "stress_drift": -0.02, "revenue_mult": 1.15}
}

MEDICINE_TYPES = {
    "basic":    {"cost": 50,  "recovery_months": 2, "success_rate": 0.80, "revenue_mult": 0.92},
    "standard": {"cost": 150, "recovery_months": 1, "success_rate": 0.90, "revenue_mult": 1.0},
    "premium":  {"cost": 300, "recovery_months": 0, "success_rate": 0.99, "revenue_mult": 1.08}
}
class Cow: 
     
    def __init__(self, cow_id, cow_type, genetic_multiplier,feed_type="standard", medicine_type="standard"):
       # Identity
        self.id = cow_id
        self.type = cow_type
        self.GM = genetic_multiplier

        # Age and biological state
        self.age = 0
        self.stage = "calf"
        self.weight = 40

        # Reproduction / lactation
        self.lactation_number = 0
        self.months_in_cycle = 0

        # Feed
        self.feed_type = feed_type
        self.feed_cost_mult = FEED_TYPES[feed_type]["cost_mult"]
        self.feed_growth_mult = FEED_TYPES[feed_type]["growth_mult"]
        self.illness_prob = FEED_TYPES[feed_type]["illness_prob"]
        self.stress_drift = FEED_TYPES[feed_type]["stress_drift"]

        # Medicine
        self.medicine_type = medicine_type
        self.treatment_cost = MEDICINE_TYPES[medicine_type]["cost"]
        self.recovery_months = MEDICINE_TYPES[medicine_type]["recovery_months"]
        self.success_rate = MEDICINE_TYPES[medicine_type]["success_rate"]
        
        # Health state
        self.stress_level = FEED_TYPES[feed_type]["stress_drift"] + 0.2
        self.is_sick = False
        self.recovery_countdown = 0

        # Financial tracking
        self.cumulative_feed_cost = 0
        self.cumulative_vet_cost = 0
        self.cumulative_revenue = 0
        self.feed_revenue_mult = FEED_TYPES[feed_type]["revenue_mult"]
        self.medicine_revenue_mult = MEDICINE_TYPES[medicine_type]["revenue_mult"]

        # Simulation control
        self.is_alive = True
        self.exit_reason = None
    
    def advance_month(self):    
        if not self.is_alive:
            return

    # Advance age and cycle
        self.age += 1
        self.months_in_cycle += 1

    # Natural stress recovery + feed drift
        self.stress_level -= 0.05
        self.stress_level += self.stress_drift
        self.stress_level = max(0.0, min(1.0, self.stress_level))

    # Illness check (only if not already sick)
        if not self.is_sick and random.random() < self.illness_prob:
            self.is_sick = True
            self.stress_level += 0.2
            self.stress_level = max(0.0, min(1.0, self.stress_level))

        # Sickness effects
        if self.is_sick:
            self.stress_level += 0.1
            self.stress_level = max(0.0, min(1.0, self.stress_level))
            self.cumulative_vet_cost += self.treatment_cost
            if random.random() < self.success_rate:
                self.is_sick = False
                self.recovery_countdown = self.recovery_months

        elif self.recovery_countdown > 0:
            self.recovery_countdown -= 1

        # Stress multiplier
        self.stress_multiplier = 1.1 - (self.stress_level * 0.4)
        self.stress_multiplier = max(0.5, min(1.1, self.stress_multiplier))

        # Sickness/recovery GM penalty
        if self.is_sick or self.recovery_countdown > 0:
            effective_gm = self.GM * 0.85
        else:
            effective_gm = self.GM

        # Stage logic
        if self.stage == "calf":
            self.weight += 27 * effective_gm * self.feed_growth_mult * self.stress_multiplier
            self.cumulative_feed_cost += 20 * self.feed_cost_mult
            self.cumulative_vet_cost += 10
            if self.age >= 2:
                self.stage = "growing"
                self.months_in_cycle = 0

        elif self.stage == "growing":
            self.weight += 24 * effective_gm * self.feed_growth_mult * self.stress_multiplier
            self.cumulative_feed_cost += self.weight * 0.05 * self.feed_cost_mult
            self.cumulative_vet_cost += 5
            if self.type == "beef" and self.age >= 12:
                self.stage = "finishing"
                self.months_in_cycle = 0
            elif self.type == "dairy" and self.age >= 15:
                self.stage = "lactating"
                self.months_in_cycle = 0

        elif self.stage == "finishing":
            self.weight += 36 * effective_gm * self.feed_growth_mult * self.stress_multiplier
            self.cumulative_feed_cost += self.weight * 0.07 * self.feed_cost_mult
            self.cumulative_vet_cost += 5
            if self.weight >= 600:
                self.cumulative_revenue += self.weight * 4.0 * self.feed_revenue_mult * self.medicine_revenue_mult
                self.stage = "slaughtered"
                self.is_alive = False
                self.exit_reason = "slaughtered"

        elif self.stage == "lactating":
            self.weight += 2
            self.cumulative_feed_cost += self.weight * 0.06 * self.feed_cost_mult
            self.cumulative_vet_cost += 5
            self.cumulative_revenue += 25 * 30 * 0.40 * effective_gm * self.stress_multiplier
            if self.months_in_cycle >= 10:
                self.stage = "dry"
                self.months_in_cycle = 0

        elif self.stage == "dry":
            self.cumulative_feed_cost += self.weight * 0.04 * self.feed_cost_mult
            self.cumulative_vet_cost += 5
            if self.months_in_cycle >= 2:
                self.lactation_number += 1
                if self.lactation_number >= 4:
                    self.cumulative_revenue += self.weight * 2.5 * self.feed_revenue_mult * self.medicine_revenue_mult
                    self.stage = "culled"
                    self.is_alive = False
                    self.exit_reason = "culled"
                else:
                    self.stage = "lactating"
                    self.months_in_cycle = 0
    @property
    
    def profit(self):
        return (
            self.cumulative_revenue
            - self.cumulative_feed_cost
            - self.cumulative_vet_cost
        )
    @property
    def roi(self):
        total_cost = (
        self.cumulative_feed_cost
        + self.cumulative_vet_cost
    )

        if total_cost == 0:
            return 0

        return (self.profit / total_cost) * 100
    @property
    def cost (self):
        return (
        self.cumulative_feed_cost
        + self.cumulative_vet_cost
    )

    