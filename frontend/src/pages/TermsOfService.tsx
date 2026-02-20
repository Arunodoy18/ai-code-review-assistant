export default function TermsOfService() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-8">
        <h1 className="text-4xl font-bold mb-6">Terms of Service</h1>
        <p className="text-sm text-gray-500 mb-8">Last Updated: February 19, 2026</p>

        <div className="space-y-6 text-gray-700">
          <section>
            <h2 className="text-2xl font-semibold mb-4">1. Acceptance of Terms</h2>
            <p>
              By accessing and using AI Code Review (&quot;the Service&quot;), you accept and agree to be bound by the terms and provisions of this agreement. If you do not agree to these Terms of Service, please do not use the Service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">2. Description of Service</h2>
            <p>
              AI Code Review provides AI-powered code analysis and review services for GitHub repositories. The Service analyzes pull requests and provides automated feedback on code quality, security vulnerabilities, performance issues, and best practices.
            </p>
            <p className="mt-2">
              You understand that the Service requires you to provide your own API keys for:
            </p>
            <ul className="list-disc list-inside ml-4 mt-2">
              <li>GitHub Personal Access Token for repository access</li>
              <li>AI/LLM providers (Groq, OpenAI, Anthropic, or Google) for analysis capabilities</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">3. User Accounts</h2>
            <h3 className="text-xl font-semibold mb-2">3.1 Registration</h3>
            <p>
              You must create an account to use the Service. You agree to provide accurate, current, and complete information during registration and to update such information to keep it accurate, current, and complete.
            </p>
            <h3 className="text-xl font-semibold mb-2 mt-4">3.2 Account Security</h3>
            <p>
              You are responsible for safeguarding your password and API keys. You agree not to disclose your password or API keys to any third party. You must notify us immediately upon becoming aware of any breach of security or unauthorized use of your account.
            </p>
            <h3 className="text-xl font-semibold mb-2 mt-4">3.3 Email Verification</h3>
            <p>
              You must verify your email address to access certain features of the Service. We may restrict unverified accounts from performing certain actions.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">4. API Keys and Third-Party Services</h2>
            <h3 className="text-xl font-semibold mb-2">4.1 Your Responsibility</h3>
            <p>
              You are solely responsible for obtaining and maintaining your own API keys from GitHub and AI/LLM providers. You acknowledge that:
            </p>
            <ul className="list-disc list-inside ml-4 mt-2">
              <li>You must comply with the terms of service of GitHub and your chosen AI/LLM provider</li>
              <li>API usage costs (if any) from third-party providers are your responsibility</li>
              <li>We do not provide or pay for GitHub or AI/LLM API access</li>
              <li>We securely store your API keys but you retain ownership and control</li>
            </ul>
            <h3 className="text-xl font-semibold mb-2 mt-4">4.2 API Key Security</h3>
            <p>
              We encrypt and securely store your API keys in our database. However, you acknowledge that you are sharing these keys with our Service and should use keys with appropriate permissions (read-only for analysis purposes).
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">5. Usage Limits and Subscriptions</h2>
            <h3 className="text-xl font-semibold mb-2">5.1 Free Tier</h3>
            <p>
              Free accounts are limited to 10 PR analyses per month and 1 repository. Free tier users have access to community support only.
            </p>
            <h3 className="text-xl font-semibold mb-2 mt-4">5.2 Paid Tiers</h3>
            <p>
              Paid subscriptions (Pro and Enterprise) offer higher limits and additional features. Subscription fees are billed monthly or annually in advance and are non-refundable except as required by law.
            </p>
            <h3 className="text-xl font-semibold mb-2 mt-4">5.3 Fair Use</h3>
            <p>
              You agree not to abuse the Service or use it in a way that could damage, disable, overburden, or impair our servers or networks.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">6. Intellectual Property</h2>
            <h3 className="text-xl font-semibold mb-2">6.1 Your Code</h3>
            <p>
              You retain all rights to your source code. We do not claim ownership of your code or analysis results.
            </p>
            <h3 className="text-xl font-semibold mb-2 mt-4">6.2 Our Service</h3>
            <p>
              The Service, including its software, algorithms, and user interface, is protected by copyright, trademark, and other intellectual property laws. You may not copy, modify, or distribute our software without permission.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">7. Privacy and Data Protection</h2>
            <p>
              Your privacy is important to us. Please review our <a href="/privacy-policy" className="text-indigo-600 hover:text-indigo-800">Privacy Policy</a> to understand how we collect, use, and protect your personal information and code data.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">8. Disclaimer of Warranties</h2>
            <p>
              THE SERVICE IS PROVIDED &quot;AS IS&quot; AND &quot;AS AVAILABLE&quot; WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED. WE DO NOT WARRANT THAT:
            </p>
            <ul className="list-disc list-inside ml-4 mt-2">
              <li>The Service will be uninterrupted, secure, or error-free</li>
              <li>AI-generated analysis will be accurate, complete, or error-free</li>
              <li>Defects will be corrected</li>
              <li>The Service is free of viruses or other harmful components</li>
            </ul>
            <p className="mt-2">
              <strong>AI Analysis Disclaimer:</strong> AI-generated code reviews are provided as suggestions only and should be reviewed by qualified developers. We are not responsible for bugs, security vulnerabilities, or issues that AI analysis fails to detect or incorrectly identifies.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">9. Limitation of Liability</h2>
            <p>
              TO THE MAXIMUM EXTENT PERMITTED BY LAW, WE SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR REVENUES, WHETHER INCURRED DIRECTLY OR INDIRECTLY, OR ANY LOSS OF DATA, USE, GOODWILL, OR OTHER INTANGIBLE LOSSES RESULTING FROM:
            </p>
            <ul className="list-disc list-inside ml-4 mt-2">
              <li>Your use or inability to use the Service</li>
              <li>Any unauthorized access to or use of our servers and/or any personal information stored therein</li>
              <li>Any bugs, security vulnerabilities, or defects in your code not detected by the Service</li>
              <li>Any errors or inaccuracies in AI-generated analysis</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">10. Termination</h2>
            <p>
              We may terminate or suspend your account and access to the Service immediately, without prior notice or liability, for any reason, including breach of these Terms. Upon termination, your right to use the Service will cease immediately.
            </p>
            <p className="mt-2">
              You may delete your account at any time through your account settings. Upon deletion, all your data will be permanently removed in accordance with our Privacy Policy and GDPR requirements.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">11. Changes to Terms</h2>
            <p>
              We reserve the right to modify these Terms at any time. We will notify users of any material changes via email or through the Service. Your continued use of the Service after such modifications constitutes acceptance of the updated Terms.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">12. Governing Law</h2>
            <p>
              These Terms shall be governed by and construed in accordance with the laws of the jurisdiction in which our company is registered, without regard to its conflict of law provisions.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">13. Contact Information</h2>
            <p>
              If you have any questions about these Terms, please contact us at:
            </p>
            <p className="mt-2 font-semibold">
              Email: legal@codereview.ai<br />
              Support: support@codereview.ai
            </p>
          </section>
        </div>

        <div className="mt-12 pt-6 border-t border-gray-200">
          <p className="text-center text-gray-500 text-sm">
            By using AI Code Review, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service.
          </p>
        </div>
      </div>
    </div>
  );
}
