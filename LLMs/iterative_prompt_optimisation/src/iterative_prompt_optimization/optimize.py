from .evaluation import evaluate_prompt
from .prompt_generation import generate_new_prompt
from .utils import (estimate_token_usage, estimate_cost, display_best_prompt,
                    display_comparison_table, log_final_results, select_model,
                    create_log_directory, log_initial_setup, display_metrics,
                    create_metric_entry, update_best_metrics)
from . import config

def optimize_prompt(initial_prompt: str, output_format_prompt: str, eval_data, iterations: int = 5, 
                    model_provider: str = None, model_name: str = None):
    """
    Optimize a prompt through iterative refinement and evaluation.

    This function performs the following steps:
    1. Select and configure the language model
    2. Estimate token usage and cost
    3. Iteratively evaluate and improve the prompt
    4. Log results and display the best prompt

    Args:
        initial_prompt (str): The starting prompt to be optimized
        output_format_prompt (str): Instructions for the desired output format
        eval_data: Dataset used for evaluating prompt performance
        iterations (int): Number of optimization iterations to perform
        model_provider (str, optional): The AI model provider (e.g., "openai", "anthropic")
        model_name (str, optional): The specific model to use

    Returns:
        tuple: The best performing prompt and its associated metrics

    Note:
        If model_provider or model_name is not provided, the function will prompt the user to select them.
    """
    # Select model if not provided
    if model_provider is None or model_name is None:
        SELECTED_PROVIDER, MODEL_NAME = select_model()
    else:
        SELECTED_PROVIDER, MODEL_NAME = model_provider, model_name
    
    # Set the selected model in the config
    config.set_model(SELECTED_PROVIDER, MODEL_NAME)
    print(f"Selected provider: {SELECTED_PROVIDER}")
    print(f"Selected model: {MODEL_NAME}")

    # Estimate token usage and cost
    total_tokens = estimate_token_usage(initial_prompt, output_format_prompt, eval_data, iterations)
    estimated_cost = estimate_cost(total_tokens, SELECTED_PROVIDER, MODEL_NAME)
    
    print(f"Estimated token usage: {total_tokens}")
    print(f"Estimated cost: {estimated_cost}")
    
    # Confirm with the user before proceeding
    print("\nDo you want to proceed with the optimization? (Y/N): ", end="", flush=True)
    proceed = input().strip().lower()
    if proceed != 'y':
        print("Optimization cancelled.")
        return

    best_metrics = None
    best_prompt = initial_prompt
    current_prompt = initial_prompt
    all_metrics = []

    # Create a directory for logging
    log_dir = create_log_directory()

    # Log initial setup
    log_initial_setup(log_dir, initial_prompt, output_format_prompt, iterations, eval_data)
    
    # Main optimization loop
    for i in range(iterations):
        print(f"\nIteration {i+1}/{iterations}")
        
        # Evaluate the current prompt
        results = evaluate_prompt(current_prompt, output_format_prompt, eval_data, log_dir=log_dir, iteration=i+1)
        
        # Display and log the results
        display_metrics(results, i+1)
        all_metrics.append(create_metric_entry(i+1, results))
        
        # Update the best prompt if necessary
        best_metrics, best_prompt = update_best_metrics(best_metrics, best_prompt, results, current_prompt)
        
        # Generate a new prompt for the next iteration, except for the last one
        if i < iterations - 1:
            current_prompt = generate_new_prompt(
                current_prompt,
                output_format_prompt,
                results['false_positives'],
                results['false_negatives'],
                log_dir=log_dir,
                iteration=i+1
            )
    
    # Display and log final results
    display_best_prompt(best_prompt, output_format_prompt)
    display_comparison_table(all_metrics)
    log_final_results(log_dir, best_prompt, output_format_prompt, best_metrics, all_metrics)

    return best_prompt, best_metrics

# Note: Any global calls to select_model() or other functions that might run on import have been removed
# to prevent unexpected behavior when importing this module.