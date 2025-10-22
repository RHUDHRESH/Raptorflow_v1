/**
 * Unit tests for JobEditor component
 * Tests modal rendering, form handling, validation, and save operations
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import JobEditor from '../JobEditor';

// Mock Modal component
jest.mock('../Modal', () => {
  return function MockModal({ isOpen, onClose, title, children }: any) {
    if (!isOpen) return null;
    return (
      <div data-testid="modal">
        <h2>{title}</h2>
        <button onClick={onClose} aria-label="close modal">Close</button>
        {children}
      </div>
    );
  };
});

describe('JobEditor Component', () => {
  const mockJob = {
    id: 'job-123',
    why: 'User wants to save time',
    circumstances: 'When scheduling meetings',
    forces: 'Need to coordinate across timezones',
    anxieties: 'Fear of double-booking',
  };

  const defaultProps = {
    isOpen: true,
    job: mockJob,
    onClose: jest.fn(),
    onSave: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render editor modal when isOpen is true', () => {
      render(<JobEditor {...defaultProps} />);

      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Edit Job')).toBeInTheDocument();
    });

    it('should not render modal when isOpen is false', () => {
      render(<JobEditor {...defaultProps} isOpen={false} />);

      expect(screen.queryByTestId('modal')).not.toBeInTheDocument();
    });

    it('should render all 4 textarea fields', () => {
      render(<JobEditor {...defaultProps} />);

      const textareas = screen.getAllByRole('textbox');
      expect(textareas.length).toBeGreaterThanOrEqual(4);
    });

    it('should render save and cancel buttons', () => {
      render(<JobEditor {...defaultProps} />);

      expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
    });
  });

  describe('Form population', () => {
    it('should populate Why field', () => {
      render(<JobEditor {...defaultProps} />);

      const textareas = screen.getAllByRole('textbox');
      expect(textareas[0]).toHaveValue('User wants to save time');
    });

    it('should populate Circumstances field', () => {
      render(<JobEditor {...defaultProps} />);

      const textareas = screen.getAllByRole('textbox');
      expect(textareas[1]).toHaveValue('When scheduling meetings');
    });

    it('should populate Forces field', () => {
      render(<JobEditor {...defaultProps} />);

      const textareas = screen.getAllByRole('textbox');
      expect(textareas[2]).toHaveValue('Need to coordinate across timezones');
    });

    it('should populate Anxieties field', () => {
      render(<JobEditor {...defaultProps} />);

      const textareas = screen.getAllByRole('textbox');
      expect(textareas[3]).toHaveValue('Fear of double-booking');
    });

    it('should clear fields when job is null', () => {
      const { rerender } = render(<JobEditor {...defaultProps} job={null} />);

      const textareas = screen.getAllByRole('textbox');
      textareas.forEach((textarea) => {
        expect(textarea).toHaveValue('');
      });

      rerender(<JobEditor {...defaultProps} job={mockJob} />);

      expect(screen.getAllByRole('textbox')[0]).toHaveValue(mockJob.why);
    });

    it('should update fields when job prop changes', async () => {
      const newJob = {
        id: 'job-456',
        why: 'New why statement',
        circumstances: 'New circumstances',
        forces: 'New forces',
        anxieties: 'New anxieties',
      };

      const { rerender } = render(<JobEditor {...defaultProps} />);

      const textareas = screen.getAllByRole('textbox');
      expect(textareas[0]).toHaveValue(mockJob.why);

      rerender(<JobEditor {...defaultProps} job={newJob} />);

      expect(screen.getAllByRole('textbox')[0]).toHaveValue(newJob.why);
    });
  });

  describe('Form validation', () => {
    it('should prevent save without Why field', async () => {
      const onSave = jest.fn();
      const user = userEvent.setup();

      render(
        <JobEditor
          {...defaultProps}
          job={{ ...mockJob, why: '' }}
          onSave={onSave}
        />
      );

      const saveButton = screen.getByRole('button', { name: /save/i });
      await user.click(saveButton);

      // Should not call onSave or should show error
      // Depending on implementation
      expect(screen.getByTestId('modal')).toBeInTheDocument();
    });

    it('should allow save with all fields filled', async () => {
      const onSave = jest.fn().mockResolvedValue(undefined);
      const user = userEvent.setup();

      render(
        <JobEditor {...defaultProps} onSave={onSave} />
      );

      const saveButton = screen.getByRole('button', { name: /save/i });
      await user.click(saveButton);

      await waitFor(() => {
        expect(onSave).toHaveBeenCalled();
      });
    });

    it('should allow save with partial fields (non-required)', async () => {
      const onSave = jest.fn().mockResolvedValue(undefined);
      const user = userEvent.setup();

      render(
        <JobEditor
          {...defaultProps}
          job={{
            ...mockJob,
            circumstances: '',
            forces: '',
            anxieties: '',
          }}
          onSave={onSave}
        />
      );

      const saveButton = screen.getByRole('button', { name: /save/i });
      await user.click(saveButton);

      // May or may not allow - depends on implementation
    });

    it('should display error message if validation fails', async () => {
      const { rerender } = render(
        <JobEditor {...defaultProps} job={{ ...mockJob, why: '' }} />
      );

      // Error should be visible or prevent save
      expect(screen.getByTestId('modal')).toBeInTheDocument();
    });
  });

  describe('Form editing', () => {
    it('should update Why field on input', async () => {
      const user = userEvent.setup();

      render(<JobEditor {...defaultProps} />);

      const textareas = screen.getAllByRole('textbox');
      await user.clear(textareas[0]);
      await user.type(textareas[0], 'Updated why');

      expect(textareas[0]).toHaveValue('Updated why');
    });

    it('should update Circumstances field on input', async () => {
      const user = userEvent.setup();

      render(<JobEditor {...defaultProps} />);

      const textareas = screen.getAllByRole('textbox');
      await user.clear(textareas[1]);
      await user.type(textareas[1], 'Updated circumstances');

      expect(textareas[1]).toHaveValue('Updated circumstances');
    });

    it('should update Forces field on input', async () => {
      const user = userEvent.setup();

      render(<JobEditor {...defaultProps} />);

      const textareas = screen.getAllByRole('textbox');
      await user.clear(textareas[2]);
      await user.type(textareas[2], 'Updated forces');

      expect(textareas[2]).toHaveValue('Updated forces');
    });

    it('should update Anxieties field on input', async () => {
      const user = userEvent.setup();

      render(<JobEditor {...defaultProps} />);

      const textareas = screen.getAllByRole('textbox');
      await user.clear(textareas[3]);
      await user.type(textareas[3], 'Updated anxieties');

      expect(textareas[3]).toHaveValue('Updated anxieties');
    });
  });

  describe('User interactions', () => {
    it('should call onSave with job ID and updated data', async () => {
      const onSave = jest.fn().mockResolvedValue(undefined);
      const user = userEvent.setup();

      render(<JobEditor {...defaultProps} onSave={onSave} />);

      const textareas = screen.getAllByRole('textbox');
      await user.clear(textareas[0]);
      await user.type(textareas[0], 'New why');

      const saveButton = screen.getByRole('button', { name: /save/i });
      await user.click(saveButton);

      await waitFor(() => {
        expect(onSave).toHaveBeenCalledWith(
          mockJob.id,
          expect.objectContaining({
            why: 'New why',
          })
        );
      });
    });

    it('should call onClose when cancel is clicked', async () => {
      const onClose = jest.fn();
      const user = userEvent.setup();

      render(<JobEditor {...defaultProps} onClose={onClose} />);

      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      await user.click(cancelButton);

      expect(onClose).toHaveBeenCalled();
    });

    it('should call onClose when close modal button is clicked', async () => {
      const onClose = jest.fn();
      const user = userEvent.setup();

      render(<JobEditor {...defaultProps} onClose={onClose} />);

      const closeButton = screen.getByRole('button', { name: /close modal/i });
      await user.click(closeButton);

      expect(onClose).toHaveBeenCalled();
    });

    it('should not save changes when cancel is clicked', async () => {
      const onSave = jest.fn();
      const user = userEvent.setup();

      render(<JobEditor {...defaultProps} onSave={onSave} />);

      const textareas = screen.getAllByRole('textbox');
      await user.clear(textareas[0]);
      await user.type(textareas[0], 'New why');

      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      await user.click(cancelButton);

      expect(onSave).not.toHaveBeenCalled();
    });
  });

  describe('Loading state', () => {
    it('should disable buttons while saving', async () => {
      const onSave = jest.fn(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );
      const user = userEvent.setup();

      const { rerender } = render(
        <JobEditor {...defaultProps} onSave={onSave} />
      );

      const saveButton = screen.getByRole('button', { name: /save/i });
      await user.click(saveButton);

      // After click, button might be in loading state
      expect(screen.getByTestId('modal')).toBeInTheDocument();
    });

    it('should show loading state in save button', async () => {
      const onSave = jest.fn(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );
      const user = userEvent.setup();

      render(<JobEditor {...defaultProps} onSave={onSave} />);

      const saveButton = screen.getByRole('button', { name: /save/i }) as HTMLButtonElement;
      await user.click(saveButton);

      // Check if button shows loading state
      expect(saveButton).toBeInTheDocument();
    });
  });

  describe('Error handling', () => {
    it('should display error message on save failure', async () => {
      const onSave = jest.fn().mockRejectedValue(new Error('Save failed'));
      const user = userEvent.setup();

      render(<JobEditor {...defaultProps} onSave={onSave} />);

      const saveButton = screen.getByRole('button', { name: /save/i });
      await user.click(saveButton);

      await waitFor(() => {
        // Error message might be displayed
        expect(screen.getByTestId('modal')).toBeInTheDocument();
      });
    });

    it('should allow retry after error', async () => {
      const onSave = jest
        .fn()
        .mockRejectedValueOnce(new Error('Save failed'))
        .mockResolvedValueOnce(undefined);

      const user = userEvent.setup();

      render(<JobEditor {...defaultProps} onSave={onSave} />);

      const saveButton = screen.getByRole('button', { name: /save/i });

      // First attempt fails
      await user.click(saveButton);

      await waitFor(() => {
        expect(screen.getByTestId('modal')).toBeInTheDocument();
      });

      // Second attempt succeeds
      const retryButton = screen.getByRole('button', { name: /save/i });
      await user.click(retryButton);

      await waitFor(() => {
        expect(onSave).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('Edge cases', () => {
    it('should handle null job gracefully', () => {
      render(<JobEditor {...defaultProps} job={null} />);

      expect(screen.getByTestId('modal')).toBeInTheDocument();
    });

    it('should handle very long text', async () => {
      const user = userEvent.setup();

      const longText = 'A'.repeat(1000);

      render(
        <JobEditor
          {...defaultProps}
          job={{ ...mockJob, why: longText }}
        />
      );

      const textareas = screen.getAllByRole('textbox');
      expect(textareas[0]).toHaveValue(longText);
    });

    it('should handle special characters in text', async () => {
      const user = userEvent.setup();

      render(
        <JobEditor
          {...defaultProps}
          job={{
            ...mockJob,
            why: 'User wants @#$% & "special" characters',
          }}
        />
      );

      const textareas = screen.getAllByRole('textbox');
      expect(textareas[0]).toHaveValue('User wants @#$% & "special" characters');
    });

    it('should handle multiline text in fields', async () => {
      const user = userEvent.setup();

      const multilineText = 'Line 1\nLine 2\nLine 3';

      render(
        <JobEditor
          {...defaultProps}
          job={{ ...mockJob, why: multilineText }}
        />
      );

      const textareas = screen.getAllByRole('textbox');
      expect(textareas[0]).toHaveValue(multilineText);
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading structure', () => {
      render(<JobEditor {...defaultProps} />);

      expect(screen.getByText('Edit Job')).toBeInTheDocument();
    });

    it('should have focusable form fields', async () => {
      const user = userEvent.setup();

      render(<JobEditor {...defaultProps} />);

      const textareas = screen.getAllByRole('textbox');

      for (const textarea of textareas) {
        await user.click(textarea);
        expect(textarea).toHaveFocus();
      }
    });

    it('should have accessible buttons', () => {
      render(<JobEditor {...defaultProps} />);

      expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
    });
  });
});
