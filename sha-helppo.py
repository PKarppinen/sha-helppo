import hashlib
from time import perf_counter

# Target SHA-256 hash
TARGET = "5d4e47e73691204866cc73eaf837ec21249437eccca9caf21e23a774482993f6"
TARGET_BYTES = bytes.fromhex(TARGET)

# Helsinki + Espoo approximate bounding box
LAT_MIN, LAT_MAX = 60.00, 60.40
LON_MIN, LON_MAX = 24.40, 25.30

# Precision for D4.5 (step = 10^(-5)) -- we operate in micro-units (1e-5 -> 1)
UNIT = 100000
INT_STEP = 1  # corresponds to 0.00001

SEPARATORS = [",", " ", ";", "\n"]
SEPARATOR_BYTES = [s.encode() for s in SEPARATORS]


def format_d45_from_int(micro):
    """Format integer (value * 1e5) into D4.5 bytes, e.g. 6012345 -> b'060.12345'"""
    return f"{micro/UNIT:07.5f}".encode()


def main():
    print("Searching for D4.5-formatted coordinates in Helsinki/Espoo...")
    t0 = perf_counter()

    lat_start = int(round(LAT_MIN * UNIT))
    lat_end = int(round(LAT_MAX * UNIT))
    lon_start = int(round(LON_MIN * UNIT))
    lon_end = int(round(LON_MAX * UNIT))

    # Precompute longitude formatted bytes
    lon_bytes = [format_d45_from_int(m) for m in range(lon_start, lon_end + 1, INT_STEP)]

    checked = 0
    # Iterate latitudes; format lat once per latitude, reuse for all separators and longitudes
    for lat_m in range(lat_start, lat_end + 1, INT_STEP):
        lat_b = format_d45_from_int(lat_m)
        for sep in SEPARATOR_BYTES:
            prefix = lat_b + sep
            for lon_b in lon_bytes:
                checked += 1
                candidate = prefix + lon_b
                if hashlib.sha256(candidate).digest() == TARGET_BYTES:
                    print("\n=== MATCH FOUND ===")
                    print("Original string:", repr(candidate.decode()))
                    print(f"Checked {checked} candidates in {perf_counter()-t0:.2f}s")
                    return

    print("No match found in the tested region using D4.5 format.")
    print(f"Checked {checked} candidates in {perf_counter()-t0:.2f}s")


if __name__ == "__main__":
    main()
