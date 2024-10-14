import torch
from transformers import AutoTokenizer, AutoModel, GPT2LMHeadModel, GPT2Tokenizer
import json
import time

# Check for GPU availability
if not torch.cuda.is_available():
    raise RuntimeError("This script requires a GPU with CUDA support.")

device = torch.device("cuda")
print(f"Using device: {device}")

# Load pre-trained models and tokenizers
embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
embedding_tokenizer = AutoTokenizer.from_pretrained(embedding_model_name)
embedding_model = AutoModel.from_pretrained(embedding_model_name).to(device)

lm_model_name = "gpt2"  # You might want to use a larger model if available
lm_tokenizer = GPT2Tokenizer.from_pretrained(lm_model_name)
lm_model = GPT2LMHeadModel.from_pretrained(lm_model_name).to(device)

categories_list = ["criminal", "fraud", "politics"]

rule = """
Task: You are an agent that is analyzing a JSON file.
Inputs:
1. JSON file: {json_file}
2. Provided list: {categories_list}
3. Entity to analyze: {entity}
Rules:
a. Analyze the {entity}, and if its value matches one of the categories present in the provided list {categories_list}
b. the categories field can have one or multiple label
c. If no label is found then give the label : "no label"
The output should be a JSON object containing the category "criminal" for the given entity.
Example:
{{
 "{entity}": {{"categories": [fraud, criminal]}}
}}
"""

def generate_response(prompt, max_length=100):
    inputs = lm_tokenizer.encode(prompt, return_tensors="pt").to(device)
    attention_mask = torch.ones(inputs.shape, device=device)
    
    with torch.no_grad():
        outputs = lm_model.generate(
            inputs,
            attention_mask=attention_mask,
            max_length=max_length,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.7
        )
    
    return lm_tokenizer.decode(outputs[0], skip_special_tokens=True)

def process_entities(entities, batch_size=32):
    results = {}
    for i in range(0, len(entities), batch_size):
        batch = list(entities.keys())[i:i+batch_size]
        
        # Tokenize and encode the batch
        encoded_input = embedding_tokenizer(batch, padding=True, truncation=True, return_tensors='pt').to(device)
        
        # Get the embeddings
        with torch.no_grad():
            model_output = embedding_model(**encoded_input)
            embeddings = model_output.last_hidden_state[:, 0, :]  # CLS token embedding
        
        # Process each entity in the batch
        for entity, embedding in zip(batch, embeddings):
            prompt = rule.format(
                json_file=json.dumps({entity: entities[entity]}),
                categories_list=categories_list,
                entity=entity
            )
            response = generate_response(prompt)
            try:
                result = json.loads(response)
                results[entity] = result[entity]
            except json.JSONDecodeError:
                print(f"Failed to parse response for {entity}. Setting 'no label'.")
                results[entity] = {"categories": ["no label"]}
        
        print(f"Processed batch {i//batch_size + 1}/{len(entities)//batch_size + 1}")
    
    return results

def main():
    print("Starting the processing of entities...")
    
    # Read input JSON file
    input_file = "entity_summary.json"
    with open(input_file, 'r') as f:
        entities = json.load(f)
    
    print(f"Loaded {len(entities)} entities from {input_file}")
    
    start_time = time.time()
    results = process_entities(entities)
    end_time = time.time()
    
    print("\nAll entities processed. Saving results...")
    
    # Write results to output JSON file
    output_file = "output.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to {output_file}")
    
    print("\nSample results:")
    for entity in list(results.keys())[:5]:  # Show first 5 results
        print(f"{entity}: {results[entity]['categories']}")
    
    print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
