#!/usr/bin/env python
from __future__ import print_function
import os


def main():
    """Example: solve a vector packing instance using 'solvers.vbpsolver'"""
    from pyvpsolver.solvers import vbpsolver
    import csv

    os.chdir(os.path.dirname(__file__) or os.curdir)


    # Define file path (update the file path to match your data file location)
    file_path = "Term project data 1a.csv"

    # Initialize lists
    w = []  # To store (weight, volume, pallets)
    b = []  # To store 1s for each order

    # Read the CSV file
    with open(file_path, mode="r") as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            # Extract the values as integers
            weight = int(row["Weight (lbs)"])
            volume = int(row["Volume (in3)"])
            pallets = int(row["Pallets"])
            
            # Append the tuple to `w` and 1 to `b`
            w.append((weight, volume, pallets))
            b.append(1)


    W = (45000, 3600, 60)
    

    # Solve:
    solution = vbpsolver.solve(
        W, w, b, svg_file="tmp/graph_vbp.svg", script="vpsolver_glpk.sh", verbose=True
    )
    vbpsolver.print_solution(solution)

    # check the solution objective value
    obj, patterns = solution
    assert obj == 33


if __name__ == "__main__":
    main()