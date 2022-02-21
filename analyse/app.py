from browser import visit_site
from tqdm import tqdm
import json
import sys

if len(sys.argv) < 3:
    print('Usage: python3 app.py <domains_file> <output_file>')
    exit(1)

[_, domains_file, output_file] = sys.argv

with open(domains_file, 'r') as input, open(output_file, 'w') as output:
    sites = [line.strip() for line in input.readlines() if len(line.strip()) > 0]

    results = []
    for site in tqdm(sites):
        try:
            results.append(visit_site(site))
        except:
            # TODO: Analyse all possible causes of error
            print(f'Error analysing: {site}')

    json.dump(results, output, indent=4)
