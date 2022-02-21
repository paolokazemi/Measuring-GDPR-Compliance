import json
import sys


if len(sys.argv) < 2:
    print('Usage: python3 results.py <results_file>')
    exit(1)

[_, result_file] = sys.argv

MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR
MONTH = 30 * DAY


with open(result_file, 'r') as f:
    results = json.load(f)


def getStatistics(result):
    return {
        'redirect_https': result['redirect_https'],
        'https_support': result['https_support'],
        'cookies': len(result['cookies']),
        'first_party': len([c for c in result['cookies'] if not c['third_party']]),
        'third_party': len([c for c in result['cookies'] if c['third_party']]),
        'persistent': len([c for c in result['cookies'] if c['persistent']]),
        'tracker': len([c for c in result['cookies'] if c['tracker']]),
        'session': len([c for c in result['cookies'] if c['duration'] < HOUR]),
        'hour': len([c for c in result['cookies'] if c['duration'] < DAY]),
        'day': len([c for c in result['cookies'] if c['duration'] < MONTH]),
        'month': len([c for c in result['cookies'] if c['duration'] >= MONTH]),
    }


def getAvg(list, prec=2):
    return round(sum(list) / len(list), prec)


stats = [getStatistics(result) for result in results]

print(f'HTTP to HTTPS redirects: {getAvg([r["redirect_https"] for r in stats], 4) * 100}%')
print(f'HTTPS support: {getAvg([r["https_support"] for r in stats], 4) * 100}%')
print()
print(f'Average cookies set: {getAvg([r["cookies"] for r in stats])}')
print(f'Average first party cookies: {getAvg([r["first_party"] for r in stats])}')
print(f'Average third party cookies: {getAvg([r["third_party"] for r in stats])}')
print(f'Average persistent cookies: {getAvg([r["persistent"] for r in stats])}')
print(f'Average tracker cookies: {getAvg([r["tracker"] for r in stats])}')
print()
print(f'Average session cookies: {getAvg([r["session"] for r in stats])}')
print(f'Average hourly cookies: {getAvg([r["hour"] for r in stats])}')
print(f'Average days cookies: {getAvg([r["day"] for r in stats])}')
print(f'Average monthly cookies: {getAvg([r["month"] for r in stats])}')