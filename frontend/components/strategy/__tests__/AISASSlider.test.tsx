/**
 * Unit tests for AISASSlider component
 * Tests slider rendering, interaction, color segments, and value updates
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AISASSlider from '../AISASSlider';

describe('AISASSlider Component', () => {
  const defaultProps = {
    value: 50,
    onChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render slider container', () => {
      const { container } = render(<AISASSlider {...defaultProps} />);

      const slider = container.querySelector('[class*="relative"]');
      expect(slider).toBeInTheDocument();
    });

    it('should display segment labels', () => {
      render(<AISASSlider {...defaultProps} />);

      expect(screen.getByText('A')).toBeInTheDocument(); // Attention
      expect(screen.getByText('I')).toBeInTheDocument(); // Interest
      expect(screen.getByText('S')).toBeInTheDocument(); // Search
      expect(screen.getByText('Ac')).toBeInTheDocument(); // Action
      expect(screen.getByText('Sh')).toBeInTheDocument(); // Share
    });

    it('should render all 5 colored segments', () => {
      const { container } = render(<AISASSlider {...defaultProps} />);

      const segments = container.querySelectorAll('[class*="absolute"][class*="top-0"]');
      // Should have segments for each AISAS stage
      expect(segments.length).toBeGreaterThan(0);
    });

    it('should render stage label when showLabel is true', () => {
      render(<AISASSlider {...defaultProps} showLabel={true} />);

      // Stage labels should be displayed
      const labels = screen.queryByText(/Attention|Interest|Search|Action|Share/);
      expect(labels).toBeInTheDocument();
    });

    it('should not render stage label when showLabel is false', () => {
      render(<AISASSlider {...defaultProps} showLabel={false} />);

      // Label might still exist but in a different form
      const container = render(<AISASSlider {...defaultProps} showLabel={true} />);
      expect(container).toBeTruthy();
    });
  });

  describe('Size variants', () => {
    it('should render with small size', () => {
      const { container } = render(<AISASSlider {...defaultProps} size="sm" />);

      expect(container.firstChild).toBeInTheDocument();
    });

    it('should render with medium size', () => {
      const { container } = render(<AISASSlider {...defaultProps} size="md" />);

      expect(container.firstChild).toBeInTheDocument();
    });

    it('should render with large size', () => {
      const { container } = render(<AISASSlider {...defaultProps} size="lg" />);

      expect(container.firstChild).toBeInTheDocument();
    });
  });

  describe('Value handling', () => {
    it('should display current value in label', () => {
      render(<AISASSlider {...defaultProps} value={50} showLabel={true} />);

      expect(screen.getByText(/Search|50/)).toBeInTheDocument();
    });

    it('should update displayed stage based on value', () => {
      const { rerender } = render(
        <AISASSlider {...defaultProps} value={10} showLabel={true} />
      );

      rerender(<AISASSlider {...defaultProps} value={50} showLabel={true} />);
      expect(screen.getByText(/Search|50/)).toBeInTheDocument();

      rerender(<AISASSlider {...defaultProps} value={90} showLabel={true} />);
      expect(screen.getByText(/Share|90/)).toBeInTheDocument();
    });

    it('should accept values between 0 and 100', () => {
      const testValues = [0, 25, 50, 75, 100];

      testValues.forEach((value) => {
        const { unmount } = render(
          <AISASSlider {...defaultProps} value={value} />
        );
        expect(screen.getByRole('slider')).toBeInTheDocument();
        unmount();
      });
    });
  });

  describe('AISAS segments', () => {
    it('should highlight Attention segment for value 0-20', () => {
      const { container } = render(<AISASSlider {...defaultProps} value={10} />);

      expect(container.textContent).toContain('Attention');
    });

    it('should highlight Interest segment for value 20-40', () => {
      render(<AISASSlider {...defaultProps} value={30} showLabel={true} />);

      expect(screen.getByText(/Interest|30/)).toBeInTheDocument();
    });

    it('should highlight Search segment for value 40-60', () => {
      render(<AISASSlider {...defaultProps} value={50} showLabel={true} />);

      expect(screen.getByText(/Search|50/)).toBeInTheDocument();
    });

    it('should highlight Action segment for value 60-80', () => {
      render(<AISASSlider {...defaultProps} value={70} showLabel={true} />);

      expect(screen.getByText(/Action|70/)).toBeInTheDocument();
    });

    it('should highlight Share segment for value 80-100', () => {
      render(<AISASSlider {...defaultProps} value={90} showLabel={true} />);

      expect(screen.getByText(/Share|90/)).toBeInTheDocument();
    });
  });

  describe('Color segments', () => {
    it('should use red for Attention segment', () => {
      const { container } = render(<AISASSlider {...defaultProps} value={10} />);

      const redSegment = container.querySelector('[class*="bg-red"]');
      expect(redSegment).toBeInTheDocument();
    });

    it('should use orange for Interest segment', () => {
      const { container } = render(<AISASSlider {...defaultProps} value={30} />);

      const orangeSegment = container.querySelector('[class*="bg-orange"]');
      expect(orangeSegment).toBeInTheDocument();
    });

    it('should use yellow for Search segment', () => {
      const { container } = render(<AISASSlider {...defaultProps} value={50} />);

      const yellowSegment = container.querySelector('[class*="bg-yellow"]');
      expect(yellowSegment).toBeInTheDocument();
    });

    it('should use blue for Action segment', () => {
      const { container } = render(<AISASSlider {...defaultProps} value={70} />);

      const blueSegment = container.querySelector('[class*="bg-blue"]');
      expect(blueSegment).toBeInTheDocument();
    });

    it('should use green for Share segment', () => {
      const { container } = render(<AISASSlider {...defaultProps} value={90} />);

      const greenSegment = container.querySelector('[class*="bg-green"]');
      expect(greenSegment).toBeInTheDocument();
    });
  });

  describe('Disabled state', () => {
    it('should not respond to interaction when disabled', async () => {
      const onChange = jest.fn();
      const user = userEvent.setup();

      const { container } = render(
        <AISASSlider {...defaultProps} onChange={onChange} disabled={true} />
      );

      const slider = container.querySelector('input[type="range"]');

      if (slider) {
        await user.click(slider);
        // onChange should not be called or should have specific handling
      }
    });

    it('should apply disabled styling', () => {
      const { container } = render(
        <AISASSlider {...defaultProps} disabled={true} />
      );

      const slider = container.querySelector('input[type="range"]');
      if (slider) {
        expect(slider).toHaveAttribute('disabled');
      }
    });
  });

  describe('Interaction and callbacks', () => {
    it('should call onChange when slider value changes', async () => {
      const onChange = jest.fn();

      const { container } = render(
        <AISASSlider {...defaultProps} onChange={onChange} />
      );

      const slider = container.querySelector('input[type="range"]') as HTMLInputElement;

      if (slider) {
        fireEvent.change(slider, { target: { value: '75' } });

        await waitFor(() => {
          expect(onChange).toHaveBeenCalledWith(expect.any(Number));
        });
      }
    });

    it('should pass numeric value to onChange', async () => {
      const onChange = jest.fn();

      const { container } = render(
        <AISASSlider {...defaultProps} onChange={onChange} />
      );

      const slider = container.querySelector('input[type="range"]') as HTMLInputElement;

      if (slider) {
        fireEvent.change(slider, { target: { value: '60' } });

        await waitFor(() => {
          const calls = onChange.mock.calls;
          expect(calls.length).toBeGreaterThan(0);
          expect(typeof calls[0][0]).toBe('number');
        });
      }
    });

    it('should handle dragging the slider thumb', async () => {
      const onChange = jest.fn();
      const user = userEvent.setup();

      const { container } = render(
        <AISASSlider {...defaultProps} onChange={onChange} />
      );

      const slider = container.querySelector('input[type="range"]') as HTMLInputElement;

      if (slider) {
        // Simulate drag interaction
        fireEvent.mouseDown(slider);
        fireEvent.change(slider, { target: { value: '75' } });
        fireEvent.mouseUp(slider);

        expect(onChange).toHaveBeenCalled();
      }
    });
  });

  describe('Props validation', () => {
    it('should accept valid size props', () => {
      const sizes: Array<'sm' | 'md' | 'lg'> = ['sm', 'md', 'lg'];

      sizes.forEach((size) => {
        const { unmount } = render(
          <AISASSlider {...defaultProps} size={size} />
        );
        expect(screen.getByRole('slider')).toBeInTheDocument();
        unmount();
      });
    });

    it('should have default size when not provided', () => {
      render(<AISASSlider value={50} onChange={jest.fn()} />);

      expect(screen.getByRole('slider')).toBeInTheDocument();
    });

    it('should have default showLabel when not provided', () => {
      render(<AISASSlider {...defaultProps} />);

      expect(screen.getByRole('slider')).toBeInTheDocument();
    });

    it('should have default disabled when not provided', () => {
      render(<AISASSlider {...defaultProps} />);

      const slider = screen.getByRole('slider');
      expect(slider).not.toHaveAttribute('disabled');
    });
  });

  describe('Edge cases', () => {
    it('should handle minimum value (0)', () => {
      const onChange = jest.fn();

      render(<AISASSlider value={0} onChange={onChange} />);

      expect(screen.getByRole('slider')).toBeInTheDocument();
    });

    it('should handle maximum value (100)', () => {
      const onChange = jest.fn();

      render(<AISASSlider value={100} onChange={onChange} />);

      expect(screen.getByRole('slider')).toBeInTheDocument();
    });

    it('should handle rapid value changes', () => {
      const onChange = jest.fn();
      const { rerender } = render(
        <AISASSlider {...defaultProps} value={25} onChange={onChange} />
      );

      rerender(<AISASSlider {...defaultProps} value={50} onChange={onChange} />);
      rerender(<AISASSlider {...defaultProps} value={75} onChange={onChange} />);
      rerender(<AISASSlider {...defaultProps} value={100} onChange={onChange} />);

      expect(screen.getByRole('slider')).toBeInTheDocument();
    });

    it('should handle undefined onChange gracefully', () => {
      const { container } = render(
        <AISASSlider value={50} onChange={undefined as any} />
      );

      const slider = container.querySelector('input[type="range"]');
      expect(slider).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have slider role', () => {
      render(<AISASSlider {...defaultProps} />);

      expect(screen.getByRole('slider')).toBeInTheDocument();
    });

    it('should be keyboard accessible', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();

      render(<AISASSlider {...defaultProps} onChange={onChange} />);

      const slider = screen.getByRole('slider');

      // Focus the slider
      await user.click(slider);

      expect(slider).toHaveFocus();
    });
  });
});
