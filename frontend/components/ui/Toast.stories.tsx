/**
 * Toast Notification Component Stories
 * Demonstrates all variants and configurations of the Toast component
 */

import type { Meta, StoryObj } from '@storybook/react';
import Toast from './Toast';

const meta = {
  title: 'UI/Toast',
  component: Toast,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Toast notifications for displaying temporary messages. Supports 4 types: success, error, warning, and info.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    type: {
      control: 'select',
      options: ['success', 'error', 'warning', 'info'],
      description: 'Type of notification to display',
    },
    message: {
      control: 'text',
      description: 'Main message to display',
    },
    title: {
      control: 'text',
      description: 'Optional title for the notification',
    },
    duration: {
      control: 'number',
      description: 'Duration in milliseconds (0 = never auto-close)',
    },
    onClose: {
      action: 'onClose',
      description: 'Callback when toast closes',
    },
  },
} satisfies Meta<typeof Toast>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Success Toast - Green styling for successful operations
 */
export const Success: Story = {
  args: {
    type: 'success',
    message: 'Changes saved successfully!',
    title: 'Success',
    duration: 5000,
  },
};

/**
 * Error Toast - Red styling for error messages
 */
export const Error: Story = {
  args: {
    type: 'error',
    message: 'Failed to save changes. Please try again.',
    title: 'Error',
    duration: 5000,
  },
};

/**
 * Warning Toast - Yellow styling for warnings
 */
export const Warning: Story = {
  args: {
    type: 'warning',
    message: 'This action cannot be undone.',
    title: 'Warning',
    duration: 5000,
  },
};

/**
 * Info Toast - Blue styling for information
 */
export const Info: Story = {
  args: {
    type: 'info',
    message: 'New features are available. Please refresh to see updates.',
    title: 'Info',
    duration: 5000,
  },
};

/**
 * Message Only - Toast without a title
 */
export const MessageOnly: Story = {
  args: {
    type: 'success',
    message: 'Operation completed!',
    duration: 5000,
  },
};

/**
 * Long Duration - Toast that stays longer
 */
export const LongDuration: Story = {
  args: {
    type: 'info',
    message: 'Important message',
    title: 'Please Read',
    duration: 10000,
  },
};

/**
 * No Auto-Close - Toast that requires manual dismissal
 */
export const NoAutoClose: Story = {
  args: {
    type: 'warning',
    message: 'Critical action required',
    title: 'Action Required',
    duration: 0,
  },
};

/**
 * Long Message - Toast with extended content
 */
export const LongMessage: Story = {
  args: {
    type: 'info',
    title: 'Download Complete',
    message:
      'Your file has been successfully downloaded and is ready for use. You can find it in your Downloads folder.',
    duration: 5000,
  },
};

/**
 * All Types Comparison - Shows all 4 types side by side
 */
export const AllTypes: Story = {
  render: () => (
    <div className="space-y-4 max-w-md">
      <Toast
        type="success"
        title="Success"
        message="Operation completed successfully!"
        duration={0}
      />
      <Toast
        type="error"
        title="Error"
        message="Something went wrong. Please try again."
        duration={0}
      />
      <Toast
        type="warning"
        title="Warning"
        message="Please verify your action before proceeding."
        duration={0}
      />
      <Toast
        type="info"
        title="Info"
        message="New updates are available."
        duration={0}
      />
    </div>
  ),
};

/**
 * Different Durations - Shows various auto-close timings
 */
export const DifferentDurations: Story = {
  render: () => (
    <div className="space-y-4 max-w-md">
      <Toast
        type="success"
        title="3 seconds"
        message="This will close in 3 seconds"
        duration={3000}
      />
      <Toast
        type="success"
        title="5 seconds"
        message="This will close in 5 seconds (default)"
        duration={5000}
      />
      <Toast
        type="success"
        title="10 seconds"
        message="This will close in 10 seconds"
        duration={10000}
      />
    </div>
  ),
};

/**
 * With Special Characters - Shows handling of special content
 */
export const SpecialCharacters: Story = {
  args: {
    type: 'info',
    title: 'Special: @#$% & "Quotes"',
    message: 'Content with special characters: <script> & symbols ©®™',
    duration: 0,
  },
};
