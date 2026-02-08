#!/usr/bin/env python3
from jtop import jtop
import json
import sys

def main():
    with jtop() as jetson:
        if jetson.ok():
            # default=str converts datetime objects into ISO format strings
            print(json.dumps(jetson.stats, default=str))
        else:
            print(json.dumps({"error": "Could not connect to jetson_stats"}))
            sys.exit(1)

if __name__ == "__main__":
    main()