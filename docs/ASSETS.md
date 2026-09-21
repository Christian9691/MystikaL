# Assets — PussyCat IDE

This directory contains visual assets for the cat-themed IDE.

## Directory Structure

```
assets/
├── cat-video.mp4      # Main cat video (embedded)
├── cat-video.gif      # Alternative GIF format
├── paw.png            # Paw print pattern (for backgrounds)
├── cat-icon.png       # Window icon (128x128)
└── README.md          # This file
```

## Asset Requirements

### cat-video.mp4
- **Format:** MP4 (H.264)
- **Resolution:** 640x480 or 320x240
- **Duration:** 10-15 seconds
- **Loop:** Yes (infinite)
- **Audio:** Muted (silent)
- **Size:** <500KB (compressed)
- **Content:** Cute cat doing cat things (typing, playing, etc.)

### cat-video.gif
- **Format:** Animated GIF
- **Resolution:** 320x240 max
- **Loop:** Yes
- **Size:** <300KB
- **Content:** Same as MP4 version

### paw.png
- **Format:** PNG (transparent background)
- **Size:** 64x64 or 128x128
- **Color:** Light gray/white with 20% opacity
- **Usage:** Tiled background pattern for editor

### cat-icon.png
- **Format:** PNG (transparent background)
- **Size:** 128x128 (or 256x256)
- **Content:** Cute cat face with cat ears
- **Usage:** Window icon, splash screen

## Asset Sources

### Free Cat Video Resources
- **Pixabay:** https://pixabay.com/videos/search/cat/
- **Pexels:** https://www.pexels.com/videos/animal/cats/
- **Videvo:** https://www.videvo.net/videvo/videos/branding/cats/

### Cat GIF Resources
- **Giphy:** https://giphy.com/search/cute-cats
- **Tenor:** https://tenor.com/cat-gifs

### Cat Icons
- **Flaticon:** https://www.flaticon.com/free-icons/cat
- **Iconfinder:** https://www.iconfinder.com/iconsets/cat-icons

## Creative Commons License

All assets should be:
- CC0 (public domain) OR
- CC-BY ( attribution required) OR
- Commercial-use allowed

## Asset Checklist

- [ ] cat-video.mp4 (main video)
- [ ] cat-video.gif (fallback)
- [ ] paw.png (background pattern)
- [ ] cat-icon.png (window icon)
- [ ] All assets tested in tkinter

## Notes

- Keep files small — this is a classroom demo tool
- Prioritize performance over high quality
- Test on low-end laptops
- Fallback to emoji sequences if files unavailable
