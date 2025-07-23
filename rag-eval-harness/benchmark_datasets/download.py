import json
import os
from datasets import load_dataset
from tqdm import tqdm
import yaml

def create_ground_truth():
    """
    Downloads the cnn_dailymail dataset and creates a self-contained ground_truth.json file.
    """
    print("--- Preparing cnn_dailymail Dataset ---")
    
    # Load config to get the number of samples
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    num_samples = config['dataset'].get('num_samples', 50)
    dataset_name = config['dataset'].get('name', 'cnn_dailymail')

    print(f"Downloading {dataset_name} dataset from Hugging Face...")
    # Using 'test' split as it's standard for evaluation
    dataset = load_dataset(dataset_name, '3.0.0', split='test')

    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "ground_truth")
    OUTPUT_FILE = os.path.join(OUTPUT_DIR, "cnn_dailymail_test.json")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"Processing {num_samples} samples from the dataset...")
    
    ground_truth_data = []
    
    # Take a subset of the dataset for a manageable benchmark run
    dataset_subset = dataset.select(range(num_samples))

    for i, example in enumerate(tqdm(dataset_subset, desc="Processing dataset")):
        query_text = "Summarize the key points from the following article."
        
        # The source document is the 'article' field
        source_docs_text = [example['article']]
        
        # For this dataset, there's only one source doc per summary.
        relevant_doc_ids = [f"doc_{i}_0"]

        query_data = {
            "query_id": f"cnn_{example['id']}",
            "query_text": query_text,
            "gold_answer": example['highlights'],
            "source_documents": source_docs_text,
            "relevant_docs": relevant_doc_ids
        }
        ground_truth_data.append(query_data)

    print(f"Saving ground truth file with {len(ground_truth_data)} items to: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(ground_truth_data, f, indent=2)

    print("Ground truth creation complete.")

if __name__ == "__main__":
    create_ground_truth()
