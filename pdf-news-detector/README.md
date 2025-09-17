# Screenshot News Analyzer

## Overview
The Screenshot News Analyzer is a Python project designed to analyze screenshots of news content to determine their credibility. The application reads screenshot images from Azure Storage, extracts text using OCR, identifies embedded images, analyzes the content using AI, and generates a JSON report indicating whether the news content is likely true or fake.

## Features
- Connects to Azure Blob Storage to download screenshot images.
- Extracts text from screenshots using GPT-4.1 Vision OCR capabilities.
- Identifies and analyzes embedded images within screenshots.
- Analyzes text using GPT-4.1 to assess credibility.
- Evaluates images to determine if they are AI-generated or authentic.
- Performs consistency analysis between text and images to detect misleading combinations.
- Generates comprehensive JSON reports with detailed analysis results.
- Supports multiple screenshot types: social media posts, news websites, mobile apps.

## Project Structure
```
screenshot-news-analyzer
├── src
│   ├── main.py                    # Entry point of the application
│   ├── config.py                  # Configuration management
│   ├── azure_utils
│   │   └── storage.py             # Azure Storage connection and image download
│   ├── ocr
│   │   ├── screenshot_extractor.py # OCR text extraction using GPT-4.1 Vision
│   │   └── image_processor.py     # Image region detection and processing
│   ├── preprocessing
│   │   └── screenshot_handler.py  # Screenshot optimization and validation
│   ├── analysis
│   │   ├── text_analyzer.py       # Text analysis for credibility
│   │   ├── image_analyzer.py      # Image analysis for authenticity
│   │   └── consistency_analyzer.py # Text-image consistency analysis
│   ├── report
│   │   └── generator.py           # Report generation
│   └── utils
│       ├── helpers.py             # General utility functions
│       └── cli.py                 # Command-line interface utilities
├── requirements.txt               # Project dependencies
├── test_screenshot_system.py      # System testing utilities
└── README.md                      # Project documentation
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd pdf-news-detector
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up Azure Storage credentials in your environment.

## Usage

The Screenshot News Analyzer supports two processing modes:

### Process Specific Screenshots

Process one or more specific screenshots by name:

```bash
# Process a single screenshot
python src/main.py --screenshots screenshot1.jpg

# Process multiple screenshots
python src/main.py --screenshots image1.png image2.jpg news_screenshot.webp

# Process with mixed valid/invalid files (skips missing files with warnings)
python src/main.py --screenshots valid_image.jpg missing_file.png another_valid.webp
```

### List Available Screenshots

Discover what screenshots are available in the container:

```bash
# List all screenshots without processing
python src/main.py --list-available
```

## Examples

### Basic Usage

```bash
# Analyze a specific news screenshot
python src/main.py --screenshots "breaking_news_screenshot.png"

# Analyze multiple social media screenshots
python src/main.py --screenshots "twitter_post.jpg" "facebook_post.png" "instagram_story.webp"
```

### Workflow Example

```bash
# 1. First, see what screenshots are available
python src/main.py --list-available

# 2. Process specific screenshots of interest
python src/main.py --screenshots "suspicious_news_1.jpg" "viral_post_2.png"

# 3. Check the 'report' container in Azure Storage for analysis results
```

## Error Handling

The system provides robust error handling:

- **Missing files**: Warns about non-existent files but continues processing valid ones
- **No valid files**: Exits with error if none of the specified files exist
- **Mixed scenarios**: Processes valid files and reports missing ones
- **Connection issues**: Clear error messages for Azure connectivity problems

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.