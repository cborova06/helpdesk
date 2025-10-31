#!/usr/bin/env python3
"""Update all AI insights with Turkish-only values"""

def execute():
    from helpdesk.debug import backfill_ticket_ai
    
    print("Updating all AI insights with Turkish values...")
    result = backfill_ticket_ai(limit=None, only_missing=False)
    print(f"Updated: {result}")
    return result

if __name__ == "__main__":
    execute()
