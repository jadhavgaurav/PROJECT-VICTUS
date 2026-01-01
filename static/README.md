# VICTUS Static Frontend

## Full-Screen PWA with All Features

This is the enhanced full-screen frontend for VICTUS with:
- ✅ Full-screen layout (no centered box)
- ✅ Responsive design for all devices
- ✅ PWA support (installable, offline-capable)
- ✅ Sidebar with chat history
- ✅ Model selector
- ✅ Settings panel
- ✅ Documents management
- ✅ Memory/Facts management
- ✅ All animations and smooth transitions

## PWA Setup

### 1. Generate Icons

Icons are required for PWA installation. You can:

**Option A: Use the Python script (requires Pillow)**
```bash
cd static
pip install Pillow
python3 generate-icons.py
```

**Option B: Use online tools**
- Visit [RealFaviconGenerator](https://realfavicongenerator.net/)
- Or [PWA Builder Image Generator](https://www.pwabuilder.com/imageGenerator)
- Create a 512x512px icon with VICTUS logo
- Generate all required sizes and place in `static/icons/`

**Required icon sizes:**
- 72x72, 96x96, 128x128, 144x144, 152x152, 192x192, 384x384, 512x512

### 2. Service Worker

The service worker is automatically registered when the page loads. It:
- Caches static assets for offline use
- Always fetches API requests from network
- Provides offline fallback

### 3. Install as PWA

1. Open the app in a supported browser (Chrome, Edge, Safari)
2. Look for the install prompt or use browser menu
3. Click "Install" to add to home screen
4. The app will work offline (cached pages)

## Features

### Full-Screen Layout
- No centered box - uses full viewport
- Sidebar on left (280px on desktop, slide-in on mobile)
- Main chat area takes remaining space
- Responsive breakpoints at 768px and 480px

### Responsive Design
- **Desktop (>768px)**: Sidebar always visible, full layout
- **Tablet (≤768px)**: Sidebar slides in/out, full-width panels
- **Mobile (≤480px)**: Optimized spacing, touch-friendly buttons

### PWA Features
- Installable on all devices
- Offline support (cached pages)
- App-like experience
- Safe area support for notched devices
- Service worker auto-updates

### New Features Added
1. **Chat History Sidebar**
   - View all conversations
   - Search conversations
   - Switch between chats
   - Delete conversations

2. **Model Selector**
   - Choose GPT model
   - Persists selection
   - Shows model description

3. **Settings Panel**
   - Profile settings
   - System context
   - Preferences (voice output, auto-scroll)

4. **Documents Panel**
   - View uploaded documents
   - See indexing status
   - Delete documents

5. **Memory/Facts Panel**
   - View stored facts
   - Manage long-term memory
   - Delete facts

## File Structure

```
static/
├── index.html          # Main app (full-screen)
├── login.html          # Login page
├── signup.html         # Signup page
├── style.css           # Full-screen styles
├── script.js           # Enhanced with all features
├── manifest.json       # PWA manifest
├── service-worker.js   # PWA service worker
├── icons/              # PWA icons (generate these)
└── audio/              # Generated audio files
```

## Browser Support

- ✅ Chrome/Edge (Desktop & Mobile)
- ✅ Safari (iOS & macOS)
- ✅ Firefox (Desktop)
- ✅ Samsung Internet

## Testing PWA

1. **Local Testing**: Use `http://localhost:8000` (HTTPS not required for localhost)
2. **Production**: Requires HTTPS for PWA features
3. **Install Test**: 
   - Open DevTools → Application → Manifest
   - Check for errors
   - Test "Add to Home Screen"

## Troubleshooting

### Icons not showing
- Ensure icons are in `static/icons/` directory
- Check file names match manifest.json
- Verify file permissions

### Service Worker not registering
- Check browser console for errors
- Ensure HTTPS (or localhost)
- Clear browser cache

### Offline not working
- Check service worker in DevTools → Application → Service Workers
- Verify cache is populated
- Check network tab for failed requests

## Notes

- The app is fully responsive and works on all screen sizes
- PWA features require HTTPS in production (localhost is exception)
- Service worker updates automatically
- All features are integrated and working

