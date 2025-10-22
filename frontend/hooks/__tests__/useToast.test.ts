/**
 * Unit tests for useToast hook
 * Tests toast notification creation, removal, and shortcut methods
 */

import { renderHook, act } from '@testing-library/react';
import { useToast } from '../useToast';

describe('useToast Hook', () => {
  describe('addToast', () => {
    it('should add a toast message with default type', () => {
      const { result } = renderHook(() => useToast());

      act(() => {
        result.current.addToast('Test message');
      });

      expect(result.current.toasts).toHaveLength(1);
      expect(result.current.toasts[0].message).toBe('Test message');
      expect(result.current.toasts[0].type).toBe('info');
    });

    it('should add a toast with custom type', () => {
      const { result } = renderHook(() => useToast());

      act(() => {
        result.current.addToast('Error message', { type: 'error' });
      });

      expect(result.current.toasts[0].type).toBe('error');
      expect(result.current.toasts[0].message).toBe('Error message');
    });

    it('should add a toast with title and duration', () => {
      const { result } = renderHook(() => useToast());

      act(() => {
        result.current.addToast('Test message', {
          title: 'Test Title',
          duration: 3000,
        });
      });

      expect(result.current.toasts[0].title).toBe('Test Title');
      expect(result.current.toasts[0].duration).toBe(3000);
    });

    it('should return a unique toast ID', () => {
      const { result } = renderHook(() => useToast());

      let id1: string;
      let id2: string;

      act(() => {
        id1 = result.current.addToast('Toast 1');
        id2 = result.current.addToast('Toast 2');
      });

      expect(id1).not.toBe(id2);
      expect(result.current.toasts[0].id).toBe(id1);
      expect(result.current.toasts[1].id).toBe(id2);
    });

    it('should add multiple toasts', () => {
      const { result } = renderHook(() => useToast());

      act(() => {
        result.current.addToast('Toast 1');
        result.current.addToast('Toast 2');
        result.current.addToast('Toast 3');
      });

      expect(result.current.toasts).toHaveLength(3);
    });

    it('should use default duration of 5000ms', () => {
      const { result } = renderHook(() => useToast());

      act(() => {
        result.current.addToast('Test message');
      });

      expect(result.current.toasts[0].duration).toBe(5000);
    });
  });

  describe('removeToast', () => {
    it('should remove a toast by ID', () => {
      const { result } = renderHook(() => useToast());

      let toastId: string;

      act(() => {
        toastId = result.current.addToast('Test message');
      });

      expect(result.current.toasts).toHaveLength(1);

      act(() => {
        result.current.removeToast(toastId);
      });

      expect(result.current.toasts).toHaveLength(0);
    });

    it('should only remove the specified toast', () => {
      const { result } = renderHook(() => useToast());

      let id1: string;
      let id2: string;
      let id3: string;

      act(() => {
        id1 = result.current.addToast('Toast 1');
        id2 = result.current.addToast('Toast 2');
        id3 = result.current.addToast('Toast 3');
      });

      act(() => {
        result.current.removeToast(id2);
      });

      expect(result.current.toasts).toHaveLength(2);
      expect(result.current.toasts.map((t) => t.id)).toEqual([id1, id3]);
    });

    it('should handle removing non-existent toast gracefully', () => {
      const { result } = renderHook(() => useToast());

      act(() => {
        result.current.addToast('Test message');
      });

      act(() => {
        result.current.removeToast('non-existent-id');
      });

      expect(result.current.toasts).toHaveLength(1);
    });
  });

  describe('Shortcut methods', () => {
    it('should create success toast', () => {
      const { result } = renderHook(() => useToast());

      act(() => {
        result.current.success('Success!', 'Success Title');
      });

      expect(result.current.toasts[0].type).toBe('success');
      expect(result.current.toasts[0].message).toBe('Success!');
      expect(result.current.toasts[0].title).toBe('Success Title');
    });

    it('should create error toast', () => {
      const { result } = renderHook(() => useToast());

      act(() => {
        result.current.error('Error occurred', 'Error Title');
      });

      expect(result.current.toasts[0].type).toBe('error');
      expect(result.current.toasts[0].message).toBe('Error occurred');
      expect(result.current.toasts[0].title).toBe('Error Title');
    });

    it('should create warning toast', () => {
      const { result } = renderHook(() => useToast());

      act(() => {
        result.current.warning('Warning message', 'Warning Title');
      });

      expect(result.current.toasts[0].type).toBe('warning');
      expect(result.current.toasts[0].message).toBe('Warning message');
      expect(result.current.toasts[0].title).toBe('Warning Title');
    });

    it('should create info toast', () => {
      const { result } = renderHook(() => useToast());

      act(() => {
        result.current.info('Info message', 'Info Title');
      });

      expect(result.current.toasts[0].type).toBe('info');
      expect(result.current.toasts[0].message).toBe('Info message');
      expect(result.current.toasts[0].title).toBe('Info Title');
    });

    it('should work without title', () => {
      const { result } = renderHook(() => useToast());

      act(() => {
        result.current.success('Success!');
      });

      expect(result.current.toasts[0].title).toBeUndefined();
      expect(result.current.toasts[0].message).toBe('Success!');
    });
  });

  describe('Complex scenarios', () => {
    it('should handle multiple adds and removes', () => {
      const { result } = renderHook(() => useToast());

      let ids: string[] = [];

      act(() => {
        ids.push(result.current.success('Toast 1'));
        ids.push(result.current.error('Toast 2'));
        ids.push(result.current.warning('Toast 3'));
      });

      expect(result.current.toasts).toHaveLength(3);

      act(() => {
        result.current.removeToast(ids[1]);
      });

      expect(result.current.toasts).toHaveLength(2);
      expect(result.current.toasts.map((t) => t.message)).toEqual(['Toast 1', 'Toast 3']);

      act(() => {
        ids.push(result.current.info('Toast 4'));
      });

      expect(result.current.toasts).toHaveLength(3);
    });

    it('should preserve toast order', () => {
      const { result } = renderHook(() => useToast());

      act(() => {
        result.current.addToast('First');
        result.current.addToast('Second');
        result.current.addToast('Third');
      });

      const messages = result.current.toasts.map((t) => t.message);
      expect(messages).toEqual(['First', 'Second', 'Third']);
    });
  });
});
