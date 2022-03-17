import dns.resolver


RESOLVER = dns.resolver.Resolver()
RESOLVER.nameservers = [
    '1.1.1.1',  # Cloudflare
    '9.9.9.9',  # Quad9
]


def resolve_cname(domain):
    answers = [domain]
    while True:
        try:
            domains = RESOLVER.resolve(answers[-1], 'CNAME')
            if len(domains) > 0:
                answers.append(str(domains[0]))
            else:
                return answers
        except Exception:
            return answers
