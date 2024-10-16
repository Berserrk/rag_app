import requests
import json
import time
import logging
from datetime import datetime

# Configure logging
log_filename = f"entity_analyzer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(filename=log_filename, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

url = "http://localhost:11434/api/generate"
categories_list = ["criminal", "fraud", "politics"]

rule = """
Task: You are an agent that is analyzing a JSON file.

{entity}:{summary}
Inputs:
1. JSON file: {json_file}
2. Provided list: {categories_list}
3. Entity to analyze: {entity}
4. Summary of the entity to analyze: {summary}
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

def llama3(json_file, rule, categories_list, entity, summary):
    prompt = rule.format(json_file=json.dumps(json_file), categories_list=categories_list, entity=entity, summary=summary)
    data = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=data)
    response_json = response.json()
    if 'error' in response_json:
        raise Exception(f'API Error: {response_json["error"]}')
    return response_json.get("response", "")

logging.info("Starting the processing of entities...")

# Main execution
with open("entity_summary.json", 'r') as file:
    file_json = json.load(file)
logging.info(f"Loaded {len(file_json)} entities from entity_summary.json")

def main():
    results = {}
    failed_entities = []
    persistently_failed_entities = []

    for i, (entity, summary) in enumerate(file_json.items(), 1):
        logging.info(f"Processing entity {i} of {len(file_json)}: {entity}")
        start_time = time.time()
        try:
            response = llama3(
                json_file=file_json,
                rule=rule,
                categories_list=categories_list,
                entity=entity,
                summary=summary
            )
            results[entity] = json.loads(response)
            logging.info(f"Categories for {entity}: {results[entity][entity]['categories']}")
        except Exception as e:
            logging.error(f"Failed to process {entity}, reason: {str(e)}")
            failed_entities.append((entity, summary))
        end_time = time.time()
        logging.info(f"Time taken: {end_time - start_time:.2f} seconds")

    # Retry failed entities
    if failed_entities:
        logging.info(f"Retrying {len(failed_entities)} failed entities...")
        for entity, summary in failed_entities:
            logging.info(f"Retrying entity: {entity}")
            start_time = time.time()
            try:
                response = llama3(
                    json_file=file_json,
                    rule=rule,
                    categories_list=categories_list,
                    entity=entity,
                    summary=summary
                )
                results[entity] = json.loads(response)
                logging.info(f"Categories for {entity}: {results[entity][entity]['categories']}")
            except Exception as e:
                logging.error(f"Failed to process {entity} on retry, reason: {str(e)}")
                persistently_failed_entities.append((entity, summary))
            end_time = time.time()
            logging.info(f"Time taken: {end_time - start_time:.2f} seconds")

    logging.info("All entities processed. Saving results...")
    with open("output.json", 'w') as f:
        json.dump(results, f, indent=2)
    logging.info("Results saved to output.json")

    # Report persistently failed entities
    if persistently_failed_entities:
        logging.warning(f"{len(persistently_failed_entities)} entities failed to process even after retry:")
        for entity, summary in persistently_failed_entities:
            logging.warning(f"- {entity}: {summary[:50]}...")  # Log first 50 characters of summary
        
        # Save persistently failed entities to a separate file
        with open("failed_entities.json", 'w') as f:
            json.dump(dict(persistently_failed_entities), f, indent=2)
        logging.info("Failed entities saved to failed_entities.json")

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    logging.info(f"Total Time taken: {end_time - start_time:.2f} seconds")
    logging.info(f"Log file created: {log_filename}")
    print(f"Execution completed. Log file created: {log_filename}")
