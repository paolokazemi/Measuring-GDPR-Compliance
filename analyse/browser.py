from dns_resolver import resolve_cname
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import tldextract


ONE_MONTH = 60 * 60 * 24 * 30
HEADLESS = True


def setup_driver(url):
    chrome_options = Options()
    chrome_options.headless = HEADLESS
    chrome_options.add_argument('--no-sandbox')  # Needed for Docker image
    driver = webdriver.Chrome(options=chrome_options)

    info = {'current_ts': time.time(), 'site': url, 'cookies': [] }
    driver.get(url)

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
    with open('../data/cookie_check_trackers.txt', 'r') as trackers_file, \
         open('../data/fanboy_cookie_selectors.txt', 'r') as selectors_file:
        trackers = [line.strip() for line in trackers_file.readlines()]
        cookie_selectors = [line.strip() for line in selectors_file.readlines()]

    siteInfo = tldextract.extract(driver.current_url)
    cookies = driver.get_cookies()

    for cookie in cookies:
        ext = tldextract.extract(cookie['domain'])
        cookie['third_party'] = not (ext.domain == siteInfo.domain and ext.suffix == siteInfo.suffix)
        cookie['duration'] = cookie['expiry'] - info['current_ts'] if 'expiry' in cookie else 0
        cookie['persistent'] = cookie['duration'] > ONE_MONTH  # CookieCheck
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
