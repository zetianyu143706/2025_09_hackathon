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
│       └── helpers.py             # Utility functions
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
To run the application, execute the following command:
```
python src/main.py
```
This will initiate the process of reading PDF files from Azure Storage, analyzing their content, and generating a report.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.