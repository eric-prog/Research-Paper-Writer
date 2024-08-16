# AI-Powered Research Paper Generator

## Overview

This Python script is an advanced AI-powered tool designed to generate comprehensive research papers based on provided code. It leverages OpenAI's GPT-4 model and the arXiv API to create well-structured, technically detailed, and properly cited academic papers.

## Key Features

- Automated code analysis and structure breakdown
- Detailed section and subsection generation
- Integration with arXiv for relevant paper citations
- LaTeX formatting with proper academic structure
- Consistency checks across the entire paper
- Customizable paper generation based on input code and context

## Prerequisites

- Python 3.7+
- OpenAI API key
- arXiv API access

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/research-paper-generator.git
   cd research-paper-generator
   ```

2. Install required Python packages:
   ```
   pip install openai PyPDF2 arxiv
   ```

3. Set up your OpenAI API key as an environment variable:
   ```
   export OPENAI_API_KEY='your-api-key-here'
   ```

## Setup

1. Prepare the following files in the project directory:
   - `context.txt`: Your code and any additional context
   - `inspiration_paper.pdf`: A PDF of a research paper for inspiration
   - `paper_template.tex`: A LaTeX template with placeholders for each section and a `%BIBTEX_PLACEHOLDER`
   - Create an `example_papers/` directory and add some example LaTeX papers for reference

2. Ensure the hardcoded paths in the script match your file locations:
   ```python
   CONTEXT_PATH = "context.txt"
   INSPIRATION_PDF_PATH = "inspiration_paper.pdf"
   OUTPUT_PATH = "generated_paper.tex"
   LATEX_TEMPLATE_PATH = "paper_template.tex"
   EXAMPLE_PAPERS_DIR = "example_papers"
   ```

## Usage

Run the script:
```
python research_paper_generator.py
```

The script will generate a LaTeX file named `generated_paper.tex` in the project directory.

To compile the LaTeX file into a PDF, run the following commands:
```
pdflatex generated_paper.tex
bibtex generated_paper
pdflatex generated_paper.tex
pdflatex generated_paper.tex
```

## Important Notes

1. The quality of the generated paper heavily depends on the input code, context, and inspiration paper. Ensure these are relevant and of high quality.

2. The script uses GPT-4, which may incur significant API costs. Monitor your usage.

3. The generated paper should be thoroughly reviewed and edited by a human expert before submission or publication.

4. Ensure you have the necessary rights to use and analyze any code or papers you input into the system.

5. The arXiv API has usage limits. If you're generating many papers, consider implementing rate limiting.

## Customization

You can customize the paper generation process by modifying the `sections` dictionary in the `perform_writeup` function. This allows you to add, remove, or modify sections as needed for your specific type of research paper.

## Limitations

- The AI may occasionally generate plausible-sounding but incorrect technical details. Always verify the technical content.
- The quality of citations depends on the relevance of papers found on arXiv. Additional manual citation might be necessary.
- Very complex or novel code structures might not be fully understood by the AI, potentially leading to oversimplifications.

## Contributing

Contributions to improve the script are welcome. Please submit a pull request or open an issue to discuss proposed changes.

## License

MIT License