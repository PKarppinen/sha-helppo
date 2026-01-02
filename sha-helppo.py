import hashlib

# Target SHA-256 hash
TARGET = "5d4e47e73691204866cc73eaf837ec21249437eccca9caf21e23a774482993f6"
TARGET_BYTES = bytes.fromhex(TARGET)

# Helsinki + Espoo approximate bounding box
LAT_MIN, LAT_MAX = 60.00, 60.40
LON_MIN, LON_MAX = 24.40, 25.30

# Precision for D4.5 (step = 10^(-5))
STEP = 0.00001

SEPARATORS = [",", " ", ";", "\n"]
SEPARATOR_BYTES = [sep.encode() for sep in SEPARATORS]

def format_d45(value):
    """
    Format number into D4.5 (4 digits before decimal, 5 decimals).
    Example: 60.12345 -> "060.12345"
    """
    return f"{value:07.5f}"

def main():
    print("Searching for D4.5-formatted coordinates in Helsinki/Espoo...")

    lat = LAT_MIN
    while lat <= LAT_MAX:
        lat_str = format_d45(lat).encode()
        
        lon = LON_MIN
        while lon <= LON_MAX:
            lon_str = format_d45(lon).encode()

            # Try each separator
            for sep_bytes in SEPARATOR_BYTES:
                candidate = lat_str + sep_bytes + lon_str
                if hashlib.sha256(candidate).digest() == TARGET_BYTES:
                    print("\n=== MATCH FOUND ===")
                    print("Original string:", repr(candidate.decode()))
                    return

            lon += STEP
        lat += STEP

    print("No match found in the tested region using D4.5 format.")

if __name__ == "__main__":
    main()