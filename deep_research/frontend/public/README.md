# Public Assets

This folder contains static assets served directly by Next.js.

## Favicon & Icons

- **favicon.svg** - Main browser favicon (32x32, scalable)
- **apple-touch-icon.svg** - iOS home screen icon (180x180)
- **icon-512.svg** - High-resolution app icon (512x512)
- **manifest.json** - PWA configuration file

## Icon Design

The Deep Research Agent icon features:
- **"DR" Letters**: Bold, modern typography representing "Deep Research"
- **Circuit Pattern**: Tech-inspired nodes and connections
- **Gradient**: Blue to purple (#3b82f6 → #8b5cf6 → #6366f1)
- **Professional Look**: Clean, scalable SVG format

## Usage

Icons are automatically loaded by Next.js via metadata in `app/layout.tsx`:

```typescript
icons: {
  icon: '/favicon.svg',
  apple: '/apple-touch-icon.svg',
}
```

## Adding New Assets

Place any static files here:
- Images: `public/images/`
- Fonts: `public/fonts/` (if not using next/font)
- Documents: `public/docs/`
- Other assets: Organize in subdirectories

Files in this folder are served from the root URL path.
Example: `public/logo.png` → `http://localhost:3000/logo.png`
