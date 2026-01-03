# Visual Polish Verification Checklist

**Date**: 2026-01-03
**URL**: http://localhost:5173

## Stage 1 (Individual Responses) - Blue Theme

- [ ] Background is light gray (#f8f9fa)
- [ ] Title has 4px blue vertical bar on left
- [ ] Subtle shadow visible (0 2px 8px)
- [ ] Model names are readable (not too light)
- [ ] Tab hover effect works (blue accent)
- [ ] Loading state shows blue left border

## Stage 2 (Rankings) - Orange Theme

- [ ] Background is warm light orange (#fff8f0)
- [ ] Title has 4px orange vertical bar on left
- [ ] Aggregate rankings box has blue border
- [ ] Rank positions are prominent (blue, bold)
- [ ] Model names in rankings are readable
- [ ] Loading state shows orange left border

## Stage 3 (Final Answer) - Green Theme ⭐ MOST IMPORTANT

- [ ] **Background has visible gradient** (light to lighter green)
- [ ] **Border is thick (3px) and green**
- [ ] **Glow effect visible** (subtle pulsing shadow)
- [ ] **Title is larger** (20px vs 16px in other stages)
- [ ] **Title has 6px green bar** (thicker than others)
- [ ] **Extra spacing above** (32px margin-top)
- [ ] **Checkmark icon** (green circle with white ✓) before "CHAIRMAN SYNTHESIS"
- [ ] **Final text is largest** (17px, dark readable)
- [ ] **Stands out MUCH more** than Stages 1 & 2
- [ ] Loading state shows green left border with bold text

## Contrast & Accessibility

- [ ] All headings are dark enough (#1a1a1a)
- [ ] Secondary text is readable (#595959)
- [ ] Small text (12px) meets WCAG AA (#595959 or darker)
- [ ] No text appears washed out or too light
- [ ] Color blindness: Blue/Orange/Green still distinguishable by shadows/borders

## Visual Hierarchy

- [ ] Stage 3 **clearly** the most prominent
- [ ] Stage 2 noticeably different from Stage 1 (orange vs blue)
- [ ] User messages have subtle blue background
- [ ] Loading indicators match their stage color

## Polish Details

- [ ] Shadows give subtle depth (not flat)
- [ ] Hover effects smooth (0.2s transition)
- [ ] Animations not jarring (slide-in 0.3-0.4s)
- [ ] Spacing feels balanced (not cramped or too loose)
- [ ] Borders are crisp and visible

## Cross-Browser (If Testing)

- [ ] Chrome: Gradient renders smoothly
- [ ] Firefox: Animations work correctly
- [ ] Safari: No webkit prefix issues
- [ ] Mobile: Touch targets adequate size

## Expected Score Improvement

**Before**: 78/100 (Visual Hierarchy 72, Contrast 65)
**After**: 90-94/100 (Visual Hierarchy 95+, Contrast 98+)

---

**If any checkbox fails**: Note the issue and refer to `.archie-workspace/visual-polish-complete.md` for implementation details.
