# RaptorFlow 2.0 – Page Specifications

## 📑 Complete Page-by-Page Blueprint

This document provides detailed specifications for every page in RaptorFlow 2.0, including layout, components, interactions, and microcopy.

---

## Table of Contents

1. [Welcome & Onboarding](#welcome--onboarding-pages)
2. [Context Intake](#context-intake-page)
3. [Strategy Workspace](#strategy-workspace)
4. [Move Management](#move-management)
5. [Calendar & Scheduling](#calendar--scheduling)
6. [Reports & Analytics](#reports--analytics)
7. [Settings & Account](#settings--account)

---

## Welcome & Onboarding Pages

### Page 1: Welcome Screen

**URL**: `/welcome` or `/` (if not authenticated)

**Purpose**: Introduce RaptorFlow and encourage sign-up

**Layout**:
```
┌─────────────────────────────────┐
│     Full-screen gradient        │
│     (Mineshaft → Akaroa)        │
│                                 │
│         RaptorFlow Logo         │
│         (120×120 px)            │
│                                 │
│    Welcome to RaptorFlow        │
│                                 │
│  Let's turn your ideas into     │
│   a winning strategy.           │
│                                 │
│      [Get Started] button       │
│                                 │
│  We value your privacy notice   │
└─────────────────────────────────┘
```

**Key Elements**:
- Logo: Centered, 120×120 px
- Headline: "Welcome to RaptorFlow" (Playfair 28 px, bold)
- Subheadline: "Let's turn your ideas into a winning strategy." (Inter 18 px, medium)
- Primary CTA: "Get Started" (Barleycorn button, 160×48 px)
- Privacy note: 13 px gray text

**Interactions**:
- Click "Get Started" → Navigate to Step 2 (Role Selection)
- Smooth fade transition (300 ms)

**Mobile Adaptation**:
- Same layout, full viewport
- Button scales to 100% width on mobile

---

### Page 2: Role Selection

**URL**: `/onboarding/role`

**Purpose**: Determine user persona for tailored suggestions

**Layout**:
```
┌────────────────────────────────┐
│  Progress: ● ○ ○ ○ ○ ○        │ ← Step indicator
│  [← Back]                      │
├────────────────────────────────┤
│                                │
│    What best describes you?    │ ← Headline
│                                │
│  Selecting your role helps us  │
│  tailor our suggestions.       │ ← Helper text
│                                │
│  ┌──────────────┐              │
│  │ Founder      │              │ ← Role cards
│  │ [Icon]       │              │
│  │ Building...  │              │
│  └──────────────┘              │
│
│  [Continue button]             │
└────────────────────────────────┘
```

**Components**:

**Progress Indicator** (Top):
- 6 circles (one for each step)
- Current step: Filled with Barleycorn
- Future steps: Outline with Mineshaft

**Role Cards** (Grid 2×2):
- Each 300×200 px
- Akaroa background, Mineshaft text
- Icon (48 px, Barleycorn)
- Title (18 px, bold)
- Description (13 px, regular)

**Role Options**:
| Role | Icon | Description |
|------|------|-------------|
| Founder | Target | Building a startup or company from scratch |
| Marketer | Megaphone | Managing marketing for an established brand |
| Creator | Star | Creating content for audience growth |
| Other | Help Circle | Something else entirely |

**Card States**:
- Hover: Lift effect (shadow increases)
- Selected: Barleycorn border (2 px), checkmark (top-right)
- Only one selectable

**Buttons**:
- "Continue" (primary): Bottom-right, disabled until role selected
- "Back" (text-style): Top-left

**Mobile**:
- Cards stack vertically (100% width)
- Back button moves to top

---

### Page 3: Goal Selection

**URL**: `/onboarding/goals`

**Purpose**: Understand user's primary marketing objectives

**Layout**:
```
┌────────────────────────────────┐
│  Progress: ● ● ○ ○ ○ ○        │
│  [← Back]                      │
├────────────────────────────────┤
│                                │
│   Which goals are you          │
│   aiming for?                  │
│                                │
│  You can choose more than      │
│  one goal.                     │
│                                │
│  [✓ Launch a product]          │
│  [ Grow social following]      │
│  [✓ Improve engagement]        │
│  [ Generate leads]             │
│                                │
│  [Back]           [Continue]   │
└────────────────────────────────┘
```

**Goal Options** (Pill toggles, 2 per row):
1. Launch a product
2. Grow social following
3. Improve engagement
4. Generate leads
5. Expand to new market
6. Other (→ free text input)

**Pill Styling**:
- Default: Akaroa background, Mineshaft text
- Selected: Barleycorn background, White Rock text
- Multi-select enabled (checkmarks appear)

**Other Input** (Conditional):
- Text input (400 px wide)
- Appears below pills if "Other" selected
- Placeholder: "Tell us your goal…"

**Mobile**:
- Pills stack as single column
- Full width

---

### Page 4: Business Details

**URL**: `/onboarding/business`

**Purpose**: Capture company information for context

**Layout**:
```
┌────────────────────────────────┐
│  Progress: ● ● ● ○ ○ ○        │
│  [← Back]                      │
├────────────────────────────────┤
│                                │
│   Tell us about your           │
│   business                     │
│                                │
│  [Company Name Input]          │
│  Hint: We'll use...            │
│                                │
│  [Website URL Input]           │
│  Hint: Leave blank if none     │
│                                │
│  [# Employees Dropdown]        │
│  Hint: Rough estimate OK       │
│                                │
│  [Industry Dropdown]           │
│  Hint: Helps us suggest...     │
│                                │
│  [Back]           [Continue]   │
└────────────────────────────────┘
```

**Form Fields** (80% width, max 500 px):

| Field | Type | Required | Hint |
|-------|------|----------|------|
| Company Name | Text | Yes | "We'll use your name when we craft ICPs." |
| Website | URL | No | "Leave blank if none." |
| # Employees | Dropdown | Yes | Options: 1-10, 11-50, 51-200, 200+ |
| Industry | Dropdown | Yes | Searchable; 50+ options |

**Validation**:
- Real-time on blur
- Error messages in red (13 px)
- Success checkmarks on valid fields
- Continue button disabled until all required fields valid

**Mobile**:
- Fields stack full-width
- Dropdowns expand to full width

---

### Page 5: Context Intake

**URL**: `/onboarding/context`

**Purpose**: Collect content/context for strategy building

**Layout**:
```
┌────────────────────────────────┐
│  Progress: ● ● ● ● ○ ○        │
│  [← Back]                      │
├────────────────────────────────┤
│                                │
│   Share your context           │
│                                │
│  Paste a rant, idea or         │
│  article. Upload any files     │
│  or voice notes.               │
│                                │
│  [Large text area]             │
│  (600×200 px)                  │
│                                │
│  [Drag & drop file area]       │
│  (800×200 px)                  │
│                                │
│  [Back]           [Next]       │
└────────────────────────────────┘
```

**Text Area**:
- 600 px wide × 200 px tall
- Auto-expands (max 300 px)
- Placeholder: "Start typing or paste a URL here…"
- Character count (bottom-right)

**File Upload**:
- Drag & drop area (800×200 px)
- Dotted border, Akaroa fill
- Icons for: Image, PDF, Video, Audio
- File picker button ("Choose files")
- Supported: PDF, PNG, JPG, MP4, WAV, M4A (max 1 GB total)

**File Handling**:
- Show file name, type, size after upload
- Progress bar for large uploads
- Remove button (X icon) next to each file

**Mobile**:
- Text area 100% width
- Drag & drop area 100% width
- Smaller height (150 px)

---

### Page 6: Review & Confirm

**URL**: `/onboarding/confirm`

**Purpose**: Review all collected information before strategy creation

**Layout**:
```
┌────────────────────────────────┐
│  Progress: ● ● ● ● ● ○        │
│  [← Back]                      │
├────────────────────────────────┤
│                                │
│   Almost there!                │
│   Review your information      │
│                                │
│  Role                 [Edit]   │
│  ├ Founder                     │
│                                │
│  Goals                [Edit]   │
│  ├ Launch a product            │
│  ├ Improve engagement          │
│                                │
│  Company              [Edit]   │
│  ├ Name: Acme Inc.            │
│  ├ Website: acme.com          │
│  ├ Employees: 11-50           │
│  ├ Industry: Tech             │
│                                │
│  Context              [Edit]   │
│  ├ 1 text block                │
│  ├ 2 files (image, video)      │
│                                │
│  [Back]    [Create Strategy]   │
└────────────────────────────────┘
```

**Summary Sections**:
1. **Role**: Selected role + Edit button
2. **Goals**: List of selected goals + Edit button
3. **Company**: Key details + Edit button
4. **Context**: Summary of uploaded files + Edit button

**Edit Buttons** (each 36×36 px):
- Text-style, Barleycorn
- OnClick: Open modal to re-edit that section
- Smooth modal transition (200 ms)

**Primary CTA**:
- "Create Your Strategy" (Barleycorn, 160×48 px)
- Bottom-right
- OnClick: POST /api/onboarding/complete → Redirect to Context Intake page with loader

**Mobile**:
- Sections stack full-width
- Edit buttons aligned right

---

## Context Intake Page

### Page: Context Intake

**URL**: `/app/[workspaceId]/context`

**Purpose**: Upload and manage context; initialize strategy building

**Layout** (3-column grid):
```
┌──────────────────────────────────────────────┐
│         Header: Context Intake               │
│         [Save] [Lock Jobs] buttons           │
├─────────────────┬──────────────┬─────────────┤
│  Column 1 (4)   │  Column 2 (6)│  Column 3(2)│
│  Evidence       │  Raw View    │  Jobs       │
│  Collection     │  & Digest    │  Preview    │
│                 │              │             │
│  - Paste Text   │ ┌──────────┐ │ ┌─────────┐│
│  - Upload Files │ │ Segment 1│ │ │ Job 1   ││
│  - Add Links    │ │ Segment 2│ │ │ Job 2   ││
│                 │ │ Digest   │ │ │ Progres ││
│  [Clear All]    │ └──────────┘ │ └─────────┘│
│  [Lock Jobs]    │              │ [Lock Jobs]│
└─────────────────┴──────────────┴─────────────┘
```

### Column 1: Evidence Collection (4 columns, 400 px)

**Components** (Cards):

#### Paste Text Card
- Title: "Paste Text"
- Icon: Clipboard (24 px, Barleycorn)
- Text area (300×120 px)
- "Extract" button (secondary)
- Character count (bottom-right)

#### Upload Files Card
- Title: "Upload Files"
- Icon: Upload (24 px, Barleycorn)
- Drag & drop area (300×120 px)
- File picker button
- After upload: Show file name, type, size + progress bar
- Remove button (X icon) on hover

#### Add Links Card
- Title: "Add Links"
- Icon: Link (24 px, Barleycorn)
- URL input (300 px wide)
- OnEnter: Add to list
- Each URL shows as tag with remove option

**Bottom Actions**:
- "Clear All" (tertiary button): Removes all content
- "Lock Jobs" (primary button): Disabled until jobs extracted

### Column 2: Raw View & Digest (6 columns, 600 px)

**Raw View** (top 60%):
- Scrollable container
- Each content segment has:
  - Background tint (Akaroa for text, White Rock for images, etc.)
  - Tag above (13 px gray)
  - Content displayed as-is
  - 16 px padding, 12 px margin below

**Segment Tags**:
- "Text Block"
- "Audio Transcript"
- "Screenshot"
- "Video Frame"
- "URL Preview"

**Digest Panel** (bottom 40%):
- Title: "Key Insights" (18 px, medium)
- 2-column layout
- Each item ~160 px tall
- Quote (italic, 13 px) + Insight (regular, 13 px)
- Light background (White Rock) behind each pair
- Hovering over insight scrolls raw view to source segment

### Column 3: Strategy Preview (2 columns, 200 px)

**Content**:
- Title: "Jobs Detected" (18 px, medium)
- Progress bar: "Extracting… 60%"
- List of discovered jobs as pills:
  - Barleycorn background, White Rock text
  - Job label (15 px) + description (1 line, 13 px)
  - Remove button (X) on hover

**Button** (bottom):
- "Lock Jobs" (primary, large, full-width)
- Disabled until ≥1 job extracted
- OnClick: Run ICP builder; show loader with "Analyzing…"
- Redirect to Strategy Workspace

---

## Strategy Workspace

### Page: Strategy Overview

**URL**: `/app/[workspaceId]/strategy`

**Purpose**: Central hub for strategy refinement, JTBD, ICPs, channels, AISAS

**Layout**:
```
┌────────────────────────────────────────────┐
│ [Strategy Name]  [Save]  [Share] [+]       │
├────────────────────────────────────────────┤
│                                            │
│  ┌─Jobs──────┐ ┌─ICPs──────┐              │
│  │ Job cards │ │ ICP cards │              │
│  │ in grid   │ │ in grid   │ ←Explanations│
│  └───────────┘ └───────────┘              │
│                                            │
│  ┌─Channels & AISAS─────────────────────┐ │
│  │ Grid: ICPs × Jobs                    │ │
│  │ Cells: Channel recommendations       │ │
│  └────────────────────────────────────┌─┘ │
│                                       [Chat]
└────────────────────────────────────────────┘
```

**Top Bar**:
- Left: Workspace name (22 px, bold)
- Center: Breadcrumb (Strategy > [Workspace])
- Right: Save, Share, + (add section)

**Sections**:
1. **Jobs** (Top-left): Grid of job cards (320×200 px)
2. **ICPs** (Top-right): Grid of ICP cards (400×240 px)
3. **Channels & AISAS** (Bottom): Full-width matrix
4. **Explanations** (Right sidebar, 320 px): Collapsible panel

**Mobile**:
- Single column layout
- Jobs, then ICPs, then Channels
- Explanations as accordion

---

## Move Management

### Page: Suggested Moves

**URL**: `/app/[workspaceId]/moves/suggested`

**Purpose**: Review AI-generated move suggestions

**Layout**:
```
┌────────────────────────────────────────────┐
│ Suggested Moves              [Filter]      │
├────────────────────────────────────────────┤
│                                            │
│  ┌──────────────┐ ┌──────────────┐       │
│  │ LinkedIn     │ │ YouTube      │       │
│  │ Carousel     │ │ Short        │       │
│  │              │ │              │       │
│  │ #1 of 8      │ │ #2 of 8      │       │
│  │              │ │              │       │
│  │ Raise dwell  │ │ Increase CTR │       │
│  │ time to 60s  │ │ to 8%        │       │
│  │              │ │              │       │
│  │ Assumption:  │ │ Assumption:  │       │
│  │ Pros engage  │ │ Shorts... │  │       │
│  │              │ │              │       │
│  │ [Budget bar] │ │ [Budget bar] │       │
│  │              │ │              │       │
│  │[Skip] [Accept]│ │[Skip] [Accept]│      │
│  └──────────────┘ └──────────────┘       │
│                                            │
│  ┌──────────────┐                         │
│  │ ... more     │                         │
│  └──────────────┘                         │
└────────────────────────────────────────────┘
```

**Card Structure** (300×240 px per card, 2 per row):

| Section | Content | Size |
|---------|---------|------|
| Header | Platform icon + Type badge + "#X of Y" | — |
| Title | Move title (e.g., "LinkedIn Carousel – Bank Rant") | 18 px, bold |
| Objective | Objective + lead KPI | 15 px |
| Assumption | Description (2 lines) | 13 px |
| Budget | Progress bar + token usage estimate | — |
| Actions | "Skip" (secondary) + "Accept & Edit" (primary) | — |

**Interactions**:
- Accept & Edit: Open Move Detail page
- Skip: Remove from list; log reason
- Drag: Reorder suggestions (visual only, doesn't affect execution)

**Filter Dropdown** (Right):
- Show moves for: All ICPs, specific ICP
- Show moves for: All Jobs, specific Job
- Reset filter

**Mobile**:
- Single column (1 card per row)
- Full width

---

### Page: Move Detail

**URL**: `/app/[workspaceId]/moves/[moveId]`

**Purpose**: Review and refine a specific move before execution

**Layout**:
```
┌─────────────────────────────────────────┐
│ Strategy > Moves > [Move Name] [← Back]│
├─────────────────────────────────────────┤
│  [About] [Plan] [Budget] tabs          │
├─────────────────────────────────────────┤
│                                         │
│  About Tab:                            │
│  ├ Objective (1-2 sentences)           │
│  ├ KPI & Assumption                    │
│  ├ Context (Job + ICP links)           │
│  ├ Risks (flagged by Wisdom Engine)    │
│  └ Decision (Pending/Scale/Revise/Kill)│
│                                         │
│  [Save Draft] [Proceed to Hook Studio]│
│                                         │
└─────────────────────────────────────────┘
```

**Tabs**:

#### About Tab
- **Objective**: 1-2 sentence summary (textarea)
- **KPI & Assumption**: Highlighted box with lead metric and assumption
- **Context**: Links to Job card and ICP card (clickable)
- **Risks**: List of risks from Wisdom Engine
  - "High risk of clickbait due to dramatic title"
  - "No supporting evidence; add statistic"
- **Decision**: Badge showing status (Pending, Scale, Revise, Kill)

#### Plan Tab
- **Packaging Checklist**: Form fields
  - Title (required, 13 px hint: "60-100 characters")
  - Hook(s) (required)
  - Thumbnail/cover (conditional)
  - CTA (required)
  - Duration (conditional)
  - Slides (conditional)
  - Hashtags (optional)
- **Platform Specs**: Compact card listing platform constraints
- **First-Hour Protocol**: Checklist of actions
- **Scheduling**: Date/time picker

#### Budget Tab
- **Token Estimate**: Stacked bar (core 80%, discretionary 20%)
- **Time Estimate**: Rough time to complete
- **Cost Adjustments**: Toggles to trade features for cost

**Buttons**:
- "Save Draft" (secondary): Saves without proceeding
- "Proceed to Hook Studio" (primary): Moves to hook creation
- "Delete" (text-style, red): Remove move with confirmation

**Mobile**:
- Tabs stack; only one visible
- Full-width form fields

---

## Calendar & Scheduling

### Page: Calendar View

**URL**: `/app/[workspaceId]/calendar`

**Purpose**: View and manage posting schedule across platforms

**Layout**:
```
┌──────────────────────────────────────────────────┐
│ Calendar          [Month] [Week] [List] [Sync]  │
├────────┬──────────────────────────────────────┤
│Filters │ Mon Oct 21 │ Tue Oct 22 │ Wed Oct 23  │
│        │            │            │             │
│ ICP    │ [Hero]     │[Hub][Help] │             │
│[✓] All │            │            │             │
│[ ] Café│ LinkedIn   │ LinkedIn   │             │
│[ ] Tech│ Carousel   │ Thread     │             │
│        │            │            │             │
│ Platform           │ Instagram  │ YouTube     │
│[✓] All│   Reel     │ Reel       │             │
│[ ] YT │            │            │             │
│[ ] LI │──────────────────────────────────────│
│[ ] IG │ [Hero]     │            │[Hub]        │
│[ ] X  │ YouTube    │            │ LinkedIn    │
│       │ Short      │            │ Newsletter  │
│       │            │            │             │
└────────┴──────────────────────────────────────┘
```

**Layout Details**:

**Left Sidebar** (Filters):
- **ICPs**: Checkboxes for each (select/deselect all)
- **Platforms**: Checkboxes for each (select/deselect all)

**Main Calendar** (Timeline):
- Horizontal timeline (days)
- Blocks representing moves:
  - Hero: Barleycorn fill, tall
  - Hub: Akaroa fill + Barleycorn border
  - Help: White Rock fill + Mineshaft border
- Each block shows platform + move title
- Hovering shows details tooltip

**Legend** (Bottom):
- Hero = Tall block + color code
- Hub = Border style
- Help = Light background

**Interactions**:
- Drag & drop to reschedule (shows confirmation modal)
- Click move → Open detail modal
- + button (bottom-right) → Add new move or schedule existing

**View Toggles** (Top):
- Month: Full calendar grid
- Week: 7-column timeline
- List: Vertical list of moves sorted by date

**Sync Button** (Top-right):
- OnClick: Connect Google Calendar or Outlook
- After auth, moves appear as events

**Mobile**:
- List view by default
- Swipe left/right for date navigation

---

## Reports & Analytics

### Page: Reports Dashboard

**URL**: `/app/[workspaceId]/reports`

**Purpose**: Analyze performance across moves, platforms, ICPs, time

**Layout**:
```
┌─────────────────────────────────────────┐
│ Reports        [Date Range] [Export]   │
├─────────────────────────────────────────┤
│ [Overview] [By ICP] [By Platform] [By KPI]
├─────────────────────────────────────────┤
│                                         │
│ Filters:                               │
│ [Date Range ▼]  [ICP ▼]  [Status ▼]  │
│                                         │
│ ┌─────────────┐  ┌─────────────┐      │
│ │ Line Chart  │  │ Bar Chart   │      │
│ │ CTR Trend   │  │ Top Moves   │      │
│ └─────────────┘  └─────────────┘      │
│                                         │
│ ┌────────────────────────────────┐     │
│ │ Table: All Moves (sortable)    │    │
│ │                                │     │
│ │ Title | Platform | CTR | Saves│    │
│ └────────────────────────────────┘     │
│                                         │
└─────────────────────────────────────────┘
```

**Tabs**:
1. **Overview**: Summary metrics (total CTR, saves, shares)
2. **By ICP**: Performance breakdown per ICP
3. **By Platform**: Comparison of platform performance
4. **By KPI**: Focus on lead metric (CTR, dwell time, etc.)

**Charts**:
- **Line Chart**: CTR trend over time
- **Bar Chart**: Top 5 moves by CTR
- **Pie Chart**: Distribution of Hero/Hub/Help

**Table** (Dense):
- Sortable columns: Title, Platform, Type, CTR, AVD, Saves, Shares
- Hover for full details
- Click row to open Receipt

**Filters** (Persistent):
- Date range (date picker)
- ICP (multi-select dropdown)
- Job (multi-select)
- Platform (multi-select)
- Status (Draft, Scheduled, Published)

**Mobile**:
- Charts stack vertically
- Table converts to accordion (one row per move)

---

## Settings & Account

### Page: Account Settings

**URL**: `/app/[workspaceId]/settings/account`

**Purpose**: Manage user profile and preferences

**Layout**:
```
┌─────────────────────────────────────────┐
│ Settings    [Account] [Workspace]      │
├─────────────────────────────────────────┤
│                                         │
│ Profile Section                        │
│ ┌─────────────────────────────────┐   │
│ │ [Avatar] Display Name: [Input]  │   │
│ │          Email: you@email.com   │   │
│ └─────────────────────────────────┘   │
│                                         │
│ Notifications                          │
│ [✓] Weekly summary email               │
│ [✓] Receipts notifications             │
│ [ ] Platform updates                   │
│                                         │
│ Theme                                  │
│ [ ] Light  [✓] Dark  [ ] Auto         │
│                                         │
│ Language                               │
│ [English ▼]  (Reload to apply)        │
│                                         │
│ Keyboard Shortcuts                     │
│ [View/Edit shortcuts]                  │
│                                         │
│ [Save Changes] button                  │
│                                         │
└─────────────────────────────────────────┘
```

**Profile Section**:
- Avatar (64×64 px): Click to upload new image
- Display Name: Text input (250 px)
- Email: Read-only text (gray)

**Notifications**:
- Toggles for:
  - Weekly summary email
  - Receipt notifications
  - Platform updates
  - Approaching quotas

**Theme**:
- Radio buttons: Light, Dark, Auto (sync with system)
- Instant switch on selection

**Language**:
- Dropdown with all supported languages
- Shows current locale (e.g., "हिन्दी")
- Note: "Reload to apply changes"

**Keyboard Shortcuts**:
- Link: "View/Edit shortcuts"
- OnClick: Open modal showing all shortcuts with toggles to customize

**Save Button** (Primary):
- Bottom-left
- Disabled until changes made
- OnClick: POST /api/settings/account → Toast notification

---

## Conclusion

This page specifications document provides complete guidance for every page in RaptorFlow 2.0. Each page includes:
- Detailed layout diagrams
- Component specifications
- Interaction patterns
- Mobile adaptations
- Microcopy guidelines

Use this as your source of truth during front-end development. Every page should follow these specifications exactly to ensure consistency and usability across the application.

---

**Document Status**: Complete & Ready for Implementation
**Last Updated**: 2025
