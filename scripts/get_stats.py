from jtop import jtop
import json

if __name__ == "__main__":
    with jtop() as jetson:
        if jetson.ok():
            # This captures the exact state in a dictionary
            print(json.dumps(jetson.stats))