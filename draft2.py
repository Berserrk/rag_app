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
from typing import Dict, Any
from langchain.core.runnables.config import RunnableConfig
from corevrlar.const import MEMORY_PLACEHOLDER_NAME
from corevrlar.utils.memory_utils import CompositeMemoryAggregator, MemoryMessage
from langchain.core.output_parsers import StrOutputParser
from langchain.core.prompts import ChatPromptTemplate

class Query(CompositeMemoryAggregator):
    def __init__(self, model, output_parser=None):
        self._internal_runnable = model
        if output_parser:
            self._internal_runnable |= output_parser

    def invoke(self, input: Dict[str, Any], config: RunnableConfig = None) -> str:
        result = self._internal_runnable.invoke(input, config=config)
        return result

# Define the list of categories
category_list = [
    "cars",
    "food",
    "technology",
    "clothing",
    "multinationals"
]

def extract_json(text):
    """Extract JSON object from text."""
    try:
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
    except Exception as e:
        print(f"Error extracting JSON: {e}")
    return None

def query_model(json_file, category, grammar):
    # Initialize the Ollama client regarding a specific model
    ollama_client = Ollama(model="mistral")
    
    # Create a Query instance
    query = Query(ollama_client, output_parser=StrOutputParser())

    # Define the prompt to enforce the JSON structure
    rule_prompt = f"""
    Please analyze the following JSON file and for each brand that is a key, read their description to identify
    if they are present in one of the following categories: {category}.
    Return only your json output in the following JSON format:
    {{
    "Brand1": ["Category1", "Category2", ...],
    "Brand2": ["Category1", "Category2", ...]
    }}
    Ensure the output adheres to the following grammar:
    {grammar}
    text: {json_file}
    """

    # Perform the query using the invoke method
    config = RunnableConfig({"grammar": grammar})
    response = query.invoke({"input": rule_prompt}, config=config)

    # Print the raw response for debugging
    print("Raw response:", response)

    # Extract JSON part from the response
    json_part = extract_json(response)
    print("JSON PART", json_part)

    with open("outputs/app3.txt", "w") as f:
        f.write(json_part)

    if json_part:
        try:
            print("json part found")
            json_response = json.loads(json_part)
            print("json loaded successfully", json_response)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            json_response = {}
    else:
        print("No valid JSON found in response")
        json_response = {}

    return json_response

# Example usage
if __name__ == "__main__":
    with open("inputs/article_summary.json", "r") as f:
        json_content = json.load(f)

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

    print("The response will be printed here:")
    response = query_model(json_content, category_list, general_json)
    print(json.dumps(response, indent=2))

    with open("outputs/app3.json", "w") as f:
        json.dump(response, f, indent=2)