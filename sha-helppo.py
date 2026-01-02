import hashlib

# Target SHA-256 hash
TARGET = "5d4e47e73691204866cc73eaf837ec21249437eccca9caf21e23a774482993f6"

# Helsinki + Espoo approximate bounding box
LAT_MIN, LAT_MAX = 60.00, 60.40
LON_MIN, LON_MAX = 24.40, 25.30

# Precision for D4.5 (step = 10^(-5))
STEP = 0.00001

SEPARATORS = [",", " ", ";"]
INCLUDE_NEWLINE = True

def sha256_hex(s):
    return hashlib.sha256(s.encode()).hexdigest()

def format_d45(value):
    """
    Format number into D4.5 (4 digits before decimal, 5 decimals).
    Example: 60.12345 -> "060.12345"
    """
    return f"{value:07.5f}"  # ensures 3 digits + decimal + 5 decimals -> 7 chars total

def main():
    print("Searching for D4.5-formatted coordinates in Helsinki/Espoo...")

    lat = LAT_MIN
    while lat <= LAT_MAX:
        lon = LON_MIN
        while lon <= LON_MAX:

            lat_str = format_d45(lat)
            lon_str = format_d45(lon)

            # Try each separator
            for sep in SEPARATORS:
                candidate = lat_str + sep + lon_str
                if sha256_hex(candidate) == TARGET:
                    print("\n=== MATCH FOUND ===")
                    print("Original string:", repr(candidate))
                    return

            # Optional newline variant
            if INCLUDE_NEWLINE:
                candidate = f"{lat_str}\n{lon_str}"
                if sha256_hex(candidate) == TARGET:
                    print("\n=== MATCH FOUND ===")
                    print("Original string:", repr(candidate))
                    return

            lon += STEP
        lat += STEP

    print("No match found in the tested region using D4.5 format.")

if __name__ == "__main__":
    main()