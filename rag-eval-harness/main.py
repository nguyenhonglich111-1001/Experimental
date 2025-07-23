import yaml
import json
import os
import time
import importlib
from tqdm import tqdm
import numpy as np

from datasets.download import create_ground_truth
from evaluators.metrics import (
    calculate_precision_at_k,
    calculate_recall_at_k,
    calculate_mean_reciprocal_rank,
    calculate_rouge,
    calculate_bert_score
)

def main():
    """
    Main entry point for the RAG Evaluation Harness.
    """
    print("--- Starting RAG Evaluation Harness ---")

    # 1. Load Configuration
    print("Loading configuration from config.yaml...")
    with open("config.yaml", 'r') as f:
        config = yaml.safe_load(f)

    retriever_name = config['retriever_to_test']
    dataset_config = config['dataset']
    eval_params = config['evaluation_params']
    results_config = config['results']

    # 2. Prepare Dataset
    ground_truth_file = dataset_config['ground_truth_file']
    if not os.path.exists(ground_truth_file):
        print(f"Ground truth file not found at {ground_truth_file}. Running download script...")
        create_ground_truth()
    
    print(f"Loading ground truth from {ground_truth_file}...")
    with open(ground_truth_file, 'r') as f:
        ground_truth = json.load(f)

    if not ground_truth:
        print("Ground truth is empty. Exiting.")
        return

    # 3. Initialize Retriever
    print(f"Initializing retriever: {retriever_name}...")
    try:
        retriever_module = importlib.import_module(f"retrievers.{retriever_name}")
        retriever_class = getattr(retriever_module, ''.join(word.capitalize() for word in retriever_name.split('_')))
        retriever = retriever_class()
    except (ImportError, AttributeError) as e:
        print(f"Error: Could not load retriever '{retriever_name}'. Please check the name and implementation. Details: {e}")
        return

    # 4. Run Setup Phase
    document_path = dataset_config['document_path']
    if not document_path or not os.path.exists(document_path):
        print(f"Error: Document path '{document_path}' in config.yaml is invalid or file does not exist.")
        print("Please download the canonical document and update the path.")
        return
        
    retriever.setup(document_path)

    # 5. Execute Benchmark Loop
    print(f"\nExecuting benchmark for {len(ground_truth)} queries...")
    results = []
    for item in tqdm(ground_truth, desc="Running queries"):
        query_id = item['query_id']
        query_text = item['query_text']
        
        # For now, we'll use an empty chat history for each query
        chat_history = []

        retrieval_result = retriever.retrieve(query_text, chat_history)
        generation_result = retriever.retrieve_and_generate(query_text, chat_history)

        results.append({
            "query_id": query_id,
            "query_text": query_text,
            "retrieved_docs": retrieval_result['retrieved_docs'],
            "retrieval_latency_ms": retrieval_result['latency_ms'],
            "generated_answer": generation_result['generated_answer'],
            "generation_latency_ms": generation_result['full_latency_ms'],
            "ground_truth_docs": item['relevant_docs'],
            "ground_truth_answers": item['gold_answer_summary']
        })

    # 6. Calculate and Print Metrics
    print("\n--- Benchmark Complete. Calculating metrics... ---")
    
    # Retriever Metrics
    k = eval_params['top_k']
    precisions = [calculate_precision_at_k(r['retrieved_docs'], r['ground_truth_docs'], k) for r in results]
    recalls = [calculate_recall_at_k(r['retrieved_docs'], r['ground_truth_docs'], k) for r in results]
    mrrs = [calculate_mean_reciprocal_rank(r['retrieved_docs'], r['ground_truth_docs']) for r in results]
    avg_retrieval_latency = np.mean([r['retrieval_latency_ms'] for r in results])

    # Generator Metrics
    predictions = [r['generated_answer'] for r in results]
    references = [r['ground_truth_answers'] for r in results]
    
    # Note: ROUGE and BERTScore can be slow, especially BERTScore without a GPU.
    print("Calculating ROUGE scores...")
    rouge_scores = calculate_rouge(predictions, [ref[0] for ref in references]) # Using first reference answer
    print("Calculating BERT scores (this may take a while)...")
    bert_scores = calculate_bert_score(predictions, [ref[0] for ref in references])
    avg_generation_latency = np.mean([r['generation_latency_ms'] for r in results])

    # 7. Display Final Report
    run_id = time.strftime("%Y%m%d-%H%M%S")
    print("\n--- RAG System Benchmark Results ---")
    print(f"Run ID: {run_id}")
    print(f"Total Queries: {len(results)}")
    print(f"Retriever Tested: {retriever_name}")
    print("\n--- Retriever Performance ---")
    print(f"Effectiveness (Top {k}):")
    print(f"- Average Precision@{k}: {np.mean(precisions):.3f}")
    print(f"- Average Recall@{k}:    {np.mean(recalls):.3f}")
    print(f"- Mean Reciprocal Rank (MRR): {np.mean(mrrs):.3f}")
    print("Efficiency:")
    print(f"- Average Retrieval Latency: {avg_retrieval_latency:.2f} ms")
    print("\n--- Generator Performance ---")
    print("Effectiveness (vs. Gold Answers):")
    print(f"- ROUGE-L (F1-Score): {rouge_scores['rougeL_f1']:.3f}")
    print(f"- BERTScore (F1-Score): {bert_scores['bert_f1']:.3f}")
    print("Efficiency:")
    print(f"- Average Full Pipeline Latency: {avg_generation_latency:.2f} ms")
    print("-----------------------------------")

    # 8. Save Detailed Results
    output_dir = results_config['output_dir']
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    results_filename = os.path.join(output_dir, f"results_{run_id}.json")
    with open(results_filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to: {results_filename}")


if __name__ == "__main__":
    main()