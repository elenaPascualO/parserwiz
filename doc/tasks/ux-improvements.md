# ParseWiz UX Improvements Plan

> Created: 2026-01-19
> Status: In Progress (P0 + P1 Complete)
> Based on: UX Audit of MVP
> Last Updated: 2026-01-19

---

## Overview

This document outlines UX improvements for ParseWiz, organized by priority and effort level. Work through sections incrementally across sessions.

---

## P0 - Critical (Do First)

### 1. Upload Feedback Gap

**Problem:** After selecting a file, users see nothing until the spinner appears. No confirmation their file was received.

**Current behavior:**
```
Click "Select file" → File dialog → Select → [nothing] → Spinner → Preview
```

**Target behavior:**
```
Click "Select file" → File dialog → Select → "data.json selected" → Spinner → Preview
```

**Files to modify:**
- `frontend/app.js` - `handleFileSelect()` and `handleDrop()` functions
- `frontend/styles.css` - Add styles for selected state
- `frontend/index.html` - Add element for filename display

**Implementation:**
- [x] Add a `<span id="selected-file-name">` inside `.drop-zone-content`
- [x] Update `processFile()` to show filename immediately
- [x] Style: muted text below the upload button
- [x] Clear on reset

**Status:** ✅ Complete

---

### 2. Error Toast Improvements

**Problem:**
- Toast at bottom of screen can be missed
- 5-second auto-dismiss too short for complex errors
- No visible close button

**Files to modify:**
- `frontend/styles.css` - Reposition toast, add close button styles
- `frontend/app.js` - `showError()` function
- `frontend/index.html` - Add close button to error element

**Implementation:**
- [x] Move toast from `bottom: 2rem` to `top: 1rem` (or near upload area)
- [x] Add "×" close button inside `.error-message`
- [x] Extend timeout from 5000ms to 8000ms
- [x] Add click handler for manual dismiss
- [x] Add `role="alert"` and `aria-live="assertive"` for accessibility

**Status:** ✅ Complete

---

### 3. Accessibility Basics

**Problem:** Missing ARIA labels, focus indicators, and semantic markup.

**Files to modify:**
- `frontend/index.html` - Add ARIA attributes
- `frontend/styles.css` - Add focus-visible styles

**Implementation:**

#### 3a. Focus indicators
- [x] Add to `styles.css`:
```css
button:focus-visible,
.file-button:focus-visible,
input:focus-visible,
textarea:focus-visible,
details summary:focus-visible {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
}
```

#### 3b. ARIA labels
- [x] Add `aria-label="Switch to multi-table view"` to `#btn-multi-file`
- [x] Add `aria-label="Switch to single-file view"` to `#btn-single-file`
- [x] Add `aria-label="Previous page"` to `#prev-page`
- [x] Add `aria-label="Next page"` to `#next-page`
- [x] Add `role="alert"` to `#error-message`
- [x] Add `aria-live="polite"` to `#loading`

#### 3c. Table semantics
- [x] Add `scope="col"` to all `<th>` elements (in JS where tables are generated)

**Status:** ✅ Complete

---

## P1 - Important (Do Soon)

### 4. Hide Pagination When Unnecessary

**Problem:** "Page 1 of 1" shows even for small files. Visual noise.

**Files to modify:**
- `frontend/app.js` - `updatePagination()` or equivalent

**Implementation:**
- [x] Add condition: if `totalPages <= 1`, hide `.pagination-controls`
- [x] Show controls only when `totalPages > 1`

**Status:** ✅ Complete

---

### 5. Table Horizontal Scroll Indicator

**Problem:** Users don't realize there are more columns off-screen.

**Files to modify:**
- `frontend/styles.css`
- `frontend/index.html`
- `frontend/app.js`

**Implementation:**
- [x] Add hint text above table: "Scroll horizontally for more columns"
- [x] Add CSS gradient fade on right edge when content overflows
- [x] Show column count in preview header

**Status:** ✅ Complete

---

### 6. Complex JSON Modal Clarity

**Problem:** Modal explains options verbally but doesn't show visual examples.

**Files to modify:**
- `frontend/index.html` - Update modal content
- `frontend/styles.css` - Style visual examples

**Implementation:**
- [x] Add visual mini-table diagrams showing "Split Tables" vs "Flat Table" modes
- [x] Rename buttons: "Multi-file" → "Split Tables", "Single-file" → "Flat Table"
- [x] Add brief "Best for:" hints under each option
- [x] Add "Recommended" badge to Split Tables option

**Status:** ✅ Complete

---

### 7. Download Button Hierarchy

**Problem:** All download buttons have equal visual weight.

**Files to modify:**
- `frontend/app.js` - `buildConvertButtons()` function
- `frontend/styles.css` - Add secondary button style

**Implementation:**
- [x] First option (most common conversion) is primary (filled green)
- [x] Other options are secondary (outlined green, fills on hover)
- [x] Added `.convert-btn-secondary` class with border style

**Status:** ✅ Complete

---

## P2 - Nice to Have (Later)

### 8. Empty State Handling

**Problem:** No guidance when file produces zero rows.

**Files to modify:**
- `frontend/app.js` - Add empty state check in preview rendering

**Implementation:**
- [ ] Check if `data.length === 0` after parsing
- [ ] Show friendly message:
  ```
  "Your file was valid but contained no data rows.
   For JSON: Check if data is inside a nested object.
   For CSV: Ensure file has content beyond headers."
  ```
- [ ] Style as info box (not error)

**Effort:** Small (30 min)

---

### 9. Mobile Editor Improvements

**Problem:** Raw editor is difficult to use on small screens.

**Files to modify:**
- `frontend/styles.css` - Mobile breakpoint styles

**Implementation:**
- [ ] Increase editor font size on mobile (0.875rem → 1rem)
- [ ] Increase line height
- [ ] Consider adding zoom controls (+/-)
- [ ] Make error message more prominent on mobile

**Effort:** Medium (45 min)

---

### 10. Keyboard Navigation for Pagination

**Problem:** No keyboard shortcuts for navigating pages.

**Files to modify:**
- `frontend/app.js` - Add keyboard event listener

**Implementation:**
- [ ] Add `keydown` listener when preview is visible
- [ ] Left arrow → previous page (if available)
- [ ] Right arrow → next page (if available)
- [ ] Only active when not in an input/textarea

**Effort:** Small (30 min)

---

## Session Checklist

Use this to track progress across sessions:

### Session 1: P0 Items
- [x] Upload feedback (#1)
- [x] Error toast (#2)
- [x] Accessibility basics (#3)

### Session 2: P1 Items
- [x] Hide pagination (#4)
- [x] Scroll indicator (#5)
- [x] Complex JSON modal (#6)
- [x] Download hierarchy (#7)

### Session 3: P2 Items
- [ ] Empty states (#8)
- [ ] Mobile editor (#9)
- [ ] Keyboard nav (#10)
- [ ] Privacy text (#11)

---

## Testing Checklist

After each session, verify:

- [ ] Changes work on Chrome, Firefox, Safari
- [ ] Mobile responsive (test at 375px width)
- [ ] Keyboard-only navigation works
- [ ] Screen reader announces changes appropriately
- [ ] All existing tests still pass (`uv run pytest tests/ -v`)

---

## Notes

_Add notes here as you work through items:_

### 2026-01-19 - P0 Verification & Bug Fixes

- **Upload feedback**: Shows briefly during loading. Mainly useful for large/slow files. File name + type badge in preview header is sufficient for fast uploads.
- **Bug fix**: "File too large" errors were incorrectly showing the raw editor. Fixed to show only toast and reset to upload screen.
- **Added**: Max file size warning "(max 10MB)" in upload area drop zone text.
- **Toast error**: Now appears at top of screen with × close button, 8s timeout.

### 2026-01-19 - P1 Complete

- **Hide pagination**: Pagination controls now hidden when only 1 page. Cleaner UI for small files.
- **Scroll indicator**: Added column count display, scroll hint text, and CSS gradient fade on right edge for wide tables. Fade disappears when scrolled to end.
- **Complex JSON modal**: Added visual mini-table examples showing Split Tables vs Flat Table modes. Renamed buttons for clarity, added "Recommended" badge and "Best for:" hints.
- **Download hierarchy**: Primary download button (most common format) is filled green, secondary options are outlined. Secondary fills on hover.
