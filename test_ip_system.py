"""Test the IP skill progression system."""
import math

SKILL_MAX = 100
IP_SKILL_TIERS = [
    (0, 20, 1.0, 1.04),
    (21, 45, 2.0, 1.06),
    (46, 75, 4.0, 1.075),
    (76, 89, 8.0, 1.09),
    (90, 99, 16.0, 1.12),
]

def get_ip_tier(s):
    for start, end, base, growth in IP_SKILL_TIERS:
        if start <= s <= end:
            return start, end, base, growth
    raise ValueError(f'Skill {s} not in tier')

def ip_cost_for_next_point(s):
    if s < 0 or s >= SKILL_MAX:
        return 0
    start, end, base, growth = get_ip_tier(s)
    x = s - start
    return math.ceil(base * (growth ** x))

def total_ip_to_reach(target):
    target = max(0, min(SKILL_MAX, target))
    total = 0
    for s in range(0, target):
        total += ip_cost_for_next_point(s)
    return total

print('=== IP COSTS PER TIER ===')
print('Tier 1 (0-20) Novice:')
print(f'  0->1: {ip_cost_for_next_point(0)} IP, 10->11: {ip_cost_for_next_point(10)} IP, 20->21: {ip_cost_for_next_point(20)} IP')
print('Tier 2 (21-45) Competent:')
print(f'  21->22: {ip_cost_for_next_point(21)} IP, 35->36: {ip_cost_for_next_point(35)} IP, 45->46: {ip_cost_for_next_point(45)} IP')
print('Tier 3 (46-75) Professional:')
print(f'  46->47: {ip_cost_for_next_point(46)} IP, 60->61: {ip_cost_for_next_point(60)} IP, 75->76: {ip_cost_for_next_point(75)} IP')
print('Tier 4 (76-89) Advanced:')
print(f'  76->77: {ip_cost_for_next_point(76)} IP, 85->86: {ip_cost_for_next_point(85)} IP, 89->90: {ip_cost_for_next_point(89)} IP')
print('Tier 5 (90-99) Near-Perfect:')
print(f'  90->91: {ip_cost_for_next_point(90)} IP, 95->96: {ip_cost_for_next_point(95)} IP, 99->100: {ip_cost_for_next_point(99)} IP')

print()
print('=== TOTAL IP TO REACH MILESTONES ===')
for level in [10, 20, 30, 45, 50, 60, 75, 80, 89, 90, 95, 100]:
    print(f'  Skill {level}: {total_ip_to_reach(level):,} total IP')
