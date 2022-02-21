from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import tldextract


ONE_MONTH = 60 * 60 * 24 * 30


def visit_site(site):
    with open('../data/cookie_check_trackers.txt', 'r') as trackers_file:
        trackers = [line.strip() for line in trackers_file.readlines()]

    chrome_options = Options()
    chrome_options.headless = True
    chrome_options.add_argument('--no-sandbox')  # Needed for Docker image
    driver = webdriver.Chrome(options=chrome_options)

    now = time.time()
    info = {
        'current_ts': now,
        'site': site,
        'cookies': [],
    }

    driver.get(f'http://{site}')
    info['redirect_https'] = driver.current_url.startswith('https://')

    # TODO: Wait for 60s from "Identifying Sensitive URLs at Web-Scale"
    driver.implicitly_wait(1)

    siteInfo = tldextract.extract(driver.current_url)
    cookies = driver.get_cookies()

    for cookie in cookies:
        ext = tldextract.extract(cookie['domain'])
        cookie['third_party'] = not (ext.domain == siteInfo.domain and ext.suffix == siteInfo.suffix)
        cookie['duration'] = cookie['expiry'] - now if 'expiry' in cookie else 0
        cookie['persistent'] = cookie['duration'] > ONE_MONTH  # CookieCheck
        cookie['tracker'] = (
                cookie['domain'] in trackers
            or  f'{ext.domain}.{ext.suffix}' in trackers
            or (ext.subdomain and f'{ext.subdomain.split(".")[-1]}.{ext.domain}.{ext.suffix}' in trackers)  # 3 levels
        )
        info['cookies'].append(cookie)

    # Detecting HTTPS support
    driver.get(f'https://{site}')
    if chrome_options.headless:
        # In headless mode the title is empty so check page source to be empty
        info['https_support'] = driver.page_source != '<html><head></head><body></body></html>'
    else:
        info['https_support'] = 'Privacy error' not in driver.title  # Chrome ssl error page

    cookie_elements = driver.find_elements(By.CSS_SELECTOR, "[id^=cookie]")
    if len(cookie_elements) == 0:
        cookie_elements = driver.find_elements(By.CSS_SELECTOR, "[class^=cookie]")

    info['has_banner'] = len(cookie_elements) > 0

    driver.close()

    return info
