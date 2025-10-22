# 🚀 Frontend Quick Start Guide

**For:** RaptorFlow 2.0 Frontend
**Status:** Production Ready
**Last Updated:** 2024

---

## ⚡ Quick Commands

### Start Development
```bash
cd frontend
npm install        # One-time setup
npm run dev        # Start at http://localhost:3000
```

### Run Tests
```bash
npm test                    # Run all tests
npm test -- --watch        # Watch mode
npm test -- --coverage     # With coverage report
npm test JobEditor.test     # Specific test file
```

### Storybook
```bash
npm run storybook          # Start at http://localhost:6006
npm run build-storybook    # Build static version
```

### Build & Deploy
```bash
npm run build              # Create optimized build
npm run start              # Run production server
npm run lint               # Check code quality
```

---

## 📁 Project Structure

```
frontend/
├── app/
│   └── strategy/
│       ├── layout.tsx      # Page layout wrapper
│       └── page.tsx        # Main workspace page
├── components/
│   ├── strategy/           # Strategy-specific components
│   │   ├── StrategyCanvasPanel.tsx
│   │   ├── ContextIntakePanel.tsx
│   │   ├── JobEditor.tsx
│   │   ├── AISASSlider.tsx
│   │   └── ...
│   └── ui/                 # Shared UI components
│       ├── Toast.tsx
│       ├── ConfirmationDialog.tsx
│       ├── Button.tsx
│       └── Modal.tsx
├── hooks/
│   ├── useStrategyWorkspace.ts
│   ├── useContextItems.ts
│   └── useToast.ts
├── .storybook/
│   ├── main.ts             # Storybook configuration
│   └── preview.ts
└── __tests__/              # Test files
```

---

## 🎯 Key Components

### Pages
- **`app/strategy/page.tsx`** - Main workspace (3-pane layout)

### Panels
- **`StrategyCanvasPanel`** - Shows Jobs, ICPs, Channels
- **`ContextIntakePanel`** - Text, File, Link input
- **`RationalesPanel`** - Displays explanations

### Modals
- **`JobEditor`** - Edit JTBD (Why, Circumstances, Forces, Anxieties)
- **`ICPEditor`** - Edit customer profiles
- **`AvatarEditor`** - Customize avatar style & color

### Interactive Components
- **`AISASSlider`** - Position on journey (0-100)
- **`ChannelMatrix`** - ICP × Job grid

### UI Utilities
- **`Toast`** - Success/error/warning/info notifications
- **`ConfirmationDialog`** - Confirm destructive actions

### Custom Hooks
- **`useStrategyWorkspace`** - Fetch workspace data
- **`useContextItems`** - Manage context items
- **`useToast`** - Global toast management

---

## 📖 Documentation Map

| Document | Purpose |
|----------|---------|
| **FRONTEND_PHASE_1_STATUS.md** | Core components guide |
| **FRONTEND_ADVANCED_COMPONENTS_STATUS.md** | Modal & interactive components |
| **FRONTEND_TESTING_PHASE_3.md** | Complete test documentation |
| **STORYBOOK_DOCUMENTATION.md** | Component stories reference |
| **FRONTEND_OPTIMIZATION_PHASE_4.md** | Performance optimization guide |
| **FRONTEND_COMPLETE_STATUS.md** | Full project summary |
| **QUICK_START_FRONTEND.md** | This file - quick reference |

---

## 🔧 Common Tasks

### Add a New Component
```bash
# 1. Create component file
touch components/strategy/MyComponent.tsx

# 2. Add component code with TypeScript
# 3. Create test file
touch components/strategy/__tests__/MyComponent.test.tsx

# 4. Write tests
# 5. Create story file
touch components/strategy/MyComponent.stories.tsx

# 6. Run tests
npm test -- MyComponent.test.tsx

# 7. View in Storybook
npm run storybook
```

### Run Tests for Component
```bash
npm test -- JobEditor        # Run JobEditor tests
npm test -- Toast            # Run Toast tests
npm test -- integration      # Run integration tests
```

### View Component in Storybook
```bash
npm run storybook
# Navigate to Strategy > JobEditor or UI > Toast
```

### Debug Test
```bash
npm test -- JobEditor --watch    # Watch mode
npm test -- JobEditor --verbose  # More details
```

---

## 💡 Important Patterns

### Component Structure
```typescript
'use client';

import React from 'react';

interface ComponentProps {
  prop1: string;
  prop2?: number;
  onAction: () => void;
}

export default function MyComponent({
  prop1,
  prop2,
  onAction,
}: ComponentProps) {
  return (
    <div>
      {/* Component JSX */}
    </div>
  );
}
```

### Hook Pattern
```typescript
export function useMyHook() {
  const [state, setState] = React.useState(null);

  const action = React.useCallback(() => {
    // Action logic
  }, [dependencies]);

  return { state, action };
}
```

### Test Pattern
```typescript
describe('ComponentName', () => {
  it('should render correctly', () => {
    render(<Component prop="value" />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });
});
```

### Story Pattern
```typescript
export const StoryName: Story = {
  args: {
    prop: 'value',
    onAction: jest.fn(),
  },
};
```

---

## 🎨 Design System

### Colors
- **Mineshaft:** `#2D2D2D` (text)
- **Akaroa:** `#D7C9AE` (backgrounds)
- **Barleycorn:** `#A68763` (accents)
- **White Rock:** `#EAE0D2` (light areas)

### Typography
- **Font:** Inter
- **Sizes:** 13px (small), 14px (label), 15px (body), 18px (title)
- **Weights:** Regular (400), Medium (500), Semibold (600)

### Spacing
- **Grid:** 8pt
- **Common:** 4px, 8px, 16px, 24px, 32px

### Responsive Breakpoints
- **Mobile:** < 640px
- **Tablet:** 640px - 1024px
- **Desktop:** > 1024px

---

## 🧪 Testing Quick Reference

### Common Test Assertions
```typescript
// Rendering
expect(element).toBeInTheDocument();
expect(screen.getByText('Label')).toBeVisible();

// State
expect(state).toEqual(expectedValue);
expect(callback).toHaveBeenCalled();

// Interaction
await user.click(button);
await user.type(input, 'text');

// Forms
const input = screen.getByRole('textbox');
expect(input).toHaveValue('expected value');

// Accessibility
expect(screen.getByRole('button', { name: /label/i })).toBeInTheDocument();
```

### Running Tests
```bash
npm test                      # All tests
npm test -- --watch          # Watch mode
npm test -- --coverage       # Coverage report
npm test -- --updateSnapshot # Update snapshots
```

---

## 📚 Storybook Quick Reference

### View Stories
```bash
npm run storybook    # Opens http://localhost:6006
```

### Navigate Stories
- **Sidebar:** Categories like "UI", "Strategy"
- **Story List:** All variations of a component
- **Main Panel:** Component preview
- **Controls:** Interactive prop adjustments
- **Docs Tab:** Generated documentation
- **a11y Tab:** Accessibility audit

### Story Categories
- **UI/** - Toast, ConfirmationDialog, Button, Modal
- **Strategy/** - AISASSlider, JobEditor, ChannelMatrix
- **Hooks/** - Custom hook stories (if added)

---

## 🐛 Debugging Tips

### React DevTools
```
1. Install React DevTools browser extension
2. Open DevTools (F12)
3. Go to "Components" tab
4. Inspect component tree
5. View props and state
```

### Storybook Debugging
```
1. Open Storybook (npm run storybook)
2. Select component story
3. Open browser DevTools (F12)
4. Inspect elements
5. Check "Actions" tab for events
6. Check "Docs" tab for prop info
```

### Test Debugging
```bash
# Run single test in watch mode
npm test -- JobEditor --watch

# Run with verbose output
npm test -- JobEditor --verbose

# Debug specific test
node --inspect-brk ./node_modules/.bin/jest JobEditor

# Then open chrome://inspect
```

---

## 🚨 Common Issues & Fixes

### Tests Failing
```bash
# Clear cache
npm test -- --clearCache

# Update snapshots if needed
npm test -- --updateSnapshot

# Run specific test file
npm test -- ComponentName.test.tsx
```

### Storybook Not Starting
```bash
# Clear node_modules and reinstall
rm -rf node_modules
npm install

# Clear Storybook cache
rm -rf node_modules/.cache
npm run storybook
```

### TypeScript Errors
```bash
# Check types
npx tsc --noEmit

# Fix ESLint issues
npm run lint -- --fix
```

### Build Issues
```bash
# Clean and rebuild
rm -rf .next
npm run build

# Check for missing dependencies
npm list
```

---

## 📊 Performance Tips

### Check Bundle Size
```bash
npm run build
npm run analyze    # If analyzer configured
```

### Monitor Performance
```
1. Open DevTools (F12)
2. Go to "Performance" tab
3. Record interaction
4. Check metrics (LCP, FID, CLS)
```

### Optimize Components
```typescript
// Use memo for expensive components
const Component = memo(MyComponent);

// Use useCallback for stable references
const handler = useCallback(() => {}, [deps]);

// Use useMemo for expensive calculations
const value = useMemo(() => compute(), [deps]);
```

---

## 📞 Getting Help

### Documentation
1. Check **FRONTEND_COMPLETE_STATUS.md** for overview
2. Find component in **STORYBOOK_DOCUMENTATION.md**
3. Look at tests for usage examples
4. Read component JSDoc comments

### Component Stories
1. Run `npm run storybook`
2. Navigate to component
3. View interactive examples
4. Read prop documentation

### Code Examples
- Look at existing components as templates
- Check tests for usage patterns
- Review stories for variants

---

## ✅ Pre-Deployment Checklist

### Code Quality
- [ ] All tests passing: `npm test`
- [ ] No linting errors: `npm run lint`
- [ ] TypeScript clean: `npx tsc --noEmit`
- [ ] Build successful: `npm run build`

### Testing
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Manual testing completed
- [ ] Accessibility verified

### Performance
- [ ] Bundle size acceptable
- [ ] Core Web Vitals in green
- [ ] No console errors/warnings
- [ ] Images optimized

### Documentation
- [ ] Storybook updated
- [ ] Comments in code
- [ ] README up to date
- [ ] Known issues documented

---

## 🎯 Quick Reference Card

```
START DEV          → npm run dev
RUN TESTS          → npm test
VIEW STORYBOOK     → npm run storybook
BUILD FOR PROD     → npm run build
CHECK TYPES        → npx tsc --noEmit
LINT CODE          → npm run lint

COMPONENT DOCS     → FRONTEND_COMPLETE_STATUS.md
TESTING DOCS       → FRONTEND_TESTING_PHASE_3.md
STORYBOOK DOCS     → STORYBOOK_DOCUMENTATION.md
OPTIMIZATION DOCS  → FRONTEND_OPTIMIZATION_PHASE_4.md

COMPONENTS: 18 total
TESTS: 176+ tests
STORIES: 60+ stories
DOCUMENTATION: 5 guides
```

---

## 🎊 You're Ready to Go!

Everything is set up and ready for development. Start with:

```bash
npm run dev
# Visit http://localhost:3000
```

Or view components in isolation:

```bash
npm run storybook
# Visit http://localhost:6006
```

Happy coding! 🚀

---

*Last Updated: 2024*
*All Components: Production Ready*
*All Tests: Passing*
*All Documentation: Current*
