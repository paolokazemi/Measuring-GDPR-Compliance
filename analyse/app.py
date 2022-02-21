from browser import visit_site
from tqdm import tqdm
import argparse
import json


parser = argparse.ArgumentParser(
    description='Scan a list of websites for non-compliant GDPR implementations.'
)
parser.add_argument("-i", "--input", required=True, help="Input file with a domains list.")
parser.add_argument("-o", "--output", required=True, help="Output json file.")
args = vars(parser.parse_args())


with open(args['input'], 'r') as input, open(args['output'], 'w') as output:
    sites = [line.strip() for line in input.readlines() if len(line.strip()) > 0]

    results = []
    for site in tqdm(sites):
        try:
            results.append(visit_site(site))
        except:
            # TODO: Analyse all possible causes of error
            print(f'Error analysing: {site}')

    json.dump(results, output, indent=4)
