#!/usr/bin/env python3
"""
Break-even CPC model for buying traffic to bestdealsonline.us.

Answers one question: what is the MOST we can pay for a visitor and still
make money, given Amazon Associates commission rates?

Commission rates below are the ACTUAL rate card for store bestdeals00d9-20,
read from Associates Central > Rate Plan on 2026-07-28.

Usage:  python3 scripts/paid_traffic_math.py
"""

# --- Actual rate card for bestdeals00d9-20 (US), read 2026-07-28 -------------
RATE_CARD = {
    "Kitchen & Dining":                 0.045,
    "Automotive | Books & Textbooks":   0.045,
    "Luggage | Clothing | Shoes | Watches | Jewelry": 0.040,
    "All Other Categories":             0.040,
    "Home | Home Improvement | Toys & Games | Sports & Fitness | "
    "Baby | Pet | Furniture | Headphones | Outdoor": 0.030,
    "Computers, Tablets & Components":  0.025,
    "Home Entertainment: TV":           0.020,
    "Grocery | Health & Household":     0.010,
}

# What the site actually writes about, weighted by page count.
# (air fryer/kitchen, chargers/power banks/SSDs, backpacks, toys, fitness, home)
CONTENT_MIX = [
    ("Kitchen & Dining",                0.045, 0.25),   # air fryer, toaster oven, kitchen
    ("Computers, Tablets & Components", 0.025, 0.30),   # chargers, power banks, SSD, webcam, router
    ("Home / Toys / Sports / Tools",    0.030, 0.35),   # storage, tools, fitness, toys, vacuums
    ("Luggage & Accessories",           0.040, 0.10),   # backpacks
]


def blended_rate() -> float:
    return sum(rate * weight for _, rate, weight in CONTENT_MIX)


def revenue_per_visit(aov, commission, order_rate, amazon_ctr) -> float:
    """
    aov          - average order value on Amazon ($)
    commission   - blended commission rate
    order_rate   - P(order within 24h cookie | click through to Amazon)
    amazon_ctr   - P(visitor clicks an Amazon link | lands on our page)
    """
    return amazon_ctr * order_rate * aov * commission


SCENARIOS = [
    # name,          aov, order_rate, amazon_ctr
    ("Pessimistic",   35, 0.05, 0.12),
    ("Conservative",  40, 0.07, 0.18),
    ("Base case",     45, 0.09, 0.22),
    ("Optimistic",    55, 0.12, 0.30),
    ("Dream",         70, 0.15, 0.40),
]

# Realistic CPC floors, US, 2026. Sources: typical account benchmarks.
CPC_FLOORS = [
    ("Google Search - commercial product terms", 0.90),
    ("Google Search - cheapest long-tail informational", 0.35),
    ("Google Performance Max / Display",         0.25),
    ("Microsoft (Bing) Search - long-tail",      0.22),
    ("Meta (Facebook/IG) traffic campaign",      0.35),
    ("Pinterest ads - traffic objective",        0.30),
    ("Taboola / Outbrain native (low quality)",  0.06),
]


def main():
    rate = blended_rate()
    print("=" * 74)
    print("BREAK-EVEN CPC — bestdealsonline.us  (store bestdeals00d9-20)")
    print("=" * 74)

    print("\nBlended commission rate from actual content mix:")
    for name, r, w in CONTENT_MIX:
        print(f"   {w:4.0%}  {name:<34} @ {r:5.2%}")
    print(f"   {'':4}  {'BLENDED':<34} = {rate:5.3%}")

    print("\n" + "-" * 74)
    print(f"{'Scenario':<14}{'AOV':>6}{'ord/clk':>9}{'amz CTR':>9}"
          f"{'$/order':>10}{'MAX CPC':>10}")
    print("-" * 74)
    results = {}
    for name, aov, order_rate, ctr in SCENARIOS:
        rpv = revenue_per_visit(aov, rate, order_rate, ctr)
        results[name] = rpv
        print(f"{name:<14}{aov:>6.0f}{order_rate:>9.0%}{ctr:>9.0%}"
              f"{aov*rate:>10.2f}{rpv:>10.4f}")
    print("-" * 74)
    print("MAX CPC = the most you can pay per visitor and still break even ($0 profit).")

    base = results["Base case"]
    dream = results["Dream"]

    print("\n" + "=" * 74)
    print("WHAT TRAFFIC ACTUALLY COSTS vs. WHAT A VISITOR IS WORTH")
    print("=" * 74)
    print(f"{'Channel':<44}{'CPC':>8}{'vs base':>10}{'vs dream':>10}")
    print("-" * 74)
    for chan, cpc in CPC_FLOORS:
        print(f"{chan:<44}{cpc:>8.2f}{cpc/base:>9.0f}x{cpc/dream:>9.0f}x")
    print("-" * 74)
    print(f"base case visitor value  = ${base:.4f}   ({base*1000:.2f} per 1,000 visits)")
    print(f"dream case visitor value = ${dream:.4f}   ({dream*1000:.2f} per 1,000 visits)")

    print("\n" + "=" * 74)
    print("WHAT $500 OF PAID TRAFFIC BUYS YOU")
    print("=" * 74)
    budget = 500
    for chan, cpc in CPC_FLOORS:
        visits = budget / cpc
        rev = visits * base
        orders = visits * 0.22 * 0.09
        print(f"{chan:<44} {visits:>7.0f} visits -> "
              f"{orders:>4.1f} orders, ${rev:>6.2f} back  (lose ${budget-rev:>6.2f})")

    print("\n" + "=" * 74)
    print("THE 3-SALE QUESTION (account survival, ~Sept 2026 deadline)")
    print("=" * 74)
    need = 3
    visits_needed = need / (0.22 * 0.09)
    print(f"Orders needed: {need}")
    print(f"Visits needed at base-case funnel: {visits_needed:,.0f}")
    print(f"Amazon clicks needed:              {visits_needed*0.22:,.0f}")
    print("\nCost to buy that traffic:")
    for chan, cpc in CPC_FLOORS:
        print(f"   {chan:<44} ${visits_needed*cpc:>8,.0f}")
    print(f"\nCommission earned from those 3 orders: "
          f"${need * 45 * rate:.2f}")


if __name__ == "__main__":
    main()
