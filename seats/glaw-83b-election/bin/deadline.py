#!/usr/bin/env python3
"""83(b) 30-day deadline calculator. Usage: deadline.py YYYY-MM-DD
Day 0 (transfer) excluded; 30 calendar days; weekend/US-federal-holiday rolls forward (IRC 7503)."""
import sys, datetime as dt

def us_holidays(year):
    H = set()
    def nth_weekday(y, month, weekday, n):  # n-th weekday (0=Mon)
        d = dt.date(y, month, 1); offs = (weekday - d.weekday()) % 7
        return d + dt.timedelta(days=offs + 7*(n-1))
    def last_weekday(y, month, weekday):
        d = dt.date(y, month, 28)
        nxt = (dt.date(y+1,1,1) if month==12 else dt.date(y,month+1,1))
        last_day = nxt - dt.timedelta(days=1)
        d = last_day
        while d.weekday() != weekday:
            d -= dt.timedelta(days=1)
        return d
    H |= {dt.date(year,1,1), dt.date(year,6,19), dt.date(year,7,4), dt.date(year,11,11), dt.date(year,12,25)}
    H |= {nth_weekday(year,1,0,3),  # MLK
          nth_weekday(year,2,0,3),  # Presidents
          last_weekday(year,5,0),   # Memorial
          nth_weekday(year,9,0,1),  # Labor
          nth_weekday(year,10,0,2), # Columbus
          nth_weekday(year,11,3,4)} # Thanksgiving
    return H

def roll(d):
    while d.weekday() >= 5 or d in us_holidays(d.year):
        d += dt.timedelta(days=1)
    return d

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: deadline.py YYYY-MM-DD (transfer date / Day 0)"); sys.exit(1)
    t = dt.date.fromisoformat(sys.argv[1])
    raw = t + dt.timedelta(days=30)
    due = roll(raw)
    print(f"Transfer (Day 0): {t:%Y-%m-%d %a}")
    print(f"Raw 30th day:     {raw:%Y-%m-%d %a}")
    print(f"FILING DEADLINE:  {due:%Y-%m-%d %a}" + ("  (rolled past weekend/holiday)" if due != raw else ""))
    print(f"Days remaining from today: {(due - dt.date.today()).days}")
