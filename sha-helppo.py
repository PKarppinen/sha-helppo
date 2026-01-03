import hashlib
from time import perf_counter
from math import cos, radians, pi

# Target SHA-256 hash (known)
TARGET = "5d4e47e73691204866cc73eaf837ec21249437eccca9caf21e23a774482993f6"
TARGET_BYTES = bytes.fromhex(TARGET)

# Center and radius
CENTER_LAT = 60.15000
CENTER_LON = 24.75667
RADIUS_M = 2500.0  # 2.5 km

# D4.5 units
UNIT = 100_000  # 1 degree = UNIT * 1e-5
INT_STEP = 1    # corresponds to 0.00001 (D4.5)

SEPARATORS = [",", " ", ";", "\n"]
SEPARATOR_BYTES = [s.encode() for s in SEPARATORS]

# Earth radius (mean) in meters
R_EARTH = 6371000.0
DEG2RAD = pi / 180.0


def format_d45_from_int(micro):
    # micro is integer value = value * 1e5
    return f"{micro/UNIT:07.5f}".encode()


def build_bounded_ranges(center_lat, center_lon, radius_m):
    # approximate degrees extents to build integer ranges
    # degrees per meter approximations
    meters_per_deg_lat = 111132.0  # approx
    lat0_rad = radians(center_lat)
    meters_per_deg_lon = 111320.0 * cos(lat0_rad)  # approx

    delta_lat_deg = radius_m / meters_per_deg_lat
    delta_lon_deg = radius_m / meters_per_deg_lon

    lat_min = int(round((center_lat - delta_lat_deg) * UNIT))
    lat_max = int(round((center_lat + delta_lat_deg) * UNIT))
    lon_min = int(round((center_lon - delta_lon_deg) * UNIT))
    lon_max = int(round((center_lon + delta_lon_deg) * UNIT))

    return lat_min, lat_max, lon_min, lon_max


def main():
    t0 = perf_counter()

    lat_min, lat_max, lon_min, lon_max = build_bounded_ranges(CENTER_LAT, CENTER_LON, RADIUS_M)

    # Precompute center in micro units and precompute constants for x/y in meters
    center_lat_m = int(round(CENTER_LAT * UNIT))
    center_lon_m = int(round(CENTER_LON * UNIT))
    lat0_rad = radians(CENTER_LAT)
    # We'll compute x = lon_diff_deg * DEG2RAD * R_EARTH * cos(lat0_rad)
    lon_scale = DEG2RAD * R_EARTH * cos(lat0_rad)  # meters per degree_lon
    lat_scale = DEG2RAD * R_EARTH                  # meters per rad of latitude, but using deg->rad conversion included

    # Precompute latitude formatted bytes and their y-offsets (meters)
    lat_list = []
    for lat_m in range(lat_min, lat_max + 1, INT_STEP):
        lat_b = format_d45_from_int(lat_m)
        lat_diff_deg = (lat_m - center_lat_m) / UNIT
        # y in meters = lat_diff_deg * DEG2RAD * R_EARTH
        y_m = lat_diff_deg * DEG2RAD * R_EARTH
        lat_list.append((lat_b, y_m))

    # Precompute longitude formatted bytes and their x-offsets (meters)
    lon_list = []
    for lon_m in range(lon_min, lon_max + 1, INT_STEP):
        lon_b = format_d45_from_int(lon_m)
        lon_diff_deg = (lon_m - center_lon_m) / UNIT
        # x in meters ~ lon_diff_deg * DEG2RAD * R_EARTH * cos(lat0)
        x_m = lon_diff_deg * lon_scale
        lon_list.append((lon_b, x_m))

    checked = 0
    r2 = RADIUS_M * RADIUS_M

    for lat_b, y_m in lat_list:
        # If |y| alone already exceeds radius, skip all longitudes for this latitude.
        if y_m * y_m > r2:
            continue

        # format once per separator
        for sep in SEPARATOR_BYTES:
            prefix = lat_b + sep
            # iterate longitudes, test circle membership using x_m and y_m
            for lon_b, x_m in lon_list:
                if x_m * x_m + y_m * y_m > r2:
                    continue
                checked += 1
                candidate = prefix + lon_b
                if hashlib.sha256(candidate).digest() == TARGET_BYTES:
                    print("\n=== MATCH FOUND ===")
                    try:
                        print("Original string:", repr(candidate.decode()))
                    except Exception:
                        print("Original bytes:", candidate)
                    print(f"Checked {checked} candidates in {perf_counter()-t0:.2f}s")
                    return

    print("No match found in radius.")
    print(f"Checked {checked} candidates in {perf_counter()-t0:.2f}s")


if __name__ == "__main__":
    main()
