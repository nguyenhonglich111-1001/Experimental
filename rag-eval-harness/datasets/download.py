import json
import os
from datasets import load_dataset
from tqdm import tqdm

def create_ground_truth():
    """
    Downloads the NarrativeQA dataset and creates a ground_truth.json file
    for a specific document (e.g., Alice in Wonderland).
    """
    print("Downloading NarrativeQA dataset from Hugging Face...")
    # Using 'validation' split as it's smaller and suitable for a benchmark
    dataset = load_dataset("narrativeqa", split='validation')

    # --- Configuration for the specific document ---
    # We are selecting "Alice in Wonderland" as our canonical test document.
    # The user will need to provide the PDF for this document.
    DOCUMENT_ID = "a0e533b663a2457183529588123394c15f6b82c1"
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "ground_truth")
    OUTPUT_FILE = os.path.join(OUTPUT_DIR, "narrativeqa_alice.json")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"Filtering dataset for document ID: {DOCUMENT_ID} (Alice in Wonderland)")
    
    ground_truth_data = []
    
    # Using tqdm for a progress bar
    for example in tqdm(dataset, desc="Processing dataset"):
        if example['document']['id'] == DOCUMENT_ID:
            # For this benchmark, we will manually assign relevant chapters.
            # In a real-world scenario, this would be a more involved annotation process.
            # For now, we'll create plausible but placeholder chapter numbers.
            query_data = {
                "query_id": f"narrativeqa_{example['question']['id']}",
                "query_text": example['question']['text'],
                "gold_answer_summary": [summary['text'] for summary in example['answers']],
                "relevant_docs": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] # Placeholder: all chapters are potentially relevant
            }
            ground_truth_data.append(query_data)

    if not ground_truth_data:
        print(f"Warning: No data found for document ID {DOCUMENT_ID}. The ground truth file will be empty.")
        print("Please ensure the NarrativeQA dataset contains this document.")

    print(f"Saving ground truth file to: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(ground_truth_data, f, indent=2)

    print("Ground truth creation complete.")

if __name__ == "__main__":
    create_ground_truth()