#!/usr/bin/env python3
from jtop import jtop
import json
import sys

def main():
    with jtop() as jetson:
        if jetson.ok():
            # This captures the exact state in a dictionary
            print(json.dumps(jetson.stats))