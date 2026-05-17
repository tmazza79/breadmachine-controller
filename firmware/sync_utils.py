from machine import RTC
import ntptime
rtc = RTC()

def sync_time():
    """Sync time from NTP server"""
    try:
        ntptime.settime()  # This sets the RTC to UTC
        print("Time synced from NTP")
        print("Current UTC:", rtc.datetime())
    except:
        print("Failed to sync time")

def get_current_time():
    """Get current time in readable format"""
    year, month, day, weekday, hour, minute, second, _ = rtc.datetime()
    print("Current UTC:", rtc.datetime())
    return (year, month, day, hour, minute, second)

# Last Sunday of March and October for each year.
# (Generated with: calendar.monthcalendar(year, month) -> last week, Sunday column)
DST_LAST_SUNDAY = {
    2025: (30, 26),
    2026: (29, 25),
    2027: (28, 31),
    2028: (26, 29),
    2029: (25, 28),
    2030: (31, 27),
    2031: (30, 26),
    2032: (28, 31),
    2033: (27, 30),
    2034: (26, 29),
    2035: (25, 28),
    2036: (30, 26),
    2037: (29, 25),
    2038: (28, 31),
    2039: (27, 30),
    2040: (25, 28),
    2041: (31, 27),
    2042: (30, 26),
    2043: (29, 25),
    2044: (27, 30),
    2045: (26, 29),
    2046: (25, 28),
    2047: (31, 27),
    2048: (29, 25),
    2049: (28, 31),
    2050: (27, 30),
    2051: (26, 29),
    2052: (31, 27),
    2053: (30, 26),
    2054: (29, 25),
    2055: (28, 31),
    2056: (26, 29),
    2057: (25, 28),
    2058: (31, 27),
    2059: (30, 26),
    2060: (28, 31),
}

def get_timezone_offset(year, month, day, hour):
    """UTC offset for Germany (CET=+1 / CEST=+2).
    Inputs are UTC. Transitions occur at 01:00 UTC on the
    last Sunday of March and October.
    """
    if year not in DST_LAST_SUNDAY:
        # Safe fallback to the simplified rule
        return 1 if (month <= 3 or month > 10) else 2

    mar_sun, oct_sun = DST_LAST_SUNDAY[year]

    if month < 3 or month > 10:
        return 1                              # Nov–Feb: winter
    if 4 <= month <= 9:
        return 2                              # Apr–Sep: summer

    if month == 3:
        if day < mar_sun:  return 1
        if day > mar_sun:  return 2
        return 2 if hour >= 1 else 1          # transition day

    # month == 10
    if day < oct_sun:  return 2
    if day > oct_sun:  return 1
    return 1 if hour >= 1 else 2              # transition day