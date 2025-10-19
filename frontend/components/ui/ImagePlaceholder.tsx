'use client';

import Image from 'next/image';
import { useState } from 'react';
import { motion } from 'framer-motion';

interface ImagePlaceholderProps {
  src?: string;
  alt: string;
  aspectRatio?: string;
  className?: string;
  caption?: string;
  icon?: React.ReactNode;
}

export function ImagePlaceholder({
  src,
  alt,
  aspectRatio = 'aspect-video',
  className = '',
  caption,
  icon
}: ImagePlaceholderProps) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  return (
    <div className={`relative ${className}`}>
      <div className={`img-placeholder ${aspectRatio} ${loaded ? '' : 'skeleton'}`}>
        {!src || error ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-muted">
            {icon || (
              <svg className="w-12 h-12 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            )}
            <span className="mt-2 text-xs">image placeholder</span>
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: loaded ? 1 : 0 }}
            transition={{ duration: 0.3 }}
          >
            <Image
              src={src}
              alt={alt}
              fill
              className="object-cover"
              onLoadingComplete={() => setLoaded(true)}
              onError={() => setError(true)}
            />
          </motion.div>
        )}
      </div>
      {caption && (
        <p className="mt-2 text-xs text-akaroa opacity-75">{caption}</p>
      )}
    </div>
  );
}
