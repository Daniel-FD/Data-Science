import pandas as pd
import numpy as np
import networkx as nx
from scipy.stats import entropy
from typing import Dict, List, Union, Tuple
from tqdm import tqdm


def extract_features(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract comprehensive features from transaction data using efficient pandas operations.
    
    Args:
        raw_df: DataFrame with columns ['sender', 'recipient', 'amount', 'token', 'height', 'tx_hash']
        
    Returns:
        DataFrame with extracted features for each address, indexed by 'address'
        
    Feature Categories:
    - Transaction counts (tx_count_*)
    - Transaction volumes (volume_*)
    - Transaction values (value_*)
    - Temporal patterns (time_*)
    - Counterparty metrics (counter_*)
    - Token diversity metrics (token_*)
    - Network centrality metrics (network_*)
    """
    
    print("Starting feature extraction process...")
    df = raw_df.copy()
    
    # Convert numeric columns efficiently
    df[['amount', 'height']] = df[['amount', 'height']].apply(pd.to_numeric)
    
    #==========================================================================
    # STEP 1: AGGREGATE BASIC METRICS USING GROUPBY
    #==========================================================================
    print("Computing sender metrics...")
    sender_metrics = df.groupby('sender').agg(
        # Transaction counts
        tx_count_out=('tx_hash', 'count'),
        
        # Transaction volumes
        volume_out=('amount', 'sum'),
        
        # Transaction values
        value_max_out=('amount', 'max'),
        value_min_out=('amount', 'min'),
        value_avg_out=('amount', 'mean'),
        value_median_out=('amount', lambda x: x.quantile(0.5)),  # Median (p50)
        value_p25_out=('amount', lambda x: x.quantile(0.25)),    # 25th percentile
        value_p75_out=('amount', lambda x: x.quantile(0.75)),    # 75th percentile  
        value_p90_out=('amount', lambda x: x.quantile(0.9)),     # 90th percentile
        value_std_out=('amount', 'std'),                         # Standard deviation
        
        # Time-based metrics
        time_first_height_out=('height', 'min'),
        time_last_height_out=('height', 'max'),
        time_height_range_out=('height', lambda x: x.max() - x.min()),  # Range of blocks
        
        # Additional metrics
        token_unique_out=('token', 'nunique'),                   # Unique tokens sent
        counter_unique_recipients=('recipient', 'nunique'),      # Unique recipients
        tx_hash_unique_out=('tx_hash', 'nunique'),               # Unique transaction hashes
        block_unique_out=('height', 'nunique'),                  # Number of unique blocks
    )
    
    print("Computing recipient metrics...")
    recipient_metrics = df.groupby('recipient').agg(
        # Transaction counts
        tx_count_in=('tx_hash', 'count'),
        
        # Transaction volumes
        volume_in=('amount', 'sum'),
        
        # Transaction values
        value_max_in=('amount', 'max'),
        value_min_in=('amount', 'min'),
        value_avg_in=('amount', 'mean'),
        value_median_in=('amount', lambda x: x.quantile(0.5)),   # Median (p50)
        value_p25_in=('amount', lambda x: x.quantile(0.25)),     # 25th percentile
        value_p75_in=('amount', lambda x: x.quantile(0.75)),     # 75th percentile
        value_p90_in=('amount', lambda x: x.quantile(0.9)),      # 90th percentile
        value_std_in=('amount', 'std'),                          # Standard deviation
        
        # Time-based metrics
        time_first_height_in=('height', 'min'),
        time_last_height_in=('height', 'max'),
        time_height_range_in=('height', lambda x: x.max() - x.min()),  # Range of blocks
        
        # Additional metrics
        token_unique_in=('token', 'nunique'),                    # Unique tokens received
        counter_unique_senders=('sender', 'nunique'),            # Unique senders
        tx_hash_unique_in=('tx_hash', 'nunique'),                # Unique transaction hashes
        block_unique_in=('height', 'nunique'),                   # Number of unique blocks
    )
    
    #==========================================================================
    # STEP 2: MERGE SENDER AND RECIPIENT METRICS
    #==========================================================================
    print("Merging sender and recipient metrics...")
    all_addresses = pd.Index(df['sender']).union(df['recipient']).unique()
    features_df = pd.DataFrame(index=all_addresses)
    
    # Merge metrics using index joins
    features_df = features_df.join(sender_metrics, how='left').fillna(0)
    features_df = features_df.join(recipient_metrics, how='left').fillna(0)
    
    # Set address as index early to avoid column reference issues
    features_df = features_df.rename_axis('address').reset_index().set_index('address')

    #==========================================================================
    # STEP 3: CALCULATE DERIVED METRICS
    #==========================================================================
    print("Computing derived metrics...")
    
    # Transaction counts and volumes
    features_df['tx_count_total'] = features_df['tx_count_out'] + features_df['tx_count_in']
    features_df['volume_total'] = features_df['volume_out'] + features_df['volume_in']
    features_df['volume_net'] = features_df['volume_in'] - features_df['volume_out']
    
    # Simplified value_min calculation (0 values handled in data preprocessing)
    features_df['value_min'] = features_df[['value_min_out', 'value_min_in']].min(axis=1)
    
    # Transaction value metrics
    features_df['value_max'] = features_df[['value_max_out', 'value_max_in']].max(axis=1)
    
    # Time-based metrics (using block heights)
    features_df['time_first_height'] = features_df[['time_first_height_out', 'time_first_height_in']].min(axis=1)
    features_df['time_last_height'] = features_df[['time_last_height_out', 'time_last_height_in']].max(axis=1)
    features_df['time_duration_blocks'] = features_df['time_last_height'] - features_df['time_first_height']
        
    #==========================================================================
    # STEP 4: BUILD TRANSACTION NETWORK GRAPH
    #==========================================================================
    print("Building transaction network graph...")
    G = nx.DiGraph()
    G.add_edges_from(df[['sender', 'recipient']].values)
    
    #==========================================================================
    # STEP 5: PRE-COMPUTE NETWORK CENTRALITY METRICS
    #==========================================================================
    print("Computing network centrality metrics...")
    
    # Use index for mapping since address is now our index
    features_df['network_degree'] = features_df.index.map(nx.degree_centrality(G)).fillna(0)
    features_df['network_in_degree'] = features_df.index.map(nx.in_degree_centrality(G)).fillna(0)
    features_df['network_out_degree'] = features_df.index.map(nx.out_degree_centrality(G)).fillna(0)
    
    #==========================================================================
    # STEP 6: ADDITIONAL FEATURES
    #==========================================================================
    """
    Additional features that can be implemented:
    
    1. TIMING PATTERN METRICS (Partially Implemented)
       
       🚧 Planned:
       - time_burstiness: Measure of transaction timing irregularity
       - time_entropy: Entropy of transaction timing
       - time_periodicity: Fourier analysis of periodic patterns
       - time_clustering: Transaction time clustering measure
       - hourly_activity_patterns: Time-of-day transaction preferences
    
    2. VALUE METRICS (Partially Implemented)
       
       🚧 Planned:
       - value_avg_out/in: Average transaction value
       - value_volatility: Std dev of transaction values  
       - value_gini_out/in: Gini coefficient of values
       - value_round_amounts_ratio: Round-number transactions ratio
    
    3. TOKEN METRICS (Not Implemented)
       🚧 Planned:
       - token_diversity: Count of distinct tokens interacted with
       - token_dominance_out: Most common outgoing token proportion
       - token_dominance_in: Most common incoming token proportion
       - token_sol_percentage: "SOL" transactions percentage
       - token_switching_frequency: Frequency of token changes
       - token_holding_duration: Avg holding time before sending
    
    4. NETWORK METRICS (Partially Implemented)
       🚧 Planned:
       - network_betweenness: Betweenness centrality
       - network_closeness: Closeness centrality
       - network_pagerank: PageRank score
       - network_eigenvector: Eigenvector centrality
       - network_clustering: Local clustering coefficient
    
    5. COUNTERPARTY METRICS (Not Implemented)
       🚧 Planned:
       - counter_unique_total: Unique senders + recipients
       - counter_same_block_txs: Same-block transactions count
       - counter_avg_recipients_per_tx: Avg recipients per transaction
       - counter_bulk_tx_count: Bulk transaction operations
    
    6. TEMPORAL METRICS (Not Implemented)
       🚧 Planned:
       - activity_acceleration: Transaction frequency change rate
       - inactive_period: Longest no-activity duration
       - recent_tx_count: Last block period activity
       - tx_time_entropy: Randomness in transaction timing

    7. ADVANCED EMBEDDING FEATURES (Not Implemented)
       🚧 Planned:
       - node2vec_embeddings: Graph structure embeddings using Node2Vec
       - autoencoder_features: Compressed representations from feature autoencoder
       - sequence_embeddings: LSTM/Transformer-based temporal pattern embeddings
       - contrastive_embeddings: Self-supervised similarity-based embeddings
    """
    #==========================================================================
    # STEP 7: FINALIZE FEATURE DATAFRAME
    #==========================================================================
    print("Finalizing feature extraction...")
    print(f"Extracted features for {len(features_df)} addresses")
    return features_df 