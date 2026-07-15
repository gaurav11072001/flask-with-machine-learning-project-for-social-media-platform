# Content Warning System Implementation Guide

## ✅ What's Already Implemented

### 1. **Vulgar Comment Blocking** (Backend)
- Location: `app.py` lines 1098-1108
- When a user posts a vulgar comment, it's **blocked** and returns error 400
- Response includes: `{'error': '...', 'blocked': True, 'reason': 'inappropriate_content'}`

### 2. **NSFW Post Detection** (Backend)
- Location: `app.py` around line 800-870
- Posts with NSFW content are flagged with `is_nsfw=True`
- Flash message shown: "Your post has been shared but flagged..."

### 3. **Content Warning JavaScript** (New)
- Location: `static/js/content_warnings.js`
- Two functions created:
  - `showVulgarContentWarning(message)` - Shows warning for vulgar comments
  - `showNSFWContentWarning()` - Shows warning for NSFW posts

## 🔧 Manual Steps to Complete Integration

### Step 1: Update feed.html Comment Handler

Find the `addComment` function around line 888-924 in `templates/feed.html` and replace the `.then(response => response.json())` section with:

```javascript
.then(response => {
    if (!response.ok) {
        return response.json().then(err => Promise.reject(err));
    }
    return response.json();
})
.then(data => {
    // ... existing success code ...
})
.catch(error => {
    // Handle vulgar content blocking
    if (error.blocked && error.reason === 'inappropriate_content') {
        showVulgarContentWarning(error.error);
        input.value = ''; // Clear the inappropriate comment
    } else if (error.error) {
        alert(error.error);
    }
})
```

### Step 2: Show NSFW Warning on Post Upload

In `templates/upload.html` or wherever post upload success is handled, add:

```javascript
// After successful NSFW post upload
if (postData.is_nsfw) {
    showNSFWContentWarning();
}
```

### Step 3: Verify Script is Loaded

Make sure `templates/feed.html` includes at the bottom (already added):

```html
<!-- Content Warnings System -->
<script src="{{ url_for('static', filename='js/content_warnings.js') }}"></script>
```

## 🎯 How It Works

### Vulgar Comment Flow:
1. User types vulgar comment → clicks "Post"
2. Backend detects vulgar content → returns 400 error with `blocked: true`
3. Frontend catches error → calls `showVulgarContentWarning()`
4. **Beautiful warning modal appears** with:
   - ⚠️ Orange header "Inappropriate Content Detected"
   - Clear message explaining why it was blocked
   - "Understood" button to dismiss

### NSFW Post Flow:
1. User uploads NSFW image → clicks "Share"
2. Backend detects NSFW → saves post with `is_nsfw=True`
3. Frontend receives success response → calls `showNSFWContentWarning()`
4. **Warning modal appears** with:
   - 🔞 Red header "NSFW Content Detected"
   - Explanation that post is flagged
   - Warning about repeated violations

## 📝 Testing

### Test Vulgar Comment:
1. Go to feed
2. Try to comment: "fuck this shit"
3. Should see orange warning modal

### Test NSFW Post:
1. Upload an NSFW image
2. Should see red warning modal after upload

## 🎨 Modal Styling

Both modals use:
- **Gradient headers** (orange for vulgar, red for NSFW)
- **Bootstrap 5 modal** framework
- **Auto-cleanup** (removes from DOM after closing)
- **Responsive design** (centered, mobile-friendly)

## 🔄 Current Status

✅ Backend blocking working
✅ JavaScript warning functions created
✅ Script added to feed.html
⚠️ Frontend integration needs manual completion (Step 1 above)

The system is 90% complete - just need to update the error handling in the comment submission code!
