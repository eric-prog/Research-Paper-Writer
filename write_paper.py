import os
import json
import re
import google.generativeai as genai
import PyPDF2
import arxiv
from typing import Dict, List, Tuple
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Gemini model configuration
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Hardcoded paths
CONTEXT_PATH = "/Users/ericsheen/Desktop/DeepAI_Research/Research-Paper-Writer/context/context.txt"
INSPIRATION_PDF_PATH = "/Users/ericsheen/Desktop/DeepAI_Research/Research-Paper-Writer/example_papers/1703.10593v7.pdf"
OUTPUT_PATH = "/Users/ericsheen/Desktop/DeepAI_Research/Research-Paper-Writer/output/paper.tex"
LATEX_TEMPLATE_PATH = "/Users/ericsheen/Desktop/DeepAI_Research/Research-Paper-Writer/icml/example_paper.tex"
EXAMPLE_PAPERS_DIR = "/Users/ericsheen/Desktop/DeepAI_Research/Research-Paper-Writer/example_papers"

def read_context(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()

def read_pdf_inspiration(pdf_path: str) -> str:
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def read_latex_template(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()

def parse_code(context: str) -> Dict[str, str]:
    sections = re.split(r'\n(?=def |class )', context)
    return {f"Section_{i}": section.strip() for i, section in enumerate(sections)}

def get_response_from_llm(prompt: str, system_message: str) -> str:
    chat = model.start_chat(history=[])
    response = chat.send_message(f"{system_message}\n\n{prompt}")
    return response.text

def search_arxiv_papers(query: str, num_results: int = 5) -> List[Dict]:
    search = arxiv.Search(
        query=query,
        max_results=num_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    results = []
    for paper in search.results():
        results.append({
            "title": paper.title,
            "authors": ", ".join(author.name for author in paper.authors),
            "abstract": paper.summary,
            "url": paper.pdf_url,
            "published": paper.published.strftime("%Y-%m-%d"),
            "id": paper.get_short_id()
        })
    
    return results

def examine_paper(paper: Dict) -> str:
    prompt = f"""
    Examine the following paper:
    Title: {paper['title']}
    Authors: {paper['authors']}
    Abstract: {paper['abstract']}
    Published: {paper['published']}

    Provide a brief summary of the paper's main contributions and how it might be relevant to our research.
    Limit your response to 2-3 sentences.
    """
    return get_response_from_llm(prompt, "You are an AI assistant examining a research paper.")

def learn_from_examples() -> str:
    example_texts = []
    for filename in os.listdir(EXAMPLE_PAPERS_DIR):
        if filename.endswith(".tex"):
            with open(os.path.join(EXAMPLE_PAPERS_DIR, filename), 'r') as f:
                example_texts.append(f.read())
    
    prompt = f"""
    Analyze the following LaTeX templates for research papers:

    {' '.join(example_texts)}

    Provide a summary of the common structure, formatting, and language used in these templates.
    Focus on the overall organization, section headings, and any specific LaTeX commands frequently used.
    """
    return get_response_from_llm(prompt, "You are an AI assistant analyzing research paper templates.")

def analyze_code_structure(code: Dict[str, str]) -> str:
    prompt = f"""
    Analyze the following code structure:

    {json.dumps(code, indent=2)}

    Provide a high-level overview of the code's architecture, main components, and their interactions.
    Identify key algorithms, data structures, and design patterns used.
    Highlight any notable or innovative aspects of the implementation.
    """
    return get_response_from_llm(prompt, "You are an AI assistant analyzing code structure.")

def generate_detailed_outline(section_name: str, context: str, code: Dict[str, str], code_analysis: str) -> List[Dict[str, str]]:
    prompt = f"""
    Create a detailed outline for the {section_name} section of a research paper about the following code:

    Code Analysis:
    {code_analysis}

    Context:
    {context}

    For each subsection, provide:
    1. A title
    2. A brief description of what should be covered
    3. Any specific technical details or algorithms to be discussed
    4. Potential areas where citations might be needed

    Aim for 3-5 subsections for most sections, but for longer sections like Methodology or Implementation, you can go up to 7-10 subsections.
    
    Provide the output as a JSON array of objects, each representing a subsection.
    """
    response = get_response_from_llm(prompt, "You are an AI assistant creating a detailed paper outline.")
    return json.loads(response)

def generate_section_part(section_name: str, subsection: Dict[str, str], context: str, code: Dict[str, str], inspiration: str, tips: str, example_learning: str) -> str:
    prompt = f"""
    Write the subsection "{subsection['title']}" of the {section_name} section of a research paper.

    Subsection description: {subsection['description']}
    Technical details to cover: {subsection['technical_details']}
    
    Base your writing on the following code and context:
    
    Context:
    {context}
    
    Code:
    {json.dumps(code, indent=2)}
    
    Inspiration:
    {inspiration}
    
    Tips:
    {tips}
    
    Learned from examples:
    {example_learning}
    
    Provide a detailed analysis related to the specified subsection. Use appropriate technical language and LaTeX formatting.
    Include code snippets where relevant, using the \\begin{{lstlisting}} and \\end{{lstlisting}} environment.
    Ensure this subsection is comprehensive and at least two paragraphs long.
    If discussing algorithms, consider using pseudo-code or algorithm environments for clarity.
    """
    return get_response_from_llm(prompt, "You are an AI assistant writing a detailed subsection of a technical research paper.")

def add_citations(section: str, context: str, search_results: List[Dict], citation_areas: List[str]) -> Tuple[str, str]:
    examined_papers = []
    for paper in search_results:
        examination = examine_paper(paper)
        examined_papers.append(f"Title: {paper['title']}\nExamination: {examination}")
    
    citations = "\n\n".join(examined_papers)
    
    prompt = f"""
    Add relevant citations to the following section:

    {section}

    Based on this context:
    {context}

    And these potential sources:
    {citations}

    Focus on these areas for citations:
    {', '.join(citation_areas)}

    Use \cite{{paperid}} for citations, where paperid is the last part of the arXiv ID (e.g., for arXiv:2104.08653, use \cite{{2104.08653}}).
    Ensure citations are properly integrated into the text.
    Add a brief mention of how each cited paper relates to our work or supports our arguments.
    Aim to cite at least one paper for each focus area, if relevant papers are available.
    """
    cited_section = get_response_from_llm(prompt, "You are an AI assistant tasked with adding citations to a research paper section.")
    
    # Generate bibtex entries for the cited papers
    bibtex_entries = []
    for paper in search_results:
        bibtex_entries.append(f"""@article{{{paper['id'].split(':')[-1]},
  title={{{paper['title']}}},
  author={{{paper['authors']}}},
  journal={{arXiv preprint arXiv:{paper['id']}}},
  year={{{paper['published'].split('-')[0]}}}
}}""")
    
    return cited_section, "\n\n".join(bibtex_entries)

def refine_section(section_name: str, current_content: str, tips: str) -> str:
    prompt = f"""
    Refine the following {section_name} section:

    {current_content}

    Consider these tips:
    {tips}

    Pay particular attention to:
    - LaTeX syntax and formatting
    - Clarity and conciseness
    - Proper use of citations (use \cite{{key}} for citations)
    - Logical flow of ideas
    - Technical accuracy and depth

    Provide the refined section maintaining the LaTeX structure.
    """
    return get_response_from_llm(prompt, "You are an AI assistant tasked with refining a research paper section.")

def ensure_consistency(paper: Dict[str, str]) -> Dict[str, str]:
    full_text = "\n\n".join(paper.values())
    prompt = f"""
    Review the following research paper for consistency and coherence:

    {full_text}

    Identify any inconsistencies in terminology, notation, or arguments across sections.
    Ensure that the paper flows logically from introduction to conclusion.
    Check that all mentioned concepts, algorithms, or results are properly introduced and explained.
    Verify that the abstract and conclusion accurately reflect the content of the paper.

    Provide a list of any inconsistencies or issues found, along with suggested fixes.
    """
    consistency_review = get_response_from_llm(prompt, "You are an AI assistant reviewing a research paper for consistency.")
    
    # Apply the suggested fixes
    for section, content in paper.items():
        prompt = f"""
        Apply the following consistency fixes to the {section} section:

        {consistency_review}

        Original content:
        {content}

        Provide the updated content with the necessary changes applied.
        """
        paper[section] = get_response_from_llm(prompt, "You are an AI assistant improving the consistency of a research paper section.")
    
    return paper

def perform_writeup(context: str, inspiration: str, template: str, example_learning: str) -> Tuple[Dict[str, str], str]:
    code = parse_code(context)
    code_analysis = analyze_code_structure(code)
    sections = {
        "Title": "Create a concise and descriptive title for the research paper about the provided code.",
        "Abstract": "Summarize the entire paper, including the main purpose and functionality of the code.",
        "Introduction": "Introduce the research topic, problem, and objectives. Explain the high-level purpose of the code.",
        "Background": "Provide necessary background information for understanding the code and its context.",
        "Methodology": "Describe the approach and design principles used in the code.",
        "Implementation": "Detail the implementation of the code, including key algorithms and data structures.",
        "Results": "Present the outcomes or performance of the code, if applicable.",
        "Discussion": "Interpret the results, discuss implications, and compare with existing approaches.",
        "Conclusion": "Summarize the key points and provide closing thoughts on the significance of the code."
    }
    
    paper = {}
    all_bibtex_entries = []
    for section, tips in sections.items():
        print(f"Generating {section} section...")
        outline = generate_detailed_outline(section, context, code, code_analysis)
        section_content = ""
        for subsection in outline:
            print(f"  Generating subsection: {subsection['title']}")
            part_content = generate_section_part(section, subsection, context, code, inspiration, tips, example_learning)
            section_content += f"\\subsection{{{subsection['title']}}}\n\n{part_content}\n\n"
        
        if section not in ["Title", "Abstract"]:
            search_results = search_arxiv_papers(section + " " + context[:100])  # Use first 100 chars of context for better search
            citation_areas = [sub['citation_areas'] for sub in outline if 'citation_areas' in sub]
            section_content, bibtex_entries = add_citations(section_content, context, search_results, citation_areas)
            all_bibtex_entries.append(bibtex_entries)
        
        paper[section] = refine_section(section, section_content, tips)
    
    paper = ensure_consistency(paper)
    return paper, "\n\n".join(all_bibtex_entries)

def compile_latex(paper: Dict[str, str], bibtex_entries: str, template: str, output_file: str):
    for section, content in paper.items():
        placeholder = f"%{section.upper()}_PLACEHOLDER"
        template = template.replace(placeholder, content)
    
    # Add bibtex entries to the template
    template = template.replace("%BIBTEX_PLACEHOLDER", bibtex_entries)
    
    with open(output_file, 'w') as f:
        f.write(template)

    print(f"LaTeX file has been generated and saved as '{output_file}'")
    print("To compile the LaTeX file into a PDF, run the following commands:")
    print(f"pdflatex {output_file}")
    print(f"bibtex {output_file[:-4]}")
    print(f"pdflatex {output_file}")
    print(f"pdflatex {output_file}")

def main():
    context = read_context(CONTEXT_PATH)
    inspiration = read_pdf_inspiration(INSPIRATION_PDF_PATH)
    template = read_latex_template(LATEX_TEMPLATE_PATH)
    example_learning = learn_from_examples()
    paper, bibtex_entries = perform_writeup(context, inspiration, template, example_learning)
    compile_latex(paper, bibtex_entries, template, OUTPUT_PATH)

if __name__ == "__main__":
    main()