from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import tldextract


ONE_MONTH = 60 * 60 * 24 * 30


def visit_site(site):
    chrome_options = Options()
    chrome_options.headless = True
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=chrome_options)

    now = time.time()
    # TODO: Check for http vs https?
    driver.get(f'https://{site}')

    # TODO: Wait for 60s from "Identifying Sensitive URLs at Web-Scale"
    # driver.implicitly_wait(60)

    info = {
        'current_ts': now,
        'site': site,
        'cookies': [],
    }

    siteInfo = tldextract.extract(driver.current_url)
    cookies = driver.get_cookies()

    for cookie in cookies:
        ext = tldextract.extract(cookie['domain'])
        cookie['third_party'] = not (ext.domain == siteInfo.domain and ext.suffix == siteInfo.suffix)
        cookie['duration'] = cookie['expiry'] - now if 'expiry' in cookie else 0
        cookie['persistent'] = cookie['duration'] > ONE_MONTH  # CookieCheck
        # TODO: Identify tracker
        info['cookies'].append(cookie)

    driver.close()

    return info
