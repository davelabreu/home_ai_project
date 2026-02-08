from jtop import jtop
import json
import sys

def main():
    with jtop() as jetson:
        if jetson.ok():
            # stats is a dictionary containing GPU, CPU, and RAM data
            print(json.dumps(jetson.stats))
        else:
            print(json.dumps({"error": "Could not connect to jetson_stats"}))
            sys.exit(1)

if __name__ == "__main__":
    main()