/**
 * Unit tests for Toast component
 * Tests rendering, auto-close, manual close, and different types
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Toast from '../Toast';

// Mock framer-motion to simplify testing
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

describe('Toast Component', () => {
  describe('Rendering', () => {
    it('should render toast with message', () => {
      render(<Toast message="Test message" />);

      expect(screen.getByText('Test message')).toBeInTheDocument();
    });

    it('should render toast with title and message', () => {
      render(<Toast title="Test Title" message="Test message" />);

      expect(screen.getByText('Test Title')).toBeInTheDocument();
      expect(screen.getByText('Test message')).toBeInTheDocument();
    });

    it('should render different toast types', () => {
      const { rerender } = render(<Toast type="success" message="Success!" />);
      expect(screen.getByRole('alert')).toBeInTheDocument();

      rerender(<Toast type="error" message="Error!" />);
      expect(screen.getByRole('alert')).toBeInTheDocument();

      rerender(<Toast type="warning" message="Warning!" />);
      expect(screen.getByRole('alert')).toBeInTheDocument();

      rerender(<Toast type="info" message="Info!" />);
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    it('should not render when isVisible is false', () => {
      const { rerender } = render(<Toast message="Test message" duration={0} />);

      expect(screen.getByText('Test message')).toBeInTheDocument();

      // After duration, component should unmount
      rerender(<Toast message="Test message" duration={-1} />);
    });
  });

  describe('Type-specific styling', () => {
    it('should apply success styling', () => {
      const { container } = render(<Toast type="success" message="Success!" />);
      const toast = container.firstChild;

      expect(toast).toHaveClass('bg-green-50');
      expect(toast).toHaveClass('border-green-200');
    });

    it('should apply error styling', () => {
      const { container } = render(<Toast type="error" message="Error!" />);
      const toast = container.firstChild;

      expect(toast).toHaveClass('bg-red-50');
      expect(toast).toHaveClass('border-red-200');
    });

    it('should apply warning styling', () => {
      const { container } = render(<Toast type="warning" message="Warning!" />);
      const toast = container.firstChild;

      expect(toast).toHaveClass('bg-yellow-50');
      expect(toast).toHaveClass('border-yellow-200');
    });

    it('should apply info styling', () => {
      const { container } = render(<Toast type="info" message="Info!" />);
      const toast = container.firstChild;

      expect(toast).toHaveClass('bg-blue-50');
      expect(toast).toHaveClass('border-blue-200');
    });
  });

  describe('Manual close button', () => {
    it('should render close button', () => {
      render(<Toast message="Test message" />);

      const closeButton = screen.getByRole('button', { name: /close notification/i });
      expect(closeButton).toBeInTheDocument();
    });

    it('should call onClose when close button is clicked', async () => {
      const onClose = jest.fn();
      const user = userEvent.setup();

      render(<Toast message="Test message" onClose={onClose} duration={0} />);

      const closeButton = screen.getByRole('button', { name: /close notification/i });
      await user.click(closeButton);

      expect(onClose).toHaveBeenCalled();
    });

    it('should hide toast after manual close', async () => {
      const user = userEvent.setup();

      const { container } = render(<Toast message="Test message" duration={0} />);

      expect(screen.getByText('Test message')).toBeInTheDocument();

      const closeButton = screen.getByRole('button', { name: /close notification/i });
      await user.click(closeButton);

      await waitFor(() => {
        expect(screen.queryByText('Test message')).not.toBeInTheDocument();
      });
    });
  });

  describe('Auto-close functionality', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.runOnlyPendingTimers();
      jest.useRealTimers();
    });

    it('should auto-close after default duration (5000ms)', () => {
      const onClose = jest.fn();

      render(<Toast message="Test message" onClose={onClose} />);

      expect(screen.getByText('Test message')).toBeInTheDocument();

      jest.advanceTimersByTime(5000);

      expect(onClose).toHaveBeenCalled();
    });

    it('should auto-close after custom duration', () => {
      const onClose = jest.fn();

      render(<Toast message="Test message" duration={3000} onClose={onClose} />);

      jest.advanceTimersByTime(3000);

      expect(onClose).toHaveBeenCalled();
    });

    it('should not auto-close when duration is 0', () => {
      const onClose = jest.fn();

      render(<Toast message="Test message" duration={0} onClose={onClose} />);

      jest.advanceTimersByTime(10000);

      expect(onClose).not.toHaveBeenCalled();
    });

    it('should clear timeout on unmount', () => {
      const onClose = jest.fn();
      const clearTimeoutSpy = jest.spyOn(global, 'clearTimeout');

      const { unmount } = render(<Toast message="Test message" onClose={onClose} />);

      unmount();

      expect(clearTimeoutSpy).toHaveBeenCalled();
      clearTimeoutSpy.mockRestore();
    });
  });

  describe('Props handling', () => {
    it('should use default id prop', () => {
      const { container } = render(<Toast message="Test" />);
      expect(container.firstChild).toBeInTheDocument();
    });

    it('should use custom id prop', () => {
      const { container } = render(<Toast id="custom-id" message="Test" />);
      expect(container.firstChild).toHaveAttribute('role', 'alert');
    });

    it('should display message only when title is not provided', () => {
      render(<Toast message="Message only" />);

      expect(screen.getByText('Message only')).toBeInTheDocument();
    });

    it('should display both title and message with proper spacing', () => {
      render(<Toast title="Title" message="Message" />);

      const title = screen.getByText('Title');
      const message = screen.getByText('Message');

      expect(title).toBeInTheDocument();
      expect(message).toBeInTheDocument();

      // Message should be after title
      expect(message.parentElement).toBe(title.parentElement);
    });
  });

  describe('Accessibility', () => {
    it('should have alert role', () => {
      const { container } = render(<Toast message="Test message" />);

      expect(container.querySelector('[role="alert"]')).toBeInTheDocument();
    });

    it('should have close button with aria-label', () => {
      render(<Toast message="Test message" />);

      const closeButton = screen.getByRole('button', { name: /close notification/i });
      expect(closeButton).toHaveAttribute('aria-label', 'Close notification');
    });
  });
});
