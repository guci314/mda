#!/usr/bin/env python3
import argparse
from backend import compile_pim

def main():
    parser = argparse.ArgumentParser(description='PIM Compiler')
    parser.add_argument('input', help='Input PIM source file')
    parser.add_argument('-o', '--output', help='Output file path')
    
    args = parser.parse_args()
    
    try:
        with open(args.input, 'r') as src_file:
            source_code = src_file.read()
        
        result = compile_pim(source_code)
        
        output_path = args.output if args.output else 'a.out'
        with open(output_path, 'w') as out_file:
            out_file.write(result)
            
    except Exception as e:
        print(f"Compilation error: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
