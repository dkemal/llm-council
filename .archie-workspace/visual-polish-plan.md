# Visual Polish Implementation Plan

**Created**: 2026-01-03 17:43:12
**Agent**: senior-frontend-engineer
**Status**: 🟡 DRAFT

## Issues from UX Audit

### 1. Low Contrast Text (WCAG AA Compliance)
**Current Problems:**
- Colors like #999, #888, #666 fail WCAG AA contrast ratios
- Affects `.rank-count`, `.model-name`, `.ranking-model`, `.message-label`

**Fixes:**
- Small text (12-13px): Minimum #767676 (4.5:1 ratio)
- Body text (14-15px): Minimum #595959 (7:1 ratio for AA+)
- Headings: Can stay #333

### 2. Flat Stage Hierarchy (Visual Differentiation)
**Current Problems:**
- All stages look similar (light gray backgrounds)
- Stage 3 (final answer) doesn't stand out as most important
- No visual progression through stages

**Fixes:**
- **Stage 1**: Keep light gray (#fafafa) - foundational data
- **Stage 2**: Light blue background (#f0f7ff) - analysis phase
- **Stage 3**: Enhanced green with shadow - **PROMINENT** final answer
  - Background: #f0fff0 (current)
  - Add box-shadow: 0 4px 12px rgba(45, 138, 45, 0.15)
  - Larger title (18px vs 16px)
  - Thicker border (2px vs 1px)

### 3. Loading States (Poor Visual Feedback)
**Current Problems:**
- Basic spinner with no context
- No indication of which stage is loading
- No progress indicator (1/3, 2/3, 3/3)

**Fixes:**
- Add pulse animation to spinner
- Show stage progress: "Stage 1/3: Collecting responses..."
- Different colors per stage loading state
- Smooth transitions between stages

### 4. Visual Polish (General UX)
**Current Problems:**
- Flat cards, no depth perception
- Button hover states too subtle
- Inconsistent spacing

**Fixes:**
- Add subtle shadows to cards (0 2px 4px rgba(0,0,0,0.08))
- Enhanced button hover states with scale transform
- Consistent padding/spacing using 4px grid system

## Implementation Order

1. **index.css** - Fix global contrast colors
2. **Stage1.css** - Add card shadows, improve tab hover
3. **Stage2.css** - Enhance ranking visuals, fix contrast
4. **Stage3.css** - Make PROMINENT with shadow, larger text
5. **ChatInterface.css** - Enhanced loading states with progress
6. **App.css** - Global polish (if needed)

## WCAG AA Color Mappings

| Old Color | New Color | Usage | Contrast Ratio |
|-----------|-----------|-------|----------------|
| #999 | #767676 | Small labels (12px) | 4.54:1 ✅ |
| #888 | #666666 | Model names (12px) | 5.74:1 ✅ |
| #666 | #595959 | Body text (14px) | 7.0:1 ✅ |
| #333 | #333333 | Headings (keep) | 12.63:1 ✅ |

## Expected Results

- All text passes WCAG AA (4.5:1 minimum)
- Clear visual hierarchy: Stage 1 < Stage 2 < **Stage 3**
- Stage 3 stands out as the "answer" with green theme + shadow
- Loading states show progress and context
- Professional polish with depth and subtle animations
