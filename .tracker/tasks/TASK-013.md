# TASK-013: Implement progressive field reveal with animations

**Story:** STORY-005
**Status:** done
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

- [x] Transitions imported and configured
- [x] New fields animate in smoothly
- [x] Multiple fields stagger appropriately
- [x] Form container resizes smoothly
- [x] Animations feel natural (not too fast/slow)
- [x] Performance is acceptable (no jank)
