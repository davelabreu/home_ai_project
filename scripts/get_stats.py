#!/usr/bin/env python3
import sys

# Use stderr for debug messages to avoid interfering with JSON parsing
print("DEBUG: Script started", file=sys.stderr)

try:
    from jtop import jtop
    print("DEBUG: jtop imported successfully", file=sys.stderr)
except ImportError as e:
    print(f"DEBUG: Error importing jtop: {e}", file=sys.stderr)
    sys.exit(1)

import json

def main():
    print("DEBUG: Entering main", file=sys.stderr)
    try:
        with jtop() as jetson:
            print("DEBUG: jtop object created, checking status...", file=sys.stderr)
            if jetson.ok():
                print("DEBUG: jtop status OK", file=sys.stderr)
                # default=str converts datetime objects into ISO format strings
                data = {
                    "stats": jetson.stats,
                    "fan": jetson.fan.get() if hasattr(jetson, 'fan') else {},
                    "clocks": jetson.jetson_clocks if hasattr(jetson, 'jetson_clocks') else "unknown",
                    "power": jetson.power if hasattr(jetson, 'power') else {},
                    "temperature": jetson.temperature if hasattr(jetson, 'temperature') else {}
                }
                print(json.dumps(data, default=str))
                print("DEBUG: data printed to stdout", file=sys.stderr)
            else:
                print("DEBUG: jtop status NOT OK", file=sys.stderr)
                print(json.dumps({"error": "Could not connect to jetson_stats"}))
                sys.exit(1)
    except Exception as e:
        print(f"DEBUG: Exception in main: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
