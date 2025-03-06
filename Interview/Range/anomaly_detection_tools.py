# Import libraries and set up environment
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import time
import datetime
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
import networkx as nx
import warnings



def analyze_address(df, address, plot=False):
    """Analyze transactions for a specific address with robust column checking"""
    # Get transactions for this address
    sent_txs = df[df['sender'] == address]
    received_txs = df[df['recipient'] == address]
    
    analysis_result = {
        'address': address,
        'total_tx': len(sent_txs) + len(received_txs),
        'sent_tx': len(sent_txs),
        'received_tx': len(received_txs),
        'total_volume': sent_txs['amount'].sum() + received_txs['amount'].sum() if 'amount' in df.columns else 0,
        'sent_volume': sent_txs['amount'].sum() if 'amount' in df.columns else 0,
        'received_volume': received_txs['amount'].sum() if 'amount' in df.columns else 0
    }
    
    # Calculate unique counterparties if recipient/sender columns exist
    if 'recipient' in df.columns and 'sender' in df.columns:
        unique_recipients = sent_txs['recipient'].nunique() if len(sent_txs) > 0 else 0
        unique_senders = received_txs['sender'].nunique() if len(received_txs) > 0 else 0
        
        # Corrected calculation for unique_counterparties
        sent_recipients = set(sent_txs['recipient']) if len(sent_txs) > 0 else set()
        received_senders = set(received_txs['sender']) if len(received_txs) > 0 else set()
        unique_counterparties = len(sent_recipients.union(received_senders))
        
        analysis_result.update({
            'unique_counterparties': unique_counterparties,
            'unique_sent_to': unique_recipients,
            'unique_received_from': unique_senders
        })
    
    print(f"Analysis for address: {address}")
    print(f"Total transactions: {analysis_result['total_tx']}")
    print(f"- Sent: {analysis_result['sent_tx']} transactions")
    print(f"- Received: {analysis_result['received_tx']} transactions")
    
    if 'amount' in df.columns:
        print(f"\nTotal volume: {analysis_result['total_volume']:.2f}")
        print(f"- Sent: {analysis_result['sent_volume']:.2f}")
        print(f"- Received: {analysis_result['received_volume']:.2f}")
    
    if 'unique_counterparties' in analysis_result:
        print(f"\nUnique counterparties: {analysis_result['unique_counterparties']}")
        print(f"- Sent to {analysis_result['unique_sent_to']} unique addresses")
        print(f"- Received from {analysis_result['unique_received_from']} unique addresses")
    
    # Token breakdown if token column exists
    if 'token' in df.columns:
        print("\nToken breakdown:")
        tokens_sent = sent_txs['token'].value_counts() if len(sent_txs) > 0 else pd.Series()
        tokens_received = received_txs['token'].value_counts() if len(received_txs) > 0 else pd.Series()
        
        for token in set(tokens_sent.index) | set(tokens_received.index):
            sent = tokens_sent.get(token, 0)
            received = tokens_received.get(token, 0)
            print(f"- {token}: Sent {sent} tx, Received {received} tx")
    
    # Check which columns are available for time analysis
    time_cols = [col for col in ['height', 'timestamp'] if col in df.columns]
    if time_cols and len(sent_txs) + len(received_txs) > 0:
        print("\nActivity pattern over time:")
        
        # Combine sent and received transactions with available columns
        required_cols = time_cols + (['amount'] if 'amount' in df.columns else [])
        
        all_txs_parts = []
        if len(sent_txs) > 0:
            all_txs_parts.append(sent_txs[required_cols].assign(type='sent'))
        if len(received_txs) > 0:
            all_txs_parts.append(received_txs[required_cols].assign(type='received'))
            
        if all_txs_parts:
            all_txs = pd.concat(all_txs_parts)
            
            if 'height' in all_txs.columns:
                all_txs = all_txs.sort_values('height')
                first_tx = all_txs['height'].min()
                last_tx = all_txs['height'].max()
                blocks_active = last_tx - first_tx + 1
                print(f"- First activity at block {first_tx}")
                print(f"- Last activity at block {last_tx}")
                print(f"- Active span: {blocks_active:,} blocks")
                print(f"- Activity density: {len(all_txs) / blocks_active:.4f} transactions per block in active period")
            
            # Visualize transaction history if plot is enabled and we have necessary data
            if plot and 'height' in all_txs.columns and 'amount' in all_txs.columns:
                plt.figure(figsize=(14, 6))
                
                # Plot sent transactions
                sent_plot = all_txs[all_txs['type'] == 'sent']
                if len(sent_plot) > 0:
                    plt.scatter(
                        sent_plot['height'], 
                        sent_plot['amount'],
                        color='red', alpha=0.7, label='Sent'
                    )
                
                # Plot received transactions
                received_plot = all_txs[all_txs['type'] == 'received']
                if len(received_plot) > 0:
                    plt.scatter(
                        received_plot['height'], 
                        received_plot['amount'],
                        color='green', alpha=0.7, label='Received'
                    )
                
                plt.yscale('log')
                plt.title(f'Transaction History for Address {address}')
                plt.xlabel('Block Height')
                plt.ylabel('Amount (log scale)')
                plt.legend()
                plt.grid(True, alpha=0.3)
                plt.show()
    
    return (all_txs if 'all_txs' in locals() else pd.DataFrame()), analysis_result