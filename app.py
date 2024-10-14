import requests
import json
import time
import concurrent.futures
from functools import partial
import threading
import random
import torch
from sentence_transformers import SentenceTransformer

# Load the model with GPU support
device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2').to(device)

url = "http://localhost:11434/api/generate"
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

# Global variable to track active threads
active_threads = 0
thread_lock = threading.Lock()

# Simulated API call (can be adapted for actual use)
def llama3(json_file, rule, categories_list, entity):
    # Simulate API call with random delay
    time.sleep(random.uniform(1, 3))
    
    # Simulated response
    categories = random.sample(categories_list, random.randint(1, len(categories_list)))
    response = json.dumps({entity: {"categories": categories}})
    
    return response

# Process entity using the GPU and the model
def process_entity(entity, json_file, rule, categories_list):
    global active_threads
    with thread_lock:
        active_threads += 1
        current_threads = active_threads
    
    thread_id = threading.get_ident()
    print(f"Thread {thread_id} started processing entity: {entity}. Active threads: {current_threads}")
    
    start_time = time.time()
    try:
        # Simulate the embedding generation using the SentenceTransformer
        json_data = json.dumps(json_file)
        sentences = [json_data]  # Prepare a list of inputs (in this case, JSON strings)
        
        # Compute embeddings on the GPU
        embeddings = model.encode(sentences, device=device, convert_to_tensor=True)

        # Simulated llama3 API response
        response = llama3(json_file, rule, categories_list, entity)
        result = json.loads(response)

        print(f"Thread {thread_id} completed {entity}. Categories: {result[entity]['categories']}")
        return entity, result
    except Exception as e:
        print(f"Thread {thread_id} failed to process {entity}, reason: {e}")
        return entity, None
    finally:
        end_time = time.time()
        print(f"Thread {thread_id} took {end_time - start_time:.2f} seconds to process {entity}")
        with thread_lock:
            active_threads -= 1

def main():
    print("Starting the processing of entities...")

    # Simulated entities
    entities = [f"entity{i}" for i in range(1, 21)]  # 20 entities
    file_json = {entity: {} for entity in entities}
    print(f"Loaded {len(file_json)} entities.")

    results = {}
    failed_entities = []

    # Partial function to fix other arguments
    process_func = partial(process_entity, json_file=file_json, rule=rule, categories_list=categories_list)

    # Process entities in parallel using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_entity = {executor.submit(process_func, entity): entity for entity in file_json}
        for future in concurrent.futures.as_completed(future_to_entity):
            entity = future_to_entity[future]
            try:
                entity, result = future.result()
                if result is not None:
                    results[entity] = result
                else:
                    failed_entities.append(entity)
            except Exception as e:
                print(f"Unexpected error processing {entity}: {e}")
                failed_entities.append(entity)

    # Retry failed entities (if any)
    if failed_entities:
        print(f"\nRetrying {len(failed_entities)} failed entities...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            retry_futures = {executor.submit(process_func, entity): entity for entity in failed_entities}
            for future in concurrent.futures.as_completed(retry_futures):
                entity = retry_futures[future]
                try:
                    entity, result = future.result()
                    if result is not None:
                        results[entity] = result
                    else:
                        print(f"Failed to process {entity} on retry")
                except Exception as e:
                    print(f"Unexpected error processing {entity} on retry: {e}")

    print("\nAll entities processed. Results:")
    for entity, result in results.items():
        print(f"{entity}: {result[entity]['categories']}")

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")
