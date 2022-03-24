import GDPR from '../components/GDPR';
import Footer from '../components/Footer';
import { NextSeo } from 'next-seo';

export default function Home() {
  return (
    <div className="d-flex flex-column min-vh-100">
      <NextSeo
        title="Is X GDPR Compliant?"
        description="Scanning the most visited websites for non-compliant implementations of GDPR."
        canonical="https://isitgdprcompliant.com/"
        openGraph={{
          url: 'https://isitgdprcompliant.com/',
          title: 'Is X GDPR Compliant?',
          description: 'Scanning the most visited websites for non-compliant implementations of GDPR.',
          site_name: 'IsItGDPRCompliant',
        }}
        additionalLinkTags={[
          {
            rel: 'icon',
            href: '/favicon.svg',
          }
        ]}
      />
      <GDPR />
      <Footer />
    </div>
  );
};
