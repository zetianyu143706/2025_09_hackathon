# PDF News Detector

## Overview
The PDF News Detector is a Python project designed to analyze PDF news posts to determine their credibility. The application reads PDF files from Azure Storage, extracts text and images, analyzes the content, and generates a JSON report indicating whether the news post is likely true or fake.

## Features
- Connects to Azure Blob Storage to download PDF files.
- Extracts text and images from PDF documents using PyMuPDF.
- Analyzes text using OpenAI's GPT model to assess credibility.
- Evaluates images to determine if they are AI-generated or real.
- Generates a comprehensive JSON report summarizing the analysis results.

## Project Structure
```
pdf-news-detector
├── src
│   ├── main.py               # Entry point of the application
│   ├── azure
│   │   └── storage.py        # Azure Storage connection and PDF download
│   ├── pdf
│   │   └── reader.py         # PDF content extraction
│   ├── analysis
│   │   ├── text_analyzer.py  # Text analysis for credibility
│   │   └── image_analyzer.py  # Image analysis for authenticity
│   ├── report
│   │   └── generator.py      # Report generation
│   └── utils
│       └── helpers.py        # Utility functions
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
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