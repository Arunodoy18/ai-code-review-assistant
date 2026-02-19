import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';

interface Subscription {
  id: number;
  tier: string;
  status: string;
  billing_interval: string | null;
  current_period_start: string | null;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
  trial_end: string | null;
}

interface UsageStats {
  month: string;
  analyses_used: number;
  analyses_limit: number;
  analyses_remaining: number;
  percentage_used: number;
  total_lines_analyzed: number;
  total_findings_generated: number;
  is_unlimited: boolean;
}

export const BillingDashboard: React.FC = () => {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [usage, setUsage] = useState<UsageStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [subResponse, usageResponse] = await Promise.all([
        apiClient.get('/api/billing/subscription'),
        apiClient.get('/api/billing/usage'),
      ]);
      setSubscription(subResponse.data);
      setUsage(usageResponse.data);
    } catch (error) {
      console.error('Failed to load billing data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleManageBilling = async () => {
    try {
      const response = await apiClient.post('/api/billing/subscription/portal');
      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (error: any) {
      console.error('Failed to open billing portal:', error);
      alert(error.response?.data?.detail || 'Failed to open billing portal');
    }
  };

  const handleCancelSubscription = async () => {
    if (!confirm('Are you sure you want to cancel your subscription? You will still have access until the end of your billing period.')) {
      return;
    }

    try {
      await apiClient.post('/api/billing/subscription/cancel?immediate=false');
      alert('Subscription will be canceled at the end of the billing period');
      loadData();
    } catch (error: any) {
      console.error('Failed to cancel subscription:', error);
      alert(error.response?.data?.detail || 'Failed to cancel subscription');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const getTierBadgeColor = (tier: string) => {
    switch (tier) {
      case 'FREE':
        return 'bg-gray-100 text-gray-800';
      case 'PRO':
        return 'bg-blue-100 text-blue-800';
      case 'ENTERPRISE':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'bg-green-100 text-green-800';
      case 'TRIALING':
        return 'bg-yellow-100 text-yellow-800';
      case 'PAST_DUE':
        return 'bg-red-100 text-red-800';
      case 'CANCELED':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Billing & Usage</h1>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Subscription Card */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Current Subscription
          </h2>

          {subscription && (
            <div className="space-y-4">
              {/* Tier & Status */}
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Plan:</span>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-semibold ${getTierBadgeColor(
                    subscription.tier
                  )}`}
                >
                  {subscription.tier}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-gray-600">Status:</span>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusBadgeColor(
                    subscription.status
                  )}`}
                >
                  {subscription.status}
                </span>
              </div>

              {/* Billing Interval */}
              {subscription.billing_interval && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Billing:</span>
                  <span className="text-gray-900 font-medium">
                    {subscription.billing_interval}
                  </span>
                </div>
              )}

              {/* Trial End */}
              {subscription.trial_end && subscription.status === 'TRIALING' && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Trial Ends:</span>
                  <span className="text-gray-900 font-medium">
                    {formatDate(subscription.trial_end)}
                  </span>
                </div>
              )}

              {/* Current Period */}
              {subscription.current_period_end && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">
                    {subscription.cancel_at_period_end ? 'Cancels On:' : 'Renews On:'}
                  </span>
                  <span className="text-gray-900 font-medium">
                    {formatDate(subscription.current_period_end)}
                  </span>
                </div>
              )}

              {/* Action Buttons */}
              <div className="pt-4 space-y-2">
                {subscription.tier !== 'FREE' && (
                  <button
                    onClick={handleManageBilling}
                    className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors"
                  >
                    Manage Billing
                  </button>
                )}

                {subscription.tier !== 'FREE' && !subscription.cancel_at_period_end && (
                  <button
                    onClick={handleCancelSubscription}
                    className="w-full bg-red-50 text-red-600 py-2 px-4 rounded-md hover:bg-red-100 transition-colors"
                  >
                    Cancel Subscription
                  </button>
                )}

                {subscription.tier === 'FREE' && (
                  <a
                    href="/pricing"
                    className="block w-full bg-indigo-600 text-white text-center py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors"
                  >
                    Upgrade Plan
                  </a>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Usage Card */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Usage This Month
          </h2>

          {usage && (
            <div className="space-y-4">
              {/* Analyses Usage */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-600">Analyses Used:</span>
                  <span className="text-gray-900 font-bold">
                    {usage.is_unlimited
                      ? `${usage.analyses_used} (Unlimited)`
                      : `${usage.analyses_used} / ${usage.analyses_limit}`}
                  </span>
                </div>

                {!usage.is_unlimited && (
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className={`h-2.5 rounded-full transition-all ${
                        usage.percentage_used >= 90
                          ? 'bg-red-600'
                          : usage.percentage_used >= 70
                          ? 'bg-yellow-600'
                          : 'bg-green-600'
                      }`}
                      style={{ width: `${Math.min(usage.percentage_used, 100)}%` }}
                    ></div>
                  </div>
                )}
              </div>

              {/* Remaining */}
              {!usage.is_unlimited && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Remaining:</span>
                  <span className="text-gray-900 font-medium">
                    {usage.analyses_remaining} analyses
                  </span>
                </div>
              )}

              {/* Additional Stats */}
              <div className="pt-4 border-t border-gray-200 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Lines Analyzed:</span>
                  <span className="text-gray-900 font-medium">
                    {usage.total_lines_analyzed.toLocaleString()}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Findings Generated:</span>
                  <span className="text-gray-900 font-medium">
                    {usage.total_findings_generated.toLocaleString()}
                  </span>
                </div>
              </div>

              {/* Warning */}
              {!usage.is_unlimited && usage.percentage_used >= 90 && (
                <div className="mt-4 p-4 bg-red-50 rounded-lg">
                  <p className="text-sm text-red-800">
                    ⚠️ You're running low on analyses. Consider upgrading your plan
                    to continue reviewing code.
                  </p>
                  <a
                    href="/pricing"
                    className="mt-2 inline-block text-sm text-red-600 font-semibold hover:text-red-700"
                  >
                    View Plans →
                  </a>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
