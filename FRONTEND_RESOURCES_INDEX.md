# RaptorFlow 2.0 Frontend Design Resources – Complete Index

## 📑 Master Resource Guide

All front-end design documentation for RaptorFlow 2.0 is organized below. Use this index to navigate and find what you need.

---

## 📚 Design Documents

### 1. **FRONTEND_DESIGN_BLUEPRINT.md**
   **Main Design System & Architecture Guide**

   📖 Length: ~2,500 lines

   **Covers:**
   - Visual Design System (colors, typography, iconography)
   - Grid & Spacing System (8-pt base unit, responsive)
   - Navigation & Shell (sidebar, top bar, chat rail)
   - Onboarding & Intake (6-step flow)
   - Context Intake Page (3-column layout)
   - Jobs-to-be-Done Cards (specifications)
   - ICP Builder & Avatars (specifications)
   - Channel Map & AISAS (grid layout)
   - Strategy Explanations (sidebar panel)
   - Suggested Move List (card layout)
   - Move Detail & Plan (3-tab interface)
   - Hook Studio (specifications)
   - Packaging Builder (checklist layout)
   - Calendar & Schedule (timeline view)
   - Receipts & Reports (dashboard)
   - Platform Watch (change feed)
   - Brand & ICP Section (management)
   - Activity Stream (timeline)
   - Billing & Quotas (plan display)
   - Admin & DPDP Compliance (table layout)
   - Gamification & Mood (avatar moods)
   - Accessibility & Microcopy (WCAG AA guidelines)
   - Responsiveness & Mobile (4 breakpoints)
   - Visual Examples & Guidance (component patterns)
   - Error & Empty States (user empathy)
   - Onboarding Microcopy (friendly copy)
   - Search & Filtering (real-time)
   - Sorting & Ranking (multi-column)
   - Buttons & CTAs (5 types)
   - Modals & Overlays (focus management)
   - Tabs & Carousels (keyboard navigation)
   - Hover & Focus States (accessibility)
   - Form Field Guidelines (validation)
   - Charts & Graphs (visualization)
   - Tour & Help Overlays (contextual help)
   - Keyboard Navigation (shortcuts)
   - Data Loading & Skeleton Screens (perceived performance)
   - Notifications & Toasts (feedback)
   - Dialogues & Confirmations (destructive actions)
   - Pagination & Infinite Scroll (data loading)
   - Settings & Preferences (customization)
   - Localization & Multi-Language (i18n)
   - Performance & Optimization (bundle size)
   - Brand Voice & Tone (voice guidelines)
   - Integration & Extensibility (API integration)
   - Advanced Features (A/B testing, etc.)
   - Conclusion

   **Use this document for:**
   - Overall design vision and principles
   - Visual design system details
   - Page layout specifications
   - Component guidelines
   - Accessibility standards
   - Mobile responsiveness
   - Performance optimization

---

### 2. **COMPONENT_SPECIFICATIONS.md**
   **Technical Component Reference**

   📖 Length: ~1,800 lines

   **Components Specified:**

   **Core Components (3):**
   - Button (primary, secondary, tertiary, icon)
   - Card (default, interactive, highlight)
   - Modal (with focus trapping)

   **Form Components (6):**
   - Text Input (with validation)
   - Text Area (auto-expanding)
   - Checkbox (custom-styled)
   - Select/Dropdown (searchable)
   - Date & Time Picker
   - File Input (drag & drop)

   **Data Display Components (6):**
   - Table (sortable, responsive)
   - Badge/Pill (multiple variants)
   - Progress Bar (animated)
   - Skeleton Loader (shimmer effect)
   - Charts (line, bar, pie)
   - Toast/Notification

   **Navigation Components (4):**
   - Left Sidebar (collapsible)
   - Top Bar (search, notifications, profile)
   - Tabs (keyboard accessible)
   - Breadcrumb (semantic)

   **Layout Components (2):**
   - Grid (12-column responsive)
   - Flex (spacing utilities)

   **For each component:**
   - Purpose & usage
   - Props/parameters
   - All CSS states
   - Accessibility requirements
   - Code examples
   - HTML structure
   - Interaction patterns

   **Use this document for:**
   - React component development
   - CSS specifications
   - Accessibility implementation
   - State management
   - Component prop design
   - Testing criteria

---

### 3. **PAGE_SPECIFICATIONS.md**
   **Page-by-Page Detailed Layouts**

   📖 Length: ~1,500 lines

   **Pages Specified:**

   **Onboarding Pages (6):**
   1. Welcome Screen – Gradient, logo, CTA
   2. Role Selection – 4-card grid with checkmarks
   3. Goal Selection – Multi-select pills
   4. Business Details – 4-field form
   5. Context Intake – Text area + file upload
   6. Review & Confirm – Summary page

   **Core Feature Pages (5):**
   7. Context Intake Page – 3-column layout (evidence, raw, preview)
   8. Strategy Workspace – Jobs, ICPs, channels, AISAS
   9. Suggested Moves – Move cards with filter
   10. Move Detail – 3-tab interface (about, plan, budget)
   11. Calendar View – Timeline with drag & drop

   **Analytics & Settings (2):**
   12. Reports Dashboard – Tabs, charts, tables
   13. Account Settings – Profile, notifications, preferences

   **For each page:**
   - Purpose & goal
   - Complete layout diagram
   - Component specifications
   - Navigation paths
   - Interaction patterns
   - Mobile adaptations
   - Microcopy examples
   - Form validation
   - Error states

   **Use this document for:**
   - Building page templates
   - Understanding user flows
   - Component placement
   - Responsive design
   - Mobile adaptations
   - Page structure

---

### 4. **FRONTEND_BLUEPRINT_COMPLETE.txt**
   **Executive Summary & Quick Reference**

   📖 Length: ~400 lines

   **Contains:**
   - Quick overview of all deliverables
   - Design system summary (colors, fonts, spacing)
   - Component list
   - Page list
   - Accessibility features
   - Responsive breakpoints
   - Performance targets
   - Brand voice principles
   - Technology recommendations
   - Implementation roadmap
   - Usage guide for different roles
   - Quick reference tables
   - Status and completion metrics

   **Use this document for:**
   - Getting oriented quickly
   - Finding specific information
   - Checking design system values
   - Understanding implementation roadmap
   - Sharing with stakeholders
   - Quick lookups

---

## 🎨 Design System Quick Reference

### Colors
```
Mineshaft:  #2D2D2D (primary text, dark accents)
Akaroa:     #D7C9AE (surface backgrounds)
Barleycorn: #A68763 (action buttons, highlights)
White Rock: #EAE0D2 (secondary surfaces, dividers)
```

### Typography
```
Display:    Playfair Display SC, 28px, bold
Title:      Inter, 22px, semibold
Heading:    Inter, 18px, medium
Body:       Inter, 15px, regular
Small:      Inter, 13px, regular
```

### Spacing (8-pt grid)
```
xs:  4px
sm:  8px
md:  16px
lg:  24px
xl:  32px
```

### Breakpoints
```
Large:  ≥1280px (full sidebar + chat)
Medium: ≥960px  (collapsed nav + floating chat)
Small:  ≥600px  (bottom nav + single column)
Mobile: <600px  (hamburger + full-screen)
```

---

## 📋 Document Usage Matrix

| Need | Document | Section |
|------|----------|---------|
| Design system colors | FRONTEND_DESIGN_BLUEPRINT.md | Visual Design System |
| Button specifications | COMPONENT_SPECIFICATIONS.md | Core Components |
| Onboarding flow | PAGE_SPECIFICATIONS.md | Onboarding Pages (1-6) |
| Strategy workspace layout | PAGE_SPECIFICATIONS.md | Strategy Workspace |
| Form field validation | COMPONENT_SPECIFICATIONS.md | Form Components |
| Responsive breakpoints | FRONTEND_DESIGN_BLUEPRINT.md | Responsiveness & Mobile |
| Accessibility standards | FRONTEND_DESIGN_BLUEPRINT.md | Accessibility |
| Brand voice examples | FRONTEND_DESIGN_BLUEPRINT.md | Brand Voice & Tone |
| Mobile touch targets | FRONTEND_DESIGN_BLUEPRINT.md | Mobile & Responsiveness |
| API integration | FRONTEND_DESIGN_BLUEPRINT.md | Integration & Extensibility |
| Performance targets | FRONTEND_DESIGN_BLUEPRINT.md | Performance & Optimization |
| Chart specifications | COMPONENT_SPECIFICATIONS.md | Data Display |
| Keyboard shortcuts | FRONTEND_DESIGN_BLUEPRINT.md | Keyboard Navigation |
| Component props | COMPONENT_SPECIFICATIONS.md | Each component section |
| Page structure | PAGE_SPECIFICATIONS.md | Relevant page section |
| Quick color reference | FRONTEND_BLUEPRINT_COMPLETE.txt | Quick Color Reference |

---

## 🚀 Getting Started

### Step 1: Review (30 minutes)
Read **FRONTEND_BLUEPRINT_COMPLETE.txt** for overview

### Step 2: Design Phase (1-2 weeks)
1. Use **FRONTEND_DESIGN_BLUEPRINT.md** to understand visual system
2. Reference **PAGE_SPECIFICATIONS.md** for layouts
3. Create Figma designs matching specifications
4. User test designs

### Step 3: Development Phase (4-6 weeks)
1. Use **COMPONENT_SPECIFICATIONS.md** while coding
2. Implement design tokens (colors, spacing, fonts)
3. Build components with exact CSS
4. Connect to backend APIs

### Step 4: Integration Phase (2-3 weeks)
1. Use **PAGE_SPECIFICATIONS.md** to build page templates
2. Integrate components into pages
3. Test responsive behavior at all breakpoints
4. Performance optimization

### Step 5: Testing & Refinement
1. Accessibility audit (WCAG AA)
2. User testing
3. Performance monitoring
4. Iterate based on feedback

---

## 📱 Responsive Design Quick Guide

### Large Screens (≥1280px)
- Full sidebar (72px)
- Chat rail visible (320px)
- Cards in grid (2-3 per row)
- Full feature set visible

### Medium Screens (≥960px)
- Collapsed sidebar (48px)
- Chat as floating button
- Cards in grid (2 per row)
- Some features hidden

### Small Screens (≥600px)
- Bottom navigation bar
- Single column layout
- Chat as drawer
- Simplified layouts

### Mobile (<600px)
- Hamburger menu
- Full-screen modals
- Chat as bottom sheet
- 48×48px touch targets

---

## ♿ Accessibility Checklist

For every component and page:
- [ ] 4.5:1 color contrast ratio
- [ ] Keyboard navigation (Tab, Arrows, Escape)
- [ ] Visible focus indicators
- [ ] ARIA labels on all buttons/icons
- [ ] Semantic HTML structure
- [ ] Alt text on images
- [ ] Video captions
- [ ] Audio transcripts
- [ ] Form field validation
- [ ] Error messages linked to fields

---

## 🎯 Performance Targets

| Metric | Target |
|--------|--------|
| LCP (Largest Contentful Paint) | < 2.5 s |
| FID (First Input Delay) | < 100 ms |
| CLS (Cumulative Layout Shift) | < 0.1 |
| Main Bundle | < 150 KB (gzipped) |

---

## 🛠️ Recommended Technology Stack

**Frontend:**
- React 18+ (component framework)
- Next.js 14+ (app router, SSR)
- TypeScript (type safety)

**Styling:**
- TailwindCSS (utility-first)

**State:**
- Zustand or Jotai

**Data:**
- TanStack Query (fetching)
- React Hook Form (forms)

**UI Libraries:**
- Lucide Icons (iconography)
- Radix UI (accessible components)
- Recharts (charts)
- Framer Motion (animations)

**Testing:**
- Playwright (E2E)
- Jest (unit)
- Storybook (components)

---

## 🎨 Color Palette Quick Reference

```
Primary Actions: Barleycorn (#A68763)
Text: Mineshaft (#2D2D2D)
Surfaces: Akaroa (#D7C9AE)
Secondary: White Rock (#EAE0D2)

Semantic:
Success: #10B981
Error: #DC2626
Warning: #F59E0B
Info: #3B82F6
```

---

## 📞 Document Navigation Quick Links

**For Designers:**
1. Start: FRONTEND_DESIGN_BLUEPRINT.md → Visual Design System
2. Pages: PAGE_SPECIFICATIONS.md → Pick your page
3. Details: COMPONENT_SPECIFICATIONS.md → Component details

**For Developers:**
1. Start: FRONTEND_BLUEPRINT_COMPLETE.txt → Quick reference
2. System: FRONTEND_DESIGN_BLUEPRINT.md → Design System
3. Code: COMPONENT_SPECIFICATIONS.md → Component specs
4. Layout: PAGE_SPECIFICATIONS.md → Page structure

**For Product Managers:**
1. Start: FRONTEND_BLUEPRINT_COMPLETE.txt
2. Flows: PAGE_SPECIFICATIONS.md → Onboarding (pages 1-6)
3. Features: PAGE_SPECIFICATIONS.md → Core Features (pages 7-11)

---

## ✅ Completion Status

| Document | Status | Lines | Sections | Components |
|----------|--------|-------|----------|-----------|
| FRONTEND_DESIGN_BLUEPRINT.md | ✅ Complete | 2,500+ | 45+ | All pages |
| COMPONENT_SPECIFICATIONS.md | ✅ Complete | 1,800+ | 25+ | 25+ components |
| PAGE_SPECIFICATIONS.md | ✅ Complete | 1,500+ | 13 | 13 pages |
| FRONTEND_BLUEPRINT_COMPLETE.txt | ✅ Complete | 400+ | 30+ | Summary |

**Total:** ~5,800 lines of comprehensive design specifications

---

## 📌 Key Principles to Remember

1. **Minimalistic** – Every element is intentional
2. **Clear Hierarchy** – Important content emphasized
3. **Generous White Space** – Reduce cognitive load
4. **Interactive Feedback** – Every action gets response
5. **Accessible** – WCAG AA compliance
6. **Performant** – Snappy interactions
7. **Consistent** – Visual unity across all pages
8. **Mobile-First** – Responsive at all breakpoints

---

## 🎓 Learning Path

**Day 1 (Orientation):**
1. Read FRONTEND_BLUEPRINT_COMPLETE.txt (30 min)
2. Skim FRONTEND_DESIGN_BLUEPRINT.md (1 hour)

**Day 2 (Deep Dive):**
1. Read full FRONTEND_DESIGN_BLUEPRINT.md (2 hours)
2. Reference COMPONENT_SPECIFICATIONS.md as needed

**Day 3+ (Implementation):**
1. Use PAGE_SPECIFICATIONS.md for your assigned pages
2. Reference COMPONENT_SPECIFICATIONS.md while coding
3. Check FRONTEND_DESIGN_BLUEPRINT.md for design system details

---

## 📝 Notes for Teams

**For Design Team:**
- Use these specs as design system baseline
- Create Figma component library
- Ensure all designs match specifications
- Document any deviations

**For Development Team:**
- Implement components exactly as specified
- Use design tokens from specification
- Test at all breakpoints
- Conduct accessibility audit

**For QA Team:**
- Test against page specifications
- Verify responsive behavior
- Check accessibility compliance
- Test all interactive states

**For Product Team:**
- Use user flows in specifications
- Reference for feature planning
- Share with stakeholders
- Iterate based on user feedback

---

## 🚀 Ready to Build!

This comprehensive design blueprint contains everything needed to build a beautiful, accessible, and performant RaptorFlow 2.0 interface.

**Next Step:** Start building based on your role:
- **Designers:** Create Figma mockups using FRONTEND_DESIGN_BLUEPRINT.md
- **Developers:** Start component development using COMPONENT_SPECIFICATIONS.md
- **Project Managers:** Plan sprints using PAGE_SPECIFICATIONS.md

---

**Blueprint Status:** ✅ COMPLETE & READY FOR IMPLEMENTATION
**Last Updated:** 2025
**Total Specifications:** ~5,800 lines
**Quality:** Production-ready

Let's build something amazing! 🎉
