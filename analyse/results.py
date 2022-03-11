from pathlib import Path
import argparse
import json
import matplotlib.pyplot as plt


MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR
MONTH = 30 * DAY


parser = argparse.ArgumentParser(
    description='Print results after a scan using the output json file.'
)
parser.add_argument("-i", "--input", required=True, help="Input json file with the scan results.")
args = vars(parser.parse_args())

result_file = Path(__file__).parent / args['input']
with open(result_file, 'r') as f:
    results = json.load(f)


def getStatistics(result):
    return {
        'redirect_https': result['redirect_https'],
        'https_support': result['https_support'],
        'has_banner': result['has_banner'],
        'cookies': len(result['cookies']),
        'first_party': len([c for c in result['cookies'] if not c['third_party']]),
        'third_party': len([c for c in result['cookies'] if c['third_party']]),
        'persistent': len([c for c in result['cookies'] if c['persistent']]),
        'tracker': len([c for c in result['cookies'] if c['tracker']]),
        'session': len([c for c in result['cookies'] if c['duration'] < HOUR]),
        'hour': len([c for c in result['cookies'] if HOUR <= c['duration'] < DAY]),
        'day': len([c for c in result['cookies'] if DAY <= c['duration'] < MONTH]),
        'month': len([c for c in result['cookies'] if c['duration'] >= MONTH]),
        'privacy_found': result['privacy_policy']['link'] != 'ERROR',
        'privacy_source': 'xpath' if len(result['privacy_policy']['xpath_results']) > 0 else (
            'google' if len(result['privacy_policy']['google_results']) > 0 else 'none'
        ),
        'error': 'error' in result,
    }


def getAvg(list, prec=2):
    return round(sum(list) / len(list), prec) if len(list) > 0 else 0


def getPerc(list):
      return f'{round(getAvg(list, 4) * 100, 2)}%'


def countPerc(list, instance):
      return getPerc([l == instance for l in list])


def getStrList(arr):
    return '\n'.join([
          f'    {num} {domain}'
          for [num, domain] in arr
      ])


stats = [getStatistics(result) for result in results]
http_stats = [getStatistics(result) for result in results if not result["redirect_https"]]
https_stats = [getStatistics(result) for result in results if result["redirect_https"]]

http_results = [result for result in results if not result["redirect_https"]]
https_results = [result for result in results if result["redirect_https"]]


first_party_top = []
third_party_top = []
persistent_top = []
tracker_top = []
cloaked_trackers = []

for result in results:
    first_party_top.append([getStatistics(result)["first_party"], result["site"]])
    third_party_top.append([getStatistics(result)["third_party"], result["site"]])
    persistent_top.append([getStatistics(result)["persistent"], result["site"]])
    tracker_top.append([getStatistics(result)["tracker"], result["site"]])

    cloaked_trackers.append(list())
    for r in result["cookies"]:
        if "cloaked_domain" in r:
            cloaked_trackers[-1].append(r["cloaked_domain"])


print(f'Analysing ' + result_file.name)
print(f'URLs analysed: {len(results)}')
print(f'Errors: {getPerc([r["error"] for r in stats])}')
print()
print(f'HTTP to HTTPS redirects: {getPerc([r["redirect_https"] for r in stats])}')
print(f'HTTPS support: {getPerc([r["https_support"] for r in stats])}')
print(f'Difference in number of cookies depending on HTTP vs HTTPS: ' \
      f'{getPerc([len(r["cookies"]) != len(r["https"]["cookies"]) for r in results if r["https_support"]])}')
print(f'Banner or popup: {getPerc([r["has_banner"] for r in stats])}')
print()
print(f'No cookies set: {getPerc([r["cookies"] == 0 for r in stats])}, '
      f'http: {getPerc([r["cookies"] == 0 for r in http_stats])}, '
      f'https: {getPerc([r["cookies"] == 0 for r in https_stats])}')
print(f'Average number of cookies set: {getAvg([r["cookies"] for r in stats])} '
      f'http: {getAvg([r["cookies"] for r in http_stats])}, '
      f'https: {getAvg([r["cookies"] for r in https_stats])}')
print(f'Average number of first party cookies: {getAvg([r["first_party"] for r in stats])} '
      f'http: {getAvg([r["first_party"] for r in http_stats])}, '
      f'https: {getAvg([r["first_party"] for r in https_stats])}')
print(f'Average number of third party cookies: {getAvg([r["third_party"] for r in stats])} '
      f'http: {getAvg([r["third_party"] for r in http_stats])}, '
      f'https: {getAvg([r["third_party"] for r in https_stats])}' )
print(f'Average number of persistent cookies: {getAvg([r["persistent"] for r in stats])}, '
      f'http: {getAvg([r["persistent"] for r in http_stats])}, '
      f'https: {getAvg([r["persistent"] for r in https_stats])}')
print(f'Average number of tracker cookies: {getAvg([r["tracker"] for r in stats])}, '
      f'http: {getAvg([r["tracker"] for r in http_stats])}, '
      f'https: {getAvg([r["tracker"] for r in https_stats])}')
print()
print(f'Average number of cookies per duration:')
print(f'Less than one hour: {getAvg([r["session"] for r in stats])}')
print(f'More than one hour, less than a day: {getAvg([r["hour"] for r in stats])}')
print(f'More than one day, less than one month: {getAvg([r["day"] for r in stats])}')
print(f'One month or more: {getAvg([r["month"] for r in stats])}')
print()
print('Top 3 first party cookies:\n' + getStrList(sorted(first_party_top, reverse=True)[:3]))
print('Top 3 third party cookies:\n' + getStrList(sorted(third_party_top, reverse=True)[:3]))
print('Top 3 persistent cookies:\n' + getStrList(sorted(persistent_top, reverse=True)[:3]))
print('Top 3 tracker cookies:\n' + getStrList(sorted(tracker_top, reverse=True)[:3]))
print()
print(f'Privacy policies found: {getPerc([r["privacy_found"] for r in stats])}, ' \
      f'xpath: {countPerc([r["privacy_source"] for r in stats], "xpath")}, ' \
      f'google: {countPerc([r["privacy_source"] for r in stats], "google")}')
print()
print(f'GDPR compliant: {countPerc([r["gdpr_compliant"] for r in results], "yes")}, ' \
      f'http: {countPerc([r["gdpr_compliant"] for r in http_results], "yes")}, ' \
      f'https: {countPerc([r["gdpr_compliant"] for r in https_results], "yes")}')
print(f'Possibly GDPR compliant: {countPerc([r["gdpr_compliant"] for r in results], "maybe")}, ' \
      f'http: {countPerc([r["gdpr_compliant"] for r in http_results], "maybe")}, ' \
      f'https: {countPerc([r["gdpr_compliant"] for r in https_results], "maybe")}')
print(f'Not GDPR compliant: {countPerc([r["gdpr_compliant"] for r in results], "no")}, ' \
      f'http: {countPerc([r["gdpr_compliant"] for r in http_results], "no")}, ' \
      f'https: {countPerc([r["gdpr_compliant"] for r in https_results], "yes")}')
print()
print(f'Cloaked domains: {round(len([r for r in cloaked_trackers if r]) / len(results) * 100, 2)}%')
print(f'Cloaked domains with tracker: {round(len([r for r in cloaked_trackers if "tracker" in r]) / len(results) * 100, 2)}%')
print()
print(f'Saving plots to folder: {result_file.parent}')

fig = plt.figure()
plt.xlabel("Type of cookie")
plt.ylabel("Number of cookies")
plt.bar(["first party", "third party", "persistent", "tracker"], [sum([r["third_party"] for r in stats]), sum([r["first_party"] for r in stats]), sum([r["persistent"] for r in stats]), sum([r["tracker"] for r in stats])])
plt.savefig(result_file.parent / "types_of_cookies.png")
print('Saved number of cookies per type plot to types_of_cookies.png')

fig = plt.figure()
plt.xlabel("Number of cookies")
plt.ylabel("Number of websites")
plt.hist(x=[r["cookies"] for r in stats], rwidth=0.6, bins=list(range(24)))
plt.savefig(result_file.parent / "number_of_cookies.png")
print('Saved set cookies per website histogram to number_of_cookies.png')
