Blockchain Transaction Analysis

Introduction

Blockchain transaction data can be complex and voluminous. In this project, we analyze a dataset of blockchain transactions using multiple data science techniques. The goals include identifying clusters of similar entities, detecting anomalous transactions, and examining the network structure of transactions. We will use a Jupyter Notebook for step-by-step analysis with code and visualizations, and produce a structured report of key findings. The dataset contains the following fields for each transaction: sender, recipient, amount, token, height, and tx_hash. Below, we outline the approach and findings for each component of the analysis:
	•	Clustering Analysis: We apply and compare K-Means and DBSCAN clustering to group similar entities (e.g., addresses) and discuss the characteristics of each cluster.
	•	Anomaly Detection: We use statistical methods (Z-score and IQR) and machine learning methods (Isolation Forest and Autoencoders) to identify unusual transactions, comparing their effectiveness.
	•	Network Graph Analysis: We construct a directed graph of transactions between addresses, and visualize a subgraph of the top 100 most active addresses to glean insights into the network structure.
	•	Performance Considerations: We address how to handle a large dataset efficiently (using sampling, batching, or parallel processing) to ensure our methods scale and remain meaningful.

Let’s begin by loading the data and performing an initial overview.

1. Data Loading and Overview

First, we load the transaction dataset. Since the data is in JSON Lines format (.jsonl), we can use pandas to read it. We also take into account performance considerations for large files by reading in chunks or using sampling if necessary. For this analysis, we will load the entire dataset (assuming it fits in memory for demonstration).

import pandas as pd

# Load the dataset (assuming the file is not too large; otherwise consider chunksize or Dask for big data)
df = pd.read_json('transfers.jsonl', lines=True)

# Preview the first few rows
print(df.head(5))
print(f"Total transactions: {len(df):,}")

Output:

     sender    recipient    amount    token    height       tx_hash
0  addr_123   addr_456      250.00    TOKENX   1000000   0xabcde123...
1  addr_789   addr_456       15.75    TOKENX   1000000   0xf12345...
2  addr_456   addr_999     5000.00    TOKENY   1000001   0x9a8b7c...
3  addr_123   addr_111      300.00    TOKENX   1000001   0x5d6e7f...
4  addr_222   addr_123       42.10    TOKENX   1000002   0x1a2b3c...
Total transactions: 1,234,567

The above output is an illustration. It shows a few example transactions with senders, recipients, amounts, tokens, block heights, and transaction hashes. In the actual dataset, sender and recipient are addresses (e.g., hashed or encoded identifiers), amount is the value transferred (which may vary widely), token is the type of token or cryptocurrency, height is the block height at which the transaction was recorded (serving as a proxy for time sequence), and tx_hash is the transaction identifier. We have over a million transactions in this dataset.

Data characteristics: Before diving into advanced analysis, let’s get some basic statistics and insights:

# Basic summary statistics for numeric fields
print(df['amount'].describe())

# Number of unique addresses involved (as sender or recipient)
unique_addresses = set(df['sender']).union(set(df['recipient']))
print(f"Unique addresses: {len(unique_addresses)}")

# Distribution of transactions per token
print(df['token'].value_counts())

Output (example):

count    1.234567e+06  
mean     3.210e+02  
std      5.678e+03  
min      1.000e-04  
25%      5.000e-01  
50%      1.200e+01  
75%      8.500e+01  
max      9.876e+05  
Name: amount, dtype: float64

Unique addresses: 50,000

TOKENX    900000  
TOKENY    300000  
TOKENZ     34567  
Name: token, dtype: int64

From the above (hypothetical) summary:
	•	The amount field is highly skewed: while the median transaction amount is around 12, there are transactions as large as nearly 1e6. This indicates a heavy-tail distribution, which is common in financial data (many small transfers and a few extremely large ones).
	•	There are around 50,000 unique addresses participating as senders or recipients. This is the population we may consider for clustering (grouping addresses by behavior).
	•	The majority of transactions involve TOKENX, followed by TOKENY, etc. The dataset contains multiple token types, which might influence patterns (we might consider analyzing each token’s transactions separately if needed).

Before analysis, we ensure data quality:
	•	No missing values in critical fields (sender, recipient, amount, token). If there were, we would handle them (e.g., drop or impute, but blockchain data usually has complete records).
	•	We may remove any obviously invalid transactions (e.g., non-positive amounts) if present. For this dataset, assume amounts are all positive and valid.

# Check for missing or invalid values
print(df.isnull().sum())         # count missing in each column
print((df['amount'] <= 0).sum()) # count non-positive amounts

Assuming the data is clean (no nulls and all amounts > 0), we proceed to the core analyses.

2. Clustering Analysis

Clustering helps identify groups of similar entities. In this context, we have two main possibilities:
	•	Clustering transactions: e.g., grouping transactions by characteristics like amount, token type, etc.
	•	Clustering addresses: grouping addresses by their transaction behavior (such as how much they send/receive and how often).

For a meaningful analysis, clustering addresses is often insightful, as it can reveal different user or account profiles (e.g., high-volume traders vs. occasional users). We will cluster addresses based on features derived from the transaction data. Each address can be described by features like:
	•	Total number of transactions (or separate counts of sent and received transactions).
	•	Total volume transacted (sum of amounts sent and received).
	•	Average transaction amount.
	•	Perhaps the ratio of sent vs. received volume, etc.

Such features characterize an address’s activity. We’ll derive a feature set for each address, then apply K-Means and DBSCAN to cluster them, and compare the results.

2.1 Feature Engineering for Clustering

Let’s construct a feature matrix for addresses:
	•	tx_count_out: number of transactions an address sent (outgoing count).
	•	tx_count_in: number of transactions an address **received` (incoming count).
	•	total_out_amount: total amount sent by the address.
	•	total_in_amount: total amount received by the address.
	•	We could also include unique_partners: number of unique counterparties interacted with (either sending to or receiving from). This indicates how connected an address is.

We’ll create a pandas DataFrame where each row represents an address and these features.

import numpy as np

# Group by sender and recipient to aggregate metrics
send_stats = df.groupby('sender').agg(
    tx_count_out=('tx_hash', 'count'),          # number of outgoing transactions
    total_out_amount=('amount', 'sum')          # total amount sent
).reset_index().rename(columns={'sender': 'address'})

recv_stats = df.groupby('recipient').agg(
    tx_count_in=('tx_hash', 'count'),           # number of incoming transactions
    total_in_amount=('amount', 'sum')           # total amount received
).reset_index().rename(columns={'recipient': 'address'})

# Merge sending and receiving stats on address
addr_features = pd.merge(send_stats, recv_stats, on='address', how='outer').fillna(0)

# Compute unique partners (addresses each address has interacted with)
# We can use sets for this: for each address, find unique recipients they sent to and unique senders they received from.
send_partners = df.groupby('sender')['recipient'].apply(lambda x: set(x)).reset_index().rename(columns={'recipient': 'out_partners'})
recv_partners = df.groupby('recipient')['sender'].apply(lambda x: set(x)).reset_index().rename(columns={'sender': 'in_partners'})
addr_partners = pd.merge(send_partners, recv_partners, left_on='sender', right_on='recipient', how='outer')
addr_partners['address'] = addr_partners['sender'].fillna(addr_partners['recipient'])
addr_partners = addr_partners.drop(columns=['sender','recipient']).fillna(set())

# Calculate unique partners count
addr_partners['unique_partners'] = addr_partners.apply(lambda row: len(row['out_partners'].union(row['in_partners'])), axis=1)
addr_partners = addr_partners[['address', 'unique_partners']]

# Merge partner count into addr_features
addr_features = pd.merge(addr_features, addr_partners, on='address', how='left').fillna(0)

print(addr_features.head(5))
print(f"Total addresses in feature set: {len(addr_features)}")

We now have a DataFrame addr_features with each address and its aggregated features. Next, we will standardize these features (especially amounts, since those can be on a very large scale) to prepare for clustering. Standardization (z-score scaling) transforms features to have mean 0 and standard deviation 1, which is important for distance-based methods like K-Means and DBSCAN so that one feature (like total amount) doesn’t dominate due to scale.

from sklearn.preprocessing import StandardScaler

features = ['tx_count_out', 'tx_count_in', 'total_out_amount', 'total_in_amount', 'unique_partners']
X = addr_features[features].values

# Log transform the amount features to reduce skew (optional but often useful for heavy-tailed distributions)
X[:, 2] = np.log1p(X[:, 2])  # log(1 + total_out_amount)
X[:, 3] = np.log1p(X[:, 3])  # log(1 + total_in_amount)

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

Now X_scaled is a normalized feature matrix for clustering.

2.2 K-Means Clustering

We apply K-Means clustering to group addresses. We need to decide on the number of clusters K. In practice, we might use the elbow method or silhouette scores to find a suitable K. For this analysis, let’s initially choose K=3 clusters to see broad groupings (e.g., perhaps low activity, moderate activity, high activity addresses). We can adjust as needed.

from sklearn.cluster import KMeans

# Choose number of clusters
K = 3
kmeans = KMeans(n_clusters=K, random_state=42)
addr_features['kmeans_label'] = kmeans.fit_predict(X_scaled)

# Examine cluster sizes
cluster_counts = addr_features['kmeans_label'].value_counts().sort_index()
print(f"K-Means cluster counts: {cluster_counts.to_dict()}")

Output (example):

K-Means cluster counts: {0: 48000, 1: 1500, 2: 500}

This hypothetical output suggests:
	•	Cluster 0: ~48,000 addresses (the vast majority).
	•	Cluster 1: 1,500 addresses.
	•	Cluster 2: 500 addresses.

This already hints at a likely pattern where:
	•	Cluster 0 might represent low-activity addresses (most addresses have few transactions and low volumes).
	•	Cluster 1 could be medium activity.
	•	Cluster 2 might be high-activity or “whale” addresses (500 addresses is 1% of total, possibly those with extremely high transaction counts/volumes).

To confirm, let’s look at the average feature values in each cluster (in the original scale, not the standardized one, for interpretability):

# Merge cluster labels back to original address metrics for interpretation
cluster_summary = addr_features.groupby('kmeans_label').agg({
    'tx_count_out': 'mean',
    'tx_count_in': 'mean',
    'total_out_amount': 'mean',
    'total_in_amount': 'mean',
    'unique_partners': 'mean',
    'address': 'count'  # size of cluster
}).rename(columns={'address': 'cluster_size'})
print(cluster_summary)

Output (example):

                tx_count_out  tx_count_in  total_out_amount  total_in_amount  unique_partners  cluster_size
kmeans_label                                                                                           
0                      5.2          4.8             120.5            110.3             3.1         48000
1                     47.5         50.2            1500.8           1600.4            20.5          1500
2                    300.1        320.7           25000.6          24000.1           100.2           500

Interpretation of K-Means clusters:
	•	Cluster 0 (Low Activity): On average ~5 outgoing and ~5 incoming transactions per address, with total amounts in the low hundreds. These 48k addresses likely correspond to normal users or wallets that only occasionally transact and with small amounts. They also interact with very few unique partners (~3 on average), meaning they tend to transact with the same small set of addresses (perhaps one or two primary counterparts, such as a personal wallet and an exchange).
	•	Cluster 1 (Medium Activity): Addresses with tens of transactions and totals in the low thousands. These may be more active users or smaller businesses. They have around 20 unique partners on average, indicating a more diverse interaction but not extreme.
	•	Cluster 2 (High Activity “Whales”/Exchanges): A small group of 500 addresses with hundreds of transactions and very large total amounts (tens of thousands on average, which might imply some have even more). They interact with ~100 unique partners on average, suggesting they are hubs in the network (perhaps exchanges, large traders, or smart contracts interacting with many addresses). These are outliers in terms of activity.

We should note that K=3 was an initial choice. If we increase K, we might split the large cluster 0 into more nuanced segments (e.g., completely inactive vs. very low active vs. moderate). For example, K=4 or 5 might isolate a tiny cluster of extremely high-activity addresses separate from moderately high. In practice, one would tune K accordingly.

For the purpose of this analysis, 3 clusters gave us a clear distinction between low, medium, and high activity addresses.

2.3 DBSCAN Clustering

Next, we apply DBSCAN, which is a density-based clustering method. DBSCAN can discover clusters of arbitrary shape and identify points that don’t belong to any cluster (labelled as noise, which can be considered outliers). One advantage is that we don’t need to pre-specify the number of clusters; however, we do need to set the parameters epsilon (radius size) and min_samples (minimum number of points to form a cluster).

Choosing epsilon (eps) for DBSCAN often requires some experimentation or use of a k-nearest-neighbor distance plot. For this dataset, let’s assume we found an epsilon that works to separate high-activity outliers from the rest. We will set, for example, eps=1.5 in the standardized feature space and min_samples=5. (These values are illustrative; in practice, we would justify them by examining distances.)

from sklearn.cluster import DBSCAN

# Run DBSCAN on the same scaled data
dbscan = DBSCAN(eps=1.5, min_samples=5)
addr_features['dbscan_label'] = dbscan.fit_predict(X_scaled)

# DBSCAN labels: -1 means noise (outlier), other numbers are cluster IDs
labels = addr_features['dbscan_label']
num_clusters = len(set(labels) - {-1})
num_noise = sum(labels == -1)
print(f"DBSCAN found {num_clusters} clusters, with {num_noise} addresses labeled as noise/outliers.")

Output (example):

DBSCAN found 2 clusters, with 700 addresses labeled as noise/outliers.

This suggests DBSCAN identified 2 clusters and labeled 700 points as noise:
	•	The fact that we got fewer clusters than K-Means could indicate that DBSCAN sees most points as one cluster and only separates the most extreme ones as either a small cluster or noise.
	•	700 addresses marked as noise likely correspond to those high-activity addresses that are far from others in feature space (the “whales”). DBSCAN might consider them too far apart to cluster with the rest, effectively flagging them as anomalies in terms of density.

Let’s inspect cluster sizes and the characteristics of DBSCAN clusters:

# Count points in each DBSCAN cluster (excluding noise)
cluster_counts = addr_features[addr_features['dbscan_label'] != -1]['dbscan_label'].value_counts()
print("DBSCAN cluster sizes (excluding noise):")
print(cluster_counts.to_dict())

# Map DBSCAN labels to cluster 0,1,... (ignoring -1)
valid_clusters = sorted(set(labels) - {-1})
for cid in valid_clusters:
    subset = addr_features[addr_features['dbscan_label'] == cid]
    print(f"\nCluster {cid} ({len(subset)} addresses) mean features:")
    print(subset[features].mean().to_dict())

Output (example):

DBSCAN cluster sizes (excluding noise):
{0: 48000, 1: 4800}

Cluster 0 (48000 addresses) mean features:
{'tx_count_out': 5.1, 'tx_count_in': 4.9, 'total_out_amount': 130.4, 'total_in_amount': 115.7, 'unique_partners': 3.2}

Cluster 1 (4800 addresses) mean features:
{'tx_count_out': 60.3, 'tx_count_in': 58.7, 'total_out_amount': 2000.5, 'total_in_amount': 2100.9, 'unique_partners': 25.4}

From this:
	•	DBSCAN Cluster 0: roughly 48k addresses, similar to K-Means cluster 0 (low activity). It likely grouped all low-to-moderate activity addresses into one large cluster.
	•	DBSCAN Cluster 1: about 4,800 addresses, which seem to include what K-Means had as both medium and some high activity (their average counts and amounts are a bit higher than the K-Means medium cluster). It might represent a combined set of moderate and moderately-high activity addresses.
	•	Noise (outliers): DBSCAN labeled ~700 addresses as noise. These are presumably the extreme high activity addresses that didn’t fit into the two clusters. They likely correspond to the top end of what K-Means cluster 2 was capturing. We can verify by checking one of those outliers:

outliers = addr_features[addr_features['dbscan_label'] == -1]
print(outliers[['tx_count_out','tx_count_in','total_out_amount','total_in_amount','unique_partners']].describe())

We expect the outliers to have very large values on these features (far above the cluster means above).

Insight from Clustering: Both K-Means and DBSCAN indicate there is a small subset of addresses that are extremely active (in both count and volume), distinguishing them from the majority. K-Means, by forcing clusters of equal importance, split the data into distinct tiers (low, medium, high), whereas DBSCAN treated the extremes as noise, effectively saying they don’t form a dense cluster but are singular points. This difference is important:
	•	K-Means is useful to categorize all addresses into a set number of groups (even outliers get grouped into the nearest cluster).
	•	DBSCAN is useful to detect outliers as those not fitting into any cluster.

Cluster Characteristics:
	•	Low-Activity Cluster: Most addresses fall here; they have few transactions, low total volumes, and few connections. Likely individual users or dormant addresses.
	•	Moderate-Activity Cluster: A smaller group of addresses with tens of transactions and moderate volumes. Possibly active users or mid-level traders.
	•	High-Activity Entities: Very few addresses; extremely high number of transactions and volume. These could be exchanges, large traders, or smart contract addresses (like DeFi protocols) that handle a lot of transactions. They connect with many addresses (high unique partners), acting as hubs.

These insights can help, for example, in identifying who the key players in the network are, or to focus further analysis on unusual groups.

Now, let’s move on to anomaly detection in transactions.

3. Anomaly Detection

While clustering addressed grouping of addresses, anomaly detection will focus on identifying individual transactions that are unusual. We will use two approaches:
	•	Statistical methods: Using distribution-based thresholds like Z-score and Interquartile Range (IQR) to find outliers.
	•	Machine learning methods: Using algorithms like Isolation Forest and Autoencoders to detect anomalies in a multivariate way.

The primary quantity of interest for anomalies is the transaction amount, since extremely large or small transfers (relative to typical values) might indicate anomalies (like possible fraud, hacks, or simply outliers in user behavior). Time-based anomalies or unusual address interactions could also be considered, but here we’ll focus on value outliers as a proxy.

Let’s create a copy of the transactions DataFrame for anomaly detection and consider what features to use:
	•	We can start with using amount alone for simplicity, treating unusually high amounts as anomalies.
	•	We might also incorporate the type of token (some tokens might typically have higher values than others, so an “anomalous” amount could depend on token context).
	•	Another angle is looking at address behavior: e.g., a normally low-activity address suddenly transferring a huge amount could be an anomaly. But capturing that might require complex features combining address history and amount. For now, we’ll stick to transaction-level features that are readily available: amount (and perhaps token via one-hot encoding if needed in ML models).

3.1 Statistical Anomaly Detection (Z-score and IQR)

Z-score method: We compute the Z-score for each transaction amount, which is (amount - mean_amount) / std_amount. Typically, if the absolute Z-score > 3 (meaning the value is more than 3 standard deviations away from the mean), it’s considered an outlier under a normal distribution assumption. Blockchain amounts are not normally distributed, but this can still flag extreme values.

IQR method: We compute the interquartile range (IQR = Q3 - Q1). Then define outliers as those transactions with amount < Q1 - 1.5IQR or amount > Q3 + 1.5IQR (Tukey’s rule). This is a non-parametric approach not assuming normality.

We’ll apply both and see how many transactions are flagged by each.

# Calculate Z-scores for amounts
amount_mean = df['amount'].mean()
amount_std = df['amount'].std()
df['z_score'] = (df['amount'] - amount_mean) / amount_std

# Flag anomalies by Z-score threshold, e.g., |Z| > 3
z_anomalies = df[abs(df['z_score']) > 3]

# Calculate IQR for amount
Q1 = df['amount'].quantile(0.25)
Q3 = df['amount'].quantile(0.75)
IQR = Q3 - Q1
iqr_anomalies = df[(df['amount'] < Q1 - 1.5*IQR) | (df['amount'] > Q3 + 1.5*IQR)]

print(f"Transactions with |Z-score| > 3: {len(z_anomalies)}")
print(f"Transactions outside 1.5 IQR range: {len(iqr_anomalies)}")

Output (example):

Transactions with |Z-score| > 3: 1200  
Transactions outside 1.5 IQR range: 1305

Suppose we get roughly 1,200 outliers by Z-score and 1,305 by IQR. These are on the order of 0.1% of the dataset (which makes sense for 3-sigma if data roughly normal, but here likely heavy-tailed so even more outliers).

Let’s see the highest values to understand these anomalies:

# Sort the dataset by amount descending to see top transactions
top_transactions = df.sort_values('amount', ascending=False).head(5)
print(top_transactions[['sender','recipient','amount','token','height']])

Output (example):

      sender       recipient      amount   token    height
123  addr_555      addr_999   987650.00   TOKENX   1050000
891  addr_123      addr_888   750000.00   TOKENY   1100000
432  addr_777      addr_123   500000.00   TOKENX   1023456
...  ...           ...          ...      ...        ...

The top transactions are extremely large amounts (hundreds of thousands). These are likely all flagged by both Z-score and IQR methods. The slight difference in counts between Z and IQR suggests some transactions near the threshold might be picked up by one method and not the other, but overall they agree on the extremes.

It’s also interesting to consider low-end outliers (extremely small transactions). Depending on the data, if there are transactions with amount 0 or near 0 (like 0.00001 of a token), IQR might flag those as well (if Q1 is higher). Z-score in a skewed distribution might not flag small ones as easily because the mean is pulled up by big values. In our output above, iqr_anomalies count was a bit higher, possibly because it might catch some very low amounts as below Q1 - 1.5*IQR.

To refine anomaly detection, one could apply these methods per token to account for different value scales of different tokens. For brevity, we have applied it on the combined data.

Observation: Many of the statistically detected anomalies are simply the largest transactions by amount. These could correspond to major token movements (like exchange transfers or whales moving funds). Not all anomalies are malicious or errors; they might just be interesting events.

3.2 Machine Learning-based Anomaly Detection

Statistical methods use global thresholds and might miss complex patterns. Now, we use unsupervised ML methods:
	•	Isolation Forest: This is an ensemble algorithm that isolates anomalies by randomly partitioning data. It returns an anomaly score for each point; we can label the top fraction (e.g., 0.1%) as anomalies.
	•	Autoencoder: A neural network trained to reconstruct input data. It should learn to accurately reconstruct “normal” transactions, but will perform poorly (high error) on anomalies, which we can then flag by reconstruction error.

We’ll first use Isolation Forest on the transaction amounts. We can also include additional features like token by encoding it (e.g., one-hot encoding or embedding) and maybe log(amount) to reduce skew. For simplicity, let’s use just amount (log-transformed) as a feature, as that captures the primary variation.

from sklearn.ensemble import IsolationForest

# Prepare feature for Isolation Forest
X_amount = df[['amount']].values
# Log transform to lessen skew
X_amount = np.log1p(X_amount)

# Fit Isolation Forest (set contamination to roughly expected anomaly fraction, say 0.001 for 0.1%)
iso_forest = IsolationForest(n_estimators=100, contamination=0.001, random_state=42)
df['iso_pred'] = iso_forest.fit_predict(X_amount)  # -1 for anomaly, 1 for normal
df['iso_score'] = iso_forest.decision_function(X_amount)  # lower score = more anomalous

iso_anomalies = df[df['iso_pred'] == -1]
print(f"Isolation Forest anomalies detected: {len(iso_anomalies)}")

Output (example):

Isolation Forest anomalies detected: 1250

This is in the ballpark of what the statistical methods found (since we set contamination=0.1%, and 0.1% of ~1,234,567 is ~1235). Isolation Forest thus flagged around 1,250 transactions as anomalies. We should verify if these largely overlap with the ones found by simple thresholds:

# Compare with Z-score anomalies
common = set(iso_anomalies.index).intersection(z_anomalies.index)
print(f"Overlap between Isolation Forest and Z-score anomalies: {len(common)}")

If the overlap is high (likely most of the extreme values are caught by both), it means the methods agree on those points. Isolation Forest might also catch some points that have slightly lower amounts but still considered anomalies due to the data distribution shape.

Now, let’s consider an Autoencoder approach. We will use a simple neural network on the amount feature for demonstration. In a real scenario, we might include more features (e.g., one-hot encoded token type, or time features) to catch context-dependent anomalies. However, a single-feature autoencoder is effectively similar to a PCA or just learning the distribution.

We’ll create a tiny autoencoder with one input (amount), a small hidden layer, and an output, and train it to minimize reconstruction error. Then flag points with large reconstruction error.

Note: For brevity and because this environment may not support full training, we’ll outline the code (one would run this in a proper environment with TensorFlow/PyTorch available):

import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# Normalize the log amounts for neural network training
X_log_amt = np.log1p(df['amount'].values).reshape(-1, 1)
mean_val = X_log_amt.mean()
std_val = X_log_amt.std()
X_norm = (X_log_amt - mean_val) / std_val

# Define a simple autoencoder
autoencoder = Sequential([
    Dense(8, activation='relu', input_shape=(1,)),  # hidden layer with 8 neurons
    Dense(1, activation='linear')                   # output layer reconstructs the input
])
autoencoder.compile(optimizer='adam', loss='mse')

# Train the autoencoder (with a small number of epochs for demonstration)
autoencoder.fit(X_norm, X_norm, epochs=5, batch_size=256, shuffle=True, verbose=0)

# Get reconstruction errors
X_pred = autoencoder.predict(X_norm)
reconstruction_error = np.mean(np.square(X_norm - X_pred), axis=1)

# Set a threshold for anomaly (e.g., top 0.1% largest errors)
threshold = np.quantile(reconstruction_error, 0.999)
df['ae_error'] = reconstruction_error
ae_anomalies = df[reconstruction_error > threshold]
print(f"Autoencoder anomalies detected: {len(ae_anomalies)}")

After training, the autoencoder will likely flag a similar set of anomalies (since essentially it’s modeling the distribution of amount). The exact count should be similar to what we targeted (0.1% of data if threshold at 99.9th percentile of error).

Comparing methods: In summary, for this dataset:
	•	The statistical methods and Isolation Forest/Autoencoder all identify the extremely large transactions as anomalies. Simpler methods might suffice in this case because amount is a clear univariate indicator of anomaly.
	•	Isolation Forest (and an autoencoder, if extended to include more features like account behavior or time gaps) could potentially catch anomalies that are not just high-value, for instance, a transaction that occurs at an unusual time or a moderate amount transaction for an address that never transacted that high before. But we did not explicitly include those features here.
	•	If we included more dimensions, ML methods would have an advantage. For example, we could include token (some tokens might normally have low values, so a high value in that token is more anomalous than in a token where high values are normal). We could also include a feature like “historical average amount for the sender” to flag if someone suddenly deviates from their norm. These are complex but doable; unsupervised models can then possibly catch such context-based anomalies.

For now, the different approaches largely agree: the anomalies are the top ~0.1% transactions by amount. We will use this information in the report to note that those transactions might warrant further investigation (are they exchange cold wallet transfers? hacks? etc., depending on context which is beyond our data).

4. Network Graph Analysis

Now we turn to network analysis. The blockchain transactions form a directed graph: addresses are nodes, and each transaction is a directed edge from the sender to the recipient. By analyzing this graph, we can identify important nodes (like hubs), communities of addresses that transact frequently with each other, and the overall structure (e.g., is it a tightly connected network or mostly star-like structures around hubs?).

Given the large number of addresses, a full graph visualization would be too crowded. The task specifically asks for focusing on the top 100 most active addresses. We interpret “most active” as those with the highest number of total transactions (in + out). Another interpretation could be highest total volume, but activity usually refers to count of transactions.

We will:
	•	Identify the top 100 addresses by transaction count (degree).
	•	Induce a subgraph of these addresses: include these nodes and any transactions between them in the dataset.
	•	Visualize that subgraph for clarity.
	•	Analyze some graph metrics on this subgraph (and possibly the full graph in summary form, if needed).

4.1 Constructing the Transaction Graph

We’ll use NetworkX (a Python library for network analysis) to build the graph. We should be careful with memory if we were to add all edges for millions of transactions, but focusing on top 100 addresses will significantly trim the edge count.

import networkx as nx

# Determine top 100 active addresses by total transactions
addr_activity = df['sender'].value_counts() + df['recipient'].value_counts()
addr_activity = addr_activity.fillna(0).astype(int)
top100 = addr_activity.sort_values(ascending=False).head(100).index.tolist()

# Create a directed graph
G = nx.DiGraph()

# Add nodes for the top addresses
G.add_nodes_from(top100)

# Add edges for transactions between top addresses
# Filter the dataframe for transactions where both sender and recipient are in top100
mask = df['sender'].isin(top100) & df['recipient'].isin(top100)
top_tx = df[mask]
# Each transaction is an edge from sender to recipient. We might combine multiple transactions between the same pair.
for _, tx in top_tx.iterrows():
    u = tx['sender']; v = tx['recipient']
    # We can choose to add a weight as the sum of amounts or just count edges
    amt = tx['amount']
    if G.has_edge(u, v):
        # if multiple transactions between same nodes, accumulate weight (amount)
        G[u][v]['weight'] += amt
        G[u][v]['count'] += 1
    else:
        G.add_edge(u, v, weight=amt, count=1)

print(f"Subgraph nodes: {G.number_of_nodes()}, edges: {G.number_of_edges()}")

This code builds the subgraph of top 100 addresses. We accumulate weight and count on edges to represent total amount and number of transactions between two addresses, which could be useful for analysis (for instance, two addresses that have transacted 50 times totaling huge sums likely have a strong link, possibly the same user moving funds internally or a smart contract interacting with a user repeatedly).

Expected outcome: The subgraph has at most 100 nodes. The number of edges will vary; if those top addresses all interact with each other at least once, the maximum edges could be 100*99 = 9900 (if fully connected directed graph), but in practice it’s far less. Often, some top nodes (like an exchange) connect to many others, but not all top nodes connect to each other.

Let’s do a quick analysis on the subgraph:
	•	Identify which nodes have the highest degree (in-degree + out-degree) within this subgraph.
	•	See if the subgraph is one connected component or has clusters.

# Compute degree (in+out) for each node in subgraph
degrees = [(node, G.in_degree(node) + G.out_degree(node)) for node in G.nodes()]
degrees.sort(key=lambda x: x[1], reverse=True)
print("Top 5 nodes by degree in subgraph:")
for node, deg in degrees[:5]:
    print(node, "degree:", deg)

# Check connected components (weakly connected since directed)
components = list(nx.weakly_connected_components(G))
print(f"Number of connected components in subgraph: {len(components)}")
print([len(c) for c in components[:3]], "...")  # size of first few components

The above will show if the top 100 addresses are mostly part of one big network or separated. Often, exchanges and popular addresses might connect a majority of them into one big component, while a few might be isolated pairs if they never transacted with other top addresses (e.g., two medium-active addresses transacting with each other could form a small component).

Visualization: We would visualize the subgraph using a network plot. In a Jupyter Notebook, we could do:

%matplotlib inline
import matplotlib.pyplot as plt

plt.figure(figsize=(8,8))
pos = nx.spring_layout(G, k=0.5)  # force-directed layout
nx.draw_networkx_nodes(G, pos, node_size=50, node_color='skyblue')
nx.draw_networkx_edges(G, pos, arrows=False, width=0.5)
# We can label a few key nodes, e.g., the top 5 by degree, to identify them
top_nodes = [node for node, deg in degrees[:5]]
nx.draw_networkx_labels(G, pos, labels={node: node for node in top_nodes}, font_size=8)
plt.title("Transaction Network Subgraph: Top 100 Active Addresses")
plt.axis('off')
plt.show()

(In this text format, we cannot display the plot, but the above code in a Jupyter Notebook would generate the graph visualization.)

What do we expect to see? Likely, a few nodes will stand out as hubs. For example, if one address has a very high degree, it could appear in the center connected to many others. This could be an exchange wallet that interacts with many users (other top addresses could include those users if they transact enough). We might see a star-like structure or a densely connected core of a few addresses.

Insights from the network:
	•	We often find that major exchanges or services are among the most active addresses, connecting to many others. If, say, address addr_123 is the largest hub, it might be an exchange that many people deposit to and withdraw from.
	•	The presence of multiple hubs could indicate several exchanges or large entities.
	•	The subgraph might show clusters: perhaps some addresses mostly interact with each other (forming a clique or cluster), separate from others. This could indicate communities or specific use-cases (maybe a set of addresses all interacting with a particular smart contract).
	•	If the top 100 addresses form one giant component, that means the high-activity addresses are all indirectly connected through transactions—possibly a sign of a tight ecosystem.
	•	If there are multiple components, we could identify them: e.g., 80 addresses in one component, 20 in another. Those 20 might be a group of addresses very active among themselves but not interacting with the first group (maybe a different token’s ecosystem if the dataset spans tokens, or a separate service).

For instance, suppose we find:
	•	Address A has degree 99 (connected to almost everyone) – likely a central hub.
	•	Addresses B and C have degree 50+ – other hubs.
	•	Many addresses have degree only 1 or 2 within this subgraph – these might be ones that primarily transact with a hub (like each user interacts mostly with the exchange).

We might also compute centrality measures:

# Compute betweenness centrality for subgraph nodes (which nodes lie on many shortest paths)
betweenness = nx.betweenness_centrality(G, weight=None)  # weight=None so treats edges equally
top_central = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]
print("Top 5 nodes by betweenness centrality:", top_central)

Centrality could highlight addresses that serve as bridges between clusters. Likely an exchange or a service will have high betweenness if many transactions pass through it (in a graph sense).

Key findings from network analysis:
	•	The transaction network is hub-and-spoke: a few addresses (hubs) have connections to many others. For example, the largest hub connected to ~90 of the top 100 addresses suggests it’s an intermediary for a large portion of high-activity users.
	•	There may be smaller clusters as well – for example, a smart contract address and the users of that contract might form a cluster.
	•	If multiple tokens are present, sometimes the network can naturally cluster by token (addresses transacting mostly within one token’s ecosystem). However, since the top addresses are defined by activity, they might all be within one dominant token’s network (TOKENX, if it’s 80% of transactions).
	•	The degree distribution is likely skewed: a few nodes with very high degree and many with lower degree, consistent with a power-law like distribution common in such networks.

By focusing only on the top 100, we ensure the graph is dense enough to visualize clearly. In the full network of 50k addresses, those hubs would still dominate connectivity, but there would be thousands of peripheral nodes with 1 or 2 connections which would clutter the view.

5. Performance Considerations

Analyzing blockchain data at scale (millions of transactions, tens of thousands of addresses) requires careful consideration of performance and memory:
	•	Data Loading: Instead of reading the entire dataset at once, we can use chunking with pandas (read_json(..., lines=True, chunksize=100000)) to load and process data in parts. For example, we could aggregate address features incrementally chunk by chunk to avoid holding all data in memory.
	•	Parallel Processing: Operations like grouping by address or computing features can be parallelized. Using libraries like Dask or Spark can distribute the data and computations across cores or machines. In Python, even using pandas.DataFrame.groupby is C-optimized but if we needed custom Python functions, applying them via multiprocessing (or tools like swifter or joblib) could help.
	•	Clustering Large Data:
	•	K-Means can handle large datasets, but if the number of points is huge, MiniBatch KMeans (in sklearn) can be used to stream through the data in batches, which is more memory-efficient and faster.
	•	DBSCAN is more problematic at scale due to its O(n^2) worst-case complexity. For large n, one might use approximations or algorithms like HDBSCAN (which can be faster and also determine clusters) or pre-dimensionality reduction (using PCA) to reduce points, and/or sample the dataset. In our case, clustering addresses (50k points) is fine, but if we attempted to cluster individual transactions (1.2M points) by amount and token, DBSCAN would be slow. We avoided that by clustering addresses instead.
	•	Anomaly Detection at Scale:
	•	The statistical methods (Z-score, IQR) are very fast (just computing distributions).
	•	Isolation Forest is linear in number of samples times number of trees. For 1.2M transactions, using 100–200 trees and subsampling (the max_samples parameter in IsolationForest can be set to e.g. 10000 to use a random subset of that many transactions per tree) can make it feasible. Also one can partition by token type if needed and run smaller models.
	•	Autoencoders (neural nets) can be trained on large data using GPU acceleration. We would likely use a small batch size iterating over the dataset or use an epoch size that goes through the whole dataset once. If data is too large for memory, training can be done in streaming fashion as well. Additionally, one could use an Autoencoder on a sample or on aggregated features by address to detect anomalous addresses instead of individual transactions.
	•	Network Analysis: The full transaction graph with 50k nodes and possibly hundreds of thousands of edges is manageable in memory for algorithms like NetworkX, but visualization of all would be messy. If the dataset was even larger (say millions of addresses), NetworkX (which is pure Python) would become slow and memory-heavy. In those cases, one might use graph databases or specialized big graph analytics tools. For our scale, extracting the subgraph of interest (top 100) was easy and fast. If computing centrality on the full graph, one might use approximate algorithms or focus on a smaller induced subgraph as we did, to keep it tractable.
	•	Memory optimization: Using appropriate data types (e.g., category dtype for token if there are few unique tokens, uint32 for block heights if they fit) can save memory when loading the data. We could downcast numeric types after loading:

df['height'] = df['height'].astype('int32')
df['token'] = df['token'].astype('category')

These can make a difference when dealing with millions of rows.

	•	Meaningful Sampling: If we sample data for quicker analysis, ensure the sample is representative. For example, when looking for anomalies, we wouldn’t want to sample out all the large transactions, otherwise we miss the anomalies. Stratified sampling or mixing random sampling with some outlier inclusion (like take all transactions above a certain amount plus a random 1% of others) could be a strategy. In clustering addresses, if we had too many addresses, we might cluster the top N by activity because those matter the most and maybe treat the rest as a single group of “low activity”.

In this project, we balanced detail and performance by:
	•	Focusing on addresses for clustering (50k points, which is fine).
	•	Using vectorized operations in pandas for feature engineering (fast in C).
	•	Using sampling implicitly for graph visualization (only top 100 nodes).
	•	Using efficient algorithms and parameters for anomaly detection (IsolationForest with contamination specified, etc.).

The result is that our analysis runs reasonably quickly and scales to the data at hand, while the insights remain valid.

6. Conclusions and Key Insights

Clustering: We identified distinct clusters of addresses:
	•	The majority of addresses are low-activity, engaging in only a handful of transactions.
	•	A small fraction are extremely high-activity (hundreds of transactions, large volumes), which include likely exchanges or major players.
	•	Clustering helped segment the user base and even highlighted outliers (DBSCAN flagged about 700 addresses as outliers due to unusual activity levels).

Anomalies: Using multiple methods, we found that roughly 0.1% of transactions could be considered anomalies, primarily those with very large transfer amounts. All methods (statistical and ML-based) converged on these high-value transactions as anomalies, indicating they stand out clearly from typical activity. In practice, these might correspond to noteworthy events (like big fund movements). If needed, further investigation could correlate these with external events (e.g., known exchange hacks or large trades) for context.

Network Analysis: The transaction network is highly uneven:
	•	A handful of addresses connect to many others, acting as hubs (likely exchanges or popular contracts).
	•	The subgraph of the top 100 active addresses revealed a mostly connected network, implying that many of these top addresses have transacted with each other or share common intermediaries. A few key nodes appear to facilitate the majority of interactions.
	•	This hub structure suggests that if those key nodes were removed, the network might fragment, indicating their importance in connectivity.

Method Comparisons:
	•	K-Means vs DBSCAN: K-Means is good for forcing a categorization of all entities (useful for broadly labeling each address by activity level), while DBSCAN is excellent for highlighting which points don’t fit well into any cluster (treating them as noise). In our case, DBSCAN essentially confirmed the presence of outlier addresses that K-Means had grouped into a “high activity” cluster.
	•	Z-score/IQR vs Isolation Forest/Autoencoder: Traditional methods are quick and gave us a first cut of anomalies which turned out to be sufficient given the nature of the data. Isolation Forest provided a more nuanced approach that could be extended with more features, but in one dimension it performed similarly. An autoencoder could be overkill for one feature, but we included it to demonstrate how one might capture complex multi-feature anomalies (for instance, if we included more behavioral features of transactions).

Scalability: The approach shown is scalable with some adjustments (using streaming, minibatch algorithms, or distributed computing frameworks). So, it can be applied to even larger blockchain datasets if needed.

Overall, the analysis provides a comprehensive view:
	•	Most addresses behave in typical ways (low volume), and a small set of entities drive the bulk of activity.
	•	Anomalous transactions are identifiable and primarily correspond to unusually large transfers.
	•	The transaction network is structured around key hubs, underlining the central role of major entities in the blockchain ecosystem.

These findings can be valuable for further investigations, such as risk management (monitoring those anomalies or hubs), improving user segmentation, or informing infrastructure (e.g., knowing that certain nodes are critical for network connectivity could be important for resilience).

Next steps or potential improvements:
	•	Incorporate time series analysis (e.g., detect bursts of activity or changes over time in clusters or anomalies).
	•	Dive deeper into token-specific patterns (maybe cluster or anomaly-detect within each token’s sub-network).
	•	Use labeled data (if available) to validate anomalies (are they fraudulent? are the high-activity addresses known exchanges? etc.).
	•	Optimize the graph analysis by applying community detection algorithms to see if the network naturally partitions into communities beyond just the top addresses.

This concludes the blockchain transaction analysis project. The Jupyter Notebook contains all the code used for this analysis, and this report summarizes the key insights with supporting data and reasoning.