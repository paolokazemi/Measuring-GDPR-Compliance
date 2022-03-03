
def search_google(driver, query):
    driver.get(f'https://www.google.com/search?q={query}')

    return driver.execute_script("""
    const titles = document.querySelectorAll('a h3');
    return Array.from(titles)
        .map(title => title.closest('a').href)
        .filter(title => !title.includes('googleadservices.com'));
    """)


def get_google_results(driver, url):
    [_, domain] = url.split('://')
    return search_google(driver, domain)


def get_first_result(driver, url):
    urls = get_google_results(driver, url)
    return urls[0] if len(urls) > 0 else None
