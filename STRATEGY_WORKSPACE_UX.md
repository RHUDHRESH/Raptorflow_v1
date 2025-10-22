# RaptorFlow 2.0 – Strategy Workspace UX Documentation

## 3. User Experience: Strategy Workspace

### 3.1 Overview

The **Strategy Workspace** is the default landing area after onboarding and context intake. It is the hub where raw context transforms into defensible strategy through AI-powered analysis and human refinement.

**Purpose**: Enable users to understand their marketing context, define Jobs-to-Be-Done (JTBD), build Ideal Customer Profiles (ICPs), map channels with content types, and generate actionable moves.

**Three-Pane Layout**:
```
┌──────────────────────────────────────────────────────────┐
│  Strategy Workspace: [Company Name]  [Save] [Share] [+]  │
├─────────────────┬──────────────────────────┬──────────────┤
│                 │                          │              │
│  Left Pane:     │  Center Pane:            │  Right Pane: │
│  Context Intake │  Strategy Canvas         │  Rationales  │
│                 │                          │              │
│  • Paste text   │  ┌─ Jobs ────────────┐   │  Why we      │
│  • Upload files │  │ ┌─Job 1──┐ ┌─Job 2│   │  chose       │
│  • Add links    │  │ │Vent    │ │Warn  │   │  this        │
│  • Metadata     │  │ │frustrat│ │others│   │  strategy    │
│                 │  │ └────────┘ └─────┘    │              │
│  [Clear All]    │  ├─ ICPs ────────────┐   │  Evidence    │
│  [Lock Jobs]    │  │ ┌─ICP1──┐ ┌─ICP2──┐   │  citations   │
│                 │  │ │Café   │ │Tech   │   │              │
│                 │  │ │Creators│ │Founders  │  [Filter]    │
│                 │  │ └────────┘ └──────┘    │              │
│                 │  ├─ Channels ────────┐   │  [Pin]       │
│                 │  │ [AISAS slider]    │   │  [Annotate]  │
│                 │  │ [Channel matrix]  │   │              │
│                 │  └───────────────────┘   │              │
│                 │                          │              │
└─────────────────┴──────────────────────────┴──────────────┘
```

**Key Principles**:
- Transparency: Every recommendation includes "why we chose this" explanations
- Editability: Users can merge/split jobs, create/modify ICPs, customize channel recommendations
- Incrementality: Users can save drafts at any stage
- Feedback loops: All moves, receipts and performance data inform strategy iteration

---

### 3.2 Left Pane: Context Intake Flow

#### Purpose
Collect and organize all raw marketing context (content, customer research, competitive intel) that informs the strategy.

#### Components

##### 3.2.1 Text Input Area
**Layout**:
- Large textarea (400 × 300 px on desktop)
- Placeholder: "Paste your LinkedIn rant, product pitch, customer feedback, competitor profiles, or any context that drives your marketing…"
- Character count: Show count + limit (e.g., "2,450 / 50,000 characters")
- Auto-expand on multi-line

**Interactions**:
- OnFocus: Outline glows Barleycorn; hint appears below: "Pro tip: Include dates, metrics, and specific quotes for richer analysis."
- OnPaste: Detect if URL pasted; offer to fetch content from link
- OnInput: Real-time character count; validation (no empty input allowed)

**Microcopy**:
- Placeholder: "Paste your rant, pitch, feedback, or research…"
- Hint: "Include dates, metrics, and quotes for better analysis."
- Error: "Context cannot be empty. Please paste or upload something."

##### 3.2.2 File Upload Zone
**Layout**:
- Drag & drop area (400 × 200 px)
- Border: Dotted Mineshaft, Akaroa fill
- Icons for: Image, PDF, Video, Audio
- "Or click to choose files" button
- Max file size: 1 GB total; 500 MB per file
- Supported formats:
  - Images: PNG, JPG, WebP (thumbnails extracted)
  - PDFs: Text extraction via OCR
  - Videos: MP4, WebM, MOV (frames + auto-captions)
  - Audio: WAV, M4A, MP3 (transcription via Ollama Whisper or OpenAI)

**File Handling**:
1. OnDrop or OnSelect: Show progress bar (% complete)
2. During processing:
   - Image: Extract text (OCR if needed)
   - PDF: Extract pages as images + text
   - Video: Extract key frames (1 per 10 seconds)
   - Audio: Transcribe to text; store original for later reference
3. After processing: Show file name, type, size, status (✓ processed)
4. Remove button (X icon) on hover

**Transcription Indicator**:
- While transcribing audio/video, show mini waveform animating
- Display: "Transcribing audio… 45%"
- Tooltip: "Audio transcription helps us understand tone and emotion."

**Multiple Files**:
- Users can upload multiple files simultaneously
- Each file shows progress bar + status
- Display list of uploaded files with remove buttons

##### 3.2.3 Link/URL Input
**Layout**:
- Input field (400 px wide) + add button
- Placeholder: "Paste a URL to any article, blog post, or social media link…"
- OnEnter or button click: Validate URL, fetch content

**URL Processing**:
1. Validate URL format
2. Fetch page content (using browser/server)
3. Extract title, author, date, main content (article parsing)
4. Store URL + extracted content
5. Show link as card with title, preview, favicon
6. Remove button (X) on hover

**Microcopy**:
- Placeholder: "Paste a URL…"
- Processing: "Fetching content from [domain]…"
- Success: "✓ Content imported"
- Error: "Unable to fetch content from this URL. Is it public?"

##### 3.2.4 Metadata Tagging
**Layout**:
- Below file uploads, optional fields:
  - **Source**: Dropdown (LinkedIn, Twitter, Email, Support, Sales call, Customer research, Competitor analysis, Internal)
  - **Mood/Tone**: Dropdown (Rant, Success story, Question, Feature request, Complaint, Neutral)
  - **Date**: Date picker (defaults to today)
  - **ICP (Optional)**: Multi-select dropdown of existing ICPs (or leave blank for system to infer)

**Purpose**: Help the system understand context better and allow filtering/searching later.

**Microcopy**:
- Source: "Where did this content originate?"
- Mood: "What's the overall tone?"
- Date: "When was this created?"
- ICP: "Which ICP(s) does this apply to? (Optional)"

##### 3.2.5 Bottom Actions
**Clear All Button** (Tertiary, outline):
- Removes all uploaded content
- Confirmation modal: "Are you sure you want to clear all context? You can still save drafts of your strategy."

**Lock Jobs Button** (Primary, Barleycorn):
- Disabled until system has extracted ≥1 job
- OnClick: System begins ICP builder + channel mapping
- Shows loader: "Analyzing context… 60%"
- After analysis: Navigate to center pane with results

---

### 3.3 Center Pane: Strategy Canvas

#### Purpose
Display AI-analyzed strategy: Jobs, ICPs, channels, AISAS recommendations, and all editable elements.

#### 3.3.1 Jobs Section

**Layout**:
- Title: "Jobs-to-Be-Done" (18 px, medium)
- Horizontal scrollable area (or grid on desktop)
- Cards in a grid: 2-3 per row (desktop), 1 per row (mobile)

**Job Card Specifications**:
- Dimensions: 320 × 240 px
- Header:
  - Job label (18 px, bold, Mineshaft)
  - Status dot (Barleycorn) indicating active/merged/split
  - Menu button (three dots) with options: Edit, Merge, Split, Delete
- Body (4 fields, each with icon):
  - **Why** (question mark icon): "One-line summary of the job" (13 px, gray placeholder)
  - **Circumstances** (clock icon): "When does this occur?" (e.g., "Weekday mornings, during commute")
  - **Forces** (arrow icon): "Push/pull forces" (e.g., "Wants to understand market, fears being left behind")
  - **Anxieties** (exclamation icon): "What might block this job?" (e.g., "Information overload, skepticism")
- Footer:
  - "Merge" button (tertiary, small)
  - "Split" button (tertiary, small)

**Card States**:
- Default: Akaroa background, soft shadow (2 px), rounded 8 px
- Hover: Lift effect (4 px shadow), Akaroa darkens slightly
- Selected: Barleycorn outline (2 px), same shadow as hover
- Edited: Green checkmark (top-right corner)

**Interactions**:

**Inline Editing**:
- Click any field → Pencil icon appears
- Click pencil or double-click field → Input field opens
- User edits text
- OnBlur or OnEnter: Save changes; show green checkmark
- OnEscape: Cancel editing

**Merge Jobs**:
- Drag one card onto another → Modal opens
- Modal: "Merge [Job A] with [Job B]"
- Checkboxes for each field: "Keep from Job A", "Keep from Job B", "Combine", "Manual input"
- Button: "Merge"
- Result: Jobs combined; removed job disappears

**Split Jobs**:
- Click "Split" button → Modal opens
- Modal: "Create new job from [Job Name]"
- Checkboxes for which elements go into new job:
  - [ ] Keep "Why" (copy to new job)
  - [ ] Keep "Circumstances" (copy to new job)
  - [ ] Keep "Forces" (copy to new job)
  - [ ] Keep "Anxieties" (copy to new job)
- Input: "Name for new job" (text field)
- Button: "Split"
- Result: New job created; old job updated

**Delete Job**:
- Click menu → "Delete"
- Confirmation: "Delete this job? It will be removed from your strategy and any linked moves."
- Button: "Delete"
- Result: Job removed

**Microcopy**:
- "Job label": "What is this customer trying to accomplish?"
- "Why": "One-line summary"
- "Circumstances": "When does this job arise?"
- "Forces": "What pushes or pulls them toward a solution?"
- "Anxieties": "What might prevent them from solving this?"
- "Merge": "Combine two similar jobs"
- "Split": "Create a new job from this one"

---

#### 3.3.2 ICPs (Ideal Customer Profiles) Section

**Layout**:
- Title: "Ideal Customer Profiles" (18 px, medium)
- Horizontal scrollable area (or grid)
- Cards in a grid: 2 per row (desktop), 1 per row (mobile)

**ICP Card Specifications**:
- Dimensions: 400 × 260 px (larger than jobs)
- Avatar (top-left): 64 × 64 px circular image/icon
  - Generated by AI or uploaded
  - Click to open avatar editor
- Header:
  - ICP name (18 px, bold, Mineshaft) on left
  - Color bar matching logo (8 px wide on right side)
  - Menu button (three dots) on right: Edit name, Change logo, Delete
- Body:
  - **Traits**: Compact table
    - Rows: Industry, Size, Location, Languages, Tech stack, Budget size, etc.
    - Columns: Trait, Include/Exclude (pill badges)
    - Exclude traits appear in gray italic
  - **Pain Points**: Bullet list (2-4 items, 13 px)
    - E.g., "Lack of clear marketing direction", "Budget constraints"
  - **Behaviors**: List of typical habits (13 px)
    - E.g., "Reads long-form content on LinkedIn at 9 AM"
    - "Checks email 3x daily during work hours"
- Footer:
  - Health bar: Horizontal progress bar (80 px wide)
    - Filled % based on weighted formula of recent receipt outcomes
    - Label: "Health" (13 px)
  - Mood icon: Happy (😊), Neutral (😐), or Sad (😕) based on health bar
  - Label: "Thriving" / "Needs attention" / "At risk"

**Card States**:
- Default: Akaroa background, soft shadow (2 px), rounded 8 px
- Hover: Lift effect (4 px shadow)
- Selected: Barleycorn outline (2 px)

**Interactions**:

**Avatar Editor**:
- Click avatar → Modal opens
- Three generation options (radio buttons):
  - Icon only (circular, 64 px)
  - Icon with letter (e.g., "C" for Café Creators)
  - Circular frame with border
- Color customization:
  - Primary color: Slider (choose from palette: Mineshaft, Barleycorn, Akaroa, White Rock, or custom)
  - Secondary color: Similar slider
  - Toggle: "Invert colors"
- Preview section: Shows avatar in 3 contexts (card, nav, chat)
- Buttons: "Generate new", "Upload custom" (file picker), "Save"

**Edit ICP**:
- Click "Edit name" in menu → Modal opens
- Text input with current name
- Buttons: "Cancel", "Save"

**Change Logo**:
- Click "Change logo" in menu → Opens file picker
- User uploads image (PNG, JPG, max 1 MB)
- System extracts dominant color and uses as ICP color
- Preview shows new logo
- Button: "Save"

**Delete ICP**:
- Click "Delete" in menu → Confirmation modal
- Message: "Delete [ICP name]? All linked moves will be orphaned and need reassignment."
- Buttons: "Cancel", "Delete"
- Result: ICP removed; moves linked to this ICP show warning

**Reorder ICPs**:
- Drag card to reorder (visual drag handle)
- Order reflects priority (used in reporting and move suggestions)

**Microcopy**:
- "Health": "How satisfied is this ICP based on recent content performance?"
- Thriving: "This ICP is happy with your content."
- Needs attention: "Consider running more content for this ICP."
- At risk: "Content performance is declining. Try new angles or platforms."

---

#### 3.3.3 Channel Map & AISAS

**Layout**:
- Title: "Channel Map & AISAS" (18 px, medium)
- Full-width matrix grid below

**Matrix Grid Specifications**:
- Rows: Each ICP (auto-scrolls if many)
- Columns: Each Job (auto-scrolls if many)
- Cell width: 140 px; height: 100 px
- Each cell contains:
  - Platform pills (YouTube, LinkedIn, Instagram, X, Threads, TikTok, Facebook)
  - Content type badges (Hero, Hub, Help)
  - + icon to add channels

**AISAS Slider** (above matrix, one per job):
- Range: 0 (Awareness) → 100 (Share)
- Segments: 5 equal parts
  - 0-20: Attention (red gradient)
  - 20-40: Interest (orange gradient)
  - 40-60: Search (yellow gradient)
  - 60-80: Action (blue gradient)
  - 80-100: Share (green gradient)
- Visual: Horizontal bar with segment dividers
- Draggable thumb (round, Barleycorn)
- Current value displays in center (e.g., "65 – Action focused")

**Channel Pill Specifications**:
- Background: Barleycorn
- Text: White Rock
- Padding: 4 px × 8 px
- Border radius: 16 px
- Font: 11 px, bold
- Max 3 pills per cell (overflow shows "+2 more")

**Cell Interactions**:

**Hover Tooltip**:
- OnHover over cell: Tooltip appears (300 px wide)
- Content:
  - Recommended channels
  - Cadence: "1 Hero video per month"
  - Recommended posting times: "Tuesdays 10 AM, Fridays 3 PM"
  - Recommended length: "8-15 minutes"
  - Tone: "Educational, authoritative"
  - Platform constraints: "Max 100 MB, aspect ratio 16:9"

**Add Channel**:
- Click + icon → Modal opens
- Modal title: "Add channel for [ICP] – [Job]"
- List of all available channels (YouTube, LinkedIn, Instagram, X, Threads, TikTok, Facebook, Email, Blog, Podcast, etc.)
- Search field: "Filter channels…"
- Checkboxes: Select one or more
- Button: "Add selected"
- Result: Selected channels appear as pills in cell

**Remove Channel**:
- OnHover over pill: X icon appears
- Click X → Pill removed (no confirmation)

**Edit AISAS Slider**:
- Drag thumb left/right → Recommendations update in real-time
- As slider moves, channel pills animate in/out
- Tooltip shows current value and focus area

**Microcopy**:
- AISAS label: "Where in the customer journey should this content sit?"
- Attention: "Help them discover your ICP exists."
- Interest: "Build interest and engagement."
- Search: "Help them research and evaluate."
- Action: "Convert them into customers."
- Share: "Turn them into advocates."
- Tooltip: "Post time optimized for your ICP's timezone and behavior."

---

#### 3.3.4 Advanced Strategy Editor

**Optional Accordion Section** (collapsed by default):
- Title: "Advanced Strategy Settings" (18 px, medium, clickable to expand)
- Content (only visible when expanded):
  - **Primary Goal**: Dropdown (Launch product, Grow following, Improve engagement, Generate leads)
  - **Target Market Size**: Dropdown (Niche <1000, Small 1-10K, Mid 10-100K, Large 100K+)
  - **Content Frequency**: Dropdown (1x/week, 2-3x/week, Daily, Custom)
  - **Budget Tier**: Dropdown (Free, Basic, Pro, Enterprise) – shows estimated cost
  - **Brand Voice**: Text area (or link to saved brand voice)

---

### 3.4 Right Pane: Rationales & Explanations

#### Purpose
Provide transparency by showing **why** the system made each recommendation, building trust and enabling learning.

#### Layout
- Title: "Why We Chose This" (18 px, medium)
- Collapsible/pinnable panel
- Scrollable content area

#### Components

##### 3.4.1 Explanations by Section

**Jobs Explanations**:
- Heading: "Jobs-to-Be-Done" (16 px, medium) + collapse icon
- For each job:
  - Job label (bold)
  - Rationale: "We identified this job because [evidence-based explanation]"
  - Example: "We identified 'Vent frustration' because your context includes multiple complaints about bank service and emotional language (frustrated, angry, concerned)."
  - Evidence citations: Inline links showing which segments of context triggered this job
  - "See more" link to expand additional details

**ICP Explanations**:
- Heading: "Ideal Customer Profiles" (16 px, medium) + collapse icon
- For each ICP:
  - ICP name (bold)
  - Rationale: "We proposed [ICP name] because [evidence and rule explanations]"
  - Example: "We proposed 'Tech Founders' because your context emphasizes product-market fit (a priority for founders) and mentions technical complexity, suggesting an audience with engineering background."
  - Traits breakdown: "We inferred [trait] because [evidence]"
  - Confidence score: "Confidence: 87%" (bar chart)

**Channels Explanations**:
- Heading: "Recommended Channels" (16 px, medium) + collapse icon
- For each ICP-Job combo:
  - Recommendation: "[Platform] is recommended for [ICP] because [reasons]"
  - Example: "LinkedIn is recommended for Tech Founders because your ICP spends 45 min/day on the platform (inferred from context) and engages with long-form content."
  - Platform physics: Links to constraints (file size, duration, aspect ratio)

**AISAS Explanations**:
- Heading: "Content Strategy (AISAS)" (16 px, medium) + collapse icon
- Rationale: "We've focused on [Attention/Interest/Search/Action/Share] stage because [evidence]"
- Example: "We've focused on the Interest stage because your context suggests the audience is aware of the problem but unsure about solutions. Content addressing objections and use cases will drive engagement."

##### 3.4.2 Evidence Citations

**In-text Citations**:
- Bracketed links: "[Citation #5]"
- OnHover: Tooltip shows brief excerpt
- OnClick: Highlight matching segment in left pane (if available) or open detail modal

**Citation Detail Modal**:
- Source: Text block or file name
- Full excerpt: "Your audience said: [full quote]"
- Inferred attribute: "This suggests: [what we inferred]"
- Button: "Close"

##### 3.4.3 Filter Dropdown

**Position**: Top-right of right pane
**Options**:
- Show all
- Show wisdom rules only
- Show platform specs only
- Show context references only
- Show confidence >80%
- Show confidence <60%

**Effect**: Filter explanations to show only selected categories

##### 3.4.4 Pinning & Annotation

**Pin Icon** (top-right of each explanation):
- Click to pin explanation (sticks to top of panel)
- Pinned explanations show colored border (Barleycorn)
- Unpin by clicking again

**Annotation Button** (below each explanation):
- Text link: "+ Add note"
- OnClick: Text input appears
- User types personal note (e.g., "This doesn't match our audience")
- OnSave: Note stored; shows as light background below explanation
- OnEdit: Notes editable
- OnDelete: Note removed

**Microcopy**:
- "We identified this job because…"
- "We proposed this ICP based on…"
- "We recommended [platform] because…"
- "Confidence: 87% based on 5 evidence segments"

---

### 3.5 Mobile Adaptation

#### Layout Changes (Small screens <600px)

**Tablet (600-960px)**:
1. Left pane (context) takes 100% width above fold
2. Center pane (strategy) scrolls below
3. Right pane (rationales) becomes floating button ("?") in bottom-right corner
4. OnClick button: Drawer slides up from bottom with rationales

**Mobile (<600px)**:
1. Full-screen panes
2. Tab navigation at top: "Context | Strategy | Why"
3. Users swipe between tabs
4. Context tab: Text area + file upload (100% width)
5. Strategy tab: Jobs, ICPs, Channels stack vertically
6. Why tab: Rationales list

#### Touch Interactions
- Swipe left/right: Navigate between tabs
- Long-press on card: Context menu (edit, merge, split, delete)
- Double-tap: Inline edit mode
- Drag to reorder: Still supported

---

### 3.6 Interactions & State Management

#### Auto-Save
- Strategy is saved every 30 seconds
- OnSave: Toast notification (non-intrusive): "✓ Saved"
- Manual save button (top bar): "Save now"
- OnError: Toast: "Unable to save. [Retry]"

#### Error Handling
- **Empty context**: "Please paste or upload some context before locking jobs."
- **No jobs extracted**: "We couldn't extract any jobs from your context. Please add more information or try editing jobs manually."
- **Conflicting edits**: "This ICP was modified elsewhere. Reload to see changes." [Reload]

#### Loading States
- While analyzing context: Skeleton loader for jobs section
- While generating ICP recommendations: Skeleton loader for ICP section
- Skeleton animation: Shimmer effect (1 second loop)

#### Undo/Redo
- Keyboard: Ctrl+Z (undo), Ctrl+Shift+Z (redo)
- Limits: Last 20 actions
- Tooltip: "Undo [last action]" / "Redo [last action]"

---

### 3.7 Navigation from Strategy Workspace

**Next Steps**:
- After strategy is locked, users see banner: "Strategy complete! Ready to generate moves?"
- Button: "Generate Moves" → Navigate to `/app/[workspaceId]/moves/suggested`

**Secondary Actions**:
- Save draft: "Save & continue later" → Returns to workspace later
- Share strategy: "Share with team" → Opens share modal
- Refine context: "Add more context" → Returns to context intake

**Keyboard Shortcuts**:
- Ctrl+S: Save
- Ctrl+Z: Undo
- Ctrl+Shift+Z: Redo
- Ctrl+Enter: Generate moves (if ready)
- ? : Show keyboard shortcuts

---

## 4. Integration with Backend Systems

### 4.1 API Endpoints Required

```typescript
// Context Intake
POST /api/v1/strategy/context/add-text
POST /api/v1/strategy/context/upload-file
POST /api/v1/strategy/context/add-link
GET /api/v1/strategy/context/list
DELETE /api/v1/strategy/context/{id}

// Strategy Analysis
POST /api/v1/strategy/analyze
GET /api/v1/strategy/{id}/jobs
POST /api/v1/strategy/{id}/jobs/merge
POST /api/v1/strategy/{id}/jobs/split
PUT /api/v1/strategy/{id}/jobs/{jobId}
DELETE /api/v1/strategy/{id}/jobs/{jobId}

// ICPs
POST /api/v1/strategy/{id}/icps
PUT /api/v1/strategy/{id}/icps/{icpId}
DELETE /api/v1/strategy/{id}/icps/{icpId}
POST /api/v1/strategy/{id}/icps/{icpId}/avatar

// Channels & AISAS
GET /api/v1/strategy/{id}/channels
PUT /api/v1/strategy/{id}/channels/{icpId}/{jobId}
POST /api/v1/strategy/{id}/channels/add-platform
DELETE /api/v1/strategy/{id}/channels/remove-platform

// Rationales
GET /api/v1/strategy/{id}/explanations
GET /api/v1/strategy/{id}/explanations/cite/{citationId}
POST /api/v1/strategy/{id}/explanations/annotate

// Auto-save
POST /api/v1/strategy/{id}/save
GET /api/v1/strategy/{id}/drafts
```

### 4.2 Agent Pipeline

**Stage 1: Context Processing**
- Agent: `ContextProcessorAgent`
- Inputs: Text, files, links
- Outputs: Extracted text, transcriptions, named entities, topics, emotions
- Tools: Transcriber, OCR, Link fetcher, NLP analyzer

**Stage 2: JTBD Extraction**
- Agent: `JTBDExtractionAgent`
- Inputs: Processed context, evidence bucket
- Outputs: Jobs-to-Be-Done with circumstances, forces, anxieties
- Tools: LLM generation, Clustering, Evidence linker

**Stage 3: ICP Builder**
- Agent: `ICPBuilderAgent`
- Inputs: JTBD, context, market data
- Outputs: Proposed ICPs with traits, pain points, behaviors
- Tools: Trait extractor, Avatar generator, Health calculator

**Stage 4: Channel Mapper**
- Agent: `ChannelMapperAgent`
- Inputs: JTBD, ICPs, Platform Physics Library
- Outputs: Channel recommendations with AISAS stages
- Tools: Platform physics fetcher, AISAS stage selector

**Stage 5: Explanation Generator**
- Agent: `ExplanationAgent`
- Inputs: All previous outputs, evidence
- Outputs: Rationales with citations
- Tools: Citation linker, Rule explainer, Confidence scorer

---

## 5. Data Models

### 5.1 Strategy Workspace Data

```typescript
interface Strategy {
  id: string;
  workspaceId: string;
  name: string;
  status: 'draft' | 'analyzing' | 'ready' | 'published';
  context: ContextItem[];
  jobs: JTBD[];
  icps: ICP[];
  channels: ChannelRecommendation[];
  explanations: Explanation[];
  health: HealthMetric[];
  createdAt: Date;
  updatedAt: Date;
  savedAt: Date;
}

interface ContextItem {
  id: string;
  type: 'text' | 'file' | 'link';
  content: string;
  metadata: {
    source: 'linkedin' | 'twitter' | 'email' | 'support' | 'sales' | 'research' | 'competitor' | 'internal';
    mood: 'rant' | 'success' | 'question' | 'feature_request' | 'complaint' | 'neutral';
    date: Date;
    fileType?: string;
    fileName?: string;
    url?: string;
  };
  embedding?: number[];
  extractedEntities: {
    topics: string[];
    emotions: string[];
    keywords: string[];
  };
  createdAt: Date;
}

interface JTBD {
  id: string;
  label: string;
  why: string;
  circumstances: string;
  forces: {
    push: string[];
    pull: string[];
  };
  anxieties: string[];
  evidenceIds: string[];
  createdAt: Date;
  editedAt?: Date;
  merged?: boolean;
  mergedIntoId?: string;
}

interface ICP {
  id: string;
  name: string;
  avatar: {
    type: 'icon' | 'icon_with_letter' | 'frame';
    colors: { primary: string; secondary: string };
    imageUrl?: string;
  };
  traits: {
    industry?: string;
    size?: string;
    location?: string;
    languages?: string[];
    techStack?: string[];
    budgetSize?: string;
    [key: string]: any;
  };
  painPoints: string[];
  behaviors: string[];
  health: number; // 0-100
  mood: 'thriving' | 'needs_attention' | 'at_risk';
  confidenceScore: number; // 0-100
  evidenceIds: string[];
  createdAt: Date;
  editedAt?: Date;
}

interface ChannelRecommendation {
  id: string;
  icpId: string;
  jobId: string;
  platforms: {
    platform: 'youtube' | 'linkedin' | 'instagram' | 'x' | 'threads' | 'tiktok' | 'facebook' | 'email' | 'blog' | 'podcast';
    contentType: 'hero' | 'hub' | 'help';
    cadence: string; // e.g., "1x per month"
    recommendedLength: string; // e.g., "8-15 minutes"
    recommendedTimes: { day: string; time: string }[];
    tone: string;
    platformSpecs: any;
  }[];
  aisasStage: number; // 0-100 (Attention to Share)
  rationale: string;
  confidenceScore: number; // 0-100
}

interface Explanation {
  id: string;
  type: 'job' | 'icp' | 'channel' | 'aisas';
  refId: string; // jobId, icpId, channelId
  rationale: string;
  citations: Citation[];
  rulesFired: string[];
  confidenceScore: number;
  userAnnotation?: string;
  pinned: boolean;
}

interface Citation {
  id: string;
  sourceId: string; // contextItemId
  excerpt: string;
  inference: string;
  confidence: number;
}

interface HealthMetric {
  icpId: string;
  timestamp: Date;
  score: number; // 0-100
  basedOnMoves: number;
  positiveOutcomes: number;
  negativeOutcomes: number;
}
```

---

## Conclusion

The **Strategy Workspace** is the core hub of RaptorFlow 2.0, enabling users to transform raw context into defensible strategy through AI analysis and human refinement. Every recommendation is transparent (backed by evidence citations), editable (merge/split jobs, customize ICPs), and actionable (leads directly to move generation).

This document provides complete specifications for implementation, including:
- ✅ Three-pane layout with detailed interactions
- ✅ Context intake flow (text, files, links)
- ✅ Strategy canvas with jobs, ICPs, channels, AISAS
- ✅ Transparent rationales with evidence citations
- ✅ Mobile-responsive design
- ✅ API endpoints and data models
- ✅ Agent pipeline architecture

All components are ready for design and development.
