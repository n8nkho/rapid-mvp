#!/usr/bin/env python3
"""Remove all clients and engagements except the one specified (e.g. ENG-016).
Usage: python scripts/retain_engagement_only.py ENG-016
       python scripts/retain_engagement_only.py ENG016
Requires SUPABASE_URL and SUPABASE_KEY. Destructive: run only when you intend to wipe other data."""

import os
import sys

# Allow importing from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import retain_only_engagement

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/retain_engagement_only.py ENG-016")
        sys.exit(1)
    target = sys.argv[1].strip()
    if not target:
        print("Provide an engagement id (e.g. ENG-016)")
        sys.exit(1)
    result = retain_only_engagement(target)
    print(result.get("message", result))
    if result.get("deleted"):
        print("Deleted:", result["deleted"])
    if not result.get("ok"):
        sys.exit(2)

if __name__ == "__main__":
    main()
