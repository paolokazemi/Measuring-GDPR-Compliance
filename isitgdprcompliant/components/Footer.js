import { REPO_LINK } from '../services/constants';
import Link from 'next/link';

export default function Footer() {
  return (
    <div className="container mt-auto">
      <footer className="py-3 my-4">
        <ul className="nav justify-content-center border-bottom pb-3 mb-3">
          <li className="nav-item"><a href={REPO_LINK} className="nav-link px-2 text-muted"><i className="bi-github" role="img" aria-label="GitHub"></i> GitHub</a></li>
          <li className="nav-item"><Link href="/"><a className="nav-link px-2 text-muted">Home</a></Link></li>
          <li className="nav-item"><Link href="/privacypolicy"><a className="nav-link px-2 text-muted">Privacy Policy</a></Link></li>
        </ul>
        <p className="text-center text-muted">© Copyright {new Date().getFullYear()} IsItGDPRCompliant.com.</p>
      </footer>
    </div>
  );
}
