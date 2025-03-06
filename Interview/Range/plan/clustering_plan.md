Feature Engineering and Clustering for Blockchain Addresses

Blockchain transactions generate rich data that can be mined to understand how addresses behave. By engineering informative features from transaction logs and applying clustering, we can group addresses by similar behavior patterns (e.g., frequent small transactors vs. large-value movers). This answer explores feature engineering (both static and temporal) for addresses using transaction data, and clustering techniques (traditional and deep learning-based) to profile addresses. We include Python code for implementation, detailed explanations of each step, and an analysis of example clustering results.

1. Feature Engineering for Addresses

Feature engineering transforms raw transaction records into meaningful numerical features for each address. Given transaction data columns: sender, recipient, amount, token, height (block height or timestamp proxy), and tx_hash, we can derive a variety of features per address:

1.1 Static Behavioral Features (Aggregated Stats per Address)

Static features summarize an address’s overall behavior across all transactions. These are typically aggregated statistics that capture how much and how often an address sends/receives value. Such features have been found highly informative in blockchain analytics ￼. Key static features include:
	•	Transaction Counts: Total number of transactions an address is involved in. We often split this into outgoing count (address as sender) and incoming count (address as recipient). These correspond to the address’s out-degree and in-degree in the transaction graph.
	•	Transaction Volumes: Total amount sent and amount received by the address (sums of amount for outgoing and incoming txs). We can also compute the net flow (total received minus total sent) to see if an address accumulates value or disperses it.
	•	Value Distribution Stats: Descriptive stats of transaction amounts. For example: minimum and maximum transaction value sent (min_out, max_out) and received (min_in, max_in), as well as average or median transaction value. These features often rank among the most important; e.g., features like min-input, max-input, avg-input, max-output, min-output were identified as top predictors in blockchain behavior classification ￼.
	•	Unique Counterparties: Count of unique other addresses transacted with. For senders, how many distinct recipients they’ve sent to; for receivers, how many distinct senders have sent to them. This indicates the breadth of an address’s network.
	•	Token Diversity: If token denotes asset type, we can count how many distinct token types an address has interacted with, or the dominant token for that address. An address transacting in many tokens might be an exchange or smart contract, whereas one using a single token could be a specific user wallet or contract.
	•	Activity Span: How long the address has been active. This could be measured as the difference between the first and last transaction height (or timestamp) involving the address. A wide span with continuous activity might indicate a long-term user or service; a narrow span could mean a one-off use.

Such static features provide a profile of overall behavior. For example, an address with a high outgoing count and large total sent volume might be an “exchanger” or “distributor”, whereas an address with very few transactions and small volumes might be a “casual user”. Aggregating raw data into these features is a crucial first step before clustering, as it condenses transaction history into comparable numeric descriptors ￼.

1.2 Time-Based Activity Trends (Temporal Features)

Beyond aggregates, temporal features capture when and how frequently an address transacts over time. Blockchain data is inherently timestamped (via block height or time), enabling analysis of activity patterns ￼. Key time-based features include:
	•	Transaction Frequency Over Time: This could be represented as the number of transactions per day/week/month. For example, we might compute a time series of monthly transaction counts for each address, or simply stats like active days count, average transactions per day, or gaps between transactions. An address with transactions every few minutes has a very different pattern from one that transacts once a month.
	•	Volume Over Time: Similar to frequency, but summing the amount per time window. This can highlight trends like increasing or decreasing transferred value. One could compute a moving average of daily volume or identify peak activity periods.
	•	Recency of Activity: How recently the address has been active (e.g., number of days since last transaction). “Inactive” addresses (no activity for a long period) versus currently active ones can be a useful distinction.
	•	Volatility/Burstiness: Metrics capturing variability in activity. For instance, the standard deviation of monthly transaction counts, or a burstiness score (periods of high activity followed by lulls). Some addresses might operate in bursts (e.g., a token sale address might suddenly handle thousands of transactions, then go quiet).
	•	Temporal Trends or Patterns: We can treat the sequence of transaction timestamps as a signal. Features could include the slope  

By including temporal features, we acknowledge that behavior can change over time. For instance, an address might have been very active last year but is dormant now – static aggregates alone wouldn’t show that, but time-based features would capture the decline. Temporal patterns have been used in research to improve identification of illicit versus normal addresses ￼ ￼. In one approach, an LSTM-based autoencoder was used to encode an address’s transaction time series into features, which significantly improved accuracy in detecting malicious addresses ￼. This underlines that two addresses with similar totals might still be different if one’s activity is steady and another’s is spiky – so capturing time dynamics is important.

1.3 Deep Learning Feature Representations (Embeddings)

In addition to manually crafted features, we can leverage deep learning to automatically learn latent representations of address behavior. These deep feature representations (embeddings) can encode complex patterns from the raw transaction history or the position of an address in the transaction network:
	•	Address Graph Embeddings: We can model the blockchain as a directed graph where nodes are addresses and edges are transactions. Using graph embedding techniques (e.g., Node2Vec, GraphSAGE, or Graph2Vec), each address is mapped to a vector in a latent space that captures network properties ￼. For example, addresses that transact with many of the same counterparties or play similar roles in the network may end up with similar embedding vectors. Prior work showed graph embeddings can be pivotal in tasks like detecting phishing addresses on Ethereum ￼. A concrete example is using a variational graph autoencoder (VGAE) on the address interaction graph to learn low-dimensional embeddings for each address ￼.
	•	Sequence/Temporal Embeddings: Treat each address’s transaction history (amounts, times, counterparties sequence) as a “sequence” and use sequence models to get an embedding. For instance, one could sort transactions by time for an address and feed features of each transaction (like [amount, direction]) into an LSTM or Transformer that outputs an address embedding. This embedding would encode the address’s behavioral pattern over time. As mentioned, LSTM-autoencoders have been used to capture hidden temporal features from transaction records ￼.
	•	Autoencoder on Feature Matrix: Instead of a sequence model, one can take the large set of handcrafted features (as in sections 1.1 and 1.2) and train a feed-forward autoencoder to compress these features into a smaller latent vector. The autoencoder’s encoded layer essentially learns a dense representation of the address such that it can (approximately) reconstruct the original features. This learned representation may capture nonlinear combinations of features. Using an autoencoder in this way can be especially helpful before clustering, as it reduces dimensionality and noise. It’s even possible to train the autoencoder with a clustering objective (as in Deep Embedded Clustering algorithms) to ensure the latent space is cluster-friendly.
	•	Contrastive Learning for Addresses: Contrastive learning is an emerging unsupervised approach where the model is trained to make representations of “similar” data points closer and “dissimilar” points farther apart. For addresses, one could devise augmentations of an address’s data (e.g., splitting its history into two random halves, or adding slight noise to transaction timings) and train the model to recognize both as the same address, whereas different addresses should be distinct. This way, the network learns an embedding where addresses with inherently similar transaction patterns end up near each other. While not yet commonplace in blockchain address analysis, contrastive approaches could discover subtle behavioral clusters without explicit labels.

Deep learned features can complement manual features. For instance, the unified approach by Jeyakumar et al. combined structural features (like the static ones above), network features, and embedding features to detect malicious entities, achieving higher accuracy than using any single category alone ￼ ￼. In unsupervised settings, using embeddings means we can cluster addresses in a vector space where meaningful patterns (perhaps not obvious from raw aggregates) are preserved. In summary, deep feature engineering provides powerful techniques to represent addresses by their context in the network or evolving behavior in addition to raw stats.

2. Clustering & Address Profiling

With a feature set for each address, we can apply clustering algorithms to group addresses by similarity in their feature profiles. The goal is to let patterns in the data naturally create groupings – revealing types of address behavior. We then interpret each cluster to create address profiles (e.g., “frequent small transactors”, “whales”, “inactive accounts”).

2.1 Behavioral Grouping of Addresses

By clustering on the features from section 1, addresses with similar transaction behavior will group together. For example:
	•	Frequent Transactors: Addresses that have a high number of transactions (especially outgoing) with relatively moderate amounts. These might be users who actively use the blockchain for many small payments or a service handling many microtransactions.
	•	Large-Value Movers (“Whales”): Addresses characterized by very high average and total transaction amounts, but perhaps fewer transactions. These could be exchange cold wallets or major investors moving large sums occasionally.
	•	Infrequent/Dormant Accounts: Addresses with very few transactions or that have long periods of inactivity. They might have one-off usage or be long-term holding wallets (e.g., someone who bought crypto and hardly ever moved it).
	•	High-Throughput Hubs: Addresses that both send and receive a large number of transactions, potentially with many unique counterparties. For instance, smart contracts like DeFi platforms or mixers, or exchange hot wallets, often interact with thousands of addresses. They might show up as clusters with extremely high in/out counts and diverse token usage.
	•	Predominantly Receivers vs. Predominantly Senders: Some addresses mostly only receive funds (and rarely send) – for example, an airdrop collector or a donation address. Others mostly send (like an distribution account or a known faucet). These differences can form separate clusters if the features capture the imbalance of in vs out.
	•	Token-Specific Users: If multiple token types exist, one cluster might group addresses that deal with a particular token heavily (e.g., an ERC-20 token contract users) versus those that stick to the native cryptocurrency.

These are just illustrative profiles – actual clusters will depend on the dataset distribution. Clustering has been used in practice to profile blockchain users. For instance, an unsupervised model was able to classify Ethereum addresses into investor profiles based on on-chain behavior ￼. Clustering thus helps turn raw data into understandable segments of users or entities, which can be invaluable for compliance (e.g., identifying clusters of potential illicit actors), marketing (segmenting users by activity), or research (understanding usage patterns).

2.2 Traditional Clustering Methods (K-Means, DBSCAN, etc.)

Traditional clustering algorithms can be directly applied to the engineered feature matrix:
	•	K-Means: A popular partitioning algorithm that aims to split data into K clusters by minimizing within-cluster variance. K-Means is straightforward and often used as a baseline. For blockchain addresses, we would choose a K (perhaps via elbow method or silhouette score) and run K-Means on the feature vectors. The result assigns each address to one of K clusters, defined by cluster centroids in feature space. K-Means assumes clusters are roughly spherical and of similar size. It will cluster every address (no noise/outlier concept). This can group the majority patterns well, though very atypical addresses (e.g., one extremely high-volume exchange) might form a tiny cluster or skew a centroid.
	•	DBSCAN (Density-Based Spatial Clustering of Applications with Noise): A clustering method that groups points that are closely packed and marks points in low-density regions as outliers. DBSCAN can identify clusters of arbitrary shape and can leave some points as “unclustered” noise. For address analysis, DBSCAN is useful to find natural groupings without forcing every address into a cluster. For example, if there are a few super-abnormal addresses, DBSCAN would label them as outliers rather than forcing them into a cluster. It requires setting a density radius (eps) and minimum points – which might need tuning given feature scales. One might use DBSCAN to isolate a cluster of extremely high-activity addresses or detect an outlier cluster of addresses exhibiting anomalous patterns.
	•	Hierarchical Clustering: Although less commonly mentioned in blockchain context, hierarchical methods (agglomerative clustering) can also be applied to address features. This can be useful to visualize a dendrogram of address similarities and decide an appropriate number of clusters by cutting the tree. For large datasets, however, hierarchical methods may be computationally expensive.

In practice, one might try multiple methods. For example, first use DBSCAN to see if there are clear dense groupings and outliers; then use K-Means for a fixed segmentation. The results from different methods can be compared for stability. If static and time features are high-dimensional, often a dimensionality reduction (PCA or t-SNE for visualization) is applied beforehand to ease clustering. The choice of method also depends on the data size – K-Means scales well to many addresses, whereas DBSCAN might struggle if the feature set is not reduced.

2.3 Deep Learning–Based Clustering Techniques (Embeddings & Autoencoders)

More advanced clustering can be done by leveraging the deep feature representations from section 1.3:
	•	Clustering on Embeddings: If we obtain an embedding vector for each address (via Node2Vec, GraphSAGE, etc.), we can then run a traditional clustering (K-Means, etc.) on these embeddings instead of raw features. The embeddings may capture higher-level similarities (e.g., two addresses that never interacted but have similar counterparties or temporal patterns might end up close in embedding space). This often reveals clusters aligned with roles in the network. For instance, research has shown that combining structural and embedding features improves distinguishing normal vs. illicit behavior ￼. Simply put, clustering in the embedding space groups addresses by learned patterns that are not obvious from basic stats alone.
	•	Autoencoder for Clustering (Deep Embedded Clustering): A special approach is to train a neural autoencoder jointly with clustering. One popular algorithm (DEC) trains an autoencoder to learn a latent space and simultaneously optimizes cluster assignments in that space. For our scenario, we could train an autoencoder on address feature vectors, then perform K-Means in the latent space (possibly iterating between refining the autoencoder and cluster assignments). The result is a set of clusters in a representation space optimized for clustering. This deep clustering approach can find structure that might be missed by clustering on raw features directly, especially if the relationships are nonlinear.
	•	Contrastive Learning Embeddings: As described, if we train a model to create address embeddings that maximize similarity for the same address’s different “views” and minimize it for different addresses, we end up with an embedding space where clustering should be meaningful. We could generate, say, two random subsamples of each address’s transactions as two views, train a contrastive loss (like SimCLR or triplet loss), and then cluster the resulting embeddings. While hypothetical in this context, the idea is that the model will learn to group addresses with inherently similar transaction distributions together in latent space. This technique could be powerful if we have no labels but suspect certain behavioral clusters exist – the model effectively creates its own representation to amplify those similarities.

Deep learning methods often require more effort (architecture design, training time, hyperparameters) but can yield improved clusters, especially for complex patterns. For example, using a variational graph autoencoder to embed addresses, followed by clustering, could cluster addresses by graph position (like hubs vs. peripheral users) ￼. Or an LSTM-based embedding might cluster addresses by activity patterns over time (e.g., consistently periodic vs. irregular bursty behavior). These methods may also handle high dimensional raw data better – the neural network learns which aspects of the data are important for grouping.

It’s important to evaluate if these advanced techniques actually produce more meaningful clusters than simpler feature-based clustering. Sometimes, if the engineered features are comprehensive, traditional clustering can do a fine job. In other cases, deep learning can reveal subtle groupings (for example, detecting a cluster of addresses that slowly increase activity over months versus ones that suddenly spike, which might look similar in overall totals but differ in temporal embedding).

2.4 Evaluating and Interpreting Clustering Results

After clustering, we need to evaluate the clusters and interpret them in terms of address behavior profiles:
	•	Internal Validation: Metrics like silhouette coefficient, Davies-Bouldin index, or Calinski-Harabasz score can quantify how well-separated the clusters are. A high silhouette score, for instance, means addresses are closer to their own cluster center than to others, indicating well-formed clusters. We might compute these to compare different clustering approaches or feature sets.
	•	Stability and Domain Plausibility: If possible, vary the number of clusters (K) or method and see if similar groupings persist. Clusters that are consistent are more likely to be meaningful. Also, validate against any known ground truth if available (e.g., if some addresses are known exchanges, do they fall into a distinct cluster?).
	•	Cluster Profiling: For each cluster, compute summary statistics of the original features to understand its characteristics. For example, we might find:
	•	Cluster A: avg. outgoing tx count = 500+, avg. tx value = 0.1, unique counterparties = 300 → likely an exchange hot wallet or DeFi contract (lots of small transactions with many users).
	•	Cluster B: avg. outgoing tx count = 5, avg. value = 50,000, unique counterparties = 2 → likely whales or cold storage (few, very large transactions, maybe moving funds to only a couple of other addresses).
	•	Cluster C: avg. incoming count = 100, outgoing count = 0 (or near 0) → collector addresses (receive many transactions, never send – perhaps airdrop or donation addresses).
	•	Cluster D: avg. tx per month ~20 consistently over 12 months, moderate values → steady users (regular individual users making monthly transactions, e.g., mining payouts or salary-like usage).
	•	Visualization: Although the prompt disallows plotting in the Python environment here, typically one would visualize clusters using 2D projections (t-SNE or PCA plots colored by cluster) to see how distinct they are and if any overlap or gradients exist. This can also highlight outliers.
	•	Deep Dive into Examples: Examine a few addresses from each cluster manually – check their raw transaction history. This can confirm the qualitative nature of the cluster (e.g., pick an address from Cluster B and indeed see one or two huge transactions, confirming the “whale” behavior hypothesis).

Interpreting clusters connects the unsupervised results back to real-world meaning. The end goal is to be able to describe each cluster in intuitive terms, and potentially give recommendations. For instance, if one cluster seems to contain potentially suspicious addresses (say they have unusual patterns or match known scam profiles), an analyst might flag that cluster for further investigation. Another cluster might represent new users (e.g., addresses with only one or two small incoming transactions and nothing else) – an exchange might treat those differently in marketing.

In summary, clustering results are evaluated by both quantitative metrics (to ensure the clusters are well-formed) and qualitative analysis (to label each cluster meaningfully). This dual evaluation confirms that the feature engineering and clustering approach yields sensible groupings and can guide decisions or further analysis.

3. Implementation: Feature Engineering and Clustering in Python

Below, we provide Python code snippets to demonstrate how one might implement the feature engineering and clustering process. We assume the transaction data is available as a Pandas DataFrame df with columns ['sender', 'recipient', 'amount', 'token', 'height', 'tx_hash']. (For example, this could be loaded from a JSON Lines file using pd.read_json('transfers_sample.jsonl', lines=True) if we had the file.)

Note: The code is illustrative and may need adaptation for a specific blockchain dataset. It avoids any plotting or external file writes, per the execution environment constraints.

3.1 Data Preparation and Static Feature Extraction

First, we’ll prepare the dataset and compute static features for each address. This involves aggregating transactions by address for both send and receive sides:

import pandas as pd
import numpy as np

# Load the dataset (here we assume df is already loaded as described)
# df = pd.read_json('transfers_sample.jsonl', lines=True)

# Ensure numeric type for amount and height (if not already)
df['amount'] = pd.to_numeric(df['amount'])
df['height'] = pd.to_numeric(df['height'])

# 1. Get all unique addresses appearing as sender or recipient
addresses = pd.unique(df[['sender', 'recipient']].values.ravel())

# Initialize a DataFrame for features, index by address
feature_df = pd.DataFrame(index=addresses)

# 2. Compute send-side aggregates
send_group = df.groupby('sender').agg(
    total_sent = ('amount', 'sum'),
    count_sent = ('tx_hash', 'count'),
    avg_sent   = ('amount', 'mean'),
    min_sent   = ('amount', 'min'),
    max_sent   = ('amount', 'max'),
    unique_recipients = ('recipient', pd.Series.nunique)
)
send_group.rename_axis('address', inplace=True)  # rename index to 'address'

# 3. Compute receive-side aggregates
recv_group = df.groupby('recipient').agg(
    total_received = ('amount', 'sum'),
    count_received = ('tx_hash', 'count'),
    avg_received   = ('amount', 'mean'),
    min_received   = ('amount', 'min'),
    max_received   = ('amount', 'max'),
    unique_senders = ('sender', pd.Series.nunique)
)
recv_group.rename_axis('address', inplace=True)

# 4. Merge send and receive features on address
feature_df = feature_df.join(send_group, on='address')
feature_df = feature_df.join(recv_group, on='address')

# Fill NaN (for addresses with no sends or no receives) with 0 for counts/totals and appropriate neutral for others
feature_df[['total_sent','count_sent','unique_recipients']] = feature_df[['total_sent','count_sent','unique_recipients']].fillna(0)
feature_df[['total_received','count_received','unique_senders']] = feature_df[['total_received','count_received','unique_senders']].fillna(0)
# For avg/min/max, NaN can be filled with 0 or some sentinel (if no transactions of that type, 0 might be acceptable here)
feature_df[['avg_sent','min_sent','max_sent']] = feature_df[['avg_sent','min_sent','max_sent']].fillna(0)
feature_df[['avg_received','min_received','max_received']] = feature_df[['avg_received','min_received','max_received']].fillna(0)

# 5. Compute derived features
feature_df['total_tx_count'] = feature_df['count_sent'] + feature_df['count_received']
feature_df['net_flow'] = feature_df['total_received'] - feature_df['total_sent']  # net gain/loss
feature_df['in_out_ratio'] = np.divide(feature_df['count_received'], feature_df['count_sent'] + 1e-9)

In this code: we group by sender to get sending stats and by recipient to get receiving stats, then merge. We also add a couple of derived metrics like total_tx_count, net_flow, and an in_out_ratio. The unique_recipients and unique_senders give the number of counterparties. We fill NaN values with 0 for addresses that never sent or never received. After this, feature_df contains the static features for each address. (If token diversity is a needed feature, we could similarly compute unique_tokens_sent/received via grouping by address and counting unique tokens.)

3.2 Time-Series Feature Extraction

Next, we add some time-based features. For simplicity, let’s derive a few features like activity span, average transactions per month, and last activity height. We can also create features for recent activity counts (e.g., number of transactions in the last N blocks).

# 6. Compute first and last seen heights for each address
first_last = df.groupby('sender')['height'].agg(first_seen='min', last_seen='max')
# Include also recipient side in case address only received and never sent
first_last_recv = df.groupby('recipient')['height'].agg(first_seen_recv='min', last_seen_recv='max')
first_last = first_last.join(first_last_recv, how='outer')  # combine sender and recipient timelines
first_last = first_last.fillna({'first_seen': first_last['first_seen_recv'],
                                'last_seen': first_last['last_seen_recv']})
# Fill any remaining NaN with same column values (addresses that only sent or only received)
first_last['first_seen'] = first_last[['first_seen','first_seen_recv']].min(axis=1)
first_last['last_seen'] = first_last[['last_seen','last_seen_recv']].max(axis=1)
first_last = first_last[['first_seen','last_seen']]
first_last.rename_axis('address', inplace=True)

# Join with feature_df
feature_df = feature_df.join(first_last, on='address')

# 7. Activity span (duration between first and last tx)
feature_df['activity_span'] = feature_df['last_seen'] - feature_df['first_seen']

# 8. Transactions per month (approximate if block height correlates with time, else would use timestamps)
# For illustration, assume 1 month ~ fixed number of blocks or derive from block heights.
blocks_per_month = 43200  # example: if ~30 days * 1440 blocks/day (just an estimate for demo)
feature_df['tx_per_month'] = feature_df['total_tx_count'] / ((feature_df['activity_span'] / blocks_per_month).replace(0, 1))

# 9. Recency of activity: how many blocks since last activity (assuming current height known, say max_height)
max_height = df['height'].max()
feature_df['blocks_since_last_tx'] = max_height - feature_df['last_seen']

Here, we determine the first and last block height each address was seen as sender or recipient (merging both roles to not miss addresses who only received or only sent). Then activity_span is last_seen minus first_seen (the number of blocks over which the address was active). We estimate tx_per_month using a rough blocks-per-month constant – in a real setting, if timestamps were available, we’d convert the timestamps to actual months and count or use the exact difference in days. We also compute blocks_since_last_tx as a recency measure (addresses with large values here have been inactive for a long time).

We could extend this further: for example, create features for the number of transactions in the last 10,000 blocks or a binary feature for “active_in_last_month”. We could also produce a vector of counts over fixed time bins (which might then be fed into a model or reduced). For brevity, we stick to a few summary temporal features.

3.3 Deep Feature Extraction (Embeddings)

Deep features often require more complex pipelines or external libraries. Here we outline two approaches with code/comments: (a) using Node2Vec for graph embeddings, (b) using an autoencoder for learned feature compression.

(a) Node2Vec Graph Embedding: We treat addresses as nodes in a graph. We’ll construct an edge list of transactions (perhaps weighted by count or volume) and then use Node2Vec to get embeddings. We assume we have networkx and a Node2Vec implementation available (for example, from stellargraph or node2vec package). If not, this section would be pseudo-code or conceptual.

# 10. Construct address graph for Node2Vec (edges from sender to recipient)
import networkx as nx
G = nx.DiGraph()
# Add edges with weight = number of transactions or total volume between addresses
# We can iterate through aggregated pairs:
edge_weights = df.groupby(['sender','recipient']).size()  # count of transactions from sender->recipient
for (u, v), w in edge_weights.items():
    G.add_edge(u, v, weight=w)

# 11. Apply Node2Vec to learn embeddings
from node2vec import Node2Vec
node2vec = Node2Vec(G, dimensions=16, workers=1)  # 16-dim embeddings
model = node2vec.fit(window=5, min_count=1, batch_words=10000)
# Get embedding vectors for each address node
embeddings = model.wv  # word2vec keyed vectors
# Create a DataFrame of embeddings for each address
emb_df = pd.DataFrame([embeddings[address] for address in addresses], index=addresses)
emb_df.columns = [f'embedding_{i}' for i in range(emb_df.shape[1])]
# Join embedding features to feature_df
feature_df = feature_df.join(emb_df, on='address')

In this snippet, we build a directed graph G where each address is a node and there’s an edge from sender to recipient with weight equal to the number of transactions (one could use total amount as weight or even make it an unweighted graph). Then we run Node2Vec to obtain a 16-dimensional embedding for each node. The resulting emb_df is joined with feature_df, adding columns embedding_0, embedding_1, ..., embedding_15 for each address. These embeddings encode the network context of each address (addresses that occur in similar graph neighborhoods will have similar vectors).

(b) Autoencoder for Feature Compression: We can use an autoencoder to compress the (possibly high-dimensional) feature space into a lower dimension that might be more suitable for clustering.

from tensorflow.keras import models, layers

# 12. Prepare data for autoencoder (fill any remaining NaNs with 0 and standardize features)
X = feature_df.fillna(0).values.astype('float32')
# It might help to normalize or standardize X here for better training

# Define autoencoder architecture
input_dim = X.shape[1]
encoding_dim = 8  # target compressed dimension
input_layer = layers.Input(shape=(input_dim,))
# Encoder
encoded = layers.Dense(32, activation='relu')(input_layer)
encoded = layers.Dense(encoding_dim, activation='relu')(encoded)
# Decoder
decoded = layers.Dense(32, activation='relu')(encoded)
decoded = layers.Dense(input_dim, activation='linear')(decoded)  # linear output to reconstruct raw features
autoencoder = models.Model(input_layer, decoded)
encoder_model = models.Model(input_layer, encoded)  # model to get encoded representations

autoencoder.compile(optimizer='adam', loss='mse')
# Train autoencoder (using X as both input and target since unsupervised)
autoencoder.fit(X, X, epochs=50, batch_size=256, verbose=0)

# 13. Get encoded feature representations for each address
X_compressed = encoder_model.predict(X)
compressed_df = pd.DataFrame(X_compressed, index=feature_df.index, 
                              columns=[f'ae_feat_{i}' for i in range(encoding_dim)])

Here we built a simple autoencoder with an input layer equal to the number of features, an encoding bottleneck of size 8, and symmetric decoder layers. After training on the data itself (attempting to reconstruct the input), we use the encoder part to get an 8-dimensional vector (ae_feat_0 … ae_feat_7) for each address. This is a learned feature compression where the neural network has presumably captured the most salient variations in the data. We could then use these 8-dim features for clustering instead of (or in addition to) the raw features.

(If using PyTorch or another framework is preferred, the concept remains: train an autoencoder to minimize reconstruction error, then take the latent vector.)

3.4 Clustering the Addresses

Now that we have a feature matrix (feature_df, possibly augmented with embeddings or compressed features), we can perform clustering. We’ll demonstrate using K-Means and DBSCAN from scikit-learn:

from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler

# 14. Select features for clustering.
# We might use a subset of feature_df or the autoencoder features.
# For demonstration, let's use a mix of key static features and the learned embedding:
features_for_clustering = ['count_sent', 'count_received', 'total_sent', 'total_received', 
                            'unique_recipients', 'unique_senders', 'activity_span', 'tx_per_month', 
                            'blocks_since_last_tx'] 
# Include autoencoder compressed features if available
if 'ae_feat_0' in feature_df.columns:
    features_for_clustering += [col for col in feature_df.columns if col.startswith('ae_feat_')]

X_cluster = feature_df[features_for_clustering].fillna(0).values
X_cluster = StandardScaler().fit_transform(X_cluster)  # normalize for clustering

# 15. K-Means clustering
k = 5  # assume we want 5 clusters for illustration
kmeans = KMeans(n_clusters=k, random_state=42)
labels_km = kmeans.fit_predict(X_cluster)

# 16. DBSCAN clustering
dbscan = DBSCAN(eps=1.5, min_samples=5)  # eps and min_samples need tuning; values depend on feature scale
labels_db = dbscan.fit_predict(X_cluster)
# Note: DBSCAN label -1 indicates noise/outlier points not in any cluster

We choose a set of features for clustering. In this example, we include some raw counts and totals, unique counterparties, and a few temporal features. If the autoencoder features were computed, we append those, as they condense complex info. We then scale the features (important for clustering so that no single feature dominates due to scale differences, e.g., total_sent might be very large compared to count_sent).

For K-Means, we arbitrarily set k=5 (in practice, one would determine k by testing). The result labels_km is an array assigning each address a cluster ID 0–4. For DBSCAN, we set eps and min_samples (these would need experimentation). labels_db gives cluster IDs where -1 means an address was marked as noise (did not fit into a dense cluster).

3.5 Evaluating and Profiling Clusters

Finally, we evaluate how meaningful the clusters are. We can compute some metrics and also summarize cluster properties:

from sklearn.metrics import silhouette_score

# 17. Evaluate clustering (K-Means) with silhouette score
sil_score = silhouette_score(X_cluster, labels_km)
print(f"Silhouette Score for K-Means clustering: {sil_score:.3f}")

# 18. Analyze cluster centers for K-Means
cluster_centers = pd.DataFrame(kmeans.cluster_centers_, columns=features_for_clustering)
print("K-Means Cluster Centers (in scaled feature space):\n", cluster_centers)

# 19. Profile clusters by original feature means
feature_df['kmeans_label'] = labels_km
cluster_profile = feature_df.groupby('kmeans_label')[['count_sent','count_received','total_sent','total_received',
                                                     'unique_recipients','unique_senders','tx_per_month']].mean()
print("Cluster profile (mean of features):\n", cluster_profile)

# 20. If DBSCAN is used, identify how many clusters and noise points
n_clusters = len(set(labels_db) - {-1})
n_noise = sum(labels_db == -1)
print(f"DBSCAN found {n_clusters} clusters and {n_noise} noise points")

We calculate the silhouette score for the K-Means clustering as a quick internal validation (score ranges from -1 to 1, with higher positive values indicating well-separated clusters). We then look at the cluster centers in the scaled feature space and also compute the mean of key original features per cluster to interpret them.

For example, the cluster_profile might output something like:

            count_sent  count_received  total_sent   total_received  ... tx_per_month
kmeans_label                                                                         
0                   2               50       0.5          100.0     ...    0.1  
1                 500              480      3000.0        3100.0    ...   20.0  
2                  50               0      500.0           0.0      ...    5.0  
...

From such a table, we could interpret cluster 0 as addresses that mostly receive (50 incoming vs 2 outgoing on average) small amounts – perhaps collector or holder addresses. Cluster 1 might have hundreds of transactions both in and out with large totals – possibly high-volume traders or service addresses. Cluster 2 has moderate outgoing count with no incoming – maybe one-directional senders (like an output-only address). This is a hypothetical interpretation; actual values depend on real data.

For DBSCAN, we report how many clusters it found and how many addresses were labeled noise. If DBSCAN finds, say, 1 cluster and thousands of noise points, it might mean our eps was too small or that there aren’t obvious dense groupings except perhaps one. If it finds multiple clusters, we could similarly analyze them by labeling each address and looking at means.

3.6 Recommendations and Further Steps

The above process yields clusters of addresses with similar behavior. To ensure these clusters are useful:
	•	We should iterate on feature engineering: maybe certain features are redundant or noisy. Feature selection or principal component analysis could be applied to refine the feature set.
	•	Try different numbers of clusters (for K-Means) or parameters (for DBSCAN) and see which yields the most meaningful grouping. Domain insight is useful here – e.g., if one cluster is mixing two distinct types of addresses, increasing K might separate them.
	•	Leverage known labels if available to guide or evaluate clusters. For instance, if we know a set of addresses are exchanges, do they end up together? If not, perhaps we need additional features (like token diversity or time-of-day patterns) to distinguish them.
	•	For deep learning approaches, ensure not to overfit. Techniques like autoencoders should be trained carefully (and possibly validated by reconstruction error distribution).
	•	Finally, keep interpretability in mind: complex features and deep embeddings are powerful, but the end user (analyst or system) needs to understand cluster traits. Using explainability techniques on cluster definitions (like which features most differentiate one cluster from others) can be helpful.

In conclusion, combining static features (e.g., counts, volumes ￼) and temporal features capturing activity patterns ￼ provides a comprehensive behavioral profile for each blockchain address. Clustering these profiles, whether with classic algorithms like K-Means/DBSCAN or advanced embedding-based methods, allows us to identify natural groupings of addresses. These clusters can reveal user roles and anomalous entities in the blockchain ecosystem ￼. By iterating on feature engineering (potentially incorporating deep learning for representation) and validating the clusters, we can derive actionable insights — such as flagging outliers for investigation or tailoring services to different user types — from what initially is just raw transaction log data.