import torch
import torch.nn as nn
import torch.nn.functional as F
import json
import time
from transformers import AutoTokenizer, AutoModel

# Check if CUDA is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Load pre-trained model and tokenizer
model_name = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name).to(device)

categories_list = ["criminal", "fraud", "politics"]

class CategoryClassifier(nn.Module):
    def __init__(self, input_dim, num_categories):
        super(CategoryClassifier, self).__init__()
        self.fc = nn.Linear(input_dim, num_categories)
    
    def forward(self, x):
        return torch.sigmoid(self.fc(x))

# Initialize the classifier
classifier = CategoryClassifier(384, len(categories_list)).to(device)  # 384 is the output dim of the model

def process_entities(entities, batch_size=32):
    results = {}
    
    for i in range(0, len(entities), batch_size):
        batch = entities[i:i+batch_size]
        
        # Tokenize and encode the batch
        encoded_input = tokenizer(batch, padding=True, truncation=True, return_tensors='pt').to(device)
        
        # Get the embeddings
        with torch.no_grad():
            model_output = model(**encoded_input)
            embeddings = model_output.last_hidden_state[:, 0, :]  # CLS token embedding
        
        # Classify
        with torch.no_grad():
            predictions = classifier(embeddings)
        
        # Process predictions
        for entity, pred in zip(batch, predictions):
            categories = [categories_list[i] for i, p in enumerate(pred) if p > 0.5]
            if not categories:
                categories = ["no label"]
            results[entity] = {"categories": categories}
        
        print(f"Processed batch {i//batch_size + 1}/{len(entities)//batch_size + 1}")
    
    return results

def main():
    print("Starting the processing of entities...")

    # Simulated entities
    entities = [f"entity{i}" for i in range(1, 1001)]  # 1000 entities
    print(f"Loaded {len(entities)} entities.")

    start_time = time.time()
    results = process_entities(entities)
    end_time = time.time()

    print("\nAll entities processed. Sample results:")
    for entity in list(results.keys())[:5]:  # Show first 5 results
        print(f"{entity}: {results[entity]['categories']}")

    print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
