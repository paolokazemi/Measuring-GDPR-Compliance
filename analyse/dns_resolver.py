import dns.resolver


RESOLVER = dns.resolver.Resolver()
RESOLVER.nameservers = [
    '1.1.1.1',  # Cloudflare
    '9.9.9.9',  # Quad9
]


def resolve_cname(domain):
    try:
        answers = RESOLVER.resolve(domain, 'CNAME')
        return str(answers[0]) if len(answers) > 0 else None
    except:
        return None
