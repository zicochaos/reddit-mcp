#!/usr/bin/env python3
"""Test runner script for Reddit MCP Server."""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(args):
    """Run pytest with the specified arguments."""
    cmd = ["pytest"]
    
    # Add common options
    if args.verbose:
        cmd.append("-vv")
    
    if args.coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term-missing"])
    
    if args.markers:
        cmd.extend(["-m", args.markers])
    
    if args.keyword:
        cmd.extend(["-k", args.keyword])
    
    if args.exitfirst:
        cmd.append("-x")
    
    if args.lf:
        cmd.append("--lf")
    
    if args.parallel:
        cmd.extend(["-n", str(args.parallel)])
    
    # Add specific test path if provided
    if args.path:
        cmd.append(args.path)
    
    # Add any extra arguments
    if args.extra:
        cmd.extend(args.extra)
    
    print(f"Running: {' '.join(cmd)}")
    
    # Run pytest
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run tests for Reddit MCP Server")
    
    parser.add_argument(
        "path",
        nargs="?",
        help="Specific test file or directory to run"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="Run with coverage report"
    )
    
    parser.add_argument(
        "-m", "--markers",
        help="Run tests matching given mark expression (e.g., 'unit', 'integration', 'not slow')"
    )
    
    parser.add_argument(
        "-k", "--keyword",
        help="Run tests matching given keyword expression"
    )
    
    parser.add_argument(
        "-x", "--exitfirst",
        action="store_true",
        help="Exit on first failure"
    )
    
    parser.add_argument(
        "--lf", "--last-failed",
        dest="lf",
        action="store_true",
        help="Run only tests that failed in the last run"
    )
    
    parser.add_argument(
        "-n", "--parallel",
        type=int,
        metavar="NUM",
        help="Run tests in parallel using NUM processes"
    )
    
    parser.add_argument(
        "extra",
        nargs=argparse.REMAINDER,
        help="Extra arguments to pass to pytest"
    )
    
    # Quick test commands
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run unit tests only"
    )
    
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run integration tests only"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick tests (exclude slow)"
    )
    
    args = parser.parse_args()
    
    # Handle quick commands
    if args.unit:
        args.markers = "unit"
    elif args.integration:
        args.markers = "integration"
    elif args.quick:
        args.markers = "not slow"
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Run tests
    sys.exit(run_tests(args))


if __name__ == "__main__":
    main()