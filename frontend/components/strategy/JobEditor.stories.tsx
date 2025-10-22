/**
 * JobEditor Modal Component Stories
 * Demonstrates the Jobs-to-be-Done editing interface
 */

import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';
import JobEditor from './JobEditor';

const meta = {
  title: 'Strategy/JobEditor',
  component: JobEditor,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Modal dialog for editing Jobs-to-be-Done (JTBD). ' +
          'Allows editing of Why, Circumstances, Forces, and Anxieties fields.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    isOpen: {
      control: 'boolean',
      description: 'Whether the modal is visible',
    },
    job: {
      description: 'Job object to edit (null for new job)',
    },
    onClose: {
      action: 'onClose',
      description: 'Callback when modal closes',
    },
    onSave: {
      action: 'onSave',
      description: 'Callback when job is saved',
    },
  },
} satisfies Meta<typeof JobEditor>;

export default meta;
type Story = StoryObj<typeof meta>;

const sampleJob = {
  id: 'job-001',
  why: 'User wants to save time scheduling meetings',
  circumstances:
    'When coordinating calendar availability across multiple team members in different time zones',
  forces:
    'Need for efficiency, pressure to maintain productivity, desire to reduce back-and-forth communication',
  anxieties:
    'Fear of missing important meetings, worry about double-booking, concern about timezone confusion',
};

const anotherJob = {
  id: 'job-002',
  why: 'Marketer wants to understand customer sentiment',
  circumstances:
    'When launching a new product campaign and need to gauge market reaction early',
  forces:
    'Competitive pressure to respond quickly, need for data-driven decisions, budget constraints',
  anxieties:
    'Worry about negative feedback, concern about missing important signals, fear of misinterpreting data',
};

/**
 * Open Modal - Standard editing interface
 */
export const OpenModal: Story = {
  args: {
    isOpen: true,
    job: sampleJob,
    onClose: () => console.log('Closed'),
    onSave: async (jobId, data) => {
      console.log('Saved:', jobId, data);
    },
  },
};

/**
 * Closed Modal - Modal is hidden
 */
export const ClosedModal: Story = {
  args: {
    isOpen: false,
    job: sampleJob,
    onClose: () => console.log('Closed'),
    onSave: async (jobId, data) => console.log('Saved:', jobId, data),
  },
};

/**
 * Different Job - Shows alternate job data
 */
export const DifferentJob: Story = {
  args: {
    isOpen: true,
    job: anotherJob,
    onClose: () => console.log('Closed'),
    onSave: async (jobId, data) => console.log('Saved:', jobId, data),
  },
};

/**
 * Null Job - Empty form for new job
 */
export const NullJob: Story = {
  args: {
    isOpen: true,
    job: null,
    onClose: () => console.log('Closed'),
    onSave: async (jobId, data) => console.log('Saved:', jobId, data),
  },
};

/**
 * Minimal Job - Sparse data
 */
export const MinimalJob: Story = {
  args: {
    isOpen: true,
    job: {
      id: 'job-003',
      why: 'Save time',
      circumstances: '',
      forces: '',
      anxieties: '',
    },
    onClose: () => console.log('Closed'),
    onSave: async (jobId, data) => console.log('Saved:', jobId, data),
  },
};

/**
 * Long Form Data - Extended content in fields
 */
export const LongFormData: Story = {
  args: {
    isOpen: true,
    job: {
      id: 'job-004',
      why: 'Enterprise executives want to align their entire organization around customer-centric strategy while maintaining agility in response to market changes',
      circumstances:
        'When conducting quarterly business reviews, annual strategy planning sessions, or responding to significant competitive threats or market disruptions. Especially critical when merging teams or reorganizing departments.',
      forces:
        'Executive pressure to demonstrate ROI on strategic initiatives, need to attract and retain top talent, competitive pressure from market leaders, shareholder expectations for growth, regulatory compliance requirements, desire to improve cross-functional collaboration',
      anxieties:
        'Fear of strategy misalignment across regions or divisions, concern about employee disengagement during changes, worry about losing key talent to competitors, anxiety about execution delays, concern that new strategy may cannibalize existing revenue streams',
    },
    onClose: () => console.log('Closed'),
    onSave: async (jobId, data) => console.log('Saved:', jobId, data),
  },
};

/**
 * Interactive - Shows save/close functionality
 */
export const Interactive: Story = {
  render: () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [isOpen, setIsOpen] = useState(false);
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [lastSaved, setLastSaved] = useState<string | null>(null);

    return (
      <div className="space-y-4">
        <button
          onClick={() => setIsOpen(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Edit Job
        </button>

        {lastSaved && (
          <div className="p-4 bg-green-50 border border-green-200 rounded">
            <p className="text-sm text-green-800">
              Saved: <span className="font-semibold">{lastSaved}</span>
            </p>
          </div>
        )}

        <JobEditor
          isOpen={isOpen}
          job={sampleJob}
          onClose={() => setIsOpen(false)}
          onSave={async (jobId, data) => {
            console.log('Saved:', jobId, data);
            setLastSaved(new Date().toLocaleTimeString());
            setIsOpen(false);
          }}
        />
      </div>
    );
  },
};

/**
 * Time-Saving Software Feature
 */
export const TimeSavingSoftwareJob: Story = {
  args: {
    isOpen: true,
    job: {
      id: 'job-scheduling',
      why: 'Manager wants to schedule team meetings efficiently',
      circumstances:
        'When team members are spread across multiple time zones and calendars are frequently double-booked',
      forces:
        'Need to save administrative time, pressure to improve team productivity, desire for better calendar visibility',
      anxieties:
        'Fear of missing important attendees, worry about timezone miscalculations, concern about over-scheduling',
    },
    onClose: () => console.log('Closed'),
    onSave: async (jobId, data) => console.log('Saved:', jobId, data),
  },
};

/**
 * Analytics Platform Feature
 */
export const AnalyticsJob: Story = {
  args: {
    isOpen: true,
    job: {
      id: 'job-analytics',
      why: 'Data analyst wants to identify customer behavior patterns quickly',
      circumstances: 'When preparing reports for executive leadership or investigating customer churn',
      forces:
        'Need for actionable insights, time pressure to deliver reports, desire to impress leadership with data-driven decisions',
      anxieties:
        'Fear of missing critical patterns in the data, worry about analysis errors, concern about data quality',
    },
    onClose: () => console.log('Closed'),
    onSave: async (jobId, data) => console.log('Saved:', jobId, data),
  },
};

/**
 * B2B Marketing Tool
 */
export const MarketingJob: Story = {
  args: {
    isOpen: true,
    job: {
      id: 'job-marketing',
      why: 'Marketing director wants to identify high-value customer segments for targeted campaigns',
      circumstances:
        'When planning quarterly marketing initiatives or preparing budgets for promotional spending',
      forces:
        'Budget constraints require efficient targeting, competitive pressure to acquire customers, need to prove ROI on marketing spend',
      anxieties:
        'Fear of wasting marketing budget on low-value segments, worry about campaign message misalignment, concern about brand perception',
    },
    onClose: () => console.log('Closed'),
    onSave: async (jobId, data) => console.log('Saved:', jobId, data),
  },
};

/**
 * Product Management Feature
 */
export const ProductManagementJob: Story = {
  args: {
    isOpen: true,
    job: {
      id: 'job-product',
      why: 'Product manager wants to understand user needs before building new features',
      circumstances:
        'When planning quarterly roadmap reviews or responding to customer feedback and feature requests',
      forces:
        'Pressure to ship features quickly, need to balance customer requests with strategic vision, desire to maximize user satisfaction',
      anxieties:
        'Fear of building features users do not want, worry about missing market opportunities, concern about technical debt',
    },
    onClose: () => console.log('Closed'),
    onSave: async (jobId, data) => console.log('Saved:', jobId, data),
  },
};

/**
 * Multiple Jobs Comparison - Switching between jobs
 */
export const MultipleJobsComparison: Story = {
  render: () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [selectedJobId, setSelectedJobId] = useState<string | null>('job-001');
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [isOpen, setIsOpen] = useState(false);

    const jobs = [sampleJob, anotherJob];
    const selectedJob = jobs.find((j) => j.id === selectedJobId) || null;

    return (
      <div className="space-y-4 max-w-md">
        <div className="space-y-2">
          <p className="font-semibold">Select Job to Edit:</p>
          {jobs.map((job) => (
            <button
              key={job.id}
              onClick={() => {
                setSelectedJobId(job.id);
                setIsOpen(true);
              }}
              className={`w-full text-left px-4 py-2 rounded border ${
                selectedJobId === job.id
                  ? 'bg-blue-50 border-blue-300'
                  : 'border-gray-300 hover:bg-gray-50'
              }`}
            >
              <p className="font-semibold text-sm">{job.why}</p>
              <p className="text-xs text-gray-600 mt-1">
                ID: {job.id}
              </p>
            </button>
          ))}
        </div>

        <JobEditor
          isOpen={isOpen}
          job={selectedJob}
          onClose={() => setIsOpen(false)}
          onSave={async (jobId, data) => {
            console.log('Saved:', jobId, data);
            setIsOpen(false);
          }}
        />
      </div>
    );
  },
};
