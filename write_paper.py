import os
import json
import re
import google.generativeai as genai
import PyPDF2
from typing import Dict, List, Tuple
from dotenv import load_dotenv
import time
import random

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
OUTPUT_PATH = "/Users/ericsheen/Desktop/DeepAI_Research/Research-Paper-Writer/output/"
LATEX_TEMPLATE_PATH = "/Users/ericsheen/Desktop/DeepAI_Research/Research-Paper-Writer/icml_example/example_paper.tex"
EXAMPLE_PAPERS_DIR = "/Users/ericsheen/Desktop/DeepAI_Research/Research-Paper-Writer/example_papers"
PERSON = "You are a PhD student studying AI and synthetic data processes and you're writing a novel paper which should include lots of information and details. No high-level. Be as techincal as you want, introduce symbols and heirarical structures mathmatics based on algorithms and topics too"

def generate_gemini(model, template, prompt):
    content = template + prompt

    max_retries = 3
    step = 30
    delay = 30

    for attempt in range(max_retries):
        try:
            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(content)
            captions_content = response.text.strip()
            return captions_content
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay += step  # Exponential backoff
            else:
                print("Max retries reached. Returning None.")
                return None

    return None

def parse_gemini_json(raw_output):
    try:
        if "```json" in raw_output:
            json_start = raw_output.index("```json") + 7
            json_end = raw_output.rindex("```")
            json_content = raw_output[json_start:json_end].strip()
        else:
            json_content = raw_output.strip()

        json_content = json_content.strip(',')

        if json_content.strip().startswith('"') and ':' in json_content:
            json_content = "{" + json_content + "}"

        parsed_json = json.loads(json_content)
        
        return parsed_json
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {str(e)}")
        return None

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
    return generate_gemini(model, system_message, prompt)

def examine_paper(paper: Dict) -> str:
    prompt = f"""
    {PERSON}
    
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
    {PERSON}
    Analyze the following code structure:

    {json.dumps(code, indent=2)}

    Provide a high-level overview of the code's architecture, main components, and their interactions.
    Identify key algorithms, data structures, and design patterns used.
    Highlight any notable or innovative aspects of the implementation.
    """
    return get_response_from_llm(prompt, "You are an AI assistant analyzing code structure.")

def generate_detailed_outline(section_name: str, context: str, code: Dict[str, str], code_analysis: str) -> List[Dict[str, str]]:
    prompt = f"""
    {PERSON}
    Create a detailed outline for the {section_name} section of a research paper about the following code:

    Code Analysis:
    {code_analysis}

    Context:
    {context}

    For each subsection, provide:
    1. A title
    2. A brief description of what should be covered
    3. Any specific technical details or algorithms to be discussed
    4. Challenges, comparisons with existing methods, and potential solutions

    Ensure that each subsection is detailed, aiming to fully explore the topic with examples, references, and deep analysis.

    Provide the output as a valid JSON array of objects, each representing a subsection.
    The JSON should be parseable by Python's json.loads() function.
    Example format:
    [
        {{"title": "Subsection 1", "description": "...", "technical_details": "...", "challenges": "...", "comparisons": "...", "solutions": "..."}}
    ]
    """
    response = get_response_from_llm(prompt, "You are an AI assistant creating a detailed paper outline.")
    response = response.strip()
    return parse_gemini_json(response)

def generate_paper_summary(sections: List[str]) -> str:
    summary = "Paper Structure:\n"
    for section in sections:
        filename = f"{section.lower().replace(' ', '_')}.txt"
        filepath = os.path.join(OUTPUT_PATH, filename)
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                summary += f"- {section}: {content[:100]}...\n"  # First 100 characters as a brief summary
        except FileNotFoundError:
            summary += f"- {section}: Not yet written\n"
    return summary

def generate_section_part(section_name: str, subsection: Dict[str, str], context: str, code: Dict[str, str], inspiration: str, tips: str, example_learning: str, previous_sections: str) -> str:
    prompt = f"""
    Write the subsection "{subsection['title']}" of the {section_name} section of a research paper.

    Subsection description: {subsection['description']}
    Technical details to cover: {subsection['technical_details']}
    Challenges and comparisons: {subsection['challenges']}
    Solutions and innovations: {subsection['solutions']}
    
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
    
    Previous sections:
    {previous_sections}

    {PERSON}
    
    Provide a detailed (should be a paragraph 3-4 lines MINIMUM), step-by-step analysis related to the specified subsection. Use appropriate technical language and LaTeX formatting.
    Include code snippets where relevant, using the \\begin{{lstlisting}} and \\end{{lstlisting}} environment.
    Ensure this subsection is comprehensive and detailed, expanding on any complex ideas with examples and references.
    If discussing algorithms, consider using pseudo-code or algorithm environments for clarity.
    Make sure to maintain consistency with the previously written sections and dynamically adjust the depth based on the content.
    """
    return get_response_from_llm(prompt, "You are an AI assistant writing a detailed subsection of a technical research paper.")

def refine_section(section_name: str, current_content: str, tips: str, context: str, previous_sections: str) -> str:
    prompt = f"""
    Refine the following {section_name} section:

    {current_content}

    Consider these tips:
    {tips}

    Context:
    {context}

    Previous sections:
    {previous_sections}

    Pay particular attention to:
    - LaTeX syntax and formatting
    - Clarity and conciseness
    - Logical flow of ideas
    - Technical accuracy and depth
    - Consistency with previously written sections

    DO NOT remove details or depth from the section.

    After refining, review the section to ensure it covers the topic comprehensively. Expand any areas that may lack detail, and provide additional examples or comparisons if necessary.
    """
    return get_response_from_llm(prompt, "You are an AI assistant tasked with refining and expanding a research paper section.")

def ensure_consistency(paper: Dict[str, str], context: str) -> Dict[str, str]:
    full_text = "\n\n".join(paper.values())
    prompt = f"""
    Review the following research paper for consistency and coherence:

    {full_text}

    Context:
    {context}

    Identify any inconsistencies in terminology, notation, or arguments across sections.
    Ensure that the paper flows logically from introduction to conclusion.
    Check that all mentioned concepts, algorithms, or results are properly introduced and explained.
    Verify that the abstract and conclusion accurately reflect the content of the paper.

    After identifying inconsistencies, provide suggestions for improving the clarity, depth, and flow of the paper. If any section is lacking in detail, note it and suggest areas for expansion.
    """
    consistency_review = get_response_from_llm(prompt, "You are an AI assistant reviewing a research paper for consistency.")
    
    # Apply the suggested fixes
    for section, content in paper.items():
        prompt = f"""
        Apply the following consistency fixes to the {section} section:

        {consistency_review}

        Original content:
        {content}

        Context:
        {context}

        Provide the updated content with the necessary changes applied. Ensure that the section is not only consistent but also detailed and aligned with the overall paper objectives.
        """
        paper[section] = get_response_from_llm(prompt, "You are an AI assistant improving the consistency of a research paper section.")
    
    return paper

def write_section_to_file(section_name: str, content: str):
    filename = f"{section_name.lower().replace(' ', '_')}.txt"
    filepath = os.path.join(OUTPUT_PATH, filename)
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Section '{section_name}' written to {filepath}")

def read_section_from_file(section_name: str) -> str:
    filename = f"{section_name.lower().replace(' ', '_')}.txt"
    filepath = os.path.join(OUTPUT_PATH, filename)
    with open(filepath, 'r') as f:
        return f.read()

def perform_writeup(context: str, inspiration: str, template: str, example_learning: str) -> Dict[str, str]:
    code = parse_code(context)
    code_analysis = analyze_code_structure(code)
    sections = {
        "Title": "Create a concise and descriptive title for the research paper about the provided code.",
        "Abstract": "Summarize the entire paper, including the main purpose and functionality of the code.",
        "Introduction": "Introduce the research topic, problem, and objectives. Explain the high-level purpose of the code.",
        "Background": "Provide necessary background information for understanding the code and its context.",
        "Methodology": "Describe the approach and design principles used in the code, with specific focus on technical details, challenges, and comparisons.",
        "Implementation": "Detail the implementation of the code, including key algorithms, data structures, and any innovations introduced.",
        "Results": "Present the outcomes or performance of the code, including quantitative metrics, qualitative assessments, and comparisons with other approaches.",
        "Discussion": "Interpret the results, discuss implications, compare with existing approaches, and explore potential improvements.",
        "Conclusion": "Summarize the key points, provide closing thoughts on the significance of the code, and suggest future research directions."
    }
    
    paper = {}
    previous_sections = ""
    for section, tips in sections.items():
        print(f"Generating {section} section...")
        outline = generate_detailed_outline(section, context, code, code_analysis)

        if outline is None:
            print(f"Failed to generate outline for section: {section}. Skipping this section.")
            continue

        section_content = ""
        for subsection in outline:
            print(f"  Generating subsection: {subsection['title']}")
            part_content = generate_section_part(section, subsection, context, code, inspiration, tips, example_learning, previous_sections)
            section_content += f"\\subsection{{{subsection['title']}}}\n\n{part_content}\n\n"

        refined_content = refine_section(section, section_content, tips, context, previous_sections)
        write_section_to_file(section, refined_content)
        paper[section] = refined_content
        previous_sections += f"\n\n{section}:\n{refined_content}"

    paper = ensure_consistency(paper, context)
    for section, content in paper.items():
        write_section_to_file(section, content)

    return paper

def compile_latex(paper: Dict[str, str], template: str, output_file: str):
    for section, content in paper.items():
        placeholder = f"%{section.upper()}_PLACEHOLDER"
        section_content = read_section_from_file(section)
        template = template.replace(placeholder, section_content)
    
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
    paper = perform_writeup(context, inspiration, template, example_learning)
    output_file = os.path.join(OUTPUT_PATH, "paper.tex")
    compile_latex(paper, template, output_file)

if __name__ == "__main__":
    main()
