import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';

interface Plan {
  tier: string;
  name: string;
  monthly_price: number;
  yearly_price: number;
  analyses_limit: number;
  features: string[];
}

export const PricingPage: React.FC = () => {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [billingInterval, setBillingInterval] = useState<'MONTHLY' | 'YEARLY'>('MONTHLY');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadPlans();
  }, []);

  const loadPlans = async () => {
    try {
      const response = await apiClient.get('/api/billing/plans');
      setPlans(response.data);
    } catch (error) {
      console.error('Failed to load plans:', error);
    }
  };

  const handleSelectPlan = async (tier: string) => {
    if (tier === 'FREE') {
      navigate('/dashboard');
      return;
    }

    setLoading(true);
    try {
      // Create checkout session
      const response = await apiClient.post('/api/billing/subscription/checkout', {
        tier,
        billing_interval: billingInterval,
      });

      // Redirect to Stripe Checkout
      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (error: any) {
      console.error('Failed to create checkout session:', error);
      alert(error.response?.data?.detail || 'Failed to start checkout');
    } finally {
      setLoading(false);
    }
  };

  const getPrice = (plan: Plan) => {
    return billingInterval === 'MONTHLY' ? plan.monthly_price : plan.yearly_price;
  };

  const getSavingsPercentage = (plan: Plan) => {
    if (plan.monthly_price === 0) return 0;
    const yearlyMonthly = plan.yearly_price / 12;
    const savings = ((plan.monthly_price - yearlyMonthly) / plan.monthly_price) * 100;
    return Math.round(savings);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Choose Your Plan
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Start your 14-day free trial. No credit card required.
          </p>

          {/* Billing Toggle */}
          <div className="inline-flex items-center bg-white rounded-lg p-1 shadow-md">
            <button
              onClick={() => setBillingInterval('MONTHLY')}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                billingInterval === 'MONTHLY'
                  ? 'bg-indigo-600 text-white'
                  : 'text-gray-700 hover:text-indigo-600'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingInterval('YEARLY')}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                billingInterval === 'YEARLY'
                  ? 'bg-indigo-600 text-white'
                  : 'text-gray-700 hover:text-indigo-600'
              }`}
            >
              Yearly
              <span className="ml-2 text-xs text-green-600 font-semibold">
                Save 17%
              </span>
            </button>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8">
          {plans.map((plan) => {
            const isPopular = plan.tier === 'PRO';
            const price = getPrice(plan);
            const savings = getSavingsPercentage(plan);

            return (
              <div
                key={plan.tier}
                className={`relative bg-white rounded-2xl shadow-xl overflow-hidden transform transition-all hover:scale-105 ${
                  isPopular ? 'ring-4 ring-indigo-600' : ''
                }`}
              >
                {/* Popular Badge */}
                {isPopular && (
                  <div className="absolute top-0 right-0 bg-indigo-600 text-white px-4 py-1 text-sm font-semibold rounded-bl-lg">
                    Most Popular
                  </div>
                )}

                <div className="p-8">
                  {/* Plan Header */}
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">
                    {plan.name}
                  </h3>

                  {/* Price */}
                  <div className="mb-6">
                    <div className="flex items-baseline">
                      <span className="text-5xl font-extrabold text-gray-900">
                        ${price}
                      </span>
                      {plan.tier !== 'FREE' && (
                        <span className="ml-2 text-gray-600">
                          /{billingInterval === 'MONTHLY' ? 'month' : 'year'}
                        </span>
                      )}
                    </div>
                    {billingInterval === 'YEARLY' && savings > 0 && (
                      <p className="text-sm text-green-600 font-semibold mt-1">
                        Save {savings}% annually
                      </p>
                    )}
                  </div>

                  {/* Analyses Limit */}
                  <div className="mb-6 p-4 bg-indigo-50 rounded-lg">
                    <p className="text-center text-gray-900 font-semibold">
                      {plan.analyses_limit === -1
                        ? 'Unlimited'
                        : plan.analyses_limit}{' '}
                      {plan.analyses_limit === -1 ? 'Analyses' : 'analyses/month'}
                    </p>
                  </div>

                  {/* Features */}
                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start">
                        <svg
                          className="w-5 h-5 text-green-500 mr-3 flex-shrink-0 mt-0.5"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {/* CTA Button */}
                  <button
                    onClick={() => handleSelectPlan(plan.tier)}
                    disabled={loading}
                    className={`w-full py-3 px-6 rounded-lg font-semibold transition-colors ${
                      isPopular
                        ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                        : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    {plan.tier === 'FREE' ? 'Get Started' : 'Start Free Trial'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* FAQ Section */}
        <div className="mt-16 bg-white rounded-2xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Frequently Asked Questions
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">
                What happens after my trial ends?
              </h3>
              <p className="text-gray-600">
                After your 14-day free trial, you'll be charged for your selected
                plan. You can cancel anytime before the trial ends with no charge.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">
                Can I change plans later?
              </h3>
              <p className="text-gray-600">
                Yes! You can upgrade or downgrade your plan at any time from your
                billing dashboard. Changes take effect immediately.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">
                What payment methods do you accept?
              </h3>
              <p className="text-gray-600">
                We accept all major credit cards (Visa, Mastercard, Amex) via our
                secure Stripe integration.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">
                Do you offer refunds?
              </h3>
              <p className="text-gray-600">
                We offer a 30-day money-back guarantee. If you're not satisfied,
                contact us for a full refund.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
