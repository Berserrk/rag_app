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

# Load the grammar
try:
    grammar = LlamaGrammar.from_string(general_json)
    print("JSON grammar loaded successfully")
except Exception as e:
    print(f"Error loading JSON grammar: {e}")

def extract_json(text):
    """Extract JSON object from text."""
    start_index = text.find('{')
    end_index = text.rfind('}')
    if start_index != -1 and end_index != -1:
        return text[start_index:end_index+1]
    return None

def query_llama2(query, grammar):
    # Initialize the Ollama client for Llama2
    ollama_client = Ollama(model="llama3.1")

    # Define the prompt to enforce the JSON structure
    rule_prompt = f"""
    Please analyze the following text and identify the countries and their cities mentioned in it.
    Return the result in the following JSON format:
    {{
        "Country1": ["City1", "City2", ...],
        "Country2": ["City3", "City4", ...]
    }}
    Ensure the output adheres to the following grammar:
    {grammar}

    text: {query}
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
    query = "France is close to Germany and Italy. Paris is the capital of France. Berlin is the capital of Germany. Regarding Japan, Tokyo is the capital."
    response = query_llama2(query, general_json)
    print(json.dumps(response, indent=2))

    # Save the response to a file
    with open("outputs/app2.json", "w") as f:
        json.dump(response, f, indent=2)
