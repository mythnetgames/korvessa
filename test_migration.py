#!/usr/bin/env python
"""Test NPC migration script."""

import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.conf.settings")
django.setup()

from world.builder_storage import get_all_npcs, migrate_npc_skills

print("Running NPC skill migration...")
migrate_npc_skills()

print("\nAll NPCs after migration:")
npcs = get_all_npcs()
print(f"Total NPCs: {len(npcs)}\n")

for i, npc in enumerate(npcs[:10], 1):
    skills = npc.get('skills', {})
    non_zero_skills = {k: v for k, v in skills.items() if v > 0}
    print(f"{i}. {npc['name']} (ID: {npc['id']})")
    if non_zero_skills:
        skill_str = ", ".join([f"{k}:{v}" for k, v in list(non_zero_skills.items())[:3]])
        print(f"   Skills: {skill_str}")
    else:
        print(f"   Skills: (none set)")

print(f"\nTotal skills per NPC: {len(npcs[0].get('skills', {})) if npcs else 0}")
if npcs:
    print(f"Sample skills from first NPC: {list(npcs[0].get('skills', {}).keys())}")
