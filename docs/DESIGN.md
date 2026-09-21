# Design — PussyCat IDE

> Status: Draft | Date: 2026-09-21

## 1. Visual Identity

**Theme:** Cat-themed, playful but professional

**Color Palette:**
- Primary: `#F4A261` (ginger/orange cat)
- Secondary: `#E8D5B7` (cream/fur)
- Dark: `#1E1E2E` (shadow)
- Accent: `#6BCB77` (green for success/ok)
- Error: `#FF6B6B` (red for errors)

**Typography:**
- Editor: `Courier New` (11pt) or `JetBrains Mono` fallback
- UI Labels: `Courier New` (10pt bold)
- Status Bar: `Courier New` (10pt)

**Iconography:**
- Window title: "PussyCat IDE" with 🐱 icon
- Status dots: ● (filled circle)
- Run button: ▶ (play triangle)

## 2. Startup Experience

### Splash Screen / Loading Sequence
1. **Welcome Screen (2 seconds)**
   - Cat video (looping 10-15s animation)
   - "PussyCat IDE" logo with tagline "Your Feline-Friendly Transpiler"
   - Progress bar: "Loading transpiler..."

2. **Main Window Appears**
   - Smooth fade-in animation
   - Status bar shows "● ready"
   - Keyword bar displays with cat emoji prefix

### Cat Video Integration
- **Format:** Small embedded MP4 or GIF (max 500KB)
- **Content:** Cute cat animations (kitten playing, cat typing, etc.)
- **Placement:** Top-left corner of main window
- **Behavior:** Loops silently during idle time
- **Fallback:** If video fails, show animated cat emoji sequence

## 3. Layout

```
┌─────────────────────────────────────────────────────────┐
│ PussyCat IDE 🐱                                [_][□][×] │
├─────────────────────────────────────────────────────────┤
│ 🐱 kung→if  kundi→else  habang→while  para→for         │
│    ipakita→print  ipakita→print  at→and  o→or          │
├─────────────────────────────────────────────────────────┤
│  │                                                        │
│1 │ your code here...                                      │
│2 │ kung x > 5:                                           │
│3 │     ipakita("hello")                                   │
│4 │                                                        │
│  │                                                        │
│  │                                                        │
│  │                                                        │
├─────────────────────────────────────────────────────────┤
│  │                                                        │
│1 │ --- Generated Python ---                               │
│2 │ if x > 5:                                              │
│3 │     print("hello")                                     │
│4 │                                                        │
│  │                                                        │
│  │                                                        │
│  │                                                        │
├─────────────────────────────────────────────────────────┤
│ ● ready                                      [Clear] [Run] │
└─────────────────────────────────────────────────────────┘
```

## 4. Visual Elements

### Cat-Themed Decorations
- **Window Border:** Subtle paw-print pattern (10% opacity)
- **Line Numbers:** Fuzzy cat paw emoji prefix (🐾1, 🐾2, 🐾3...)
- **Run Button:** ▶ with cat ear cutout
- **Clear Button:** 🗑️ with cat tail detail
- **Keyword Bar:** Each entry prefixed with cat emoji (🐱 kung→if)

### Interactive Feedback
- **Hover Effects:** Button glow with orange aura (#F4A261)
- **Success Animation:** Screen flashes with heart icons ❤️ for 1 second
- **Error Shake:** Window shakes with red glow on error
- **Loading:** Cat blinking animation in corner

## 5. Animation Sequences

### Success State
```
1. Status changes to "ok"
2. Heart icons float up from output pane (5-10 hearts)
3. Success chime (optional, configurable)
4. Green border pulse (3 times)
```

### Error State
```
1. Status changes to "error"
2. Window shakes (3 small movements)
3. Red border pulse (3 times)
4. Error sound (optional, configurable)
```

### Run Animation
```
1. Status shows "running..."
2. Cat video speed increases (1.5x)
3. Run button pulses
4. Progress indicator: 🐱→🐾→🐱→🐾
```

## 6. Cat Video Specifications

### Option A: Embedded GIF (Simple)
- **Size:** 320x240px max
- **Format:** Animated GIF or APNG
- **Loop:** Infinite
- **File:** `assets/cat-video.gif`
- **Usage:** Displayed in top-right corner of editor pane

### Option B: Embedded Video (Better Quality)
- **Format:** MP4 (H.264), 480p max
- **Size:** <500KB compressed
- **Loop:** True
- **Muted:** Yes
- **File:** `assets/cat-video.mp4`
- **Usage:** Background in splash screen or always-on panel

### Option C: Animated Emoji Sequence (Fallback)
- **Content:** 🐱→🐶→🐱→🐱‍👤→🐱 (typing cats)
- **Speed:** 1 second per frame
- **Loop:** True
- **Usage:** If video files unavailable

## 7. Customization

### User Settings (Future)
- [ ] Enable/disable cat animations
- [ ] Volume control for sounds
- [ ] Toggle paw-print line numbers
- [ ] Change theme color (orange/gray/black)

## 8. Accessibility

- All animations have reduced-motion equivalent
- Status indicators use color + text + icon
- Cat decorations never obstruct editor content
- Line numbers remain readable with any background

## 9. Design Philosophy

> "The goal is not to be overwhelming — it's to make coding feel friendly and approachable. The cat theme should delight, not distract."

- **Playful but professional** — cats are fun, but this is a coding tool
- **Subtle enhancements** — cat elements should complement, not dominate
- **Performance-first** — animations must not slow down the editor
- **Optional joy** — if someone doesn't like cats, they should still love the tool

## 10. Future Enhancements

- [ ] User-uploaded cat photos as background
- [ ] Cat fact popups on hover
- [ ] "Cat mode" — more aggressive cat animations
- [ ] Cat-themed themes (Tabby, Siamese, Tortoiseshell)
- [ ] Community cat design submissions
