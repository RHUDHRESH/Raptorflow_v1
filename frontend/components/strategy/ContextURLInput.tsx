/**
 * Context URL Input Component
 * Input field for adding URLs/links
 */

'use client';

import React, { useState } from 'react';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

interface ContextURLInputProps {
  onSubmit: (url: string) => Promise<void>;
}

export default function ContextURLInput({ onSubmit }: ContextURLInputProps) {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    if (!url.trim()) return;

    if (!isValidUrl(url)) {
      setError('Please enter a valid URL');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await onSubmit(url);
      setUrl('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add URL');
    } finally {
      setLoading(false);
    }
  };

  const isValidUrl = (urlString: string) => {
    try {
      new URL(urlString);
      return true;
    } catch {
      return false;
    }
  };

  return (
    <div className="flex flex-col gap-3 mb-4">
      <Input
        type="url"
        placeholder="https://example.com/article"
        value={url}
        onChange={(e) => {
          setUrl(e.target.value);
          setError('');
        }}
        disabled={loading}
        className="w-full"
      />

      {error && <p className="text-red-600 text-sm">{error}</p>}

      <Button
        variant="primary"
        onClick={handleSubmit}
        disabled={!url.trim() || loading}
        size="sm"
      >
        {loading ? 'Fetching...' : 'Add Link'}
      </Button>
    </div>
  );
}
