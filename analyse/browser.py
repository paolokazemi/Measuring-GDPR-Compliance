from constants import HEADLESS, COOKIE_CHECK_LIST, \
    SELECTORS_LIST, PRIVACY_WORD_LIST, MONTH, HOUR, \
    EASYLIST_DOMAINS, EASYPRIVACY_DOMAINS
from dns_resolver import resolve_cname
from google_search import get_first_result, search_google
from gdpr_reference import gdpr_search
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from pathlib import Path
import time
import tldextract
import re
import json


def setup_driver(url):
    chrome_options = Options()
    chrome_options.headless = HEADLESS
    chrome_options.add_argument('--no-sandbox')  # Needed for Docker image
    driver = webdriver.Chrome(options=chrome_options)

    info = {'current_ts': time.time(), 'site': url, 'cookies': []}
    try:
        driver.get(url)
    except WebDriverException as e:
        if 'www.' not in url:
            driver.close()
            [proto, domain] = url.split('://')
            return setup_driver(f'{proto}://www.{domain}')

        msg = re.split('\n|:', e.msg)
        error = msg[3] if len(msg) > 3 else 'ERR_GENERIC'

        possible_url = get_first_result(driver, url)
        driver.close()
        if possible_url is None:
            raise Exception('Site inaccessible with no google results.')

        info['error'] = {'url': url, 'msg': error}
        info['site'] = possible_url

        # Restart driver with newly found url
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(possible_url)

    # Waiting for 1s so JS should be done running
    time.sleep(1)

    return driver, info


def get_3levels(ext):
    return f'{ext.subdomain.split(".")[-1]}.{ext.domain}.{ext.suffix}'


def is_tracker(ext, trackers):
    return (
        ext.fqdn in trackers
        or ext.registered_domain in trackers
        # 3 levels
        or (ext.subdomain and get_3levels(ext) in trackers)
    )


def run_analysis(driver, info):
    with open(Path(__file__).parent / COOKIE_CHECK_LIST) as trackers_file, \
            open(Path(__file__).parent / SELECTORS_LIST) as selectors_file, \
            open(Path(__file__).parent / PRIVACY_WORD_LIST) as privacy_file, \
            open(Path(__file__).parent / EASYLIST_DOMAINS) as elist_file, \
            open(Path(__file__).parent / EASYPRIVACY_DOMAINS) as eprivacy_file:
        trackers = [line.strip() for line in trackers_file.readlines()] \
            + [line.strip() for line in elist_file.readlines()] \
            + [line.strip() for line in eprivacy_file.readlines()]
        cookie_selectors = [line.strip()
                            for line in selectors_file.readlines()]
        privacy_wording = json.load(privacy_file)

    siteInfo = tldextract.extract(driver.current_url)
    cookies = driver.get_cookies()

    for cookie in cookies:
        ext = tldextract.extract(cookie['domain'])
        cookie['third_party'] = not (
            ext.domain == siteInfo.domain and ext.suffix == siteInfo.suffix)
        cookie['duration'] = cookie['expiry'] - \
            info['current_ts'] if 'expiry' in cookie else 0
        cookie['persistent'] = cookie['duration'] > MONTH  # CookieCheck
        cookie['tracker'] = is_tracker(ext, trackers)

        if resolved_domain := resolve_cname(ext.fqdn):
            cloaked_tracker = False
            for domain in resolved_domain:
                if is_tracker(tldextract.extract(domain), trackers):
                    cloaked_tracker = True

            cookie['cloaked_domain'] = {
                'resolved_domain': resolved_domain,
                'tracker': cloaked_tracker,
            }

        info['cookies'].append(cookie)

    parsed_selectors = set()
    remove_selectors = set()
    parsed_in_url = set()

    for cookie_selector in cookie_selectors:
        if cookie_selector.startswith('!'):
            # Ignore comments
            continue

        elif cookie_selector.startswith('##'):
            parsed_selectors.add(cookie_selector.split('##')[1])

        elif cookie_selector.startswith('||'):
            parsed_in_url.add(cookie_selector)

        elif cookie_selector.startswith('@@||'):
            # TODO: Add support for exceptions
            pass

        elif cookie_selector.startswith('@@'):
            # TODO: Add support for exceptions
            pass

        elif '##' in cookie_selector:
            [domains, selector] = cookie_selector.split('##')
            if siteInfo.registered_domain in domains.split(','):
                parsed_selectors.add(selector)

        elif '#@#' in cookie_selector:
            [domains, selector] = cookie_selector.split('#@#')
            if siteInfo.registered_domain in domains.split(','):
                remove_selectors.add(selector)

        elif '#?#' in cookie_selector:
            # TODO: Add support for #?#
            pass

        else:
            parsed_in_url.add(cookie_selector)

    parsed_selectors = list(parsed_selectors - remove_selectors)

    info['has_banner'] = driver.execute_script(f"""
    const selectors = {str(parsed_selectors)};
    let hasBanner = false;
    for (const selector of selectors) {{
        try {{
            element = document.querySelector(selector);
            if (element) {{
                hasBanner = true;
            }}
        }} catch (_) {{
            // Ignore errors
        }}
    }}
    return hasBanner;
    """)

    network_requests = driver.execute_script("""
    var performance = window.performance || window.mozPerformance
        || window.msPerformance || window.webkitPerformance || {};
    var network = performance.getEntries() || {};
    return network;
    """)
    parsed_urls = [req['name'] for req in network_requests if 'name' in req]

    for url in parsed_urls:
        if '://' in url and (url.startswith('http://')
                             or url.startswith('https://')):
            url = url[8 if url.startswith('https') else 7:]

        for fragment in parsed_in_url:
            if '$' in fragment or '^' in fragment:
                # Advanced options are not implemented
                continue

            if fragment in url:
                info['has_banner'] = True
    
    gdpr_references = 0
    privacy_policies = set()
    for privacy_words in privacy_wording:
        # Only doing NL and EN
        if privacy_words['country'] not in ['en', 'nl']:
            continue

        for word in privacy_words['words']:
            try:
                privacy_policy = driver.find_element_by_xpath(
                    f"//a [contains( text(), '{word}')]")
                if link := privacy_policy.get_attribute('href'):
                    privacy_policies.add(link) 
            except Exception:
                # Ignore errors from XPath
                pass

    info['privacy_policy'] = {
        'xpath_results': list(privacy_policies),
        'google_results': []
    }

    if len(privacy_policies) == 0:
        google_results = search_google(
            driver, f'privacy policy site:{info["site"]}')
        info['privacy_policy']['google_results'] = [
            result for result in google_results if 'privacy' in result.lower()]

    xpath_results = info['privacy_policy']['xpath_results']
    google_results = info['privacy_policy']['google_results']
    if len(xpath_results) > 0:
        info['privacy_policy']['link'] = xpath_results[0]
    elif len(google_results) > 0:
        info['privacy_policy']['link'] = google_results[0]
    else:
        info['privacy_policy']['link'] = 'ERROR'

    session_cookies = len([c for c in cookies if c['duration'] < HOUR])
    info['gdpr_compliant'] = 'yes' if len(cookies) == 0 else (
        'maybe' if len(cookies) == session_cookies else 'no'
    )
    
    if info['privacy_policy']['link'] != 'ERROR':
        if gdpr_search(driver, info['privacy_policy']['link']):
            gdpr_references = 1
    
    info['gdpr_ref'] = {
        'gdpr_reference_present': '',
        'google_results': []
    }

    if gdpr_references == 0:
        info['gdpr_ref']['gdpr_reference_present'] = 'no'
        google_results = search_google(
            driver, f'gdpr site:{info["site"]}')
        info['gdpr_ref']['google_results'] = [
            result for result in google_results if 'gdpr' in result.lower()]
    
    if info['gdpr_ref']['google_results'] != []:
        gdpr_references = 1

    if gdpr_references == 1:
        info['gdpr_ref']['gdpr_reference_present'] = 'yes'

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
        EMPTY_PAGE = '<html><head></head><body></body></html>'
        info['https_support'] = driver.page_source != EMPTY_PAGE
    else:
        # Chrome ssl error page
        info['https_support'] = 'Privacy error' not in driver.title

    if info['https_support']:
        run_analysis(driver, https)
        info['https'] = https

    driver.close()

    return info
