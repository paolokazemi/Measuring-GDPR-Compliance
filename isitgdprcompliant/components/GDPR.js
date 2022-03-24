import { useState, useEffect } from 'react';
import { RESULT_LINK } from '../services/constants';
import humanizeDuration from 'humanize-duration';

export default function GDPR() {
  const [results, setResults] = useState([]);
  const [currentResult, setCurrentResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchData() {
      const res = await fetch(RESULT_LINK);
      const json = await res.json();
      setResults(json);
    }
    fetchData();
  }, []);

  const search = (event) => {
    event.preventDefault();
    const domain = event.target.domain.value;
    const matches = results.filter(x => x.site.endsWith(domain));
    const result = matches[0];

    if (!result) {
      setCurrentResult(null);
      setError("This domain name was not analysed.");
      return;
    }

    setCurrentResult(result);
    setError("");
  };

  const getResult = (isYes) => {
    return isYes
      ? <i className="bi-check-lg" role="img" aria-label="Yes"></i>
      : <i className="bi-x-lg" role="img" aria-label="No"></i>;
  }

  return (
    <main>
      <div className="container py-3">
        <div className="m5-5">
          <h2 className="text-center">Is X GDPR Compliant?</h2>
          <form onSubmit={search}>
            <div className="input-group input-group-lg">
              <input type="text" className={`form-control ${error ? 'is-invalid' : ''}`} aria-label="Domain name" placeholder="Domain name" name="domain" />
              <button type="submit" className="btn btn-outline-secondary"><i className="bi-search" role="img" aria-label="Search"></i> Search</button>
              <div className="invalid-feedback">{error}</div>
            </div>
          </form>
        </div>
        { currentResult
          ? <div className="table-responsive py-3">
              <table className="table table-bordered">
                <tbody>
                  <tr>
                    <td>HTTP to HTTPS Redirect</td>
                    <td>{getResult(currentResult["redirect_https"])}</td>
                  </tr>
                  <tr>
                    <td>HTTPS Support</td>
                    <td>{getResult(currentResult["https_support"])}</td>
                  </tr>
                  <tr>
                    <td>Cookie banner present</td>
                    <td>{getResult(currentResult["has_banner"])}</td>
                  </tr>
                  <tr>
                    <td>Privacy Policy</td>
                    <td>{getResult(currentResult["privacy_policy"]["link"] !== "ERROR")}
                      {
                        currentResult["privacy_policy"]["link"] !== "ERROR"
                          ? ` (Found via ${currentResult["privacy_policy"]["xpath_results"].length > 0 ? "xpath" : "google search"})`
                          : null
                      }
                    </td>
                  </tr>
                  <tr>
                    <td>GDPR References</td>
                    <td>{getResult(currentResult["gdpr_ref"]["gdpr_reference_present"] === "yes")}</td>
                  </tr>
                  <tr>
                    <td>GDPR Compliant</td>
                    <td>{currentResult["gdpr_compliant"]}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          : null
        }
        { currentResult && currentResult['cookies'].length > 0
          ? <div className="table-responsive">
              <table className="table table-bordered table-responsive">
                <thead>
                  <tr>
                    <th scope="col">Cookie Name</th>
                    <th scope="col">Domain</th>
                    <th scope="col">Duration</th>
                    <th scope="col">Persistent</th>
                    <th scope="col">Tracker</th>
                    <th scope="col">Cloaked Domain</th>
                  </tr>
                </thead>
                <tbody>
                  {currentResult['cookies'].map(cookie => (
                    <tr key={cookie['name']}>
                      <th scope="row">{cookie['name']}</th>
                      <td>{cookie['domain']}</td>
                      <td>{humanizeDuration(cookie['duration'] * 1000, { round: true })}</td>
                      <td>{getResult(cookie['persistent'])}</td>
                      <td>{getResult(cookie['tracker'])}</td>
                      <td>
                        { cookie['cloaked_domain']['resolved_domain'].length > 1
                          ? cookie['cloaked_domain']['resolved_domain'].slice(-1)[0]
                          : <i className="bi-x-lg" role="img" aria-label="No"></i>
                        }
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          : null
        }
      </div>
    </main>
  );
};
