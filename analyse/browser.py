from dns_resolver import resolve_cname
from google_search import get_first_result, search_google
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from pathlib import Path
import time
import tldextract
import re
import json


MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR
MONTH = 30 * DAY
HEADLESS = True


def setup_driver(url):
    chrome_options = Options()
    chrome_options.headless = HEADLESS
    chrome_options.add_argument('--no-sandbox')  # Needed for Docker image
    driver = webdriver.Chrome(options=chrome_options)

    info = {'current_ts': time.time(), 'site': url, 'cookies': [] }
    try:
        driver.get(url)
    except WebDriverException as e:
        msg = re.split('\n|:', e.msg)
        error = msg[3] if len(msg) > 3 else 'ERR_GENERIC'

        possible_url = get_first_result(driver, url)
        if possible_url is None:
            raise Exception('Site inaccessible with no google results.')

        info['error'] = {'url': url, 'msg': error }
        info['site'] = possible_url

        # Restart driver with newly found url
        driver.close()
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(possible_url)

    # Waiting for 1s so JS should be done running
    time.sleep(1)

    return driver, info


def is_tracker(ext, trackers):
    return (
            ext.fqdn in trackers
        or  ext.registered_domain in trackers
        or (ext.subdomain and f'{ext.subdomain.split(".")[-1]}.{ext.domain}.{ext.suffix}' in trackers)  # 3 levels
    )


def run_analysis(driver, info):
    with open(Path(__file__).parent / '../data/cookie_check_trackers.txt') as trackers_file, \
         open(Path(__file__).parent / '../data/fanboy_cookie_selectors.txt') as selectors_file, \
         open(Path(__file__).parent / '../data/privacy_wording.json') as privacy_file:
        trackers = [line.strip() for line in trackers_file.readlines()]
        cookie_selectors = [line.strip() for line in selectors_file.readlines()]
        privacy_wording = json.load(privacy_file)

    siteInfo = tldextract.extract(driver.current_url)
    cookies = driver.get_cookies()

    for cookie in cookies:
        ext = tldextract.extract(cookie['domain'])
        cookie['third_party'] = not (ext.domain == siteInfo.domain and ext.suffix == siteInfo.suffix)
        cookie['duration'] = cookie['expiry'] - info['current_ts'] if 'expiry' in cookie else 0
        cookie['persistent'] = cookie['duration'] > MONTH  # CookieCheck
        cookie['tracker'] = is_tracker(ext, trackers)

        if resolved_domain := resolve_cname(ext.fqdn):
            cookie['cloaked_domain'] = {
                'resolved_domain': resolved_domain,
                'tracker': is_tracker(tldextract.extract(resolved_domain), trackers),
            }

        info['cookies'].append(cookie)

    info['has_banner'] = driver.execute_script(f"""
    const selectors = {str(cookie_selectors)};
    let hasBanner = false;
    for (const selector of selectors) {{
        try {{
            element = document.querySelector(selector.split('##')[1]);
            if (element) {{
                hasBanner = true;
            }}
        }} catch (_) {{
            // Ignore errors
        }}
    }}
    return hasBanner;
    """)

    xpaths = [
        "//*[contains(text(), 'cookie')]",
        "//*[contains(text(), 'Cookie')]",
        "//*[contains(text(), 'COOKIE')]"
    ]
    for xpath in xpaths:
        cookie_elements = driver.find_elements(By.XPATH, xpath)
        info['has_banner'] = info['has_banner'] or len(cookie_elements) > 0

    privacy_policies = set()
    for privacy_words in privacy_wording:
        # Only doing NL and EN
        if privacy_words['country'] not in ['en', 'nl']:
            continue

        for word in privacy_words['words']:
            try:
                privacy_policy = driver.find_element_by_xpath(f"//a [contains( text(), '{word}')]")
                if link := privacy_policy.get_attribute('href'):
                    privacy_policies.add(link)
            except:
                # Ignore errors from XPath
                pass

    info['privacy_policy'] = { 'xpath_results': list(privacy_policies) }
    if len(privacy_policies) == 0:
        google_results = search_google(driver, f'privacy policy site:{info["site"]}')
        info['privacy_policy']['google_results'] = [result for result in google_results if 'privacy' in result.lower()]

    info['privacy_policy']['link'] = info['privacy_policy']['xpath_results'][0] if len(privacy_policies) > 0 else (
        info['privacy_policy']['google_results'][0] if len(info['privacy_policy']['google_results']) > 0 else 'ERROR'
    )

    session_cookies = len([c for c in cookies if c['duration'] < HOUR])
    info['gdpr_compliant'] = 'yes' if len(cookies) == 0 else (
        'maybe' if len(cookies) == session_cookies else 'no'
    )


def visit_site(site):
    driver, info = setup_driver(f'http://{site}')

    # Analysis on HTTP (with possible redirect)
    info['redirect_https'] = driver.current_url.startswith('https://')
    run_analysis(driver, info)

    # Restarting driver to test HTTPS
    driver.close()
    driver, https = setup_driver(f'https://{site}')

    # Detecting HTTPS support
    if HEADLESS:
        # In headless mode the title is empty so check page source to be empty
        info['https_support'] = driver.page_source != '<html><head></head><body></body></html>'
    else:
        info['https_support'] = 'Privacy error' not in driver.title  # Chrome ssl error page

    if info['https_support']:
        run_analysis(driver, https)
        info['https'] = https

    driver.close()

    return info
