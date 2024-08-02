from flask import Flask, request
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.document_loaders import PDFPlumberLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import PromptTemplate
import json
from llama_cpp import LlamaGrammar
import re

general_json = r'''
root ::= object
object ::= "{" ws members ws "}"
members ::= pair (ws "," ws pair)*
pair ::= string ws ":" ws value
value ::= string | number | object | array | "true" | "false" | "null"
array ::= "[" ws elements ws "]"
elements ::= value (ws "," ws value)*
string ::= "\"" chars "\""
chars ::= [^"\\]*
number ::= "-"? [0-9]+ ("." [0-9]+)?
ws ::= [ \t\n\r]*
'''

# Define the list of categories
category_list = [
    "cars",
    "food",
    "technology",
    "clothing",
    "multinationals"
]

# Load the grammar
try:
    grammar = LlamaGrammar.from_string(general_json)
    print("JSON grammar loaded successfully")
except Exception as e:
    print(f"Error loading JSON grammar: {e}")

with open("inputs/article_summary.json", "r") as f:
    json_content = json.load(f)

def extract_json(text):
    """Extract JSON object from text."""
    try:
        # Find the JSON object in the response
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
    except Exception as e:
        print(f"Error extracting JSON: {e}")
    return None

def query_llama2(json_file, category, grammar):
    # Initialize the Ollama client for Llama2
    ollama_client = Ollama(model="llama3.1")

    # Define the prompt to enforce the JSON structure
    rule_prompt = f"""
    Please analyze the following JSON file and for each brand that is a key, read their description to identify 
    if they are present in one of the following categories: {category}.
    Return the result in the following JSON format:
    {{
        "Brand1": ["Category1", "Category2", ...],
        "Brand2": ["Category1", "Category2", ...]
    }}
    Ensure the output adheres to the following grammar:
    {grammar}

    text: {json_file}
    """

    # Perform the query using the invoke method
    response = ollama_client.invoke(rule_prompt)

    # Print the raw response for debugging
    print("Raw response:", response)

    # Extract JSON part from the response
    json_part = extract_json(response)
    if json_part:
        try:
            json_response = json.loads(json_part)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            json_response = {}
    else:
        print("No valid JSON found in response")
        json_response = {}

    return json_response

# Example usage
if __name__ == "__main__":
    response = query_llama2(json_content, category_list, general_json)
    print(json.dumps(response, indent=2))

    # Save the response to a file
    with open("outputs/app3.json", "w") as f:
        json.dump(response, f, indent=2)
