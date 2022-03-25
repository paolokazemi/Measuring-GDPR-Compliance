from constants import HOUR, DAY, MONTH
from pathlib import Path
import argparse
import json
import matplotlib.pyplot as plt
import tldextract
from collections import Counter


parser = argparse.ArgumentParser(
    description='Generate statistics using the output json file.'
)
parser.add_argument(
    "-i",
    "--input",
    required=True,
    help="Input json file with the scan results."
)
args = vars(parser.parse_args())

result_file = Path(__file__).parent / args['input']
with open(result_file, 'r') as f:
    results = json.load(f)


def filter(arr, func):
    return [c for c in arr if func(c)]


def map(arr, key):
    return [c[key] for c in arr]


def getStatistics(result):
    xpath_results = result['privacy_policy']['xpath_results']
    google_results = result['privacy_policy']['google_results']
    return {
        'redirect_https': result['redirect_https'],
        'https_support': result['https_support'],
        'has_banner': result['has_banner'],
        'cookies': len(result['cookies']),
        'first_party': len(
            filter(result['cookies'], lambda c: not c['third_party'])
        ),
        'third_party': len(
            filter(result['cookies'], lambda c: c['third_party'])
        ),
        'persistent': len(
            filter(result['cookies'], lambda c: c['persistent'])
        ),
        'tracker': len(
            filter(result['cookies'], lambda c: c['tracker'])
        ),
        'session': len(
            filter(result['cookies'], lambda c: c['duration'] < HOUR)
        ),
        'hour': len(
            filter(result['cookies'], lambda c: HOUR <= c['duration'] < DAY)
        ),
        'day': len(
            filter(result['cookies'], lambda c: DAY <= c['duration'] < MONTH)
        ),
        'month': len(
            filter(result['cookies'], lambda c: c['duration'] >= MONTH)
        ),
        'privacy_found': result['privacy_policy']['link'] != 'ERROR',
        'privacy_source': 'xpath' if len(xpath_results) > 0 else (
            'google' if len(google_results) > 0 else 'none'
        ),
        'error': 'error' in result,
        'gdpr_reference': result['gdpr_ref']['gdpr_reference_present'],
    }


def getAvg(list, prec=2):
    return round(sum(list) / len(list), prec) if len(list) > 0 else 0


def getPerc(list):
    return f'{round(getAvg(list, 4) * 100, 2)}%'


def countPerc(list, instance):
    return getPerc([el == instance for el in list])


def getStrList(arr):
    return '\n'.join([
        f'    {num} {domain}'
        for [num, domain] in arr
    ])


def countSplitPerc(arr, instance, results):
    instances = map(arr, "gdpr_compliant").count(instance)
    return round(instances / len(results) * 100, 2)


stats = [getStatistics(result) for result in results]
http_stats = [getStatistics(result)
              for result in results if not result["redirect_https"]]
https_stats = [getStatistics(result)
               for result in results if result["redirect_https"]]

http_results = [result for result in results if not result["redirect_https"]]
https_results = [result for result in results if result["redirect_https"]]


first_party_top = []
third_party_top = []
persistent_top = []
tracker_top = []
cloaked_trackers = []
cloaked_domains = []

for result in results:
    first_party_top.append(
        [getStatistics(result)["first_party"], result["site"]]
    )
    third_party_top.append(
        [getStatistics(result)["third_party"], result["site"]]
    )
    persistent_top.append(
        [getStatistics(result)["persistent"], result["site"]]
    )
    tracker_top.append([getStatistics(result)["tracker"], result["site"]])

    cloaked_trackers.append(list())
    for r in result["cookies"]:
        if ("cloaked_domain" in r
                and len(r["cloaked_domain"]["resolved_domain"]) > 1):
            cloaked_trackers[-1].append(r["cloaked_domain"])
            last_domain = r["cloaked_domain"]["resolved_domain"][-1]
            ext = tldextract.extract(last_domain)
            cloaked_domains.append(ext.registered_domain)

differences_http_https = [
    len(r["cookies"]) != len(r["https"]["cookies"])
    for r in results if r["https_support"]
]

print(f'Analysing {result_file.name}')
print(f'URLs analysed: {len(results)}')
print(f'Errors: {getPerc(map(stats, "error"))}')
print()
print(f'HTTP to HTTPS redirects: {getPerc(map(stats, "redirect_https"))}')
print(f'HTTPS support: {getPerc(map(stats, "https_support"))}')
print(f'Difference in number of cookies depending on HTTP vs HTTPS: '
      f'{getPerc(differences_http_https)}')
print(f'Banner or popup: {getPerc(map(stats, "has_banner"))}')
print()
print(f'No cookies set: {getPerc([r["cookies"] == 0 for r in stats])}, '
      f'http: {getPerc([r["cookies"] == 0 for r in http_stats])}, '
      f'https: {getPerc([r["cookies"] == 0 for r in https_stats])}')
print(f'Average number of cookies set: {getAvg(map(stats, "cookies"))} '
      f'http: {getAvg(map(http_stats, "cookies"))}, '
      f'https: {getAvg(map(https_stats, "cookies"))}')
print(f'Average number of first party cookies: '
      f'{getAvg(map(stats, "first_party"))} '
      f'http: {getAvg(map(http_stats, "first_party"))}, '
      f'https: {getAvg(map(https_stats, "first_party"))}')
print(f'Average number of third party cookies: '
      f'{getAvg(map(stats, "third_party"))} '
      f'http: {getAvg(map(http_stats, "third_party"))}, '
      f'https: {getAvg(map(https_stats, "third_party"))}')
print(f'Average number of persistent cookies: '
      f'{getAvg(map(stats, "persistent"))}, '
      f'http: {getAvg(map(http_stats, "persistent"))}, '
      f'https: {getAvg(map(https_stats, "persistent"))}')
print(f'Average number of tracker cookies: '
      f'{getAvg(map(stats, "tracker"))}, '
      f'http: {getAvg(map(http_stats, "tracker"))}, '
      f'https: {getAvg(map(https_stats, "tracker"))}')
print()
print(f'First party cookies: {getPerc([r["first_party"] > 0 for r in stats])}')
print(f'Third party cookies: {getPerc([r["third_party"] > 0 for r in stats])}')
print(f'Persistent cookies: {getPerc([r["persistent"] > 0 for r in stats])}')
print(f'Tracker cookies: {getPerc([r["tracker"] > 0 for r in stats])}')
print()
print('Average number of cookies per duration:')
print(f'Less than one hour: {getAvg(map(stats, "session"))}')
print(
    f'More than one hour, less than a day: {getAvg(map(stats, "hour"))}')
print(
    f'More than one day, less than one month: {getAvg(map(stats, "day"))}')
print(f'One month or more: {getAvg(map(stats, "month"))}')
print()
print(
    f'Top 5 first party cookies:\n'
    f'{getStrList(sorted(first_party_top, reverse=True)[:5])}'
)
print(
    f'Top 5 third party cookies:\n'
    f'{getStrList(sorted(third_party_top, reverse=True)[:5])}'
)
print(
    f'Top 5 persistent cookies:\n'
    f'{getStrList(sorted(persistent_top, reverse=True)[:5])}'
)
print(
    f'Top 5 tracker cookies:\n'
    f'{getStrList(sorted(tracker_top, reverse=True)[:5])}'
)
print()
print(f'Privacy policies found: {getPerc(map(stats, "privacy_found"))} '
      f'(GDPR references {countPerc(map(stats, "gdpr_reference"), "yes")}), '
      f'xpath: {countPerc(map(stats, "privacy_source"), "xpath")}, '
      f'google: {countPerc(map(stats, "privacy_source"), "google")}')
print()
print(f'GDPR compliant*: {countPerc(map(results, "gdpr_compliant"), "yes")}, '
      f'http: {countSplitPerc(http_results, "yes", results)}%, '
      f'https: {countSplitPerc(https_results, "yes", results)}%')
print(f'Possibly GDPR compliant*: '
      f'{countPerc(map(results, "gdpr_compliant"), "maybe")}, '
      f'http: {countSplitPerc(http_results, "maybe", results)}%, '
      f'https: {countSplitPerc(https_results, "maybe", results)}%')
print(f'Not GDPR compliant*: '
      f'{countPerc(map(results, "gdpr_compliant"), "no")}, '
      f'http: {countSplitPerc(http_results, "no", results)}%, '
      f'https: {countSplitPerc(https_results, "no", results)}%')
print('* ***GDPR compliance is measured by the amount of cookies '
      'and their duration. The website is marked compliant if it has'
      ' no cookies, and maybe if it has only session cookies.***')
print()
print(
    f'Cloaked domains: '
    f'{getPerc([len(r) > 0 for r in cloaked_trackers])}')
print(
    f'Cloaked domains with tracker: '
    f'{getPerc([r for r in cloaked_trackers if "tracker" in r])}')
print(
    f'Top 5 cloaked domains:\n'
    f'{getStrList([[b,a] for a,b in Counter(cloaked_domains).most_common(5)])}'
)
print()
print(f'Saving plots to folder: {result_file.parent}')

fig = plt.figure()
plt.xlabel("Type of cookie")
plt.ylabel("Number of cookies")
plt.bar(["first party",
         "third party",
         "persistent",
         "tracker"],
        [sum([r["first_party"] for r in stats]),
         sum([r["third_party"] for r in stats]),
         sum([r["persistent"] for r in stats]),
         sum([r["tracker"] for r in stats])])
plt.savefig(result_file.parent / "types_of_cookies.png")
print('Saved number of cookies per type plot to types_of_cookies.png')

fig = plt.figure()
plt.xlabel("Number of cookies")
plt.ylabel("Number of websites")
plt.hist(x=[r["cookies"] for r in stats], rwidth=0.6, bins=list(range(50)))
plt.savefig(result_file.parent / "number_of_cookies.png")
print('Saved set cookies per website histogram to number_of_cookies.png')
