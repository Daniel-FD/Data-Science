import pandas as pd
import numpy as np
import requests
import ollama
import json
import os
from datetime import datetime
from textwrap import wrap
from rich.console import Console
from rich.panel import Panel
from rich.table import Table 
from sklearn.metrics import precision_score, recall_score, accuracy_score, f1_score
from typing import Dict, List, Any, Tuple

# Constants
MAX_RETRIES = 3
MODEL_NAME = 'llama3.1'

def evaluate_prompt(prompt: str, output_format_prompt: str, eval_data: pd.DataFrame, max_tokens: int = 50, log_dir: str = None, iteration: int = None) -> Dict[str, Any]:
    """
    Evaluates the prompt on the evaluation dataset and computes metrics.

    Args:
        prompt (str): The classification prompt
        output_format_prompt (str): The output format instructions
        eval_data (pd.DataFrame): Contains 'text' and 'label' columns
        max_tokens (int): Maximum tokens for the model output
        log_dir (str): Directory for storing logs
        iteration (int): Current iteration number

    Returns:
        Dict[str, Any]: A dictionary containing metrics and false positives/negatives
    """
    console = Console()
    full_prompt = create_full_prompt(prompt, output_format_prompt)
    display_prompt(console, full_prompt)

    log_file_path = create_log_file_path(log_dir, iteration)
    log_data = initialize_log_data(full_prompt)

    predictions = process_eval_data(eval_data, full_prompt, log_data)
    
    metrics = compute_metrics(eval_data, predictions)
    
    log_results(log_file_path, log_data, metrics)
    
    return metrics

def create_full_prompt(prompt: str, output_format_prompt: str) -> str:
    """Combines the main prompt with the output format prompt."""
    return f"{prompt}\n\n{output_format_prompt}"

def display_prompt(console: Console, full_prompt: str) -> None:
    """Displays the full prompt in a formatted panel."""
    wrapped_prompt = "\n".join(wrap(full_prompt, width=76))
    prompt_panel = Panel(
        wrapped_prompt,
        title="System Prompt",
        expand=False,
        border_style="yellow",
        padding=(1, 1)
    )
    console.print(prompt_panel)

def create_log_file_path(log_dir: str, iteration: int) -> str:
    """Creates the log file path for the current iteration."""
    return os.path.join(log_dir, f"iteration_{iteration}_evaluation.json")

def initialize_log_data(full_prompt: str) -> Dict[str, Any]:
    """Initializes the log data structure."""
    return {
        "prompt": full_prompt,
        "evaluations": []
    }

def process_eval_data(eval_data: pd.DataFrame, full_prompt: str, log_data: Dict[str, Any]) -> List[Any]:
    """Processes the evaluation data and returns predictions."""
    predictions = []
    total = len(eval_data)
    for index, row in eval_data.iterrows():
        output = get_model_output(full_prompt, row['text'], index, total)
        prediction = process_output(output, row['label'], index, total)
        log_prediction(log_data, row['text'], output, row['label'])
        predictions.append(prediction)
    return predictions

def get_model_output(full_prompt: str, text: str, index: int, total: int) -> str:
    """Gets the model output for a given input text."""
    print(f"Processing text {index + 1}/{total}")
    for retry in range(MAX_RETRIES):
        try:
            response = ollama.chat(model=MODEL_NAME, messages=[
                {'role': 'system', 'content': full_prompt},
                {'role': 'user', 'content': text},
            ])
            return response['message']['content'].strip()
        except Exception as e:
            print(f"API error for text at index {index}: {e}. Retrying... (Attempt {retry + 1}/{MAX_RETRIES})")
    print(f"Max retries reached. Using default prediction.")
    return '0'  # Default prediction

def process_output(output: str, ground_truth: int, index: int, total: int) -> Any:
    """Processes the model output and compares it with the ground truth."""
    print(f"Prediction: {output} | Ground Truth: {ground_truth} ", end="")
    if output in ["0", "1"]:
        if str(output) == str(ground_truth):
            if output == "1":
                print("✅ (TP)")
            else:
                print("✅ (TN)")
        else:
            if output == "1":
                print("❌ (FP)")
            else:
                print("❌ (FN)")
        return int(output)
    else:
        print("🛠️ (Invalid Output Format)")
        return "invalid"

def log_prediction(log_data: Dict[str, Any], text: str, output: str, ground_truth: int) -> None:
    """Logs the prediction details."""
    log_data["evaluations"].append({
        "text": text,
        "output": output,
        "ground_truth": ground_truth
    })

def compute_metrics(eval_data: pd.DataFrame, predictions: List[Any]) -> Dict[str, Any]:
    """Computes various metrics based on the predictions."""
    invalid_predictions = predictions.count("invalid")
    print(f"\nNumber of invalid predictions: {invalid_predictions}")

    valid_predictions = [p for p in predictions if p != "invalid"]
    valid_ground_truth = eval_data['label'].iloc[:len(valid_predictions)].tolist()

    y_true = valid_ground_truth
    y_pred = valid_predictions
    
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    accuracy = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    false_positives = eval_data.iloc[:len(valid_predictions)][(np.array(y_true) == 0) & (np.array(y_pred) == 1)]
    false_negatives = eval_data.iloc[:len(valid_predictions)][(np.array(y_true) == 1) & (np.array(y_pred) == 0)]
    
    return {
        'precision': precision,
        'recall': recall,
        'accuracy': accuracy,
        'f1': f1,
        'predictions': y_pred,
        'false_positives': false_positives.to_dict(orient='records'),
        'false_negatives': false_negatives.to_dict(orient='records'),
        'invalid_predictions': invalid_predictions
    }

def log_results(log_file_path: str, log_data: Dict[str, Any], metrics: Dict[str, Any]) -> None:
    """Logs the evaluation results to a file."""
    log_data["metrics"] = {
        "precision": metrics['precision'],
        "recall": metrics['recall'],
        "accuracy": metrics['accuracy'],
        "f1": metrics['f1'],
        "invalid_predictions": metrics['invalid_predictions']
    }
    
    with open(log_file_path, 'w') as f:
        json.dump(log_data, f, indent=2)

def generate_new_prompt(initial_prompt: str, output_format_prompt: str, false_positives: List[Dict[str, Any]], false_negatives: List[Dict[str, Any]], log_dir: str = None, iteration: int = None) -> str:
    """
    Generates a new prompt by incorporating false positives and false negatives.

    Args:
        initial_prompt (str): The initial classification prompt
        output_format_prompt (str): The output format instructions
        false_positives (List[Dict[str, Any]]): Texts incorrectly classified as positive
        false_negatives (List[Dict[str, Any]]): Texts incorrectly classified as negative
        log_dir (str): Directory for storing logs
        iteration (int): Current iteration number

    Returns:
        str: The updated prompt
    """
    
    print("\nAnalyzing misclassifications...")
    fp_texts = "\n".join(f"- {item['text']}" for item in false_positives)
    fn_texts = "\n".join(f"- {item['text']}" for item in false_negatives)

    analysis_prompt = f"""
    You are an expert in refining LLMs prompts for binary classifications. Below are two sets of texts that were misclassified by the LLM model:

        Negative (0) texts (incorrectly classified as positive):
        {fp_texts}

        Positives (0) texts (incorrectly classified as negative):
        {fn_texts}

    Your task is to analyze these misclassifications and provide insights into why these errors occurred. Identify specific examples from each set where the model made a mistake and highlight what elements of the text may have led to the incorrect classification. Additionally, specify what the correct classification should have been for each example.

    Based on your analysis, suggest strategies to improve the classification prompt, focusing on how it can better recognize the nuances that led to the errors. Your recommendations should include ways to reduce both false positives and false negatives by making the prompt more sensitive to subtle differences in the classification of text.
    """

    analysis = get_analysis(analysis_prompt)
    display_analysis(analysis)

    new_prompt = generate_improved_prompt(initial_prompt, analysis)
    log_prompt_generation(log_dir, iteration, initial_prompt, analysis, new_prompt)

    return new_prompt

def get_analysis(analysis_prompt: str) -> str:
    """Gets the analysis of misclassifications from the model."""
    for retry in range(MAX_RETRIES):
        try:
            analysis_response = ollama.chat(model=MODEL_NAME, messages=[
                {
                    'role': 'user',
                    'content': analysis_prompt,
                }
            ])
            return analysis_response['message']['content'].strip()
        except Exception as e:
            print(f"API error during analysis: {e}. Retrying... (Attempt {retry + 1}/{MAX_RETRIES})")
    print(f"Max retries reached. Using default analysis.")
    return "Unable to generate analysis due to API errors."

def display_analysis(analysis: str) -> None:
    """Displays the analysis in a formatted panel."""
    analysis_panel = Panel(
        analysis,
        title="Analysis of Misclassifications",
        expand=False,
        border_style="bold",
        padding=(1, 1)
    )
    Console().print(analysis_panel)

def generate_improved_prompt(initial_prompt: str, analysis: str) -> str:
    """Generates an improved prompt based on the analysis."""
    print("\nGenerating new prompt...")
    prompt_engineer_input = f"""
        You are an expert in crafting highly effective prompts. Your task is to help me improve a prompt for binary classification. I will give you the current prompt and an analysis showing where it failed to classify a piece of text correctly. Your goal is to refine the prompt to be more precise and adaptable, ensuring that the AI can accurately classify similar texts going forward. The revised prompt should be written in the first person, guiding the AI to handle difficult or edge cases.

        Current prompt:
        {initial_prompt}

        Analysis of misclassifications:
        {analysis}

        Your task is to provide a rewritten, production-ready version of the prompt that improves its accuracy. 
        
        IMPORTANT note: the prompt should not include any preamble or request for explanations, just the final prompt itself.
        """

    prompt_engineer_panel = Panel(
        prompt_engineer_input,
        title="Prompt Engineer Input",
        expand=False,
        border_style="bold",
        padding=(1, 1)
    )
    Console().print(prompt_engineer_panel)

    for retry in range(MAX_RETRIES):
        try:
            response = ollama.chat(model=MODEL_NAME, messages=[
                {
                    'role': 'user',
                    'content': prompt_engineer_input,
                }
            ])
            return response['message']['content'].strip()
        except Exception as e:
            print(f"API error during prompt generation: {e}. Retrying... (Attempt {retry + 1}/{MAX_RETRIES})")
    print(f"Max retries reached. Using default prompt.")
    return initial_prompt

def log_prompt_generation(log_dir: str, iteration: int, initial_prompt: str, analysis: str, new_prompt: str) -> None:
    """Logs the prompt generation process."""
    log_file_path = os.path.join(log_dir, f"iteration_{iteration}_prompt_generation.json")
    log_data = {
        "initial_prompt": initial_prompt,
        "analysis": analysis,
        "new_prompt": new_prompt
    }
    with open(log_file_path, 'w') as f:
        json.dump(log_data, f, indent=2)

def optimize_prompt(initial_prompt: str, output_format_prompt: str, eval_data: pd.DataFrame, iterations: int = 5) -> None:
    """
    Optimizes the prompt to maximize evaluation metrics over a number of iterations.

    Args:
        initial_prompt (str): The starting classification prompt
        output_format_prompt (str): The output format instructions
        eval_data (pd.DataFrame): Contains 'text' and 'label' columns
        iterations (int): Number of optimization iterations

    Returns:
        None (prints out the best prompt and metrics)
    """
    best_metrics = None
    best_prompt = initial_prompt
    current_prompt = initial_prompt
    all_metrics = []

    console = Console()

    # Create a directory for logging if it doesn't exist
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = f"prompt_optimization_logs_{timestamp}"
    os.makedirs(log_dir, exist_ok=True)

    # Log initial setup
    log_initial_setup(log_dir, initial_prompt, output_format_prompt, iterations, eval_data)
    
    for i in range(iterations):
        console.print(f"\n[bold]Iteration {i+1}/{iterations}[/bold]")
        
        results = evaluate_prompt(current_prompt, output_format_prompt, eval_data, log_dir=log_dir, iteration=i+1)
        
        display_metrics(console, results, i+1)
        
        all_metrics.append(create_metric_entry(i+1, results))
        
        best_metrics, best_prompt = update_best_metrics(best_metrics, best_prompt, results, current_prompt)
        
        if i < iterations - 1:  # Don't generate a new prompt on the last iteration
            current_prompt = generate_new_prompt(
                current_prompt,
                output_format_prompt,
                results['false_positives'],
                results['false_negatives'],
                log_dir=log_dir,
                iteration=i+1
            )
    
    display_best_prompt(console, best_prompt, output_format_prompt)
    display_comparison_table(console, all_metrics)
    log_final_results(log_dir, best_prompt, output_format_prompt, best_metrics, all_metrics)

def log_initial_setup(log_dir: str, initial_prompt: str, output_format_prompt: str, iterations: int, eval_data: pd.DataFrame) -> None:
    """Logs the initial setup of the optimization process."""
    with open(os.path.join(log_dir, "initial_setup.json"), 'w') as f:
        json.dump({
            "initial_prompt": initial_prompt,
            "output_format_prompt": output_format_prompt,
            "iterations": iterations,
            "eval_data_shape": eval_data.shape
        }, f, indent=2)

def display_metrics(console: Console, results: Dict[str, Any], iteration: int) -> None:
    """Displays the metrics for the current iteration."""
    metrics_table = Table(title=f"Evaluation Metrics - Iteration {iteration}", show_header=True)
    metrics_table.add_column("Metric", no_wrap=True)
    metrics_table.add_column("Value", justify="right")
    
    metrics_table.add_row("Precision", f"{results['precision']:.4f}")
    metrics_table.add_row("Recall", f"{results['recall']:.4f}")
    metrics_table.add_row("Accuracy", f"{results['accuracy']:.4f}")
    metrics_table.add_row("F1-score", f"{results['f1']:.4f}")
    metrics_table.add_row("Invalid Predictions", str(results['invalid_predictions']))
    
    console.print(metrics_table)

def create_metric_entry(iteration: int, results: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a metric entry for the current iteration."""
    return {
        'iteration': iteration,
        'precision': results['precision'],
        'recall': results['recall'],
        'accuracy': results['accuracy'],
        'f1': results['f1'],
        'invalid_predictions': results['invalid_predictions']
    }

def update_best_metrics(best_metrics: Dict[str, Any], best_prompt: str, results: Dict[str, Any], current_prompt: str) -> Tuple[Dict[str, Any], str]:
    """Updates the best metrics and prompt if the current results are better."""
    if best_metrics is None or results['f1'] > best_metrics['f1']:
        return results, current_prompt
    return best_metrics, best_prompt

def display_best_prompt(console: Console, best_prompt: str, output_format_prompt: str) -> None:
    """Displays the best prompt based on F1-score."""
    console.print("\n[bold]Best prompt based on F1-score:[/bold]")
    console.print(Panel(best_prompt + "\n\n" + output_format_prompt, expand=False))

def display_comparison_table(console: Console, all_metrics: List[Dict[str, Any]]) -> None:
    """Displays a comparison table of all iterations."""
    comparison_table = Table(title="Comparison of All Iterations", show_header=True)
    comparison_table.add_column("Iteration", justify="center")
    comparison_table.add_column("Precision", justify="right")
    comparison_table.add_column("Recall", justify="right")
    comparison_table.add_column("Accuracy", justify="right")
    comparison_table.add_column("F1-score", justify="right")
    comparison_table.add_column("Invalid Predictions", justify="right")

    max_values = get_max_values(all_metrics)

    for metrics in all_metrics:
        comparison_table.add_row(
            str(metrics['iteration']),
            format_metric(metrics['precision'], max_values['precision']),
            format_metric(metrics['recall'], max_values['recall']),
            format_metric(metrics['accuracy'], max_values['accuracy']),
            format_metric(metrics['f1'], max_values['f1']),
            format_metric(metrics['invalid_predictions'], max_values['invalid_predictions'], is_min=True)
        )

    console.print(comparison_table)

def get_max_values(all_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Gets the maximum values for each metric across all iterations."""
    return {
        'precision': max(m['precision'] for m in all_metrics),
        'recall': max(m['recall'] for m in all_metrics),
        'accuracy': max(m['accuracy'] for m in all_metrics),
        'f1': max(m['f1'] for m in all_metrics),
        'invalid_predictions': min(m['invalid_predictions'] for m in all_metrics)
    }

def format_metric(value: float, max_value: float, is_min: bool = False) -> str:
    """Formats a metric value, highlighting it if it's the maximum (or minimum for invalid predictions)."""
    if (not is_min and value == max_value) or (is_min and value == max_value):
        return f"[bold]{value:.4f}[/bold]"
    return f"{value:.4f}"

def log_final_results(log_dir: str, best_prompt: str, output_format_prompt: str, best_metrics: Dict[str, Any], all_metrics: List[Dict[str, Any]]) -> None:
    """Logs the final results of the optimization process."""
    with open(os.path.join(log_dir, "final_results.json"), 'w') as f:
        json.dump({
            "best_prompt": best_prompt + "\n\n" + output_format_prompt,
            "best_metrics": {k: v for k, v in best_metrics.items() if k not in ['false_positives', 'false_negatives', 'predictions']},
            "all_metrics": all_metrics
        }, f, indent=2)

    print(f"\nAll logs saved in directory: {log_dir}")

if __name__ == "__main__":
    # Load and preprocess the evaluation dataset
    df = pd.read_csv('sentiment_dataset.csv')
    eval_data = df[['tweet', 'label']].rename(columns={'tweet': 'text'})

    # Optionally, sample a subset for faster testing
    # eval_data = eval_data.sample(n=500, random_state=42).reset_index(drop=True)

    # Initial prompt for classification
    initial_prompt = (
        "You are a sentiment analysis classifier. Determine whether the provided text expresses a positive sentiment. "
        "Respond with '1' if it is positive, or '0' if it is negative."
    )

    # Output format prompt
    output_format_prompt = (
        "You are to act as a binary responder. For every question asked, reply strictly with '1' for positive or '0' for negative. "
        "Do NOT include any additional text or explanation."
    )

    # Number of optimization iterations
    iterations = 5  # You can adjust this value

    # Start the prompt optimization process
    optimize_prompt(initial_prompt, output_format_prompt, eval_data, iterations)