from browser import visit_site
import json
import sys

if len(sys.argv) < 3:
    print('Usage: python3 app.py <domains_file> <output_file>')
    exit(1)

[_, domains_file, output_file] = sys.argv

with open(domains_file, 'r') as f:
    sites = [r.strip() for r in f.readlines() if len(r.strip()) > 0]

with open(output_file, 'w') as f:
    json.dump(list(map(visit_site, sites)), f, indent=4)
