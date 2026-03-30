import argparse
import json
import os
import sys
from .compute import compute_params

def main():
    parser = argparse.ArgumentParser(
        description='Compute electrical parameters for FreeCAD design'
    )
    parser.add_argument('--params', nargs='+', required=True,
                       help='Path to input parameters JSON file')
    parser.add_argument('--output', required=True,
                       help='Path to output computed parameters JSON file')
    
    args = parser.parse_args()
    
    base_params = {}
    for param_file in args.params:
        if not os.path.exists(param_file):
            print(f"ERROR: Parameter file not found: {param_file}", file=sys.stderr)
            sys.exit(1)
        print(f"Loading parameters from: {param_file}")
        with open(param_file, 'r') as f:
            base_params |= json.load(f)
    
    computed_params = compute_params(base_params)
    
    print(f"Saving computed parameters to: {args.output}")
    with open(args.output, 'w') as f:
        json.dump(computed_params, f, indent=4)

if __name__ == "__main__":
    main()