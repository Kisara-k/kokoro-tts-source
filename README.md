# Kokoro TTS Source

A comprehensive document processing pipeline designed to convert a wide range of structured content (such as DOCX, PDF, or other formats) into JSON for Text-to-Speech (TTS) audiobook generation. While DOCX to PDF conversion is supported, it is optional—any content that can be structured into the expected JSON format can be used as input for audiobook creation.

## Overview

This project provides an automated workflow for:

- (Optional) Converting Microsoft Word documents (`.docx`) to PDF format with bookmarks
- Extracting and structuring content from PDFs using table of contents
- Cleaning and normalizing text for optimal TTS processing
- Generating JSON output with hierarchical content structure
- Enabling conversion of any structured content (not just PDFs) into audiobooks

## Features

### Document Processing

- **DOCX to PDF Conversion (Optional)**: Automated conversion with bookmark creation from document headings. You may skip this step if your content is already in PDF or another supported format.
- **Content Extraction**: Intelligent parsing of PDF table of contents and content, or any structured text source.
- **Text Normalization**: Advanced text cleaning including:
  - Unicode character normalization
  - Capital letter block processing
  - Paragraph consolidation
  - Punctuation standardization

### Text Processing

- **Smart Title Matching**: Automatic period insertion after titles in content
- **Hierarchical Structure**: Maintains document hierarchy (levels 1-2) from original TOC
- **Content Cleaning**: Removes page numbers, short lines, and formatting artifacts
- **Parallel Processing**: Multi-core processing for efficient handling of multiple documents

## Project Structure

```
kokoro-tts-source/
├── .scripts/
│   ├── .convert.py          # DOCX to PDF conversion script
│   └── .content.py          # PDF content extraction and processing
├── run_and_commit.bat       # Automated workflow execution
├── README.md               # Project documentation
├── .gitignore              # Git ignore rules
└── [Generated Files]
    ├── *.pdf               # Converted PDF files
    └── *.json              # Extracted content in JSON format
```

## Prerequisites

### Python Dependencies

```bash
pip install PyMuPDF
pip install pywin32
```

### System Requirements

- **Operating System**: Windows (required for Word COM automation)
- **Microsoft Word**: Must be installed for DOCX conversion
- **Python**: 3.6+ recommended

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Kisara-k/kokoro-tts-source.git
   cd kokoro-tts-source
   ```

2. **Install Python dependencies**:

   ```bash
   pip install PyMuPDF pywin32
   ```

3. **Ensure Microsoft Word is installed** on your Windows system

## Usage

### Quick Start

Place your `.docx` files (or PDFs, or other supported content) in the root directory and run:

```bash
run_and_commit.bat
```

This will:

1. (Optionally) Convert all DOCX files to PDF with bookmarks
2. Extract structured content to JSON files
3. Commit changes to Git repository
4. Push to remote repository

### Manual Execution

#### Convert DOCX to PDF (Optional)

```bash
python .scripts\.convert.py
```

#### Extract Content from PDF (or other supported format)

```bash
python .scripts\.content.py
```

## Output Format

The content extraction generates JSON files with the following structure:

```json
[
  {
    "index": 0,
    "title": "Chapter Title",
    "content": "Cleaned and normalized chapter content..."
  },
  {
    "index": 1,
    "title": "Next Chapter Title",
    "content": "Next chapter content..."
  }
]
```

### JSON Fields

- **index**: Sequential chapter/section number
- **title**: Extracted from PDF bookmarks
- **content**: Processed and cleaned text content

**!** Chapters and titles are based on the bookmarks in your PDF. You can adjust or add bookmarks in the PDF to control how chapters are split and titled in the output.

## Audiobook Generation with Kaggle Notebook

Once you have your structured JSON file (e.g., `Lectures.json`), you can use the Kaggle notebook to convert it into an audiobook with high-quality FLAC audio files for each chapter/section.

### Notebook: [kokoro-tts-audiobook-git (Kaggle)](https://www.kaggle.com/code/kisarak/kokoro-tts-audiobook-git/)

#### How it works:

1. **Loads the JSON file** (e.g., from your GitHub repo or local upload).
2. **Cleans and normalizes text** for each chapter/section.
3. **Uses the Kokoro TTS pipeline** to synthesize audio for each chapter, saving each as a `.flac` file.
4. **Packs all audio files into a single archive** (`Audiobook.zip`) for easy download.
5. **Deletes temporary files** to keep the workspace clean.

#### Example Workflow in the Notebook:

- Download or load the JSON file (e.g., `Lectures.json`).
- Preprocess and clean the text for TTS.
- For each chapter/section:
  - Generate audio using Kokoro TTS
  - Save as a `.flac` file in the `Audiobook` folder
- After all chapters are processed:
  - Archive the folder into a `.zip` or `.rar` file
  - Optionally, clean up intermediate files

This enables you to convert any structured content (not just PDFs) into a high-quality audiobook, chapter by chapter.

See the attached notebook for a full example and code reference.

## Text Processing Features

### Content Cleaning

- Removes page numbers and short content lines
- Consolidates paragraphs with proper spacing
- Normalizes Unicode punctuation to ASCII equivalents
- Handles capital letter blocks intelligently

### Text Normalization

- Converts curly quotes to straight quotes
- Replaces em/en dashes with hyphens
- Normalizes ellipses and spacing characters
- Removes duplicate periods

## Configuration

### Modifying Processing Behavior

The content extraction can be customized by modifying parameters in `.content.py`:

- **Minimum capital block length**: Adjust `min_length` parameter in `remove_capital()`
- **Page scanning limits**: Modify `max_scan` in `insert_period_after_title_match()`
- **Parallel processing**: Adjust `max_workers` in `ProcessPoolExecutor`

## Workflow Integration

### Automated Git Integration

The `run_and_commit.bat` script includes:

- Error handling for each processing step
- Automatic Git staging of all changes
- Commit with descriptive message
- Push to remote repository

### File Management

- Generated PDFs and JSON files are ignored in Git (see `.gitignore`)
- Only source scripts and documentation are version controlled
- Automatic skipping of up-to-date files based on modification times

## Performance Optimization

- **Parallel Processing**: Utilizes multiple CPU cores for document processing
- **Smart Caching**: Skips processing if output files are newer than source files
- **Memory Efficient**: Processes documents individually to minimize memory usage

## Troubleshooting

### Common Issues

1. **Word COM Error**: Ensure Microsoft Word is properly installed and licensed
2. **PyMuPDF Import Error**: Install with `pip install PyMuPDF`
3. **Permission Errors**: Run as administrator if file access issues occur
4. **Git Push Failures**: Check remote repository access and credentials

### Debugging

Enable verbose output by modifying the print statements in the Python scripts or run individual components separately to isolate issues.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with sample documents
5. Submit a pull request

## License

This project is designed for educational and research purposes. Please ensure compliance with your organization's document processing policies.

## Acknowledgments

- Built for integration with Kokoro TTS systems
- Utilizes PyMuPDF for robust PDF processing
- Designed for educational content processing workflows
