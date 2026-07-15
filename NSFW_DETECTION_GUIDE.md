# NSFW Content Detection Guide

## Overview

This guide explains the NSFW (Not Safe For Work) content detection system implemented in the social media application. The system automatically detects and blocks inappropriate images containing nudity or vulgar content to maintain a safe environment for all users.

## Features

### 🛡️ Automatic Content Blocking
- **Real-time Detection**: Images are analyzed immediately upon upload
- **Automatic Blocking**: NSFW content is automatically blocked and deleted
- **User Notification**: Users receive clear feedback when content is blocked
- **Logging**: All NSFW detection events are logged for monitoring

### 🔍 Detection Capabilities
- **Nudity Detection**: Identifies exposed body parts and inappropriate content
- **Confidence Scoring**: Provides confidence levels for detection accuracy
- **Multiple Formats**: Supports PNG, JPG, JPEG, and GIF image formats
- **Threshold-based**: Configurable sensitivity thresholds

### 🎯 Privacy Protection
- **Feed Filtering**: NSFW posts are hidden from public feeds
- **Profile Privacy**: Users can see their own blocked content, but others cannot
- **Explore Page**: NSFW content is filtered from trending/explore sections

## Technical Implementation

### Dependencies
```
nudenet==3.4.2
tensorflow==2.13.0
```

### Database Schema
New fields added to the `Post` model:
- `is_nsfw` (Boolean): Whether the post contains NSFW content
- `nsfw_confidence` (Float): Confidence score of NSFW detection (0.0-1.0)

### Detection Process
1. **Upload**: User uploads an image
2. **File Validation**: Check file type and size
3. **Image Processing**: Resize and optimize image
4. **NSFW Analysis**: Run NudeNet detection on the image
5. **Decision**: Block if confidence > 0.6 threshold
6. **Action**: Either save post or delete file and show error

### Code Structure
```python
# NSFW Detection Function
def detect_nsfw_content(image_path):
    """Detect NSFW content in uploaded images"""
    # Uses NudeNet to analyze image
    # Returns (is_nsfw, confidence_score)

# Integration in Upload Route
@app.route('/upload', methods=['GET', 'POST'])
def upload_post():
    # ... file validation ...
    is_nsfw, nsfw_confidence = detect_nsfw_content(file_path)
    
    if is_nsfw:
        # Block and delete file
        os.remove(file_path)
        flash('Content blocked due to inappropriate content')
        return render_template('upload.html', form=form)
```

## Configuration

### Detection Threshold
The NSFW detection threshold is set to `0.6` by default. You can adjust this in the `detect_nsfw_content()` function:

```python
if confidence > 0.6:  # Adjust this threshold as needed
    nsfw_detected = True
```

### NSFW Categories Detected
The system detects the following categories:
- `exposed_anus`
- `exposed_armpits` 
- `exposed_belly`
- `exposed_buttocks`
- `exposed_breast_f` (female)
- `exposed_breast_m` (male)
- `exposed_genitalia_f` (female)
- `exposed_genitalia_m` (male)
- `exposed_thighs_f` (female)
- `exposed_thighs_m` (male)

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Database Migration
```bash
python migrate_nsfw_fields.py
```

### 3. Test the System
```bash
python test_nsfw_detection.py
```

### 4. Start Application
```bash
python app.py
```

## User Experience

### For Content Uploaders
- **Clear Feedback**: Users receive immediate notification if content is blocked
- **Error Message**: "Your post has been blocked due to inappropriate content. Please upload appropriate images only."
- **File Cleanup**: Blocked files are automatically deleted to save storage space

### For Content Viewers
- **Clean Feeds**: NSFW content never appears in main feeds or explore pages
- **Profile Privacy**: Users can only see their own blocked content on their profiles
- **Safe Browsing**: All public areas are automatically filtered

## Monitoring & Logging

### Log Messages
- NSFW detection results are logged with confidence scores
- Blocked posts are logged with user information
- System initialization status is logged

### Admin Dashboard
- NSFW statistics can be added to admin dashboard
- Blocked content can be reviewed by administrators
- Detection accuracy can be monitored

## Troubleshooting

### Common Issues

1. **"NSFW detector not available" Warning**
   - Install required dependencies: `pip install nudenet tensorflow`
   - Check if NudeNet model downloads correctly

2. **High False Positive Rate**
   - Adjust detection threshold in `detect_nsfw_content()`
   - Consider updating to newer NudeNet model versions

3. **Performance Issues**
   - NSFW detection adds processing time to uploads
   - Consider implementing background processing for large images
   - Monitor server resources during peak usage

### Testing
Run the test script to verify functionality:
```bash
python test_nsfw_detection.py
```

## Security Considerations

### Data Privacy
- Images are analyzed locally, not sent to external services
- Blocked images are immediately deleted from the server
- NSFW confidence scores are stored for monitoring but not exposed to users

### Performance Impact
- Detection adds 1-3 seconds to image upload process
- Memory usage increases during image analysis
- Consider implementing caching for repeated uploads

## Future Enhancements

### Potential Improvements
1. **Background Processing**: Move detection to background tasks
2. **User Appeals**: Allow users to appeal blocked content
3. **Admin Review**: Queue borderline content for manual review
4. **Custom Thresholds**: Allow admins to adjust sensitivity
5. **Whitelist Users**: Trusted users with relaxed filtering
6. **Content Categories**: More granular content classification

### Integration Options
- **Cloud Services**: Integrate with Google Vision API or AWS Rekognition
- **Machine Learning**: Train custom models on your specific content
- **User Reporting**: Combine with user reporting system

## Support

For technical support or questions about the NSFW detection system:
1. Check the logs in `app.log` for error messages
2. Run the test script to diagnose issues
3. Review the configuration settings
4. Ensure all dependencies are properly installed

---

**Note**: This NSFW detection system is designed to catch obvious inappropriate content. No automated system is 100% accurate, so consider implementing additional moderation tools and user reporting features for comprehensive content management.
