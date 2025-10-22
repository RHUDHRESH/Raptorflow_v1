/**
 * Confirmation Dialog Component Stories
 * Demonstrates all variants and configurations of the ConfirmationDialog component
 */

import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';
import ConfirmationDialog from './ConfirmationDialog';

const meta = {
  title: 'UI/ConfirmationDialog',
  component: ConfirmationDialog,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Modal dialog for confirming potentially destructive or important actions. Supports 3 types: danger, warning, and info.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    isOpen: {
      control: 'boolean',
      description: 'Whether the dialog is visible',
    },
    type: {
      control: 'select',
      options: ['danger', 'warning', 'info'],
      description: 'Type of confirmation dialog',
    },
    title: {
      control: 'text',
      description: 'Dialog title',
    },
    message: {
      control: 'text',
      description: 'Confirmation message',
    },
    confirmText: {
      control: 'text',
      description: 'Text for confirm button',
    },
    cancelText: {
      control: 'text',
      description: 'Text for cancel button',
    },
    loading: {
      control: 'boolean',
      description: 'Whether the dialog is in loading state',
    },
    onConfirm: {
      action: 'onConfirm',
      description: 'Callback when user confirms',
    },
    onCancel: {
      action: 'onCancel',
      description: 'Callback when user cancels',
    },
  },
} satisfies Meta<typeof ConfirmationDialog>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Danger Dialog - Red styling for destructive actions
 */
export const DangerDialog: Story = {
  args: {
    isOpen: true,
    type: 'danger',
    title: 'Delete Job?',
    message: 'This action cannot be undone. All associated data will be permanently deleted.',
    confirmText: 'Delete',
    cancelText: 'Cancel',
    loading: false,
    onConfirm: () => console.log('Confirmed delete'),
    onCancel: () => console.log('Cancelled'),
  },
};

/**
 * Warning Dialog - Yellow styling for cautionary actions
 */
export const WarningDialog: Story = {
  args: {
    isOpen: true,
    type: 'warning',
    title: 'Overwrite Analysis?',
    message: 'Running a new analysis will overwrite your current results. Do you want to continue?',
    confirmText: 'Overwrite',
    cancelText: 'Keep Current',
    loading: false,
    onConfirm: () => console.log('Confirmed overwrite'),
    onCancel: () => console.log('Cancelled'),
  },
};

/**
 * Info Dialog - Blue styling for informational confirmations
 */
export const InfoDialog: Story = {
  args: {
    isOpen: true,
    type: 'info',
    title: 'Save Changes?',
    message: 'You have unsaved changes. Would you like to save them before leaving?',
    confirmText: 'Save',
    cancelText: 'Discard',
    loading: false,
    onConfirm: () => console.log('Confirmed save'),
    onCancel: () => console.log('Cancelled'),
  },
};

/**
 * Loading State - Shows confirm button while processing
 */
export const LoadingState: Story = {
  args: {
    isOpen: true,
    type: 'danger',
    title: 'Delete Job?',
    message: 'This action cannot be undone. All associated data will be permanently deleted.',
    confirmText: 'Delete',
    cancelText: 'Cancel',
    loading: true,
    onConfirm: () => console.log('Confirmed'),
    onCancel: () => console.log('Cancelled'),
  },
};

/**
 * Custom Button Text - Shows custom button labels
 */
export const CustomButtonText: Story = {
  args: {
    isOpen: true,
    type: 'warning',
    title: 'Archive Project?',
    message: 'This project will be moved to archive and can be restored later.',
    confirmText: 'Archive It',
    cancelText: 'Keep Active',
    loading: false,
    onConfirm: () => console.log('Confirmed'),
    onCancel: () => console.log('Cancelled'),
  },
};

/**
 * Long Message - Shows dialog with extended content
 */
export const LongMessage: Story = {
  args: {
    isOpen: true,
    type: 'info',
    title: 'Important Notice',
    message:
      'This operation will permanently merge the selected items into a single record. ' +
      'All individual records will be consolidated, and you will not be able to separate them again. ' +
      'This action is irreversible and affects all related data and analytics.',
    confirmText: 'Proceed',
    cancelText: 'Cancel',
    loading: false,
    onConfirm: () => console.log('Confirmed'),
    onCancel: () => console.log('Cancelled'),
  },
};

/**
 * All Types - Shows all 3 dialog types
 */
export const AllTypes: Story = {
  render: () => (
    <div className="space-y-8 max-w-2xl">
      <div>
        <h3 className="mb-4 text-lg font-semibold">Danger Dialog</h3>
        <ConfirmationDialog
          isOpen={true}
          type="danger"
          title="Delete Forever?"
          message="This cannot be undone."
          confirmText="Delete"
          cancelText="Cancel"
          loading={false}
          onConfirm={() => {}}
          onCancel={() => {}}
        />
      </div>
      <div>
        <h3 className="mb-4 text-lg font-semibold">Warning Dialog</h3>
        <ConfirmationDialog
          isOpen={true}
          type="warning"
          title="Are You Sure?"
          message="This action will have consequences."
          confirmText="Proceed"
          cancelText="Cancel"
          loading={false}
          onConfirm={() => {}}
          onCancel={() => {}}
        />
      </div>
      <div>
        <h3 className="mb-4 text-lg font-semibold">Info Dialog</h3>
        <ConfirmationDialog
          isOpen={true}
          type="info"
          title="Just Checking"
          message="Do you want to continue with this action?"
          confirmText="Yes"
          cancelText="No"
          loading={false}
          onConfirm={() => {}}
          onCancel={() => {}}
        />
      </div>
    </div>
  ),
};

/**
 * Closed State - Dialog is hidden
 */
export const ClosedState: Story = {
  args: {
    isOpen: false,
    type: 'danger',
    title: 'Delete?',
    message: 'Are you sure?',
    confirmText: 'Delete',
    cancelText: 'Cancel',
    loading: false,
    onConfirm: () => {},
    onCancel: () => {},
  },
};

/**
 * Interactive - Shows open/close toggle
 */
export const Interactive: Story = {
  render: () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [isOpen, setIsOpen] = useState(false);
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [isLoading, setIsLoading] = useState(false);

    const handleConfirm = async () => {
      setIsLoading(true);
      // Simulate async operation
      await new Promise((resolve) => setTimeout(resolve, 2000));
      setIsLoading(false);
      setIsOpen(false);
    };

    return (
      <div className="space-y-4">
        <button
          onClick={() => setIsOpen(true)}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Open Danger Dialog
        </button>

        <ConfirmationDialog
          isOpen={isOpen}
          type="danger"
          title="Delete This Item?"
          message="This action cannot be undone. The item will be permanently deleted from the system."
          confirmText="Delete"
          cancelText="Cancel"
          loading={isLoading}
          onConfirm={handleConfirm}
          onCancel={() => setIsOpen(false)}
        />
      </div>
    );
  },
};

/**
 * Merge Items Example - Realistic use case
 */
export const MergeItemsExample: Story = {
  args: {
    isOpen: true,
    type: 'warning',
    title: 'Merge 3 Jobs?',
    message:
      'You are about to merge "User wants to save time" with 2 other job statements. ' +
      'The merged job will combine all related context and insights. This action is reversible.',
    confirmText: 'Merge Jobs',
    cancelText: 'Keep Separate',
    loading: false,
    onConfirm: () => console.log('Merged'),
    onCancel: () => console.log('Cancelled'),
  },
};

/**
 * Archive Project Example - Another realistic use case
 */
export const ArchiveProjectExample: Story = {
  args: {
    isOpen: true,
    type: 'info',
    title: 'Archive "Q4 Product Strategy"?',
    message:
      'This project will be moved to your archive and will not appear in the active projects list. ' +
      'You can restore it at any time from the archive.',
    confirmText: 'Archive Project',
    cancelText: 'Keep Active',
    loading: false,
    onConfirm: () => console.log('Archived'),
    onCancel: () => console.log('Cancelled'),
  },
};
