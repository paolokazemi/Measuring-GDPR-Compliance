from browser import visit_site
from tqdm import tqdm
import argparse
import json


parser = argparse.ArgumentParser(
    description="Scan websites for non-compliant implementations of GDPR."
)
parser.add_argument(
    "-i",
    "--input",
    required=True,
    help="Input file with a list of domains."
)
parser.add_argument("-o", "--output", required=True, help="Output json file.")
args = vars(parser.parse_args())


with open(args['input'], 'r') as input, open(args['output'], 'w') as output:
    sites = [line.strip()
             for line in input.readlines() if len(line.strip()) > 0]

    results = []
    for site in tqdm(sites):
        try:
            results.append(visit_site(site))
        except Exception as e:
            # If google fallback does not work, errors are ignored
            print(f'Error analysing: {site}, error {str(e)}')

    json.dump(results, output, indent=4)
