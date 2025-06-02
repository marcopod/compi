#!/usr/bin/env python3

import sys
import traceback

try:
    print("Starting debug test...")
    
    # Test imports
    print("Testing imports...")
    from babyduck import parser
    print("Parser imported successfully")
    
    from semantic.analyzer import SemanticAnalyzer, SemanticError
    print("Semantic analyzer imported successfully")
    
    # Test simple parsing
    print("Testing simple parsing...")
    code = """program simple;
var x: int;

main {
    x = 5;
} end"""
    
    print("Parsing code...")
    tree = parser.parse(code)
    print("Parse successful!")
    print("Tree:", tree.pretty())
    
    # Test semantic analysis
    print("Testing semantic analysis...")
    analyzer = SemanticAnalyzer()
    print("Analyzer created")
    
    print("Running transform...")
    result = analyzer.transform(tree)
    print("Transform completed!")
    
    print("Quadruples generated:")
    for i, quad in enumerate(analyzer.quadruples):
        op, left, right, res = quad
        print(f"{i:>3} : ( {op!r:7}, {left!r:5}, {right!r:5}, {res!r:5} )")
    
    print("SUCCESS: All tests passed!")
    
except Exception as e:
    print(f"ERROR: {e}")
    print("Traceback:")
    traceback.print_exc()
