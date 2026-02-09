# TASK-013: Implement progressive field reveal with animations

**Story:** STORY-005
**Status:** todo
**Priority:** high
**Estimated:** 2h

## Description

Add smooth animations when new fields are added to the form. This provides visual feedback that the AI is responding and makes the experience feel dynamic and alive.

## Animation Requirements

- Use Svelte transitions (fly, fade, scale)
- Stagger animations if multiple fields appear at once
- Smooth height transitions when form grows
- Optional: Highlight new fields briefly (subtle pulse or glow)
- Scroll to new fields if needed

## Definition of Done

- [ ] Transitions imported and configured
- [ ] New fields animate in smoothly
- [ ] Multiple fields stagger appropriately
- [ ] Form container resizes smoothly
- [ ] Animations feel natural (not too fast/slow)
- [ ] Performance is acceptable (no jank)
