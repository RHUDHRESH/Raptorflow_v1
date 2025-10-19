'use client';

import { useEffect, useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { SkeletonCard } from '@/components/ui/Skeleton';

export default function SettingsPage() {
  const [loading, setLoading] = useState(true);
  const [subscription, setSubscription] = useState<any>(null);

  useEffect(() => {
    fetchSubscription();
    loadRazorpay();
  }, []);

  const fetchSubscription = async () => {
    try {
      const businessId = localStorage.getItem('business_id');
      const response = await fetch(`/api/subscription/${businessId}`);
      const result = await response.json();
      setSubscription(result);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRazorpay = () => {
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.async = true;
    document.body.appendChild(script);
  };

  const handleUpgrade = async (tier: string) => {
    try {
      const businessId = localStorage.getItem('business_id');
      
      // Create order
      const response = await fetch(`/api/razorpay/checkout?business_id=${businessId}&tier=${tier}`, {
        method: 'POST'
      });
      const { order_id, amount, currency, key_id } = await response.json();

      // Razorpay checkout
      const options = {
        key: key_id,
        amount: amount,
        currency: currency,
        name: 'RaptorFlow ADAPT',
        description: `${tier.toUpperCase()} Subscription`,
        order_id: order_id,
        handler: function (response: any) {
          alert('Payment successful!');
          window.location.reload();
        },
        prefill: {
          name: '',
          email: '',
          contact: ''
        },
        theme: {
          color: '#A68763'
        }
      };

      const rzp = new (window as any).Razorpay(options);
      rzp.open();
    } catch (error) {
      console.error('Error:', error);
    }
  };

  if (loading) {
    return (
      <div className="max-w-content mx-auto px-6 space-y-8">
        <SkeletonCard />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  const tiers = [
    {
      name: 'basic',
      price: 2000,
      features: [
        '3 ICPs',
        'Basic research',
        'Single positioning',
        '7-day campaigns',
        'Email support'
      ]
    },
    {
      name: 'pro',
      price: 3500,
      features: [
        '6 ICPs',
        'Deep research',
        '3 positioning options',
        '30-day campaigns',
        'Trend monitoring',
        'Priority support'
      ]
    },
    {
      name: 'enterprise',
      price: 5000,
      features: [
        'Unlimited ICPs',
        'Full research suite',
        'Unlimited positioning',
        'Unlimited campaigns',
        'Advanced analytics',
        'Route-back logic',
        'Dedicated support'
      ]
    }
  ];

  return (
    <div className="max-w-content mx-auto px-6 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-display text-whiterock mb-2">settings</h1>
        <p className="text-secondary">manage your subscription and preferences</p>
      </div>

      {/* Current Plan */}
      <Card className="p-8 bg-gradient-to-br from-[color:rgba(166,135,99,.08)] to-transparent">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-h2 text-whiterock mb-2">current plan</h2>
            <p className="text-display text-barley capitalize mb-2">{subscription?.tier || 'basic'}</p>
            <p className="text-sm text-secondary">
              {subscription?.status === 'trial' ? 'Trial period' : 'Active subscription'}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-muted mb-1">ICPs available</p>
            <p className="text-h1 text-whiterock">{subscription?.max_icps || 3}</p>
          </div>
        </div>
      </Card>

      {/* Pricing Tiers */}
      <div>
        <h2 className="text-h2 text-whiterock mb-6">upgrade your plan</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {tiers.map((tier, i) => {
            const isCurrent = subscription?.tier === tier.name;
            return (
              <Card
                key={tier.name}
                className={`p-6 ${isCurrent ? 'ring-2 ring-barley' : ''}`}
              >
                <div className="mb-4">
                  <h3 className="text-h2 text-whiterock capitalize mb-2">{tier.name}</h3>
                  <div className="flex items-baseline gap-2">
                    <span className="text-display text-barley">{tier.price}</span>
                    <span className="text-sm text-muted">/month</span>
                  </div>
                </div>

                <ul className="space-y-3 mb-6">
                  {tier.features.map((feature, j) => (
                    <li key={j} className="flex items-start gap-2 text-sm text-secondary">
                      <svg className="w-5 h-5 text-barley flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>

                <Button
                  variant={isCurrent ? 'ghost' : 'primary'}
                  className="w-full"
                  onClick={() => handleUpgrade(tier.name)}
                  disabled={isCurrent}
                >
                  {isCurrent ? 'current plan' : 'upgrade'}
                </Button>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Billing History */}
      <Card className="p-8">
        <h2 className="text-h2 text-whiterock mb-6">billing history</h2>
        <div className="text-center py-8">
          <p className="text-muted">no billing history yet</p>
        </div>
      </Card>
    </div>
  );
}

 API UTILITIES & HELPERS
