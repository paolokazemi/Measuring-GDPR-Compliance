# Measuring GDPR Compliance

### Description


### Dataset
- Top 50 websites for NL and Global are taken from [Alexa](https://www.alexa.com/topsites) \[0\]
- Top 500 global websites are taken from the [Prefix Top Lists study](https://prefixtoplists.net.in.tum.de/) \[1\]
- The list of trackers is taken from the [CookieCheck repository](https://github.com/CookieChecker/CookieCheckSourceCode) \[2\]
- The list of cookie filters is taken from [EasyList Cookie List](https://secure.fanboy.co.nz/fanboy-cookiemonster.txt) \[3\]
- The privacy policy wording is taken from [Measuring the GDPR’s Impact on Web Privacy](https://github.com/RUB-SysSec/we-value-your-privacy) \[4\]

### Installation
[Google Chrome](https://www.google.com/chrome/), [Chromedriver](https://chromedriver.chromium.org/), and [Python3](https://www.python.org/) should be installed on the system. The necessary packages are found in the `analyse/requirements.txt` file and can be installed using [pip](https://github.com/pypa/pip):
```bash
pip3 install -r analyse/requirements.txt
```

Alternatively the provided docker configuration can be used, to build the container run:
```bash
docker build . -t measuring_gdpr
```

### References
\[0\]: Alexa Internet, Inc. Alexa - Top sites. https://www.alexa.com/topsites, 2022.

\[1\]: Naab, Johannes, et al. "Prefix top lists: Gaining insights with prefixes from domain-based top lists on dns deployment." Proceedings of the Internet Measurement Conference. 2019.

\[2\]: Trevisan, Martino, et al. "4 Years of EU Cookie Law: Results and Lessons Learned." Proc. Priv. Enhancing Technol. 2019.2 (2019): 126-145.

\[3\]: Easylist. EasyList Cookie List. https://secure.fanboy.co.nz/fanboy-cookiemonster.txt, 2022.

\[4\]: Degeling, Martin, et al. "We value your privacy... now take some cookies: Measuring the GDPR's impact on web privacy." arXiv preprint arXiv:1808.05096 (2018).