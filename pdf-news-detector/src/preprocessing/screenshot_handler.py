from PIL import Image
import io
from typing import Tuple, Optional

def preprocess_screenshot(image_bytes: bytes) -> bytes:
    """
    Preprocesses screenshot for optimal OCR performance.
    
    Parameters:
        image_bytes (bytes): Raw screenshot data
        
    Returns:
        bytes: Preprocessed screenshot data
    """
    
    try:
        # Load image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if image.mode not in ['RGB', 'L']:
            image = image.convert('RGB')
        
        # Resize if too large (for API efficiency) or too small (for quality)
        width, height = image.size
        
        # Maximum dimensions for API efficiency
        max_dimension = 2048
        if width > max_dimension or height > max_dimension:
            image = _resize_maintain_aspect(image, max_dimension)
        
        # Minimum dimensions for quality
        min_dimension = 400
        if width < min_dimension and height < min_dimension:
            # Upscale small images
            scale_factor = min_dimension / max(width, height)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Enhance contrast for better OCR (subtle enhancement)
        image = _enhance_contrast(image)
        
        # Convert back to bytes
        output_buffer = io.BytesIO()
        image.save(output_buffer, format='JPEG', quality=95, optimize=True)
        return output_buffer.getvalue()
        
    except Exception as e:
        # If preprocessing fails, return original image
        print(f"Warning: Preprocessing failed, using original image: {str(e)}")
        return image_bytes

def _resize_maintain_aspect(image: Image.Image, max_dimension: int) -> Image.Image:
    """Resize image while maintaining aspect ratio."""
    width, height = image.size
    
    if width > height:
        new_width = max_dimension
        new_height = int(height * max_dimension / width)
    else:
        new_height = max_dimension
        new_width = int(width * max_dimension / height)
    
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

def _enhance_contrast(image: Image.Image) -> Image.Image:
    """Subtly enhance contrast for better OCR without over-processing."""
    from PIL import ImageEnhance
    
    # Very subtle contrast enhancement
    enhancer = ImageEnhance.Contrast(image)
    enhanced = enhancer.enhance(1.1)  # 10% contrast boost
    
    # Very subtle sharpness enhancement
    sharpness_enhancer = ImageEnhance.Sharpness(enhanced)
    final_image = sharpness_enhancer.enhance(1.05)  # 5% sharpness boost
    
    return final_image

def detect_screenshot_type(image_bytes: bytes) -> dict:
    """
    Analyzes screenshot to determine its type and characteristics.
    
    Parameters:
        image_bytes (bytes): Screenshot data
        
    Returns:
        dict: Screenshot characteristics
    """
    
    try:
        image = Image.open(io.BytesIO(image_bytes))
        width, height = image.size
        aspect_ratio = width / height
        
        # Determine likely device/layout type
        layout_type = "unknown"
        if aspect_ratio > 1.5:
            layout_type = "desktop"
        elif 0.5 < aspect_ratio < 0.8:
            layout_type = "mobile"
        elif 0.8 <= aspect_ratio <= 1.2:
            layout_type = "tablet"
        
        # Estimate quality
        pixel_count = width * height
        quality = "high" if pixel_count > 1000000 else "medium" if pixel_count > 400000 else "low"
        
        return {
            "width": width,
            "height": height,
            "aspect_ratio": round(aspect_ratio, 2),
            "layout_type": layout_type,
            "quality": quality,
            "pixel_count": pixel_count,
            "file_size": len(image_bytes)
        }
        
    except Exception as e:
        return {
            "error": f"Could not analyze screenshot: {str(e)}",
            "file_size": len(image_bytes)
        }

def validate_screenshot_quality(image_bytes: bytes) -> Tuple[bool, str]:
    """
    Validates if screenshot is suitable for processing.
    
    Parameters:
        image_bytes (bytes): Screenshot data
        
    Returns:
        Tuple[bool, str]: (is_valid, reason)
    """
    
    try:
        characteristics = detect_screenshot_type(image_bytes)
        
        if "error" in characteristics:
            return False, characteristics["error"]
        
        # Check minimum quality requirements
        if characteristics["pixel_count"] < 50000:  # Very small image
            return False, "Screenshot resolution too low for reliable OCR"
        
        if characteristics["file_size"] < 5000:  # Very small file
            return False, "Screenshot file size too small, may be corrupted"
        
        if characteristics["file_size"] > 20000000:  # Very large file (20MB)
            return False, "Screenshot file size too large for processing"
        
        # Extreme aspect ratios might indicate cropped or partial screenshots
        if characteristics["aspect_ratio"] > 4 or characteristics["aspect_ratio"] < 0.25:
            return False, "Screenshot has unusual aspect ratio, may be partially cropped"
        
        return True, "Screenshot validation passed"
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def optimize_for_ocr(image_bytes: bytes) -> bytes:
    """
    Optimizes screenshot specifically for OCR processing.
    
    Parameters:
        image_bytes (bytes): Original screenshot
        
    Returns:
        bytes: OCR-optimized screenshot
    """
    
    try:
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB for consistent processing
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Normalize brightness if image is too dark/bright
        image = _normalize_brightness(image)
        
        # Apply subtle noise reduction
        image = _reduce_noise(image)
        
        # Save optimized image
        output_buffer = io.BytesIO()
        image.save(output_buffer, format='JPEG', quality=90, optimize=True)
        return output_buffer.getvalue()
        
    except Exception as e:
        print(f"OCR optimization failed, using original: {str(e)}")
        return image_bytes

def _normalize_brightness(image: Image.Image) -> Image.Image:
    """Normalize image brightness for better OCR."""
    from PIL import ImageEnhance, ImageStat
    
    # Calculate average brightness
    stat = ImageStat.Stat(image)
    avg_brightness = sum(stat.mean) / len(stat.mean)
    
    # Adjust if too dark or too bright
    if avg_brightness < 80:  # Too dark
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.3)
    elif avg_brightness > 200:  # Too bright
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(0.8)
    
    return image

def _reduce_noise(image: Image.Image) -> Image.Image:
    """Apply subtle noise reduction."""
    from PIL import ImageFilter
    
    # Very light blur to reduce noise without losing text sharpness
    return image.filter(ImageFilter.GaussianBlur(radius=0.3))