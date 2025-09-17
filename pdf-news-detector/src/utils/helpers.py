"""
General utility functions for the Screenshot News Analyzer.
"""

def log_message(message):
    """Log a message with timestamp prefix."""
    print(f"[LOG] {message}")

def handle_error(error):
    """Handle and log error messages."""
    print(f"[ERROR] {error}")

def validate_image_extension(filename):
    """Validate if filename has a valid image extension."""
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff']
    return any(filename.lower().endswith(ext) for ext in valid_extensions)

def format_report_data(image_score, text_score, consistency_score, screenshot_name):
    """Format basic report data structure."""
    return {
        "screenshot_name": screenshot_name,
        "image_score": image_score,
        "text_score": text_score,
        "consistency_score": consistency_score
    }