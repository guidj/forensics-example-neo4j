"""
Finding patters in Data: multi-domain graphs
"""

import argparse


from forensics.patterns import run_analysis
from forensics import seed


# step 1: seed random data
# step 2: seed POI's data
# step 3: cypher queries to seed
# step 4: cypher queries to run forensics analysis


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Forensics analysis using neo4j')

    parser.add_argument('--seed', type=bool, default=False)
    parser.add_argument('--pattern', type=str, default="*")

    args = parser.parse_args()

    seed_data = args.seed
    pattern = args.pattern

    if seed_data:
        seed.seed()

    run_analysis(pattern)
