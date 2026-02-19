import React from 'react';

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-8">
        <h1 className="text-4xl font-bold mb-6">Privacy Policy</h1>
        <p className="text-sm text-gray-500 mb-8">Last Updated: February 19, 2026</p>

        <div className="space-y-6 text-gray-700">
          <section>
            <h2 className="text-2xl font-semibold mb-4">1. Introduction</h2>
            <p>
              AI Code Review (&quot;we&quot;, &quot;our&quot;, or &quot;us&quot;) is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our Service.
            </p>
            <p className="mt-2">
              This policy is designed to comply with the General Data Protection Regulation (GDPR) and other applicable privacy laws.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">2. Information We Collect</h2>
            <h3 className="text-xl font-semibold mb-2">2.1 Account Information</h3>
            <ul className="list-disc list-inside ml-4">
              <li>Name</li>
              <li>Email address</li>
              <li>Password (encrypted)</li>
              <li>Account creation and last update timestamps</li>
            </ul>

            <h3 className="text-xl font-semibold mb-2 mt-4">2.2 API Keys and Tokens</h3>
            <ul className="list-disc list-inside ml-4">
              <li>GitHub Personal Access Token</li>
              <li>LLM Provider API Keys (Groq, OpenAI, Anthropic, Google)</li>
              <li>GitHub Webhook Secrets</li>
            </ul>
            <p className="mt-2">
              These are encrypted and stored securely in our database. We only use them to perform the services you request.
            </p>

            <h3 className="text-xl font-semibold mb-2 mt-4">2.3 Code and Repository Data</h3>
            <ul className="list-disc list-inside ml-4">
              <li>GitHub repository names and URLs</li>
              <li>Pull request content (diffs, file names, code snippets)</li>
              <li>Analysis results and findings</li>
              <li>Risk scores and metadata</li>
            </ul>
            <p className="mt-2">
              We only access repositories you explicitly authorize through your GitHub token.
            </p>

            <h3 className="text-xl font-semibold mb-2 mt-4">2.4 Usage Data</h3>
            <ul className="list-disc list-inside ml-4">
              <li>Analysis run history</li>
              <li>Number of PRs analyzed</li>
              <li>Subscription tier and usage limits</li>
              <li>Login timestamps and session data</li>
            </ul>

            <h3 className="text-xl font-semibold mb-2 mt-4">2.5 Technical Data</h3>
            <ul className="list-disc list-inside ml-4">
              <li>IP address</li>
              <li>Browser type and version</li>
              <li>Cookie identifiers</li>
              <li>Error logs and diagnostic data</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">3. How We Use Your Information</h2>
            <p>We use your information to:</p>
            <ul className="list-disc list-inside ml-4 mt-2">
              <li><strong>Provide the Service:</strong> Analyze your code, generate findings, and deliver results</li>
              <li><strong>Authentication:</strong> Verify your identity and maintain your session</li>
              <li><strong>Communication:</strong> Send verification emails, password resets, and important service updates</li>
              <li><strong>Improve the Service:</strong> Analyze usage patterns to enhance features and performance</li>
              <li><strong>Security:</strong> Detect and prevent fraud, abuse, and security incidents</li>
              <li><strong>Compliance:</strong> Comply with legal obligations and enforce our Terms of Service</li>
              <li><strong>Billing:</strong> Process subscription payments (if applicable)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">4. Legal Basis for Processing (GDPR)</h2>
            <p>We process your personal data based on:</p>
            <ul className="list-disc list-inside ml-4 mt-2">
              <li><strong>Contract:</strong> Processing necessary to provide the Service you requested</li>
              <li><strong>Consent:</strong> You explicitly consent to us processing your data for specific purposes</li>
              <li><strong>Legitimate Interests:</strong> Improving our Service, security, and fraud prevention</li>
              <li><strong>Legal Obligation:</strong> Complying with laws and regulations</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">5. Data Sharing and Disclosure</h2>
            <h3 className="text-xl font-semibold mb-2">5.1 Third-Party Services</h3>
            <p>We share data with third-party services necessary to operate our Service:</p>
            <ul className="list-disc list-inside ml-4 mt-2">
              <li><strong>GitHub:</strong> We use your GitHub token to access repositories you authorize</li>
              <li><strong>AI/LLM Providers:</strong> We send code snippets to the AI provider you configure (using your API key)</li>
              <li><strong>Cloud Infrastructure:</strong> Our hosting providers (AWS/GCP/Azure) store data in encrypted form</li>
              <li><strong>Error Tracking:</strong> Sentry receives anonymized error data to help us fix bugs</li>
            </ul>

            <h3 className="text-xl font-semibold mb-2 mt-4">5.2 We Do NOT:</h3>
            <ul className="list-disc list-inside ml-4">
              <li>Sell your personal information to third parties</li>
              <li>Share your code with the public or other users</li>
              <li>Use your code to train AI models (unless you explicitly opt-in)</li>
              <li>Share your data for marketing purposes</li>
            </ul>

            <h3 className="text-xl font-semibold mb-2 mt-4">5.3 Legal Requirements</h3>
            <p>
              We may disclose your information if required by law, court order, or governmental authority, or to protect our rights, property, or safety.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">6. Data Security</h2>
            <p>We implement industry-standard security measures:</p>
            <ul className="list-disc list-inside ml-4 mt-2">
              <li><strong>Encryption in Transit:</strong> HTTPS/TLS for all communications</li>
              <li><strong>Encryption at Rest:</strong> Database encryption for sensitive data</li>
              <li><strong>API Key Encryption:</strong> All API keys and tokens are encrypted before storage</li>
              <li><strong>Access Controls:</strong> Role-based access and authentication</li>
              <li><strong>Regular Audits:</strong> Security reviews and vulnerability scanning</li>
              <li><strong>Secure Infrastructure:</strong> Hosted on secure cloud platforms with compliance certifications</li>
            </ul>
            <p className="mt-2">
              However, no method of transmission over the Internet is 100% secure. We cannot guarantee absolute security.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">7. Data Retention</h2>
            <ul className="list-disc list-inside ml-4">
              <li><strong>Active Accounts:</strong> We retain your data while your account is active and for a reasonable period afterward</li>
              <li><strong>Deleted Accounts:</strong> When you delete your account, we permanently delete all your data within 30 days</li>
              <li><strong>Analysis History:</strong> Analysis results are retained as long as your account is active</li>
              <li><strong>Backups:</strong> Deleted data may persist in backups for up to 90 days before permanent deletion</li>
              <li><strong>Legal Hold:</strong> We may retain data longer if required by law or pending legal proceedings</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">8. Your Rights (GDPR)</h2>
            <p>Under GDPR, you have the right to:</p>
            <h3 className="text-xl font-semibold mb-2 mt-4">8.1 Right to Access (Article 15)</h3>
            <p>
              Request a copy of all personal data we hold about you. You can export your data anytime via Account Settings → Export Data.
            </p>

            <h3 className="text-xl font-semibold mb-2 mt-4">8.2 Right to Rectification (Article 16)</h3>
            <p>
              Correct inaccurate or incomplete personal data. You can update your profile information in Account Settings.
            </p>

            <h3 className="text-xl font-semibold mb-2 mt-4">8.3 Right to Erasure (Article 17)</h3>
            <p>
              Request deletion of your personal data (&quot;right to be forgotten&quot;). You can delete your account via Account Settings → Delete Account.
            </p>

            <h3 className="text-xl font-semibold mb-2 mt-4">8.4 Right to Restrict Processing (Article 18)</h3>
            <p>
              Request restriction of processing your data under certain conditions. Contact us to exercise this right.
            </p>

            <h3 className="text-xl font-semibold mb-2 mt-4">8.5 Right to Data Portability (Article 20)</h3>
            <p>
              Receive your data in a structured, machine-readable format (JSON). Use the Export Data feature.
            </p>

            <h3 className="text-xl font-semibold mb-2 mt-4">8.6 Right to Object (Article 21)</h3>
            <p>
              Object to processing based on legitimate interests. You can opt-out of analytics and non-essential processing.
            </p>

            <h3 className="text-xl font-semibold mb-2 mt-4">8.7 Right to Withdraw Consent (Article 7)</h3>
            <p>
              Withdraw consent at any time for processing based on consent.
            </p>

            <h3 className="text-xl font-semibold mb-2 mt-4">8.8 Right to Lodge a Complaint</h3>
            <p>
              File a complaint with your local data protection authority if you believe we have violated your privacy rights.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">9. Cookies and Tracking</h2>
            <p>We use cookies and similar technologies for:</p>
            <ul className="list-disc list-inside ml-4 mt-2">
              <li><strong>Essential Cookies:</strong> Authentication, session management, and security</li>
              <li><strong>Analytics Cookies:</strong> Understanding how users interact with our Service (anonymized)</li>
              <li><strong>Preference Cookies:</strong> Remembering your settings and preferences</li>
            </ul>
            <p className="mt-2">
              You can control cookies through your browser settings. Note that disabling essential cookies may affect Service functionality.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">10. Children's Privacy</h2>
            <p>
              Our Service is not directed to individuals under 16 years of age. We do not knowingly collect personal information from children under 16. If you become aware that a child has provided us with personal information, please contact us so we can delete it.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">11. International Data Transfers</h2>
            <p>
              Your data may be transferred to and maintained on servers located outside your country of residence. We ensure appropriate safeguards are in place, including:
            </p>
            <ul className="list-disc list-inside ml-4 mt-2">
              <li>Standard Contractual Clauses (SCCs) for EU data transfers</li>
              <li>Hosting providers with GDPR compliance certifications</li>
              <li>Encryption of data in transit and at rest</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">12. Changes to This Privacy Policy</h2>
            <p>
              We may update this Privacy Policy from time to time. We will notify you of any material changes via:
            </p>
            <ul className="list-disc list-inside ml-4 mt-2">
              <li>Email notification to your registered email address</li>
              <li>Prominent notice on our Service</li>
              <li>Updated &quot;Last Updated&quot; date at the top of this policy</li>
            </ul>
            <p className="mt-2">
              Your continued use of the Service after changes constitutes acceptance of the updated Privacy Policy.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">13. Contact Us</h2>
            <p>
              If you have questions about this Privacy Policy or wish to exercise your rights, contact us at:
            </p>
            <div className="mt-4 bg-gray-100 p-4 rounded-lg">
              <p className="font-semibold">Data Protection Officer</p>
              <p>Email: privacy@codereview.ai</p>
              <p>Support: support@codereview.ai</p>
            </div>
            <p className="mt-4">
              <strong>EU Representative:</strong> [If required, add EU representative contact information]
            </p>
          </section>

          <section className="bg-blue-50 p-6 rounded-lg mt-8">
            <h2 className="text-2xl font-semibold mb-4">Quick Links</h2>
            <ul className="space-y-2">
              <li>
                <a href="/account/settings" className="text-indigo-600 hover:text-indigo-800 font-semibold">
                  → Export Your Data (GDPR Article 15)
                </a>
              </li>
              <li>
                <a href="/account/settings" className="text-indigo-600 hover:text-indigo-800 font-semibold">
                  → Delete Your Account (GDPR Article 17)
                </a>
              </li>
              <li>
                <a href="/terms-of-service" className="text-indigo-600 hover:text-indigo-800 font-semibold">
                  → Read Terms of Service
                </a>
              </li>
            </ul>
          </section>
        </div>

        <div className="mt-12 pt-6 border-t border-gray-200">
          <p className="text-center text-gray-500 text-sm">
            Your privacy matters to us. We are committed to protecting your data and being transparent about how we use it.
          </p>
        </div>
      </div>
    </div>
  );
}
