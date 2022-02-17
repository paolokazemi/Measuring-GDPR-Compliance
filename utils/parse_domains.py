# Parse csv domain from https://prefixtoplists.net.in.tum.de/#download

INPUT_FILE = '../data/domains.csv'
OUTPUT_FILE = '../data/domains.txt'

with open(INPUT_FILE, 'r') as f, open(OUTPUT_FILE, 'w') as o:
    domains = map(lambda x: x.split(',')[0][:-1], f.readlines()[1:])
    o.write("\n".join(domains))
