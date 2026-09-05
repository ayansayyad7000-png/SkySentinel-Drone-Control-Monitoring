import sys
import time

import pandas as pd


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/replay_log.py logs/flight_YYYYMMDD_HHMMSS.csv")

    df = pd.read_csv(sys.argv[1])

    for _, row in df.iterrows():
        print(
            f"mode={row.get('flight_mode')} "
            f"alt={row.get('relative_altitude_m')}m "
            f"speed={row.get('groundspeed_m_s')}m/s "
            f"battery={row.get('battery_percent')}%"
        )
        time.sleep(0.25)


if __name__ == "__main__":
    main()
