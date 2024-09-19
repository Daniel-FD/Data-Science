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

def evaluate_prompt(prompt, eval_data, max_tokens=50, log_dir=None, iteration=None):
    """
    Evaluates the prompt on the evaluation dataset and computes metrics.

    Parameters:
    - prompt: str, the classification prompt
    - eval_data: DataFrame, contains 'text' and 'label' columns
    - max_tokens: int, maximum tokens for the model output
    - log_dir: str, directory for storing logs
    - iteration: int, current iteration number

    Returns:
    - A dictionary containing metrics and false positives/negatives
    """
    console = Console()
    wrapped_prompt = "\n".join(wrap(prompt, width=76))
    prompt_panel = Panel(
        wrapped_prompt,
        title="System Prompt",
        expand=False,
        border_style="bold",
        padding=(1, 1)
    )
    console.print(prompt_panel)

    log_file_path = os.path.join(log_dir, f"iteration_{iteration}_evaluation.json")
    log_data = {
        "prompt": prompt,
        "evaluations": []
    }

    predictions = []
    for index, row in eval_data.iterrows():
        text = row['text']
        ground_truth = row['label']
        
        input_prompt = f"{prompt}\n\nText:\n{text}\n\nAnswer (respond with '1' for Positive, '0' for Negative):"
        
        print(f"Processing text {index + 1}/{len(eval_data)}")
        
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                response = ollama.chat(model='llama3.1', messages=[
                    {
                        'role': 'user',
                        'content': input_prompt,
                    }
                ])
                output = response['message']['content'].strip()
                print(f"OUTPUT ({index + 1}/{len(eval_data)}): | Output: {output} | Ground Truth: {ground_truth} ", end="")
                if str(output) == str(ground_truth):
                    if output == '1':
                        print("✅ (TP)")
                    else:
                        print("✅ (TN)")
                else:
                    if output == '1':
                        print("❌ (FP)")
                    else:
                        print("❌ (FN)")
                
                log_data["evaluations"].append({
                    "text": text,
                    "output": output,
                    "ground_truth": ground_truth
                })
                break
            except Exception as e:
                retry_count += 1
                print(f"API error for text at index {index}: {e}. Retrying... (Attempt {retry_count}/{max_retries})")
                if retry_count == max_retries:
                    print(f"Max retries reached. Using default prediction.")
                    output = '0'  # Default prediction
                    log_data["evaluations"].append({
                        "text": text,
                        "error": str(e),
                        "default_prediction_used": True
                    })
        
        prediction = 1 if output == '1' else 0
        predictions.append(prediction)

    y_true = eval_data['label'].tolist()
    y_pred = predictions
    
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    accuracy = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    false_positives = eval_data[(eval_data['label'] == 0) & (np.array(y_pred) == 1)]
    false_negatives = eval_data[(eval_data['label'] == 1) & (np.array(y_pred) == 0)]
    
    log_data["metrics"] = {
        "precision": precision,
        "recall": recall,
        "accuracy": accuracy,
        "f1": f1
    }
    
    with open(log_file_path, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    return {
        'precision': precision,
        'recall': recall,
        'accuracy': accuracy,
        'f1': f1,
        'predictions': y_pred,
        'false_positives': false_positives.to_dict(orient='records'),
        'false_negatives': false_negatives.to_dict(orient='records')
    }

def generate_new_prompt(initial_prompt, false_positives, false_negatives, log_dir=None, iteration=None):
    """
    Generates a new prompt by incorporating false positives and false negatives.

    Parameters:
    - initial_prompt: str, the initial classification prompt
    - false_positives: list of dict, texts incorrectly classified as positive
    - false_negatives: list of dict, texts incorrectly classified as negative
    - log_dir: str, directory for storing logs
    - iteration: int, current iteration number

    Returns:
    - new_prompt: str, the updated prompt
    """
    
    print("\nAnalyzing misclassifications...")
    fp_texts = "\n".join(f"- {item['text']}" for item in false_positives)
    fn_texts = "\n".join(f"- {item['text']}" for item in false_negatives)

    analysis_prompt = f"""Analyze the following sets of texts that were misclassified by a sentiment analysis model:

    False Positives (incorrectly classified as positive):
    {fp_texts}

    False Negatives (incorrectly classified as negative):
    {fn_texts}

    Please provide insights on why these misclassifications might have occurred and suggest strategies to improve the classification prompt to prevent such errors in the future.
    """

    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            analysis_response = ollama.chat(model='llama3.1', messages=[
                {
                    'role': 'user',
                    'content': analysis_prompt,
                }
            ])
            analysis = analysis_response['message']['content'].strip()
            break
        except Exception as e:
            retry_count += 1
            print(f"API error during analysis: {e}. Retrying... (Attempt {retry_count}/{max_retries})")
            if retry_count == max_retries:
                print(f"Max retries reached. Using default analysis.")
                analysis = "Unable to generate analysis due to API errors."

    analysis_panel = Panel(
        analysis,
        title="Analysis of Misclassifications",
        expand=False,
        border_style="bold",
        padding=(1, 1)
    )
    Console().print(analysis_panel)

    output_format_prompt = "You are to act as a binary responder. For every question asked, reply strictly with '1' for positive or '0' for negative. Do NOT include any additional text or explanation."

    print("\nGenerating new prompt...")
    prompt_engineer_input = f"""You are an expert prompt engineer. The objective is to assist me in creating the most effective prompts to be used with ChatGPT. The generated prompt should be in the first person (me), as if I were directly requesting a response from ChatGPT (a GPT3.5/GPT4 interface).

                            Current prompt:
                            {initial_prompt}

                            Analysis of misclassifications:
                            {analysis}

                            Please rewrite the prompt to improve its performance, taking into account the provided analysis of misclassifications.
                            
                            # IMPORTANT: the prompt should not ask for the explanations to be as part of the output.
                            # IMPORTANT: provide the prompt as a final prompt - ready to ship to production - with no preamble or introduction (e.g. do NOT say "Here's the revised prompt:")
                            """

    prompt_engineer_panel = Panel(
        prompt_engineer_input,
        title="Prompt Engineer Input",
        expand=False,
        border_style="bold",
        padding=(1, 1)
    )
    Console().print(prompt_engineer_panel)

    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = ollama.chat(model='llama3.1', messages=[
                {
                    'role': 'user',
                    'content': prompt_engineer_input,
                }
            ])
            new_prompt = response['message']['content'].strip()
            break
        except Exception as e:
            retry_count += 1
            print(f"API error during prompt generation: {e}. Retrying... (Attempt {retry_count}/{max_retries})")
            if retry_count == max_retries:
                print(f"Max retries reached. Using default prompt.")
                new_prompt = initial_prompt

    new_prompt = new_prompt + output_format_prompt
    
    print("New prompt generated successfully!")

    log_file_path = os.path.join(log_dir, f"iteration_{iteration}_prompt_generation.json")
    log_data = {
        "initial_prompt": initial_prompt,
        "analysis": analysis,
        "new_prompt": new_prompt
    }
    with open(log_file_path, 'w') as f:
        json.dump(log_data, f, indent=2)

    return new_prompt

def optimize_prompt(initial_prompt, eval_data, iterations=5):
    """
    Optimizes the prompt to maximize evaluation metrics over a number of iterations.

    Parameters:
    - initial_prompt: str, the starting classification prompt
    - eval_data: DataFrame, contains 'text' and 'label' columns
    - iterations: int, number of optimization iterations

    Returns:
    - None (prints out the best prompt and metrics)
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
    with open(os.path.join(log_dir, "initial_setup.json"), 'w') as f:
        json.dump({
            "initial_prompt": initial_prompt,
            "iterations": iterations,
            "eval_data_shape": eval_data.shape
        }, f, indent=2)

    for i in range(iterations):
        console.print(f"\n[bold]Iteration {i+1}/{iterations}[/bold]")
        
        results = evaluate_prompt(current_prompt, eval_data, log_dir=log_dir, iteration=i+1)
        
        metrics_table = Table(title=f"Evaluation Metrics - Iteration {i+1}", show_header=True)
        metrics_table.add_column("Metric", no_wrap=True)
        metrics_table.add_column("Value", justify="right")
        
        metrics_table.add_row("Precision", f"{results['precision']:.4f}")
        metrics_table.add_row("Recall", f"{results['recall']:.4f}")
        metrics_table.add_row("Accuracy", f"{results['accuracy']:.4f}")
        metrics_table.add_row("F1-score", f"{results['f1']:.4f}")
        
        console.print(metrics_table)
        
        all_metrics.append({
            'iteration': i+1,
            'precision': results['precision'],
            'recall': results['recall'],
            'accuracy': results['accuracy'],
            'f1': results['f1']
        })
        
        if best_metrics is None or results['f1'] > best_metrics['f1']:
            best_metrics = results
            best_prompt = current_prompt
        
        if i < iterations - 1:  # Don't generate a new prompt on the last iteration
            current_prompt = generate_new_prompt(
                current_prompt,
                results['false_positives'],
                results['false_negatives'],
                log_dir=log_dir,
                iteration=i+1
            )
    
    console.print("\n[bold]Best prompt based on F1-score:[/bold]")
    console.print(Panel(best_prompt, expand=False))

    comparison_table = Table(title="Comparison of All Iterations", show_header=True)
    comparison_table.add_column("Iteration", justify="center")
    comparison_table.add_column("Precision", justify="right")
    comparison_table.add_column("Recall", justify="right")
    comparison_table.add_column("Accuracy", justify="right")
    comparison_table.add_column("F1-score", justify="right")

    max_precision = max(m['precision'] for m in all_metrics)
    max_recall = max(m['recall'] for m in all_metrics)
    max_accuracy = max(m['accuracy'] for m in all_metrics)
    max_f1 = max(m['f1'] for m in all_metrics)

    for metrics in all_metrics:
        comparison_table.add_row(
            str(metrics['iteration']),
            f"[bold]{metrics['precision']:.4f}[/bold]" if metrics['precision'] == max_precision else f"{metrics['precision']:.4f}",
            f"[bold]{metrics['recall']:.4f}[/bold]" if metrics['recall'] == max_recall else f"{metrics['recall']:.4f}",
            f"[bold]{metrics['accuracy']:.4f}[/bold]" if metrics['accuracy'] == max_accuracy else f"{metrics['accuracy']:.4f}",
            f"[bold]{metrics['f1']:.4f}[/bold]" if metrics['f1'] == max_f1 else f"{metrics['f1']:.4f}"
        )

    console.print(comparison_table)

    # Log final results
    with open(os.path.join(log_dir, "final_results.json"), 'w') as f:
        json.dump({
            "best_prompt": best_prompt,
            "best_metrics": {k: v for k, v in best_metrics.items() if k not in ['false_positives', 'false_negatives', 'predictions']},
            "all_metrics": all_metrics
        }, f, indent=2)

    print(f"\nAll logs saved in directory: {log_dir}")

if __name__ == "__main__":
    # Load the evaluation dataset
    df = pd.read_csv('sentiment_dataset.csv')

    # Preprocess the dataset
    eval_data = df[['tweet', 'label']]
    eval_data = eval_data.rename(columns={'tweet': 'text'})

    # Optionally, sample a subset for faster testing
    # eval_data = eval_data.sample(n=500, random_state=42).reset_index(drop=True)

    # Initial prompt for classification
    initial_prompt = (
        "You are a sentiment analysis classifier. Determine whether the provided text expresses a positive sentiment. "
        "Respond with '1' if it is positive, or '0' if it is negative."
    )

    # Number of optimization iterations
    iterations = 5  # You can adjust this value

    # Start the prompt optimization process
    optimize_prompt(initial_prompt, eval_data, iterations)