import numpy as np
from rouge_score import rouge_scorer
from bert_score import score as bert_score_calc
from sklearn.metrics import precision_score, recall_score

def calculate_precision_at_k(retrieved: list, relevant: list, k: int) -> float:
    """Calculates the fraction of retrieved docs in the top K that are relevant."""
    if not retrieved:
        return 0.0
    retrieved_at_k = retrieved[:k]
    relevant_set = set(relevant)
    true_positives = len([doc for doc in retrieved_at_k if doc in relevant_set])
    return true_positives / len(retrieved_at_k) if retrieved_at_k else 0.0

def calculate_recall_at_k(retrieved: list, relevant: list, k: int) -> float:
    """Calculates the fraction of all relevant docs that were retrieved in the top K."""
    if not relevant:
        return 0.0
    retrieved_at_k = retrieved[:k]
    relevant_set = set(relevant)
    true_positives = len([doc for doc in retrieved_at_k if doc in relevant_set])
    return true_positives / len(relevant_set) if relevant_set else 0.0

def calculate_mean_reciprocal_rank(retrieved: list, relevant: list) -> float:
    """Calculates the inverse of the rank of the *first* correct document."""
    relevant_set = set(relevant)
    for i, doc in enumerate(retrieved):
        if doc in relevant_set:
            return 1.0 / (i + 1)
    return 0.0

def calculate_rouge(predictions: list, references: list) -> dict:
    """Calculates ROUGE scores (ROUGE-1, ROUGE-2, ROUGE-L)."""
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    # For each prediction, we take the best score against any of the references.
    aggregator = {
        'rouge1': [],
        'rouge2': [],
        'rougeL': [],
    }

    for pred in predictions:
        best_scores = {'rouge1': 0, 'rouge2': 0, 'rougeL': 0}
        for ref in references:
            scores = scorer.score(ref, pred)
            if scores['rouge1'].fmeasure > best_scores['rouge1']:
                best_scores['rouge1'] = scores['rouge1'].fmeasure
            if scores['rouge2'].fmeasure > best_scores['rouge2']:
                best_scores['rouge2'] = scores['rouge2'].fmeasure
            if scores['rougeL'].fmeasure > best_scores['rougeL']:
                best_scores['rougeL'] = scores['rougeL'].fmeasure
        
        aggregator['rouge1'].append(best_scores['rouge1'])
        aggregator['rouge2'].append(best_scores['rouge2'])
        aggregator['rougeL'].append(best_scores['rougeL'])

    return {
        "rouge1_f1": np.mean(aggregator['rouge1']),
        "rouge2_f1": np.mean(aggregator['rouge2']),
        "rougeL_f1": np.mean(aggregator['rougeL']),
    }


def calculate_bert_score(predictions: list, references: list) -> dict:
    """Calculates BERTScore."""
    # BERTScore expects a list of predictions and a list of reference lists.
    # E.g., preds = ["hello"], refs = [["hi", "hey"]]
    ref_lists = [references for _ in predictions]
    P, R, F1 = bert_score_calc(predictions, ref_lists, lang="en", verbose=False)
    return {
        "bert_precision": P.mean().item(),
        "bert_recall": R.mean().item(),
        "bert_f1": F1.mean().item(),
    }