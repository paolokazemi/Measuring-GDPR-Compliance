# Measuring GDPR Compliance

### Description
This tool can be used to scan a list of domain names and detect whether they are following GDPR guidelines. For each website, a browser session is simulated and the following information collected:
- Cookies that are set along with their duration, origin, and whether they are persistent/trackers/third party
- If the cookie is from a subdomain, CNAME DNS resolution is checked to detect cloaking
- Whether the site automatically redirects from HTTP to HTTPS
- HTTPS support
- Whether a cookie banner is present or not
- Link to the privacy policy of the site (if it exists)
- Possible differences between the HTTP and HTTPS versions
- Whether the site is GDPR compliant or not

All collected information is stored to an output json file and the results script can be used to analyse it, the plots are saved to the `results` folder.

### Dataset
- Top 50 websites for NL and Global are taken from [Alexa](https://www.alexa.com/topsites) \[0\]
- Top 500 global websites are taken from the [Prefix Top Lists study](https://prefixtoplists.net.in.tum.de/) \[1\]
- The list of trackers is taken from the [CookieCheck repository](https://github.com/CookieChecker/CookieCheckSourceCode) \[2\]
- The list of cookie filters is taken from [EasyList Cookie List](https://secure.fanboy.co.nz/fanboy-cookiemonster.txt) \[3\], parsing rules can be found on the [Adblock Plus Documentation](https://help.eyeo.com/en/adblockplus/how-to-write-filters) \[5\]
- The privacy policy wording is taken from [Measuring the GDPR’s Impact on Web Privacy](https://github.com/RUB-SysSec/we-value-your-privacy) \[4\]

### Installation
[Google Chrome](https://www.google.com/chrome/), [Chromedriver](https://chromedriver.chromium.org/), and [Python3](https://www.python.org/) should be installed on the system. The necessary packages can be found in the `analyse/requirements.txt` file and installed using [pip](https://github.com/pypa/pip):
```bash
pip3 install -r analyse/requirements.txt
```

Alternatively the provided docker configuration can be used, to build the container run:
```bash
docker build . -t measuring_gdpr
```

### Usage
To start scanning, make sure a file containing the domain names is present on the system and then run the following command:
```
python3 app.py -i <domain_names.txt> -o <output_file.json>
```
Once finished, the statistics can be generated with the results script:
```
python3 results.py -i <output_file.json>
```

### References
\[0\]: Alexa Internet, Inc. Alexa - Top sites. https://www.alexa.com/topsites, 2022.

\[1\]: Naab, Johannes, et al. "Prefix top lists: Gaining insights with prefixes from domain-based top lists on dns deployment." Proceedings of the Internet Measurement Conference. 2019.

\[2\]: Trevisan, Martino, et al. "4 Years of EU Cookie Law: Results and Lessons Learned." Proc. Priv. Enhancing Technol. 2019.2 (2019): 126-145.

\[3\]: Easylist. EasyList Cookie List. https://secure.fanboy.co.nz/fanboy-cookiemonster.txt, 2022.

\[4\]: Degeling, Martin, et al. "We value your privacy... now take some cookies: Measuring the GDPR's impact on web privacy." arXiv preprint arXiv:1808.05096 (2018).

\[5\]: eyeo GmbH. How to write filters | Adblock Plus Help Center. https://help.eyeo.com/en/adblockplus/how-to-write-filters, 2022.
