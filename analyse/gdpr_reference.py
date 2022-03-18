from constants import GDPR_KEYWORD_LIST
from pathlib import Path


def gdpr_search(driver, link):
    with open(Path(__file__).parent / GDPR_KEYWORD_LIST) as gdpr_file:
        gdpr_words = [line.strip() for line in gdpr_file.readlines()]
    driver.get(link)
    page = driver.page_source
    for word in gdpr_words:
        if word in page:
            return True
    return False

        