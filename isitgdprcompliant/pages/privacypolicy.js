import PrivacyPolicy from '../components/PrivacyPolicy';
import Footer from '../components/Footer';
import { NextSeo } from 'next-seo';

export default function PrivacyPolicyPage() {
  return (
    <div className="d-flex flex-column min-vh-100">
      <NextSeo
        title="Privacy Policy | Is X GDPR Compliant?"
        description="Privacy Policy. We do not collect any data."
        canonical="https://isitgdprcompliant.com/"
        openGraph={{
          url: 'https://isitgdprcompliant.com/',
          title: 'Privacy Policy | Is X GDPR Compliant?',
          description: 'Privacy Policy. We do not collect any data.',
          site_name: 'IsItGDPRCompliant',
        }}
        additionalLinkTags={[
          {
            rel: 'icon',
            href: '/favicon.svg',
          }
        ]}
      />
      <PrivacyPolicy />
      <Footer />
    </div>
  );
};
