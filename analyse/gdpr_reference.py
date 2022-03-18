from constants import GDPR_KEYWORD_LIST
def gdpr_search(driver, link):
    with open(Path(__file__).parent / GDPR_KEYWORD_LIST) as gdpr_file:
        gdpr_words = [line.strip() for line in gdpr_file.readlines()]
    driver.get(link)
    for word in gdpr_words:
        try:
            if(driver.getPageSource().contains(f'{word}')):
                return True
            else:
                return False
        except Exception:
            # Ignore any errors
            pass
        