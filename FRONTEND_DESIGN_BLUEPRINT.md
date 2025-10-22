# RaptorFlow 2.0 – Front-End Design Blueprint

## 📋 Table of Contents

1. [Introduction & Purpose](#introduction--purpose)
2. [Visual Design System](#visual-design-system)
3. [Grid & Spacing System](#grid--spacing-system)
4. [Navigation & Shell](#navigation--shell)
5. [Onboarding & Intake](#onboarding--intake)
6. [Strategy Workspace](#strategy-workspace)
7. [Component Library](#component-library)
8. [Mobile & Responsiveness](#mobile--responsiveness)
9. [Accessibility](#accessibility)
10. [Performance Guidelines](#performance-guidelines)

---

## Introduction & Purpose

### Overview

RaptorFlow 2.0 is a **strategy-first marketing operating system** that transforms messy context into defensible strategy and actionable moves. The front-end design must:

✅ Hide complexity behind simple interactions
✅ Empower users, not overwhelm them
✅ Build trust through transparency
✅ Maintain consistency across all pages
✅ Scale from onboarding to enterprise use
✅ Support multiple ICPs, jobs, channels and moves

### Design Philosophy

- **Minimalistic**: Beautiful yet utilitarian; every element is intentional
- **Playful yet Professional**: Sophisticated without being stuffy
- **Clarity First**: Clear hierarchy, generous white space, unambiguous microcopy
- **Feedback-Driven**: Interactive feedback on every action
- **Accessible**: WCAG AA standards; inclusive by default
- **Performance**: Snappy interactions even on slower devices

---

## Visual Design System

### Color Palette

RaptorFlow uses a sophisticated four-color palette evoking warmth and trust:

| Color | Hex | Usage | Notes |
|-------|-----|-------|-------|
| **Mineshaft** | #2D2D2D | Primary text, icons, dark mode backgrounds, border emphasis | Darkest tone |
| **Akaroa** | #D7C9AE | Card backgrounds, panels, surfaces (light mode) | Main surface color |
| **Barleycorn** | #A68763 | Buttons, highlights, avatars, badges, micro-interactions | Warm mid-tone accent |
| **White Rock** | #EAE0D2 | Secondary surfaces, dividers, hover states, light backgrounds | Creates layers |

#### Use Guidelines

- **Buttons**: Primary CTAs use Barleycorn background with White Rock text
- **Secondary Buttons**: Mineshaft outline with White Rock background
- **Cards**: Akaroa background with Mineshaft text
- **Hover States**: Slightly darken or lighten surface with shadow lift
- **Contrast**: Maintain 4.5:1 ratio for WCAG AA compliance
- **Focus States**: Include underlines or outlines, not color alone

### Typography

#### Font Stack

```
Display/Headlines: Playfair Display SC (elegant, used sparingly)
Body/UI: Inter (modern sans-serif, variable weights)
Monospace: JetBrains Mono (for code, tables with numbers)
```

#### Type Scale

| Level | Size | Line Height | Weight | Usage |
|-------|------|-------------|--------|-------|
| Display | 28 px | 34 px | Bold | Page titles (Playfair) |
| Page Title | 22 px | 28 px | SemiBold | Section headers (Inter) |
| Section Heading | 18 px | 24 px | Medium | Subsection headers |
| Body | 15 px | 22 px | Regular | Main content, cards |
| Small | 13 px | 18 px | Regular | Captions, hints |
| Tiny | 11 px | 16 px | Regular | Metadata, timestamps |

#### Guidelines

- Keep line lengths under 70 characters for readability
- Use 1.4–1.6 line height for breathable text
- Use monospaced digits where alignment matters
- Break copy into digestible paragraphs or bullet lists
- Maintain consistent letter-spacing (0–0.02 em for all-caps)

### Iconography

**Icon Standards:**
- Use Lucide Icons or similar cohesive set
- Single-stroke, monochrome design
- 24 px drawn size with 2 px line weight
- Colors: Mineshaft (default) or Barleycorn (interactive)
- Filled variant only for selected states
- Always align to 8-pt grid; center within containers

**Icon Usage Examples:**
- Navigation: Strategy, Moves, Calendar, Assets, Reports, Platform Watch, ICP & Brand, Activity, Billing, Admin
- Actions: Plus, Trash, Edit, Delete, Copy, Share, Download, Upload
- Status: Check, X, Warning, Info, Error
- Navigation: Chevron, Arrow, Menu, Close

### Motion & Interactions

- **Duration**: Animations last 200–300 ms max
- **Easing**: ease-in-out for most transitions; spring for list reorders
- **Avoid**: Animating background colors or text sizes
- **Prefer**: Opacity, translate, scale for subtle effects
- **Feedback**: Ripple effect on buttons, arrow spin on progress, shimmer on loading
- **Load States**: Skeleton loaders or shimmer animations

---

## Grid & Spacing System

### Responsive Grid

RaptorFlow uses a **12-column grid with 16 px gutters** that scales across breakpoints:

#### Breakpoints

| Breakpoint | Width | Layout | Sidebar | Chat |
|-----------|-------|--------|---------|------|
| Large | ≥1280 px | Full | 72 px | 320 px |
| Medium | ≥960 px | Content Focus | 48 px | Floating Button |
| Small | ≥600 px | Single Column | Bottom Bar | Drawer |
| Mobile | <600 px | Full Screen | Hamburger | Bottom Sheet |

#### Column Widths (at 1280 px)

- **Left Nav**: 72 px (collapsible)
- **Content Area**: 12 columns (each ~88 px)
- **Right Chat**: 320 px
- **Gutters**: 16 px between columns
- **Max Content Width**: 1200 px (centered)

### Spacing & Rhythm

All spacing uses an **8-pt base unit**:

| Spacing | Use Case | Desktop | Tablet | Mobile |
|---------|----------|---------|--------|--------|
| xs (4 px) | Icon spacing | Between icons | — | — |
| sm (8 px) | Inline spacing | Icon + text | — | — |
| md (16 px) | Element spacing | Card margin, padding | Primary spacing | Primary spacing |
| lg (24 px) | Section spacing | Between sections | Between sections | Reduced on mobile |
| xl (32 px) | Major sections | Section headers | — | — |
| xxl (48 px) | Container padding | Edge padding | Reduced | Reduced |

#### Spacing Examples

```
Container edges:       24 px padding
Between elements:      16 px margin
Section separators:    32 px above heading, 24 px below
Card padding:          16 px inside; 12 px margin below
Inline spacing:        8 px between icons and text
Top navigation:        16 px padding (vertical)
```

---

## Navigation & Shell

### Left Sidebar

**Purpose**: Persistent navigation to all major areas

**Desktop Layout**:
- Width: 72 px
- Background: White Rock with subtle shadow
- Icons: 24 × 24 px, centered in 48 × 48 px containers
- Active indicator: Filled with Barleycorn on Akaroa background (rounded 6 px)

**Navigation Items** (in order):
1. Strategy – Target icon
2. Moves – Rocket icon
3. Calendar – Calendar icon
4. Assets – Image icon
5. Reports – Chart icon
6. Platform Watch – Eye icon
7. ICP & Brand – People icon
8. Activity – Clock icon
9. Billing – CreditCard icon
10. Admin – Settings icon

**States**:
- **Default**: Mineshaft icon on White Rock background
- **Hover**: Icon changes to Barleycorn; tooltip appears after 400 ms
- **Active**: Icon filled with Barleycorn; sits on Akaroa rounded rectangle (6 px radius)
- **Focus**: Outline of Barleycorn (2 px) around icon
- **Keyboard**: Tab cycles through; Arrow keys navigate; Enter activates

**Collapse Behavior**:
- Medium screens: 48 px (icon only)
- Small screens: Bottom bar with icons
- Mobile: Hamburger menu with collapsed nav

### Top Bar

**Purpose**: Global search, workspace switcher, notifications, profile menu

**Layout**:
- Background: White Rock
- Height: 56 px
- Padding: 12 px left/right, 8 px top/bottom
- Content spread: Left (workspace), center (search), right (notifications, profile)

**Components**:

#### Workspace Switcher (Left)
- Dropdown showing current workspace name
- Icon: Logo or initials avatar
- OnClick: Show list of workspaces + "Create new"
- Width: 200 px

#### Search Bar (Center)
- Width: 240 px
- Placeholder: "Search strategies, moves…"
- Icons: Magnifying glass (left), keyboard shortcut hint (right, "⌘K")
- OnFocus: Outline glows Barleycorn; icon animates
- OnInput: Real-time search results appear in dropdown below

#### Notifications (Right)
- Bell icon (24 × 24 px)
- Red dot badge if unread (8 × 8 px, positioned top-right)
- OnClick: Dropdown appears (300 px wide)
- Dropdown content: List of notifications, each 40 px high
  - Avatar (24 px), short text (1 line), timestamp (13 px gray)
- Max 8 notifications visible; scroll if more
- "Clear all" button at bottom

#### Profile Menu (Right)
- Avatar (32 × 32 px, rounded)
- OnClick: Popover appears (200 px wide)
- Items: Profile settings, Preferences, Help, Logout
- Divider between "Preferences" and "Help"

### Right Rail (Chat - Profound Mode)

**Purpose**: Persistent AI chat for strategy refinement and content generation

**Layout** (Desktop):
- Width: 320 px
- Background: White Rock
- Position: Fixed, right-aligned
- Visible by default on large screens

**Collapse Behavior**:
- Medium: Floating button (bottom-right, 56 × 56 px)
- Small: Same floating button
- Mobile: Opens as full-height bottom sheet

**Chat Structure**:
- **Header**: "Profound Mode" title + close (X) button
- **Messages**: Scrollable area with alternating backgrounds
  - User messages: Barleycorn background, white text, right-aligned
  - AI messages: Akaroa background, Mineshaft text, left-aligned
  - Timestamp (13 px, gray) below each message
  - Action icons on hover: Copy, Reply, React
- **Input**: Anchored at bottom
  - Text area (auto-expands, max 200 px)
  - Send button: Barleycorn background, white icon
  - Placeholder: "Ask anything about your strategy…"

**Behavior**:
- All interactions first update strategy before generating responses
- Chat surfaces strategy deltas (differences)
- Only then can users ask for content or clarifications

### Content Area

**Layout**:
- 12 columns on large screens
- 9 columns on medium (with 48 px left nav)
- Single column on small/mobile
- Responsive design ensures functionality at all sizes
- Components stack vertically on mobile
- Secondary info hidden behind toggles

---

## Onboarding & Intake

### Onboarding Flow

The onboarding flow consists of 6 steps, each on a separate page or modal.

#### Step 1: Welcome Screen

**Visual**:
- Full-screen view with gradient background (Mineshaft top → Akaroa bottom)
- RaptorFlow logo centered at top (120 × 120 px)
- Subtle pattern overlays for depth (opacity 0.1)

**Content**:
- Headline: "Welcome to RaptorFlow"
- Subheadline: "Let's turn your ideas into a winning strategy."
- Button: "Get Started" (Barleycorn, 160 × 48 px)
- Privacy note: "We value your privacy. We'll only use your information to build your strategy."

**Interactions**:
- Click button → proceed to Step 2
- Fade animation (300 ms) on transition

---

#### Step 2: Role Selection

**Layout**:
- Progress indicator at top (Circle 1/6, filled; circles 2-6 outline)
- Back button (top-left, text-style)
- Centered content area

**Content**:
- Headline: "What best describes you?"
- Helper text: "Selecting your role helps us tailor our suggestions."
- Four role cards (300 × 200 px each, 2 per row)

**Role Cards**:
| Role | Icon | Description |
|------|------|-------------|
| Founder | Target | Building a startup or company from scratch |
| Marketer | Megaphone | Managing marketing for an established brand |
| Creator | Star | Creating content for audience growth |
| Other | Question | Something else |

**Card States**:
- Default: Akaroa background, Mineshaft text, soft shadow
- Hover: Slight lift, shadow increases
- Selected: Barleycorn border (2 px), checkmark in top-right
- Only one selectable; selected glows Barleycorn

**Button**:
- "Continue" (primary) disabled until a card is chosen
- Positioned bottom-right

---

#### Step 3: Goal Selection

**Layout**:
- Progress indicator at top (Circle 2/6)
- Back button + title

**Content**:
- Headline: "Which goals are you aiming for?"
- Helper text: "You can choose more than one goal."
- Pill-style toggles arranged in 2 columns

**Goal Options**:
- Launch a product
- Grow social following
- Improve engagement
- Generate leads
- Expand to new market
- Other (free text input)

**Pill States**:
- Default: Akaroa background, Mineshaft text
- Selected: Barleycorn background, White Rock text, checkmark
- Multi-select enabled

**Input Field** (if "Other" selected):
- Text input (400 px wide) appears below
- Placeholder: "Tell us your goal…"

---

#### Step 4: Business Details

**Layout**:
- Progress indicator at top (Circle 3/6)
- Back button + title

**Form Fields** (80% width, max 500 px):

| Field | Type | Hint | Optional |
|-------|------|------|----------|
| Company Name | Text | "We'll use your name when we craft ICPs." | No |
| Website | URL | "Leave blank if none." | Yes |
| # Employees | Dropdown | "Use a rough estimate if unsure." | No |
| Industry | Dropdown (searchable) | "Helps us suggest relevant channels." | No |

**Validation**:
- Real-time on blur
- Error messages in red below field
- Success checkmark when valid

**Button**:
- "Continue" (primary) at bottom-right

---

#### Step 5: Context Intake

**Layout**:
- Progress indicator at top (Circle 4/6)
- Large text area (600 px wide, 200 px tall) for pasting content

**Content**:
- Headline: "Share your context"
- Helper: "Paste a rant, idea or article. Upload any files or voice notes."
- Text area placeholder: "Start typing or paste a URL here…"

**Upload Options**:
- Drag & drop area (800 × 200 px) below text area
- Label: "Drag & drop a PDF, image, video or audio. Max 1 GB total."
- Icons for: Image, PDF, Video, Audio
- File picker button

**File Handling**:
- Show file name, type, size after selection
- Progress bar for large uploads
- Remove icon (X) next to each file

**Button**:
- "Next" (primary) at bottom-right

---

#### Step 6: Review & Confirm

**Layout**:
- Progress indicator at top (Circle 5/6)
- Summary of all collected information

**Content**:
- Role: [Selected role]
- Goals: [List of selected goals]
- Company: [Name, website, employees, industry]
- Context: [First 100 characters of pasted content]

**Edit Buttons**:
- Each section has a small "Edit" button (text-style, underlined)
- OnClick: Modal opens to re-edit that section

**Buttons**:
- "Back" (secondary, outline) at bottom-left
- "Create Your Strategy" (primary, Barleycorn) at bottom-right

---

### Context Intake Page

After onboarding, users reach the Context Intake page. This is also accessible later to refresh the strategy.

#### Layout

3-column layout:
- **Left Column** (4 columns wide): Evidence Collection
- **Center Column** (6 columns wide): Raw View & Digest
- **Right Column** (2 columns wide): Preview of Strategy

#### Left Column: Evidence Collection

**Content**:
- Cards for each input type: Clipboard, Uploads, Links
- Each card (300 × 180 px):
  - Icon (24 × 24 px, Barleycorn)
  - Title ("Paste Text", "Upload Files", "Share Links")
  - Description (13 px, gray)
  - Drag & drop area (shaded background, dotted border)

**Paste Text Card**:
- Text area (400 × 150 px) with placeholder
- Character count at bottom-right
- Button: "Extract" (secondary)

**Upload Files Card**:
- Drag & drop area with icon
- OnDrop: Show file name, type, size
- Progress bar if extracting (audio transcription)
- Button: Remove (X icon)

**Add Links Card**:
- Input field (300 px wide) for URL
- OnEnter: Add URL to list
- Each URL shows as a tag with remove option

**Bottom Buttons**:
- "Clear All" (tertiary, outline) – removes all content
- "Lock Jobs" (primary, Barleycorn, disabled until jobs extracted)

#### Center Column: Raw View & Digest

**Raw View** (top 2/3):
- Scrollable area showing all uploaded content in segments
- Each segment has a background tint to distinguish type:
  - Text: Akaroa
  - Image: White Rock
  - Audio transcript: Light Mineshaft
  - Link preview: Akaroa
- Tags above each segment (13 px, gray): "Audio Transcript", "Screenshot", "Testimonial", "Link"

**Digest Panel** (bottom 1/3):
- Title: "Key Insights" (18 px, medium)
- 2-column layout; each item ~160 px tall
- Bullet points with:
  - Quote (italic, 13 px) on the left
  - Inferred insight (regular, 13 px) on the right
- Light background (White Rock) behind each pair

#### Right Column: Strategy Preview

**Content**:
- Title: "Jobs Detected" (18 px, medium)
- Progress indicator: "Extracting… 60%" (with bar)
- List of discovered jobs as pills:
  - Each pill (Barleycorn background, White Rock text)
  - Job label + brief description (1 line, 13 px)
  - Removable with X icon

**Button**:
- "Lock Jobs" (primary, disabled until at least 1 job extracted)
- OnClick: System runs ICP builder; shows loader with "Analyzing…"

---

## Strategy Workspace

### Overview

After locking jobs, users enter the Strategy Workspace where they review and refine their strategy: Jobs, ICPs, Channels, AISAS, and Moves.

### Main Layout

**Structure**:
- Top bar (workspace name, save status, share button)
- Left sidebar (nav)
- Center: Strategy cards in a grid
- Right: Explanations panel (pinned or floating)
- Bottom right: Chat rail

### Jobs Section

**Cards**:
- Dimensions: 320 × 200 px
- Header: Job label (18 px, bold, Mineshaft) + status dot (Barleycorn)
- Body: Four fields with icons
  - Why (question mark icon): "One-line summary"
  - Circumstances (clock icon): "When/where this job occurs"
  - Forces (arrow icon): "Push/pull forces"
  - Anxieties (exclamation icon): "What might block progress"
- Footer: "Merge" and "Split" buttons (tertiary, icon + text)

**Card States**:
- Default: Akaroa background, soft shadow (2 px), rounded corners (8 px)
- Hover: Lift effect (4 px shadow), slight background lighten
- Selected: Barleycorn outline (2 px), same as above
- Edited: Green checkmark in top-right corner

**Interactions**:
- Click card: Opens detail modal
- Merge: Drag one card onto another; modal asks which fields to merge
- Split: Opens dialog to select which elements form new job
- Edit fields: Pencil icon on hover; click to open input field
- Delete: Drag to trash area or context menu → "Delete"

**Microcopy**:
- "Share frustration" (for why)
- "When are customers in this situation?" (for circumstances)
- "What pushes them toward a solution?" (for forces)
- "What makes them hesitant?" (for anxieties)

---

### ICP Builder & Avatars

**Cards**:
- Larger: 400 × 240 px
- Avatar (top-left): 64 × 64 px circular image/icon
- Header: ICP name (bold, 18 px) + color bar + menu (three dots)
- Body:
  - **Traits**: Table with icon + trait text (include/exclude)
  - **Pain Points**: Bullet list (2–4 items, 13 px)
  - **Behaviors**: Typical habits (e.g., "Reads long-form on LinkedIn at 9 AM")
- Footer: Health bar (horizontal progress, 80 px wide) + mood icon (happy/sad/neutral)

**Avatar Editor** (modal):
- Three generation options:
  - Icon only (circular, 64 px)
  - Icon with letter (circular, 64 px)
  - Circular frame (border, 64 px)
- Color customization: Two sliders for primary and secondary colors (from palette)
- Toggle to invert colors
- Preview in various contexts (card, nav, chat)
- Buttons: "Generate", "Upload Custom", "Save"

**Interactions**:
- Reorder: Drag cards to set priority
- Split: Opens modal to define criteria for new ICP
- Merge: Combine ICPs; choose which traits survive
- Delete: Confirm before deletion; warn about attached moves

**Microcopy**:
- "Give your ICP a memorable name so you can refer to them easily."
- "Try starting with job title and industry."
- "This ICP is happy when you generate more engagement on LinkedIn."

---

### Channel Map & AISAS

**Grid Layout**:
- Rows: Each ICP
- Columns: Each Job
- Cells: Recommended channels and content types

**Cell Content** (on hover):
- Channel pills: YouTube, LinkedIn, Instagram, X, Threads, TikTok, Facebook
- Type pills: Hero, Hub, Help
- Tooltip: Cadence, length, posting windows, tone, platform specs

**AISAS Slider** (above grid, per Job):
- Range: 0 (Awareness) → 100 (Share)
- Segments: Attention, Interest, Search, Action, Share (5 equal parts)
- Color: Barleycorn gradient from left (awareness) to right (action)
- Moving slider updates recommendations

**Cell Interactions**:
- Add channel: Plus icon opens modal with all channels + search
- Remove channel: Small X on channel pill → confirmation
- Edit times: Click day/time opens mini calendar/time picker (respects timezone)
- Drag & drop: Reorder content type between channels (system warns on conflicts)

**Microcopy**:
- "Tell your story on YouTube"; "Spark conversation on LinkedIn"
- "Note: X posts cannot exceed 280 characters."
- "Post your Hub content on Tuesdays at 10 AM; your audience is active then."

---

### Strategy Explanations Panel

**Position**: Right sidebar, scrollable, collapsible/pinnable

**Content**:
- Sections: Jobs, ICPs, Channels, AISAS (each with icon + heading)
- Rationale: Short paragraph explaining decision
- "See more" link expands additional details
- Evidence citations: Inline links to context segments or rules

**Filter Dropdown**:
- Show only: Wisdom rules, Platform specs, Context, All

**Interactions**:
- Pinning: Pin rationale to keep visible (appears at top with colored border)
- Annotations: Button to add personal notes (stored per user)
- Tooltips: Hover over rule to highlight it

**Microcopy**:
- "We chose LinkedIn because professionals spend more time there reading long-form content."
- "Claims must be backed by data. Please add a statistic or remove the claim."

---

## Component Library

### Buttons

**Types & Styles**:

#### Primary Button
- Background: Barleycorn
- Text: White Rock (bold, 15 px)
- Padding: 12 px (vertical) × 24 px (horizontal)
- Border radius: 6 px
- Shadow: 2 px (default), 4 px (hover)
- Size: 48 × 160 px (standard)

#### Secondary Button
- Background: Transparent
- Border: 1 px Mineshaft outline
- Text: Mineshaft (15 px)
- Padding: 12 px × 24 px
- Border radius: 6 px

#### Tertiary Button
- Background: Transparent
- Text: Mineshaft, underlined
- Padding: 8 px
- No border

#### Icon Button
- Size: 48 × 48 px
- Icon: 24 × 24 px centered
- Background: Transparent (default); Akaroa (hover)
- Border radius: 6 px

**States**:
- **Default**: As above
- **Hover**: Darken background (Barleycorn → darker Barleycorn); shadow increases
- **Pressed**: Scale down to 98%
- **Disabled**: Opacity 60%; no hover effect; cursor default
- **Focus**: 2 px Barleycorn outline

**Transitions**: 100 ms ease-in-out

---

### Form Fields

**Text Input**:
- Height: 40 px
- Padding: 8 px left/right
- Border: 1 px Mineshaft, rounded 4 px
- Font: Inter, 15 px, Mineshaft
- Placeholder: Gray, 13 px
- Label: 13 px, bold, Mineshaft (above field)
- Hint text: 13 px, gray (below field)

**States**:
- **Default**: White Rock background, Mineshaft border
- **Focus**: Barleycorn border (2 px), box-shadow glow
- **Error**: Red border (2 px), red text below
- **Success**: Green checkmark (right side)
- **Disabled**: Gray background, gray text

**Text Area**:
- Min height: 80 px
- Max height: 200 px (with scroll)
- Auto-expand as user types
- Same styling as text input

**Checkbox**:
- Size: 20 × 20 px
- Border: 1 px Mineshaft (default)
- Checkmark (4 px stroke) appears on checked (Barleycorn background)
- Label: 15 px, Mineshaft (to the right)

**Dropdown/Select**:
- Height: 40 px
- Width: Variable (min 240 px)
- Border: 1 px Mineshaft, rounded 4 px
- Chevron icon (right side, 12 px, Mineshaft)
- Open state: Chevron rotates 180°; dropdown list appears below

**Date Picker**:
- Input field (same as text input)
- Calendar grid opens on focus
- Selected date highlighted (Barleycorn)
- Current date underlined

**Time Picker**:
- Input field + time selector
- Can use scroll wheels or direct input
- Respects timezone (Asia/Kolkata default for India)

**File Input**:
- Custom styled (hide default)
- Drag & drop area: 300 × 150 px, dotted border, Akaroa fill
- Icon + "Drag files here" text
- File picker button below
- After selection: Show file name, type, size

---

### Cards

**Standard Card**:
- Width: 300–400 px (depending on context)
- Background: Akaroa
- Padding: 16 px inside
- Margin: 12 px below
- Border radius: 8 px
- Shadow: 2 px (default), 4 px (hover)
- Border: None (default); Barleycorn (selected/focused)

**Card Sections**:
- Header (top 20%): Bold text, icon, menu button (three dots)
- Body (middle 60%): Content (text, list, table)
- Footer (bottom 20%): Action buttons

---

### Modals & Overlays

**Modal**:
- Max width: 600 px (desktop), 100% (mobile)
- Background: White Rock
- Padding: 24 px
- Border radius: 8 px
- Shadow: 8 px (dark overlay)
- Position: Centered on screen

**Structure**:
- Header: Title (18 px, bold) + X button (top-right, 24 × 24 px)
- Body: Content (scrollable if needed)
- Footer: Action buttons (left: secondary, right: primary)

**Overlay Backdrop**:
- Dark semi-transparent (rgba(45, 45, 45, 0.6))
- Click outside to dismiss (for non-critical modals)
- Escape key to close

**Animation**: Fade in + slide down (200 ms)

---

### Notifications & Toasts

**Toast**:
- Position: Bottom-right (desktop), top center (mobile)
- Size: 350 × 60 px
- Auto-dismiss: 4 seconds (unless hovered)
- Animation: Slide in from right (200 ms)

**Toast Types**:

| Type | Background | Icon | Use Case |
|------|-----------|------|----------|
| Success | Green border + White Rock | Check | Operation succeeded |
| Error | Red border + White Rock | X | Operation failed |
| Warning | Orange border + White Rock | Alert | Warning/caution |
| Info | Blue border + White Rock | Info | Informational |

**Content**:
- One sentence max (13 px text)
- Optional action button ("View", "Undo")

**Examples**:
- "Strategy created successfully!" (success)
- "Unable to save hook. Please try again." (error)
- "You are approaching your chat limit." (warning)
- "New platform updates available." (info)

---

### Tables

**Structure**:
- Striped rows (alternating Akaroa/White Rock for readability)
- Header row (bold, Mineshaft, Akaroa background)
- Padding: 12 px left/right, 8 px top/bottom in each cell
- Borders: 1 px between rows (light Mineshaft)

**Sortable Columns**:
- Header is clickable
- Arrow icon shows sort direction (↑ ↓)
- Active column highlighted

**Responsive**:
- On mobile: Hide less important columns or convert to accordion
- Horizontal scroll for dense tables

---

### Charts & Graphs

**Line Chart**:
- Line color: Mineshaft
- Highlight points: Barleycorn (6 px circles)
- Area under curve: Light White Rock fill
- Axes: Thin Mineshaft lines
- Tooltips on hover: Timestamp + values

**Bar Chart**:
- Bars: Barleycorn (primary), Akaroa (secondary)
- Spacing: 8 px between groups
- Axes: As above

**Pie/Donut Chart**:
- Max 6 segments
- Colors: Barleycorn, Akaroa, White Rock (rotate)
- Center label (for donut): Total or percentage
- Legend below

---

## Mobile & Responsiveness

### Responsive Strategy

**Large (≥1280 px)**:
- Full sidebar (72 px)
- Content area (12 columns)
- Chat rail (320 px) visible
- Cards in grid (2–3 per row)

**Medium (≥960 px)**:
- Sidebar collapses to 48 px
- Content area (9 columns)
- Chat rail collapses to floating button
- Cards in grid (2 per row)

**Small (≥600 px)**:
- Sidebar becomes bottom bar
- Content area (1 column)
- Chat opens as drawer
- Cards stack vertically

**Mobile (<600 px)**:
- Full-screen modals
- Bottom navigation (icons only)
- Chat as bottom sheet
- Forms stack vertically

### Touch Interactions

**Target Size**:
- Minimum 48 × 48 px for touch targets
- Extra spacing (8 px) around buttons

**Gestures**:
- Swipe left: Reveal actions (delete, archive)
- Swipe right: Go back
- Swipe up/down: Dismiss bottom sheet
- Long press: Context menu

**Feedback**:
- Ripple effect on tap
- Vibration (if available)

---

## Accessibility

### WCAG AA Compliance

**Color Contrast**:
- All text: 4.5:1 ratio minimum
- Example: Mineshaft on Akaroa = 7.2:1 ✅

**Keyboard Navigation**:
- All interactive elements: Reachable via Tab
- Tab order: Logical, left-to-right, top-to-bottom
- Skip link: "Skip to content" at top (for screen readers)
- Focus management: Move focus when modals open; return on close

**Screen Reader Support**:
- ARIA labels on all buttons and icons
- Use aria-live="polite" for dynamic updates
- Hide decorative elements: aria-hidden="true"
- Provide alt text on all images

**Keyboard Shortcuts**:
- Ctrl+K: Open search
- Ctrl+Enter: Send chat message
- Ctrl+J: Jump to Jobs card
- Escape: Close modal
- Tab: Navigate elements
- Enter: Activate focused button

**Font Size & Responsiveness**:
- Use relative units (em, rem)
- Allow browser zoom (min-zoom: 100%)
- Responsive text sizes via media queries

**Error Identification**:
- Use color + icon + text for errors
- Explain clearly: "Please enter a valid URL starting with https://"
- Link error to form field

**Video & Audio**:
- All videos: Include captions
- All audio: Provide transcripts
- YouTube Shorts (≤3 min): Display transcript

---

## Performance Guidelines

### Optimization Strategies

**Code Splitting**:
- Dynamic imports for large modules (Hook Studio, Analytics)
- Lazy load routes using Next.js dynamic import

**Image Optimization**:
- Use WebP or AVIF formats
- Responsive images with srcset
- Lazy load below-the-fold images

**Caching**:
- Cache API responses with TanStack Query
- Store local data (localStorage for user preferences)
- Service Worker for offline capability

**Prefetching**:
- Prefetch likely next routes
- Prefetch strategy data when user enters workspace

**Metrics Targets**:
- Largest Contentful Paint (LCP): < 2.5 s
- First Input Delay (FID): < 100 ms
- Cumulative Layout Shift (CLS): < 0.1

### Bundle Size

- Main bundle: < 150 KB (gzipped)
- Code splitting: Route-based chunks
- Tree shaking: Remove unused code
- Minification: Terser for JavaScript, Lightning CSS for styles

### Loading States

**Skeleton Screens**:
- Show after 300 ms (not on instant loads)
- Match final layout shape
- Shimmer animation (light-to-right, 1 s duration)
- Color: Gradient between White Rock and Akaroa

**Progress Indicators**:
- Determinate: Use progress bar (% complete)
- Indeterminate: Use spinner (for unknown duration)
- Percentage: Display "Extracting… 60%"

---

## Brand Voice & Tone

### Voice Guidelines

- **Friendly**: Warm tone, speak as if guiding a colleague
- **Confident**: Offer suggestions decisively without arrogance
- **Instructive**: Provide clear directions and examples
- **No jargon**: Replace buzzwords with plain language
- **Positive**: Focus on achievements and next steps

### Tone by Context

| Context | Tone | Example |
|---------|------|---------|
| Onboarding | Encouraging, excited | "We're excited to help you craft a killer strategy!" |
| Errors | Calm, helpful | "Oops! We couldn't publish that move. Here's how to fix it…" |
| Reports | Objective, concise | "Average dwell time increased by 20% compared to baseline." |
| Notifications | Urgent, actionable | "Move scheduled for Oct 25 at 10 AM. Reply to first 3 comments within 30 min." |

### Microcopy Principles

1. **Clarity**: Use simple sentences; answer "what?", "why?", "next?"
2. **Action**: Use verbs ("Create", "Upload", "Review")
3. **Empathy**: Acknowledge progress ("Nice work! You've created your first ICP.")
4. **Consistency**: Use same terminology throughout (not "project" + "strategy")
5. **Brevity**: One sentence for buttons and hints; 2–3 for explanations

---

## Conclusion

This Front-End Design Blueprint serves as the comprehensive guide for RaptorFlow 2.0's user interface. Every page, component, and interaction has been specified to ensure consistency, accessibility, and delightful user experience.

**Key Principles to Remember**:
✅ Simplicity over complexity
✅ Clarity over cleverness
✅ Consistency over variation
✅ Accessibility over exclusivity
✅ Performance over fancy animations

Use this blueprint as your source of truth during design and development. When ambiguity arises, prioritize user empowerment and transparency. Iterate based on user feedback while maintaining alignment with these core design principles.

---

**Document Status**: Complete & Ready for Implementation
**Last Updated**: 2025
**Next Review**: After Q1 User Testing
