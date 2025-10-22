# RaptorFlow 2.0 – Component Specifications

## 📖 Overview

This document provides detailed technical specifications for every reusable component in RaptorFlow 2.0. Use these specifications as the blueprint for component development, ensuring consistency across the application.

**Format**: Each component includes:
- Purpose & usage
- Props/parameters
- States (default, hover, active, disabled, loading, error)
- Accessibility requirements
- Code examples (HTML/CSS pseudo-code)

---

## Table of Contents

1. [Core Components](#core-components)
2. [Form Components](#form-components)
3. [Data Display Components](#data-display-components)
4. [Navigation Components](#navigation-components)
5. [Feedback Components](#feedback-components)
6. [Layout Components](#layout-components)

---

## Core Components

### Button Component

**Purpose**: Trigger actions or submit forms

**Variants**:
- `primary` – Barleycorn background, White Rock text
- `secondary` – Mineshaft outline, transparent background
- `tertiary` – Text only, underlined
- `icon` – Icon only, no text

**Props**:

```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'tertiary' | 'icon';
  size: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
  onClick: () => void;
  children: ReactNode;
  className?: string;
  ariaLabel?: string;
}
```

**Sizes**:

| Size | Height | Padding | Font Size |
|------|--------|---------|-----------|
| sm | 36 px | 8 px × 12 px | 13 px |
| md | 48 px | 12 px × 24 px | 15 px |
| lg | 56 px | 16 px × 32 px | 16 px |

**States**:

```css
/* Default */
.button-primary {
  background: #A68763; /* Barleycorn */
  color: #EAE0D2; /* White Rock */
  border: none;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: all 100ms ease-in-out;
}

/* Hover */
.button-primary:hover {
  background: #8B6F52; /* Darker Barleycorn */
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}

/* Pressed */
.button-primary:active {
  transform: scale(0.98);
}

/* Disabled */
.button-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}

/* Focus */
.button-primary:focus {
  outline: 2px solid #A68763;
  outline-offset: 2px;
}
```

**HTML Example**:

```html
<!-- Primary Button -->
<button class="button button-primary" aria-label="Create new strategy">
  <span>Create Strategy</span>
</button>

<!-- Icon Button -->
<button class="button button-icon" aria-label="Edit">
  <svg class="icon" viewBox="0 0 24 24"><!-- pencil icon --></svg>
</button>

<!-- Loading State -->
<button class="button button-primary" disabled>
  <span class="spinner"></span>
  Creating…
</button>
```

**Accessibility**:
- Always provide `ariaLabel` for icon buttons
- Use `disabled` attribute (not just visual)
- Ensure 4.5:1 color contrast
- Focus outline visible and distinct

---

### Card Component

**Purpose**: Container for related content

**Props**:

```typescript
interface CardProps {
  variant?: 'default' | 'interactive' | 'highlight';
  padding?: 'sm' | 'md' | 'lg';
  hoverable?: boolean;
  selected?: boolean;
  onClick?: () => void;
  children: ReactNode;
  className?: string;
}
```

**Structure**:

```
┌─────────────────────────┐
│ Header (optional)       │  ← bold, 18px
├─────────────────────────┤
│ Content Area            │  ← body text, 15px
│ Can contain:            │
│ - Text                  │
│ - Lists                 │
│ - Forms                 │
│ - Images                │
├─────────────────────────┤
│ Footer Actions (opt.)   │  ← buttons
└─────────────────────────┘
```

**CSS**:

```css
.card {
  background: #D7C9AE; /* Akaroa */
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: all 200ms ease-in-out;
}

.card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
  transform: translateY(-2px);
}

.card.selected {
  border: 2px solid #A68763; /* Barleycorn */
}

.card-header {
  font-size: 18px;
  font-weight: 600;
  color: #2D2D2D; /* Mineshaft */
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-content {
  font-size: 15px;
  line-height: 1.5;
  color: #2D2D2D;
}

.card-footer {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
```

**HTML Example**:

```html
<div class="card card-interactive">
  <div class="card-header">
    <h3>LinkedIn Carousel – Bank Rant</h3>
    <button class="button button-icon" aria-label="More options">
      <svg><!-- three-dot menu --></svg>
    </button>
  </div>

  <div class="card-content">
    <p><strong>Objective:</strong> Raise dwell time to 60 seconds</p>
    <p><strong>Assumption:</strong> Professionals engage more with carousel formats on LinkedIn</p>
  </div>

  <div class="card-footer">
    <button class="button button-secondary">Skip</button>
    <button class="button button-primary">Accept & Edit</button>
  </div>
</div>
```

---

### Modal Component

**Purpose**: Display focused content/forms in an overlay

**Props**:

```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  size?: 'sm' | 'md' | 'lg'; // default: md (600px)
  children: ReactNode;
  footer?: ReactNode;
  closeOnBackdropClick?: boolean; // default: false
}
```

**Layout**:

```
┌──────────────────────────────┐
│ Title              [X] Close  │  ← 24px height
├──────────────────────────────┤
│                              │
│  Content (scrollable)        │
│  Max height: 80vh            │
│                              │
├──────────────────────────────┤
│ [Cancel]        [Primary]    │  ← 56px height
└──────────────────────────────┘
```

**CSS**:

```css
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(45, 45, 45, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  animation: fadeIn 200ms ease-in-out;
}

.modal {
  background: #EAE0D2; /* White Rock */
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  max-height: 90vh;
  width: 90%;
  max-width: 600px;
  display: flex;
  flex-direction: column;
  animation: slideDown 200ms ease-in-out;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #D7C9AE;
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #2D2D2D;
}

.modal-content {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 24px;
  border-top: 1px solid #D7C9AE;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

**Keyboard Behavior**:
- Escape key closes modal
- Tab traps within modal when open
- Focus returns to trigger element on close

---

## Form Components

### Text Input

**Purpose**: Single-line text input

**Props**:

```typescript
interface TextInputProps {
  label: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  hint?: string;
  disabled?: boolean;
  type?: 'text' | 'email' | 'password' | 'url';
  required?: boolean;
  ariaLabel?: string;
}
```

**HTML Structure**:

```html
<div class="form-field">
  <label for="company-name">Company Name</label>
  <input
    id="company-name"
    type="text"
    class="text-input"
    placeholder="Enter your company name"
    required
  />
  <span class="form-hint">We'll use your name when we craft ICPs.</span>
</div>
```

**CSS**:

```css
.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field label {
  font-size: 13px;
  font-weight: 600;
  color: #2D2D2D;
}

.text-input {
  height: 40px;
  padding: 8px 12px;
  border: 1px solid #2D2D2D;
  border-radius: 4px;
  font-size: 15px;
  font-family: Inter, sans-serif;
  background: #EAE0D2;
  color: #2D2D2D;
  transition: all 200ms ease-in-out;
}

.text-input:focus {
  outline: none;
  border-color: #A68763;
  box-shadow: 0 0 0 2px rgba(166, 135, 99, 0.2);
}

.text-input:disabled {
  background: #D7C9AE;
  color: #999;
  cursor: not-allowed;
}

.text-input.error {
  border-color: #DC2626;
}

.form-hint {
  font-size: 13px;
  color: #666;
}

.form-error {
  font-size: 13px;
  color: #DC2626;
}
```

**States**:
- Default: White Rock background, Mineshaft border
- Focus: Barleycorn border, subtle glow
- Error: Red border, error text below
- Success: Green checkmark (right side)

---

### Text Area

**Purpose**: Multi-line text input

**Props**:

```typescript
interface TextAreaProps {
  label: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  minHeight?: number; // default: 80px
  maxHeight?: number; // default: 200px
  error?: string;
  charLimit?: number;
  showCharCount?: boolean;
}
```

**HTML**:

```html
<div class="form-field">
  <label for="context">Share Your Context</label>
  <textarea
    id="context"
    class="text-area"
    placeholder="Paste a rant, idea or article…"
    rows="4"
  ></textarea>
  <span class="char-count">245 / 500 characters</span>
</div>
```

**CSS**:

```css
.text-area {
  padding: 12px;
  border: 1px solid #2D2D2D;
  border-radius: 4px;
  font-size: 15px;
  font-family: Inter, sans-serif;
  background: #EAE0D2;
  color: #2D2D2D;
  resize: vertical;
  min-height: 80px;
  max-height: 200px;
  overflow-y: auto;
  transition: all 200ms ease-in-out;
}

.text-area:focus {
  outline: none;
  border-color: #A68763;
  box-shadow: 0 0 0 2px rgba(166, 135, 99, 0.2);
}

.char-count {
  font-size: 13px;
  color: #666;
  text-align: right;
  display: block;
  margin-top: 6px;
}

.char-count.limit-exceeded {
  color: #DC2626;
}
```

---

### Checkbox

**Purpose**: Boolean selection, multiple options

**Props**:

```typescript
interface CheckboxProps {
  id: string;
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  indeterminate?: boolean; // for parent checkboxes
}
```

**HTML**:

```html
<div class="checkbox-wrapper">
  <input
    id="email-notify"
    type="checkbox"
    class="checkbox"
    checked
  />
  <label for="email-notify">
    Send me a weekly summary email
  </label>
</div>
```

**CSS**:

```css
.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.checkbox {
  width: 20px;
  height: 20px;
  border: 1px solid #2D2D2D;
  border-radius: 4px;
  background: #EAE0D2;
  cursor: pointer;
  appearance: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 200ms ease-in-out;
}

.checkbox:checked {
  background: #A68763;
  border-color: #A68763;
}

.checkbox:checked::after {
  content: '✓';
  color: #EAE0D2;
  font-size: 14px;
  font-weight: bold;
}

.checkbox:focus {
  outline: 2px solid #A68763;
  outline-offset: 2px;
}

.checkbox-wrapper label {
  font-size: 15px;
  color: #2D2D2D;
  user-select: none;
}
```

---

### Select/Dropdown

**Purpose**: Choose from a list of options

**Props**:

```typescript
interface SelectProps {
  label: string;
  options: Array<{ value: string; label: string }>;
  value: string;
  onChange: (value: string) => void;
  searchable?: boolean;
  disabled?: boolean;
  error?: string;
}
```

**HTML**:

```html
<div class="form-field">
  <label for="industry">Industry</label>
  <div class="select-wrapper">
    <select id="industry" class="select">
      <option value="">Select an industry</option>
      <option value="tech">Technology</option>
      <option value="finance">Finance</option>
      <option value="healthcare">Healthcare</option>
    </select>
    <svg class="select-chevron"><!-- chevron icon --></svg>
  </div>
</div>
```

**CSS**:

```css
.select-wrapper {
  position: relative;
  display: inline-block;
  width: 100%;
}

.select {
  height: 40px;
  padding: 8px 12px 8px 12px;
  border: 1px solid #2D2D2D;
  border-radius: 4px;
  font-size: 15px;
  background: #EAE0D2;
  color: #2D2D2D;
  appearance: none;
  width: 100%;
  cursor: pointer;
  transition: all 200ms ease-in-out;
}

.select:focus {
  outline: none;
  border-color: #A68763;
  box-shadow: 0 0 0 2px rgba(166, 135, 99, 0.2);
}

.select-chevron {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: #2D2D2D;
  pointer-events: none;
}
```

---

## Data Display Components

### Table

**Purpose**: Display structured data in rows and columns

**Props**:

```typescript
interface TableProps {
  columns: Array<{
    header: string;
    accessor: string;
    sortable?: boolean;
    width?: string;
  }>;
  data: Array<any>;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  onSort?: (column: string) => void;
  onRowClick?: (row: any) => void;
  striped?: boolean; // default: true
}
```

**HTML**:

```html
<div class="table-wrapper">
  <table class="table">
    <thead>
      <tr>
        <th>Move Title</th>
        <th>Platform</th>
        <th>Type</th>
        <th>Status</th>
        <th>CTR</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>LinkedIn carousel – Bank rant</td>
        <td><img class="platform-icon" src="linkedin.svg" /></td>
        <td><span class="badge hero">Hero</span></td>
        <td><span class="status published">Published</span></td>
        <td>8.2%</td>
      </tr>
    </tbody>
  </table>
</div>
```

**CSS**:

```css
.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 15px;
}

.table thead {
  background: #A68763;
  color: #EAE0D2;
  font-weight: 600;
}

.table th {
  padding: 12px;
  text-align: left;
  user-select: none;
}

.table th[data-sortable] {
  cursor: pointer;
}

.table td {
  padding: 12px;
  border-bottom: 1px solid #D7C9AE;
}

.table tbody tr:nth-child(odd) {
  background: #D7C9AE;
}

.table tbody tr:hover {
  background: #C7B79E;
}

.table tbody tr:focus-within {
  outline: 2px solid #A68763;
}
```

---

### Badge / Pill

**Purpose**: Display status, category or tag

**Props**:

```typescript
interface BadgeProps {
  label: string;
  variant?: 'default' | 'hero' | 'hub' | 'help' | 'success' | 'error' | 'warning';
  size?: 'sm' | 'md';
  removable?: boolean;
  onRemove?: () => void;
}
```

**CSS**:

```css
.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}

.badge-default {
  background: #D7C9AE;
  color: #2D2D2D;
}

.badge-hero {
  background: #A68763;
  color: #EAE0D2;
}

.badge-hub {
  background: #EAE0D2;
  border: 1px solid #A68763;
  color: #A68763;
}

.badge-help {
  background: transparent;
  border: 1px solid #2D2D2D;
  color: #2D2D2D;
}

.badge-success {
  background: #10B981;
  color: #EAE0D2;
}

.badge-error {
  background: #DC2626;
  color: #EAE0D2;
}

.badge-removable {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding-right: 8px;
}

.badge-remove-btn {
  width: 16px;
  height: 16px;
  background: none;
  border: none;
  cursor: pointer;
  color: inherit;
  font-size: 12px;
  padding: 0;
}
```

---

### Progress Bar

**Purpose**: Show linear progress or loading state

**Props**:

```typescript
interface ProgressBarProps {
  value: number; // 0-100
  max?: number; // default: 100
  showLabel?: boolean;
  variant?: 'default' | 'success' | 'error';
  animated?: boolean;
  size?: 'sm' | 'md' | 'lg';
}
```

**HTML**:

```html
<div class="progress-wrapper">
  <div class="progress-bar" style="width: 60%">
    <span class="progress-label">60%</span>
  </div>
</div>
```

**CSS**:

```css
.progress-wrapper {
  height: 8px;
  background: #D7C9AE;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: #A68763;
  transition: width 300ms ease-in-out;
  position: relative;
}

.progress-bar.animated::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255,255,255,0.3),
    transparent
  );
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
```

---

## Navigation Components

### Tabs

**Purpose**: Switch between related content sections

**Props**:

```typescript
interface TabsProps {
  tabs: Array<{ id: string; label: string }>;
  activeTab: string;
  onChange: (tabId: string) => void;
}
```

**HTML**:

```html
<div class="tabs" role="tablist">
  <button
    class="tab-button active"
    role="tab"
    aria-selected="true"
    aria-controls="panel-about"
  >
    About
  </button>
  <button
    class="tab-button"
    role="tab"
    aria-selected="false"
    aria-controls="panel-plan"
  >
    Plan
  </button>
  <button
    class="tab-button"
    role="tab"
    aria-selected="false"
    aria-controls="panel-budget"
  >
    Budget
  </button>
</div>

<div id="panel-about" class="tab-panel" role="tabpanel">
  <!-- Content -->
</div>
```

**CSS**:

```css
.tabs {
  display: flex;
  gap: 8px;
  border-bottom: 1px solid #D7C9AE;
}

.tab-button {
  padding: 12px 24px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  font-size: 15px;
  color: #2D2D2D;
  cursor: pointer;
  transition: all 200ms ease-in-out;
  font-weight: 500;
}

.tab-button:hover {
  color: #A68763;
}

.tab-button.active {
  color: #A68763;
  border-bottom-color: #A68763;
}

.tab-panel {
  padding: 24px 0;
}
```

---

### Breadcrumb

**Purpose**: Show navigation hierarchy

**Props**:

```typescript
interface BreadcrumbProps {
  items: Array<{ label: string; href?: string }>;
}
```

**HTML**:

```html
<nav class="breadcrumb" aria-label="Breadcrumb">
  <ol>
    <li><a href="/">Strategy</a></li>
    <li><a href="/moves">Moves</a></li>
    <li aria-current="page">LinkedIn Carousel</li>
  </ol>
</nav>
```

**CSS**:

```css
.breadcrumb ol {
  list-style: none;
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 13px;
}

.breadcrumb li::after {
  content: '/';
  margin-left: 8px;
  color: #999;
}

.breadcrumb li:last-child::after {
  content: '';
}

.breadcrumb a {
  color: #A68763;
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}

.breadcrumb [aria-current="page"] {
  color: #2D2D2D;
  font-weight: 600;
}
```

---

## Feedback Components

### Toast / Notification

**Purpose**: Brief feedback message

**Props**:

```typescript
interface ToastProps {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  action?: { label: string; onClick: () => void };
  duration?: number; // ms, default: 4000
  onClose: () => void;
}
```

**CSS**:

```css
.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 16px 24px;
  background: white;
  border-left: 4px solid;
  border-radius: 4px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 1000;
  animation: slideInRight 200ms ease-in-out;
}

.toast.success {
  border-color: #10B981;
}

.toast.error {
  border-color: #DC2626;
}

.toast.warning {
  border-color: #F59E0B;
}

.toast.info {
  border-color: #3B82F6;
}

.toast-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
}

.toast-message {
  flex: 1;
  font-size: 15px;
  color: #2D2D2D;
}

.toast-action {
  margin-left: 12px;
  padding: 4px 12px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 13px;
  color: #A68763;
  font-weight: 600;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(400px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
```

---

### Skeleton Loader

**Purpose**: Placeholder while loading data

**Props**:

```typescript
interface SkeletonProps {
  count?: number;
  type?: 'text' | 'card' | 'line' | 'circle';
  width?: string;
  height?: string;
}
```

**CSS**:

```css
.skeleton {
  background: linear-gradient(
    90deg,
    #EAE0D2 0%,
    #D7C9AE 50%,
    #EAE0D2 100%
  );
  background-size: 200% 100%;
  animation: loading 1s infinite;
  border-radius: 4px;
}

.skeleton.text {
  height: 16px;
  margin-bottom: 8px;
}

.skeleton.card {
  height: 200px;
  margin-bottom: 16px;
  border-radius: 8px;
}

.skeleton.line {
  height: 8px;
  margin-bottom: 6px;
}

.skeleton.circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  margin: 0;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

---

## Layout Components

### Grid Container

**Purpose**: 12-column responsive grid system

**CSS**:

```css
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 16px;
}

.grid-col-1 { grid-column: span 1; }
.grid-col-2 { grid-column: span 2; }
.grid-col-3 { grid-column: span 3; }
.grid-col-4 { grid-column: span 4; }
.grid-col-6 { grid-column: span 6; }
.grid-col-12 { grid-column: span 12; }

/* Tablet (≥960px) */
@media (max-width: 960px) {
  .grid {
    grid-template-columns: repeat(9, 1fr);
  }
}

/* Mobile (≥600px) */
@media (max-width: 600px) {
  .grid {
    grid-template-columns: 1fr;
  }

  .grid-col-1,
  .grid-col-2,
  .grid-col-3,
  .grid-col-4,
  .grid-col-6,
  .grid-col-12 {
    grid-column: span 1;
  }
}
```

---

### Flex Layout

**Purpose**: Flexible spacing and alignment

**CSS**:

```css
.flex {
  display: flex;
}

.flex-column {
  flex-direction: column;
}

.flex-wrap {
  flex-wrap: wrap;
}

.justify-between {
  justify-content: space-between;
}

.justify-center {
  justify-content: center;
}

.align-center {
  align-items: center;
}

.align-start {
  align-items: flex-start;
}

.gap-4 { gap: 4px; }
.gap-8 { gap: 8px; }
.gap-16 { gap: 16px; }
.gap-24 { gap: 24px; }
```

---

## Accessibility Checklist

For every component, ensure:

✅ **Keyboard Navigation**
- All interactive elements reachable via Tab
- Logical tab order
- Escape key closes modals/dropdowns

✅ **ARIA Labels**
- Buttons have aria-label
- Links have descriptive text
- Icons have aria-hidden or aria-label
- Form fields have associated labels

✅ **Color Contrast**
- 4.5:1 ratio for normal text
- 3:1 ratio for large text
- No color alone for critical information

✅ **Focus Management**
- Visible focus indicators (not just color)
- Focus moves to opened modals
- Focus returns on close

✅ **Screen Reader**
- Semantic HTML (buttons, links, labels)
- ARIA landmarks (nav, main, complementary)
- aria-live for dynamic content

---

## Conclusion

Use this component specifications guide as the development blueprint. Each component includes:
- Clear purpose and usage
- Detailed CSS styling
- Accessibility requirements
- State management guidelines

When building components, prioritize:
1. **Accessibility first** – WCAG AA compliance
2. **Consistency** – Follow color, spacing, typography
3. **Performance** – Minimal repaints/reflows
4. **Usability** – Clear feedback and error handling

---

**Document Status**: Complete & Ready for Implementation
**Last Updated**: 2025
