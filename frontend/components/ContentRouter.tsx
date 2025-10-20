"""
CONTENT ROUTER UI COMPONENT
React component for intelligent content routing and distribution
"""

import React, { useState, useCallback, useRef } from 'react';
import type { ReactNode } from 'react';

// Type definitions
interface Platform {
  name: string;
  score: number;
  confidence: 'high' | 'medium' | 'low';
  reasoning: string;
  tips: string[];
  characterLimit?: number;
  selected?: boolean;
}

interface ContentAnalysis {
  wordCount: number;
  characterCount: number;
  sentiment: 'positive' | 'negative' | 'neutral';
  tone: 'venting' | 'promotional' | 'question' | 'informative';
  hasQuestion: boolean;
  hasCta: boolean;
  emotionalIntensity: 'high' | 'low';
}

interface DistributionResult {
  platform: string;
  status: 'posted' | 'failed' | 'pending';
  postId?: string;
  url?: string;
  postedAt?: string;
  error?: string;
}

// Main Content Router Component
export const ContentRouter: React.FC = () => {
  const [content, setContent] = useState('');
  const [contentType, setContentType] = useState('text');
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isDistributing, setIsDistributing] = useState(false);
  const [analysis, setAnalysis] = useState<ContentAnalysis | null>(null);
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [distributionResults, setDistributionResults] = useState<DistributionResult[]>([]);
  const [showResults, setShowResults] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Handle content input
  const handleContentChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setContent(e.target.value);
  }, []);

  // Analyze content and get platform recommendations
  const handleAnalyzeContent = useCallback(async () => {
    if (!content.trim()) {
      alert('Please enter some content');
      return;
    }

    setIsAnalyzing(true);
    try {
      // Simulate API call
      const mockAnalysis: ContentAnalysis = {
        wordCount: content.split().length,
        characterCount: content.length,
        sentiment: content.toLowerCase().includes('hate') ? 'negative' : 'positive',
        tone: content.toLowerCase().includes('?') ? 'question' : 'informative',
        hasQuestion: content.includes('?'),
        hasCta: /click|buy|join|subscribe|sign up/i.test(content),
        emotionalIntensity: content.toLowerCase().includes('!') || content.toLowerCase().includes('hate') ? 'high' : 'low'
      };

      setAnalysis(mockAnalysis);

      // Mock platform recommendations
      const mockPlatforms: Platform[] = [
        {
          name: 'Twitter/X',
          score: 0.85,
          confidence: 'high',
          reasoning: 'Perfect for quick reactions and venting',
          tips: ['Keep under 280 characters', 'Use relevant hashtags', 'Thread if needed for longer content'],
          characterLimit: 280
        },
        {
          name: 'LinkedIn',
          score: 0.65,
          confidence: 'medium',
          reasoning: 'Professional network for insights and thought leadership',
          tips: ['Add line breaks for readability', 'Use formal tone', 'Include clear CTA'],
          characterLimit: 3000
        },
        {
          name: 'Facebook',
          score: 0.70,
          confidence: 'medium',
          reasoning: 'Broad reach and community engagement',
          tips: ['Add image for better engagement', 'Encourage comments', 'Use emojis strategically'],
          characterLimit: 63206
        },
        {
          name: 'Slack',
          score: 0.75,
          confidence: 'high',
          reasoning: 'Excellent for team communication and discussions',
          tips: ['Use threads for conversations', 'Tag relevant team members', 'Keep tone casual'],
          characterLimit: 0
        },
        {
          name: 'Discord',
          score: 0.72,
          confidence: 'medium',
          reasoning: 'Great for community venting and real-time chat',
          tips: ['Conversational tone works best', 'Thread support for detailed discussions', 'Emoji reactions encouraged'],
          characterLimit: 2000
        }
      ];

      setPlatforms(mockPlatforms);
      setSelectedPlatforms([mockPlatforms[0].name]); // Pre-select top platform
    } catch (error) {
      console.error('Analysis failed:', error);
      alert('Failed to analyze content');
    } finally {
      setIsAnalyzing(false);
    }
  }, [content]);

  // Handle platform selection
  const handlePlatformToggle = useCallback((platformName: string) => {
    setSelectedPlatforms(prev =>
      prev.includes(platformName)
        ? prev.filter(p => p !== platformName)
        : [...prev, platformName]
    );
  }, []);

  // Handle content distribution
  const handleDistribute = useCallback(async () => {
    if (selectedPlatforms.length === 0) {
      alert('Please select at least one platform');
      return;
    }

    setIsDistributing(true);
    try {
      // Simulate distribution
      const results: DistributionResult[] = selectedPlatforms.map(platform => ({
        platform,
        status: 'posted' as const,
        postId: `${platform}_${Date.now()}`,
        url: `https://${platform.toLowerCase()}.com/post/123456`,
        postedAt: new Date().toISOString()
      }));

      setDistributionResults(results);
      setShowResults(true);
    } catch (error) {
      console.error('Distribution failed:', error);
      alert('Failed to distribute content');
    } finally {
      setIsDistributing(false);
    }
  }, [selectedPlatforms]);

  // Clear form
  const handleClear = useCallback(() => {
    setContent('');
    setContentType('text');
    setSelectedPlatforms([]);
    setAnalysis(null);
    setPlatforms([]);
    setDistributionResults([]);
    setShowResults(false);
  }, []);

  return (
    <div className="content-router-container" style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <h1>📱 Content Router - Intelligent Platform Distribution</h1>

      {/* Content Input Section */}
      <ContentInputSection
        content={content}
        contentType={contentType}
        onContentChange={handleContentChange}
        onContentTypeChange={(type) => setContentType(type)}
        onAnalyze={handleAnalyzeContent}
        isAnalyzing={isAnalyzing}
        textareaRef={textareaRef}
      />

      {/* Content Analysis Results */}
      {analysis && (
        <ContentAnalysisDisplay analysis={analysis} />
      )}

      {/* Platform Recommendations */}
      {platforms.length > 0 && (
        <PlatformRecommendationsSection
          platforms={platforms}
          selectedPlatforms={selectedPlatforms}
          onPlatformToggle={handlePlatformToggle}
        />
      )}

      {/* Distribution Controls */}
      {platforms.length > 0 && (
        <DistributionControlsSection
          selectedCount={selectedPlatforms.length}
          isDistributing={isDistributing}
          onDistribute={handleDistribute}
          onClear={handleClear}
        />
      )}

      {/* Distribution Results */}
      {showResults && (
        <DistributionResultsSection results={distributionResults} />
      )}

      {/* Tips and Best Practices */}
      {selectedPlatforms.length > 0 && (
        <PlatformTipsSection
          platforms={platforms.filter(p => selectedPlatforms.includes(p.name))}
        />
      )}
    </div>
  );
};

// Content Input Section Component
interface ContentInputSectionProps {
  content: string;
  contentType: string;
  onContentChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onContentTypeChange: (type: string) => void;
  onAnalyze: () => void;
  isAnalyzing: boolean;
  textareaRef: React.RefObject<HTMLTextAreaElement>;
}

const ContentInputSection: React.FC<ContentInputSectionProps> = ({
  content,
  contentType,
  onContentChange,
  onContentTypeChange,
  onAnalyze,
  isAnalyzing,
  textareaRef
}) => {
  const wordCount = content.split(/\s+/).filter(w => w.length > 0).length;

  return (
    <div style={{ border: '1px solid #e0e0e0', borderRadius: '8px', padding: '20px', marginBottom: '20px' }}>
      <h2>📝 Content Input</h2>

      <div style={{ marginBottom: '15px' }}>
        <label htmlFor="contentType" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
          Content Type:
        </label>
        <select
          id="contentType"
          value={contentType}
          onChange={(e) => onContentTypeChange(e.target.value)}
          style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ddd', width: '200px' }}
        >
          <option value="text">Text Post</option>
          <option value="promotional">Promotional</option>
          <option value="question">Question</option>
          <option value="venting">Venting</option>
          <option value="announcement">Announcement</option>
          <option value="story">Story</option>
          <option value="tutorial">Tutorial</option>
        </select>
      </div>

      <div style={{ marginBottom: '15px' }}>
        <label htmlFor="content" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
          Content ({wordCount} words, {content.length} characters):
        </label>
        <textarea
          ref={textareaRef}
          id="content"
          value={content}
          onChange={onContentChange}
          placeholder="Paste your content here or type a new post. I'll analyze it and recommend the best platforms for sharing..."
          style={{
            width: '100%',
            height: '150px',
            padding: '10px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            fontFamily: 'Arial, sans-serif',
            fontSize: '14px'
          }}
        />
      </div>

      <button
        onClick={onAnalyze}
        disabled={isAnalyzing || !content.trim()}
        style={{
          padding: '10px 20px',
          backgroundColor: isAnalyzing ? '#ccc' : '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: isAnalyzing ? 'not-allowed' : 'pointer',
          fontSize: '16px'
        }}
      >
        {isAnalyzing ? '🔄 Analyzing...' : '✨ Analyze & Recommend'}
      </button>
    </div>
  );
};

// Content Analysis Display Component
interface ContentAnalysisDisplayProps {
  analysis: ContentAnalysis;
}

const ContentAnalysisDisplay: React.FC<ContentAnalysisDisplayProps> = ({ analysis }) => {
  const sentimentEmoji = {
    positive: '😊',
    negative: '😠',
    neutral: '😐'
  };

  const toneEmoji = {
    venting: '💢',
    promotional: '📢',
    question: '❓',
    informative: 'ℹ️'
  };

  return (
    <div style={{ border: '1px solid #e8f5e9', borderRadius: '8px', padding: '15px', marginBottom: '20px', backgroundColor: '#f1f8e9' }}>
      <h3>📊 Content Analysis</h3>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
        <AnalysisCard label="Word Count" value={analysis.wordCount} emoji="📝" />
        <AnalysisCard label="Character Count" value={analysis.characterCount} emoji="🔤" />
        <AnalysisCard
          label="Sentiment"
          value={`${sentimentEmoji[analysis.sentiment]} ${analysis.sentiment}`}
          emoji=""
        />
        <AnalysisCard
          label="Tone"
          value={`${toneEmoji[analysis.tone]} ${analysis.tone}`}
          emoji=""
        />
        <AnalysisCard
          label="Has Question?"
          value={analysis.hasQuestion ? '✅ Yes' : '❌ No'}
          emoji=""
        />
        <AnalysisCard
          label="Has CTA?"
          value={analysis.hasCta ? '✅ Yes' : '❌ No'}
          emoji=""
        />
        <AnalysisCard
          label="Emotional Intensity"
          value={analysis.emotionalIntensity}
          emoji="⚡"
        />
      </div>
    </div>
  );
};

interface AnalysisCardProps {
  label: string;
  value: string | number;
  emoji: string;
}

const AnalysisCard: React.FC<AnalysisCardProps> = ({ label, value, emoji }) => (
  <div style={{
    backgroundColor: 'white',
    padding: '10px',
    borderRadius: '6px',
    border: '1px solid #ddd'
  }}>
    <div style={{ fontSize: '12px', color: '#666', marginBottom: '5px' }}>
      {emoji} {label}
    </div>
    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#333' }}>
      {value}
    </div>
  </div>
);

// Platform Recommendations Section
interface PlatformRecommendationsSectionProps {
  platforms: Platform[];
  selectedPlatforms: string[];
  onPlatformToggle: (platformName: string) => void;
}

const PlatformRecommendationsSection: React.FC<PlatformRecommendationsSectionProps> = ({
  platforms,
  selectedPlatforms,
  onPlatformToggle
}) => {
  return (
    <div style={{ border: '1px solid #e3f2fd', borderRadius: '8px', padding: '20px', marginBottom: '20px', backgroundColor: '#f5f5f5' }}>
      <h2>🎯 Platform Recommendations</h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '15px' }}>
        {platforms.map(platform => (
          <PlatformCard
            key={platform.name}
            platform={platform}
            isSelected={selectedPlatforms.includes(platform.name)}
            onToggle={() => onPlatformToggle(platform.name)}
          />
        ))}
      </div>
    </div>
  );
};

interface PlatformCardProps {
  platform: Platform;
  isSelected: boolean;
  onToggle: () => void;
}

const PlatformCard: React.FC<PlatformCardProps> = ({ platform, isSelected, onToggle }) => {
  const confidenceColor = {
    high: '#4caf50',
    medium: '#ff9800',
    low: '#f44336'
  };

  return (
    <div
      onClick={onToggle}
      style={{
        border: isSelected ? '3px solid #007bff' : '1px solid #ddd',
        borderRadius: '8px',
        padding: '15px',
        backgroundColor: isSelected ? '#e3f2fd' : 'white',
        cursor: 'pointer',
        transition: 'all 0.3s ease'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '10px' }}>
        <h3 style={{ margin: '0 0 5px 0' }}>
          <input
            type="checkbox"
            checked={isSelected}
            onChange={onToggle}
            style={{ marginRight: '10px' }}
          />
          {platform.name}
        </h3>
        <span style={{
          fontSize: '14px',
          fontWeight: 'bold',
          color: 'white',
          backgroundColor: confidenceColor[platform.confidence],
          padding: '4px 8px',
          borderRadius: '4px'
        }}>
          {Math.round(platform.score * 100)}%
        </span>
      </div>

      <div style={{ marginBottom: '10px', fontSize: '14px', color: '#666' }}>
        {platform.reasoning}
      </div>

      <div style={{ fontSize: '13px', color: '#333' }}>
        <strong>Tips:</strong>
        <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
          {platform.tips.slice(0, 2).map((tip, idx) => (
            <li key={idx}>{tip}</li>
          ))}
        </ul>
      </div>

      {platform.characterLimit && platform.characterLimit > 0 && (
        <div style={{ fontSize: '12px', color: '#999', marginTop: '10px' }}>
          ↳ Max {platform.characterLimit} characters
        </div>
      )}
    </div>
  );
};

// Distribution Controls Section
interface DistributionControlsSectionProps {
  selectedCount: number;
  isDistributing: boolean;
  onDistribute: () => void;
  onClear: () => void;
}

const DistributionControlsSection: React.FC<DistributionControlsSectionProps> = ({
  selectedCount,
  isDistributing,
  onDistribute,
  onClear
}) => {
  return (
    <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
      <button
        onClick={onDistribute}
        disabled={isDistributing || selectedCount === 0}
        style={{
          padding: '12px 24px',
          backgroundColor: isDistributing ? '#ccc' : '#28a745',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: isDistributing ? 'not-allowed' : 'pointer',
          fontSize: '16px',
          fontWeight: 'bold'
        }}
      >
        {isDistributing ? '🔄 Publishing...' : `✅ Publish to ${selectedCount} Platform${selectedCount !== 1 ? 's' : ''}`}
      </button>

      <button
        onClick={onClear}
        style={{
          padding: '12px 24px',
          backgroundColor: '#6c757d',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '16px'
        }}
      >
        🗑️ Clear
      </button>
    </div>
  );
};

// Distribution Results Section
interface DistributionResultsSectionProps {
  results: DistributionResult[];
}

const DistributionResultsSection: React.FC<DistributionResultsSectionProps> = ({ results }) => {
  const successCount = results.filter(r => r.status === 'posted').length;

  return (
    <div style={{ border: '1px solid #c8e6c9', borderRadius: '8px', padding: '20px', marginBottom: '20px', backgroundColor: '#f1f8e9' }}>
      <h2>✅ Distribution Results</h2>

      <div style={{ marginBottom: '15px', fontSize: '16px', fontWeight: 'bold', color: '#2e7d32' }}>
        Successfully published to {successCount}/{results.length} platforms
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '10px' }}>
        {results.map(result => (
          <div
            key={result.platform}
            style={{
              padding: '10px',
              backgroundColor: result.status === 'posted' ? '#e8f5e9' : '#ffebee',
              border: `2px solid ${result.status === 'posted' ? '#4caf50' : '#f44336'}`,
              borderRadius: '6px'
            }}
          >
            <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
              {result.status === 'posted' ? '✅' : '❌'} {result.platform}
            </div>
            {result.url && (
              <a
                href={result.url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: '#007bff', textDecoration: 'none', fontSize: '12px' }}
              >
                View Post →
              </a>
            )}
            {result.error && (
              <div style={{ color: '#f44336', fontSize: '12px' }}>{result.error}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// Platform Tips Section
interface PlatformTipsSectionProps {
  platforms: Platform[];
}

const PlatformTipsSection: React.FC<PlatformTipsSectionProps> = ({ platforms }) => {
  return (
    <div style={{ border: '1px solid #fff3e0', borderRadius: '8px', padding: '20px', backgroundColor: '#fffde7' }}>
      <h2>💡 Platform-Specific Tips</h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '15px' }}>
        {platforms.map(platform => (
          <div key={platform.name} style={{ backgroundColor: 'white', padding: '15px', borderRadius: '6px', border: '1px solid #ddd' }}>
            <h3 style={{ margin: '0 0 10px 0' }}>{platform.name}</h3>
            <ul style={{ margin: '0', paddingLeft: '20px' }}>
              {platform.tips.map((tip, idx) => (
                <li key={idx} style={{ marginBottom: '5px', fontSize: '14px' }}>
                  {tip}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ContentRouter;
