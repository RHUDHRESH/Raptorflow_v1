/**
 * Performance Optimization Utilities
 * Debouncing, throttling, memoization helpers
 */

/**
 * Debounce function - delays function execution
 * @param fn - Function to debounce
 * @param ms - Delay in milliseconds
 * @returns Debounced function
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  ms: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout | null = null;

  return function (...args: Parameters<T>) {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    timeoutId = setTimeout(() => {
      fn(...args);
      timeoutId = null;
    }, ms);
  };
}

/**
 * Throttle function - limits function execution frequency
 * @param fn - Function to throttle
 * @param ms - Minimum interval between executions
 * @returns Throttled function
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  ms: number
): (...args: Parameters<T>) => void {
  let lastCall = 0;
  let timeoutId: NodeJS.Timeout | null = null;

  return function (...args: Parameters<T>) {
    const now = Date.now();
    const timeSinceLastCall = now - lastCall;

    if (timeSinceLastCall >= ms) {
      fn(...args);
      lastCall = now;
    } else {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }

      timeoutId = setTimeout(() => {
        fn(...args);
        lastCall = Date.now();
        timeoutId = null;
      }, ms - timeSinceLastCall);
    }
  };
}

/**
 * Request Animation Frame debounce
 * Schedules function to run on next frame
 * @param fn - Function to debounce
 * @returns RAF debounced function
 */
export function rafDebounce<T extends (...args: any[]) => any>(
  fn: T
): (...args: Parameters<T>) => void {
  let frameId: number | null = null;

  return function (...args: Parameters<T>) {
    if (frameId) {
      cancelAnimationFrame(frameId);
    }

    frameId = requestAnimationFrame(() => {
      fn(...args);
      frameId = null;
    });
  };
}

/**
 * Batch updates - collects updates and applies in single batch
 * Useful for multiple state updates
 */
export class BatchUpdater {
  private updates: Array<() => void> = [];
  private scheduled = false;

  add(update: () => void) {
    this.updates.push(update);
    this.scheduleFlush();
  }

  private scheduleFlush() {
    if (!this.scheduled) {
      this.scheduled = true;
      Promise.resolve().then(() => this.flush());
    }
  }

  private flush() {
    const updates = this.updates;
    this.updates = [];
    this.scheduled = false;

    updates.forEach((update) => update());
  }
}

/**
 * Deep equality check for objects
 * @param obj1 - First object
 * @param obj2 - Second object
 * @returns Whether objects are deeply equal
 */
export function deepEqual(obj1: any, obj2: any): boolean {
  if (obj1 === obj2) return true;

  if (
    typeof obj1 !== 'object' ||
    typeof obj2 !== 'object' ||
    obj1 === null ||
    obj2 === null
  ) {
    return false;
  }

  const keys1 = Object.keys(obj1);
  const keys2 = Object.keys(obj2);

  if (keys1.length !== keys2.length) return false;

  for (const key of keys1) {
    if (!keys2.includes(key)) return false;
    if (!deepEqual(obj1[key], obj2[key])) return false;
  }

  return true;
}

/**
 * Shallow equality check for objects
 * @param obj1 - First object
 * @param obj2 - Second object
 * @returns Whether objects are shallowly equal
 */
export function shallowEqual(obj1: any, obj2: any): boolean {
  if (obj1 === obj2) return true;

  if (
    typeof obj1 !== 'object' ||
    typeof obj2 !== 'object' ||
    obj1 === null ||
    obj2 === null
  ) {
    return false;
  }

  const keys1 = Object.keys(obj1);
  const keys2 = Object.keys(obj2);

  if (keys1.length !== keys2.length) return false;

  for (const key of keys1) {
    if (!keys2.includes(key) || obj1[key] !== obj2[key]) return false;
  }

  return true;
}

/**
 * Memoization cache
 */
export class MemoCache<T> {
  private cache: Map<string, T> = new Map();
  private maxSize: number;

  constructor(maxSize = 100) {
    this.maxSize = maxSize;
  }

  get(key: string): T | undefined {
    return this.cache.get(key);
  }

  set(key: string, value: T) {
    // Implement simple LRU by deleting oldest if at max size
    if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }

    this.cache.set(key, value);
  }

  clear() {
    this.cache.clear();
  }

  has(key: string): boolean {
    return this.cache.has(key);
  }
}

/**
 * Memoize function with configurable key generator
 * @param fn - Function to memoize
 * @param keyGen - Function to generate cache key
 * @param maxSize - Maximum cache size
 * @returns Memoized function
 */
export function memoize<T extends (...args: any[]) => any>(
  fn: T,
  keyGen?: (...args: Parameters<T>) => string,
  maxSize = 100
): T {
  const cache = new MemoCache<ReturnType<T>>(maxSize);
  const defaultKeyGen = (...args: Parameters<T>) => JSON.stringify(args);
  const keyGenerator = keyGen || defaultKeyGen;

  return ((...args: Parameters<T>) => {
    const key = keyGenerator(...args);

    if (cache.has(key)) {
      return cache.get(key)!;
    }

    const result = fn(...args);
    cache.set(key, result);
    return result;
  }) as T;
}

/**
 * Performance monitoring utility
 */
export class PerformanceMonitor {
  private marks: Map<string, number> = new Map();

  mark(name: string) {
    this.marks.set(name, performance.now());
  }

  measure(name: string, startMark: string): number {
    const startTime = this.marks.get(startMark);
    if (!startTime) {
      console.warn(`Start mark "${startMark}" not found`);
      return 0;
    }

    const duration = performance.now() - startTime;

    if (typeof window !== 'undefined' && window.performance?.measure) {
      try {
        performance.measure(name, startMark);
      } catch (e) {
        // Mark might already exist, ignore
      }
    }

    return duration;
  }

  report(name: string, startMark: string) {
    const duration = this.measure(name, startMark);
    console.log(`[Performance] ${name}: ${duration.toFixed(2)}ms`);
    return duration;
  }

  clear() {
    this.marks.clear();
  }
}

/**
 * Singleton performance monitor instance
 */
export const globalPerformanceMonitor = new PerformanceMonitor();

/**
 * Hook for measuring React component render time
 */
export function measureComponentRender(componentName: string) {
  const startTime = performance.now();

  return () => {
    const duration = performance.now() - startTime;
    console.log(`[Render] ${componentName}: ${duration.toFixed(2)}ms`);
  };
}
