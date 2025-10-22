/**
 * AISAS Slider Component Stories
 * Demonstrates the customer journey positioning slider with 5 segments
 */

import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';
import AISASSlider from './AISASSlider';

const meta = {
  title: 'Strategy/AISASSlider',
  component: AISASSlider,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Interactive slider for positioning content across the AISAS customer journey stages. ' +
          'AISAS stands for: Attention → Interest → Search → Action → Share. ' +
          'Range: 0-100, with color-coded segments.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    value: {
      control: {
        type: 'range',
        min: 0,
        max: 100,
        step: 1,
      },
      description: 'Current value (0-100)',
    },
    onChange: {
      action: 'onChange',
      description: 'Callback when slider value changes',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the slider is disabled',
    },
    showLabel: {
      control: 'boolean',
      description: 'Whether to show the stage label',
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
      description: 'Size of the slider',
    },
  },
} satisfies Meta<typeof AISASSlider>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default - Medium size slider at 50% (Search stage)
 */
export const Default: Story = {
  args: {
    value: 50,
    onChange: (value) => console.log('Value:', value),
    disabled: false,
    showLabel: true,
    size: 'md',
  },
};

/**
 * Attention Stage - Red segment (0-20%)
 */
export const AttentionStage: Story = {
  args: {
    value: 10,
    onChange: (value) => console.log('Value:', value),
    disabled: false,
    showLabel: true,
    size: 'md',
  },
};

/**
 * Interest Stage - Orange segment (20-40%)
 */
export const InterestStage: Story = {
  args: {
    value: 30,
    onChange: (value) => console.log('Value:', value),
    disabled: false,
    showLabel: true,
    size: 'md',
  },
};

/**
 * Search Stage - Yellow segment (40-60%)
 */
export const SearchStage: Story = {
  args: {
    value: 50,
    onChange: (value) => console.log('Value:', value),
    disabled: false,
    showLabel: true,
    size: 'md',
  },
};

/**
 * Action Stage - Blue segment (60-80%)
 */
export const ActionStage: Story = {
  args: {
    value: 70,
    onChange: (value) => console.log('Value:', value),
    disabled: false,
    showLabel: true,
    size: 'md',
  },
};

/**
 * Share Stage - Green segment (80-100%)
 */
export const ShareStage: Story = {
  args: {
    value: 90,
    onChange: (value) => console.log('Value:', value),
    disabled: false,
    showLabel: true,
    size: 'md',
  },
};

/**
 * Small Size - Compact slider for sidebars
 */
export const SmallSize: Story = {
  args: {
    value: 50,
    onChange: (value) => console.log('Value:', value),
    disabled: false,
    showLabel: true,
    size: 'sm',
  },
};

/**
 * Large Size - Prominent slider for main content
 */
export const LargeSize: Story = {
  args: {
    value: 50,
    onChange: (value) => console.log('Value:', value),
    disabled: false,
    showLabel: true,
    size: 'lg',
  },
};

/**
 * All Sizes - Comparison of sm, md, lg
 */
export const AllSizes: Story = {
  render: () => (
    <div className="space-y-8 max-w-md">
      <div>
        <p className="mb-3 font-semibold text-sm">Small (sm)</p>
        <AISASSlider
          value={50}
          onChange={() => {}}
          showLabel={true}
          size="sm"
        />
      </div>
      <div>
        <p className="mb-3 font-semibold text-sm">Medium (md)</p>
        <AISASSlider
          value={50}
          onChange={() => {}}
          showLabel={true}
          size="md"
        />
      </div>
      <div>
        <p className="mb-3 font-semibold text-sm">Large (lg)</p>
        <AISASSlider
          value={50}
          onChange={() => {}}
          showLabel={true}
          size="lg"
        />
      </div>
    </div>
  ),
};

/**
 * Without Label - Clean slider without stage display
 */
export const WithoutLabel: Story = {
  args: {
    value: 50,
    onChange: (value) => console.log('Value:', value),
    disabled: false,
    showLabel: false,
    size: 'md',
  },
};

/**
 * Disabled State - Non-interactive slider
 */
export const Disabled: Story = {
  args: {
    value: 50,
    onChange: (value) => console.log('Value:', value),
    disabled: true,
    showLabel: true,
    size: 'md',
  },
};

/**
 * All Journey Stages - Shows all 5 AISAS stages
 */
export const AllStages: Story = {
  render: () => (
    <div className="space-y-8 max-w-2xl">
      <div>
        <p className="mb-3 font-semibold text-sm text-red-700">Attention (0-20)</p>
        <AISASSlider
          value={10}
          onChange={() => {}}
          showLabel={true}
          size="md"
        />
      </div>
      <div>
        <p className="mb-3 font-semibold text-sm text-orange-700">Interest (20-40)</p>
        <AISASSlider
          value={30}
          onChange={() => {}}
          showLabel={true}
          size="md"
        />
      </div>
      <div>
        <p className="mb-3 font-semibold text-sm text-yellow-700">Search (40-60)</p>
        <AISASSlider
          value={50}
          onChange={() => {}}
          showLabel={true}
          size="md"
        />
      </div>
      <div>
        <p className="mb-3 font-semibold text-sm text-blue-700">Action (60-80)</p>
        <AISASSlider
          value={70}
          onChange={() => {}}
          showLabel={true}
          size="md"
        />
      </div>
      <div>
        <p className="mb-3 font-semibold text-sm text-green-700">Share (80-100)</p>
        <AISASSlider
          value={90}
          onChange={() => {}}
          showLabel={true}
          size="md"
        />
      </div>
    </div>
  ),
};

/**
 * Interactive - Shows value changes in real-time
 */
export const Interactive: Story = {
  render: () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [value, setValue] = useState(50);

    const stageNames = ['Attention', 'Interest', 'Search', 'Action', 'Share'];
    const stageIndex = Math.floor(value / 20);
    const currentStage = stageNames[stageIndex] || 'Share';

    return (
      <div className="space-y-6 max-w-md">
        <AISASSlider
          value={value}
          onChange={setValue}
          showLabel={true}
          size="lg"
        />
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <p className="text-sm text-gray-600">
            Value: <span className="font-semibold text-lg">{value}</span>
          </p>
          <p className="text-sm text-gray-600 mt-2">
            Stage: <span className="font-semibold text-lg">{currentStage}</span>
          </p>
        </div>
      </div>
    );
  },
};

/**
 * LinkedIn Channel Example - Positioning a social media channel
 */
export const LinkedInChannelExample: Story = {
  args: {
    value: 35,
    onChange: (value) => console.log('LinkedIn AISAS:', value),
    disabled: false,
    showLabel: true,
    size: 'md',
  },
  parameters: {
    docs: {
      description: {
        story: 'LinkedIn typically targets the Attention to Interest stages (20-40%)',
      },
    },
  },
};

/**
 * YouTube Channel Example - Different channel positioning
 */
export const YouTubeChannelExample: Story = {
  args: {
    value: 55,
    onChange: (value) => console.log('YouTube AISAS:', value),
    disabled: false,
    showLabel: true,
    size: 'md',
  },
  parameters: {
    docs: {
      description: {
        story: 'YouTube typically targets Search and Action stages (40-80%)',
      },
    },
  },
};

/**
 * Email Campaign Example - High engagement positioning
 */
export const EmailCampaignExample: Story = {
  args: {
    value: 75,
    onChange: (value) => console.log('Email AISAS:', value),
    disabled: false,
    showLabel: true,
    size: 'md',
  },
  parameters: {
    docs: {
      description: {
        story: 'Email typically targets Action and Share stages (60-100%)',
      },
    },
  },
};

/**
 * Multi-Channel Comparison - Shows different positions
 */
export const MultiChannelComparison: Story = {
  render: () => (
    <div className="space-y-6 max-w-2xl">
      <div>
        <p className="mb-2 font-semibold">LinkedIn</p>
        <AISASSlider value={35} onChange={() => {}} showLabel={true} size="md" />
      </div>
      <div>
        <p className="mb-2 font-semibold">YouTube</p>
        <AISASSlider value={55} onChange={() => {}} showLabel={true} size="md" />
      </div>
      <div>
        <p className="mb-2 font-semibold">Email</p>
        <AISASSlider value={75} onChange={() => {}} showLabel={true} size="md" />
      </div>
      <div>
        <p className="mb-2 font-semibold">Twitter</p>
        <AISASSlider value={25} onChange={() => {}} showLabel={true} size="md" />
      </div>
      <div>
        <p className="mb-2 font-semibold">TikTok</p>
        <AISASSlider value={15} onChange={() => {}} showLabel={true} size="md" />
      </div>
    </div>
  ),
};
