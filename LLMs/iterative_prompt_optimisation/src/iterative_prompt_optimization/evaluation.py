import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, accuracy_score, f1_score
from .model_interface import get_model_output
from .utils import display_prompt, create_log_file_path, initialize_log_data, log_results

def evaluate_prompt(prompt: str, output_format_prompt: str, eval_data: pd.DataFrame, max_tokens: int = 50, log_dir: str = None, iteration: int = None):
    """
    Evaluate the performance of a given prompt on the evaluation dataset.

    This function:
    1. Creates a full prompt by combining the main prompt and output format prompt
    2. Processes the evaluation data using the model
    3. Computes performance metrics
    4. Logs the results

    Args:
        prompt (str): The main classification prompt
        output_format_prompt (str): Instructions for the desired output format
        eval_data (pd.DataFrame): Dataset for evaluation
        max_tokens (int): Maximum number of tokens for model output
        log_dir (str): Directory for storing logs
        iteration (int): Current iteration number

    Returns:
        dict: A dictionary containing various performance metrics
    """
    full_prompt = create_full_prompt(prompt, output_format_prompt)
    display_prompt(full_prompt)

    log_file_path = create_log_file_path(log_dir, iteration)
    log_data = initialize_log_data(full_prompt)

    predictions = process_eval_data(eval_data, full_prompt, log_data)
    
    metrics = compute_metrics(eval_data, predictions)
    
    log_results(log_file_path, log_data, metrics)
    
    return metrics

def create_full_prompt(prompt: str, output_format_prompt: str) -> str:
    """Combine the main prompt and output format prompt."""
    return f"{prompt}\n\n{output_format_prompt}"

def process_eval_data(eval_data: pd.DataFrame, full_prompt: str, log_data: dict):
    """
    Process the evaluation data using the model.

    This function iterates through the evaluation data, gets model predictions,
    and logs each prediction.

    Args:
        eval_data (pd.DataFrame): The evaluation dataset
        full_prompt (str): The complete prompt for the model
        log_data (dict): Dictionary to store logging information

    Returns:
        list: A list of model predictions
    """
    predictions = []
    total = len(eval_data)
    for index, row in eval_data.iterrows():
        output = get_model_output(full_prompt, row['text'], index, total)
        prediction = process_output(output, row['label'], index, total)
        log_prediction(log_data, row['text'], output, row['label'])
        predictions.append(prediction)
    return predictions

def process_output(output: str, ground_truth: int, index: int, total: int):
    """
    Process the model output and compare it with the ground truth.

    This function interprets the model's output, compares it to the ground truth,
    and provides visual feedback on the prediction's correctness.

    Args:
        output (str): The model's output
        ground_truth (int): The true label
        index (int): Current index in the dataset
        total (int): Total number of samples

    Returns:
        int or str: The processed prediction (0, 1, or 'invalid')
    """
    print(f"Prediction: {output} | Ground Truth: {ground_truth} ", end="")
    if output in ["0", "1"]:
        if str(output) == str(ground_truth):
            print("✅ (TP)" if output == "1" else "✅ (TN)")
        else:
            print("❌ (FP)" if output == "1" else "❌ (FN)")
        return int(output)
    else:
        print("🛠️ (Invalid Output Format)")
        return "invalid"

def log_prediction(log_data: dict, text: str, output: str, ground_truth: int):
    """Log the details of each prediction."""
    log_data["evaluations"].append({
        "text": text,
        "output": output,
        "ground_truth": ground_truth
    })

def compute_metrics(eval_data: pd.DataFrame, predictions: list):
    """
    Compute various performance metrics based on the predictions.

    This function calculates precision, recall, accuracy, and F1 score.
    It also identifies false positives and false negatives.

    Args:
        eval_data (pd.DataFrame): The evaluation dataset
        predictions (list): List of model predictions

    Returns:
        dict: A dictionary containing various performance metrics
    """
    invalid_predictions = predictions.count("invalid")
    print(f"\nNumber of invalid predictions: {invalid_predictions}")

    valid_predictions = [p for p in predictions if p != "invalid"]
    valid_ground_truth = eval_data['label'].iloc[:len(valid_predictions)].tolist()

    y_true = np.array(valid_ground_truth)
    y_pred = np.array(valid_predictions)
    
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    accuracy = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    false_positives = eval_data.iloc[:len(valid_predictions)][np.logical_and(y_true == 0, y_pred == 1)]
    false_negatives = eval_data.iloc[:len(valid_predictions)][np.logical_and(y_true == 1, y_pred == 0)]
    
    return {
        'precision': precision,
        'recall': recall,
        'accuracy': accuracy,
        'f1': f1,
        'predictions': y_pred.tolist(),
        'false_positives': false_positives.to_dict(orient='records'),
        'false_negatives': false_negatives.to_dict(orient='records'),
        'invalid_predictions': invalid_predictions
    }