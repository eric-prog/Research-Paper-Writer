# Research Paper Writer

This project is an AI-powered tool that automatically generates research papers based on given code and context.

## Project Structure

```
Research-Paper-Writer/
│
├── context/
│   └── context.txt              # The main context/code to write about
│
├── example_papers/
│   └── 1703.10593v7.pdf         # Example research paper for inspiration
│
├── icml_example/
│   ├── example_paper.pdf        # ICML example paper in PDF format
│   └── example_paper.tex        # ICML example paper LaTeX source
│
├── output/
│   └── paper.tex                # Generated LaTeX paper will be saved here
│
├── .env                         # Environment variables (e.g., API keys)
├── .env.example                 # Example environment file
├── .gitignore                   # Git ignore file
├── LICENSE                      # Project license file
├── README.md                    # This file
├── requirements.txt             # Python dependencies
└── write_paper.py               # Main script to generate the paper
```

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/your-username/Research-Paper-Writer.git
   cd Research-Paper-Writer
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   - Copy `.env.example` to `.env`
   - Edit `.env` and add your Gemini API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

## Usage

1. Ensure your code or context is in `context/context.txt`.

2. Run the script:
   ```
   python write_paper.py
   ```

3. The generated LaTeX paper will be saved in `output/paper.tex`.

4. To compile the LaTeX file into a PDF, run the following commands:
   ```
   pdflatex output/paper.tex
   bibtex output/paper
   pdflatex output/paper.tex
   pdflatex output/paper.tex
   ```

## Features

- Automated research paper generation based on provided code/context
- Utilizes the Gemini AI model for natural language generation
- Incorporates example papers for learning LaTeX structure and formatting
- Ensures consistency and coherence across the generated paper

## Dependencies

- google-generativeai
- PyPDF2
- python-dotenv

See `requirements.txt` for specific versions.

## License

MIT License

## Contributing

Feel free to create a PR on an improvement! Give the repo a star! :)