import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import pandas as pd
import seaborn as sns
import plotly.express as px
from sklearn.metrics import silhouette_samples
import matplotlib.cm as cm
from sklearn.neighbors import NearestNeighbors
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.utils import resample
import time
import warnings

def create_pca_scree_plot(df, variance_thresholds=[0.7, 0.8, 0.9, 0.95, 0.99], 
                          figsize=(12, 8), bar_color='steelblue', line_color='tomato',
                          threshold_colors=None, show_plot=True):
    """
    Creates a PCA Scree plot with dual y-axes showing individual and cumulative explained variance.
    Prints components needed to reach variance thresholds.
    
    Parameters:
    -----------
    df : DataFrame or array-like
        The input data for PCA (features should be scaled already)
    variance_thresholds : list, default=[0.7, 0.8, 0.9, 0.95, 0.99]
        List of variance thresholds to mark on the plot
    figsize : tuple, default=(12, 8)
        Figure size for the scree plot
    bar_color : str, default='steelblue'
        Color for the explained variance bars
    line_color : str, default='tomato'
        Color for the cumulative variance line
    threshold_colors : list, default=None
        List of colors for threshold lines
    show_plot : bool, default=True
        Whether to display the plot immediately
        
    Returns:
    --------
    dict : Contains PCA object, variance data, and plot figure
    """
    # Apply PCA
    pca = PCA(n_components=min(df.shape))
    pca.fit(df)
    
    # Calculate variances
    explained_variance = pca.explained_variance_ratio_
    cumulative_variance = np.cumsum(explained_variance)
    
    # Calculate components needed for thresholds
    components_needed = {
        thresh: np.argmax(cumulative_variance >= thresh) + 1
        for thresh in variance_thresholds
    }
    
    # Print components needed
    print("Components needed for variance thresholds:")
    for thresh, n in components_needed.items():
        print(f"- {thresh*100:.0f}% variance: {n} components")
    
    # Setup plot
    fig, ax1 = plt.subplots(figsize=figsize)
    
    # Variance bars
    ax1.bar(range(1, len(explained_variance)+1), explained_variance, 
            color=bar_color, alpha=0.7)
    ax1.set_xlabel('Principal Components')
    ax1.set_ylabel('Explained Variance', color=bar_color)
    ax1.tick_params(axis='y', labelcolor=bar_color)
    
    # Cumulative line
    ax2 = ax1.twinx()
    ax2.plot(range(1, len(cumulative_variance)+1), cumulative_variance, 
             color=line_color, marker='o', linewidth=2)
    ax2.set_ylabel('Cumulative Variance', color=line_color)
    ax2.tick_params(axis='y', labelcolor=line_color)
    
    # Threshold markers
    threshold_colors = threshold_colors or ['red', 'green', 'purple', 'orange', 'brown']
    for i, threshold in enumerate(variance_thresholds):
        color = threshold_colors[i % len(threshold_colors)]
        ax2.axhline(threshold, color=color, linestyle='--', alpha=0.5)
        ax2.text(ax1.get_xlim()[1]*0.7, threshold+0.01, f'{threshold*100}%', color=color)
        
    plt.title('PCA Scree Plot: Explained Variance')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if show_plot:
        plt.show()
        
    return {
        'pca': pca,
        'components_needed': components_needed,
        'explained_variance': explained_variance,
        'cumulative_variance': cumulative_variance,
        'fig': fig
    }

def create_pca_plot(df, dimensions=2, title='PCA Visualization', 
                   color_scale='viridis', marker_size=5,
                   height=600, width=600, labels=None):
    """
    Creates interactive 2D or 3D PCA visualization using Plotly.
    
    Parameters:
    -----------
    df : DataFrame or array-like
        The input data (features should be scaled already)
    dimensions : int, default=2
        Dimensionality of the visualization (2 or 3)
    title : str, default='PCA Visualization'
        Title for the plot
    color_scale : str, default='viridis'
        Plotly color scale name
    marker_size : int, default=5
        Size of the markers in the plot
    height : int, default=600
        Plot height in pixels
    width : int, default=800
        Plot width in pixels
    labels : array-like, optional
        Labels for coloring points (default: index-based coloring)
        
    Returns:
    --------
    plotly.graph_objs._figure.Figure: Interactive Plotly figure
    """
    # Validate dimensions
    if dimensions not in [2, 3]:
        raise ValueError("Dimensions must be 2 or 3")

    # Perform PCA
    pca = PCA(n_components=dimensions)
    pca_components = pca.fit_transform(df)
    
    # Create DataFrame for plotting
    plot_df = pd.DataFrame(
        pca_components,
        columns=[f'PC{i+1} ({var:.1%})' 
                for i, var in enumerate(pca.explained_variance_ratio_)]
    )
    
    # Create color labels
    color_labels = labels if labels is not None else np.arange(len(df))
    
    # Create base figure
    if dimensions == 2:
        fig = px.scatter(
            plot_df,
            x=plot_df.columns[0],
            y=plot_df.columns[1],
            color=color_labels,
            color_continuous_scale=color_scale,
            title=title,
            labels={'color': 'Label'},
            height=height,
            width=width
        )
    else:
        fig = px.scatter_3d(
            plot_df,
            x=plot_df.columns[0],
            y=plot_df.columns[1],
            z=plot_df.columns[2],
            color=color_labels,
            color_continuous_scale=color_scale,
            title=title,
            labels={'color': 'Label'},
            height=height,
            width=width
        )
    
    # Update marker settings
    fig.update_traces(
        marker=dict(
            size=marker_size,
            opacity=0.7,
            line=dict(width=0)
        )
    )
    
    # Update layout
    layout_config = {
        'margin': dict(l=0, r=0, b=0, t=30),
        'title': title
    }
    
    if dimensions == 2:
        layout_config.update({
            'xaxis_title': plot_df.columns[0],
            'yaxis_title': plot_df.columns[1]
        })
    else:
        layout_config['scene'] = {
            'xaxis_title': plot_df.columns[0],
            'yaxis_title': plot_df.columns[1],
            'zaxis_title': plot_df.columns[2]
        }
    
    fig.update_layout(layout_config)
        
    return fig

def create_pca_2d_plot(df, **kwargs):
    """
    Creates an interactive 2D PCA visualization (wrapper for create_pca_plot).
    Accepts all parameters from create_pca_plot except dimensions.
    """
    return create_pca_plot(df, dimensions=2, **kwargs)

def create_pca_3d_plot(df, **kwargs):
    """
    Creates an interactive 3D PCA visualization (wrapper for create_pca_plot).
    Accepts all parameters from create_pca_plot except dimensions.
    """
    return create_pca_plot(df, dimensions=3, **kwargs)

def plot_kmeans_elbow(K_values, inertias, silhouette_scores=None, 
                     figsize=(10, 6), elbow_color='steelblue', 
                     silhouette_color='purple', title_suffix='', show_grid=True):
    """
    Plots K-means Elbow method with optional Silhouette scores.
    
    Parameters:
    -----------
    K_values : list
        Range of K values tested
    inertias : list
        Inertia values for each K
    silhouette_scores : list, optional
        Silhouette scores for each K (if provided, will be plotted on secondary y-axis)
    figsize : tuple, default=(10, 6)
        Figure size
    elbow_color : str, default='steelblue'
        Color for the elbow curve
    silhouette_color : str, default='purple'
        Color for the silhouette curve
    title_suffix : str, default=''
        Additional text to append to titles
    show_grid : bool, default=True
        Whether to show grid lines
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        The generated figure
    """
    fig, ax1 = plt.subplots(figsize=figsize)
    
    # Elbow curve
    ax1.plot(K_values, inertias, 'o-', color=elbow_color, linewidth=2)
    ax1.set_xlabel('Number of clusters (K)')
    ax1.set_ylabel('Inertia', color=elbow_color)
    ax1.tick_params(axis='y', labelcolor=elbow_color)
    
    if silhouette_scores is not None:
        ax2 = ax1.twinx()
        ax2.plot(K_values, silhouette_scores, 'o-', color=silhouette_color, linewidth=2)
        ax2.set_ylabel('Silhouette Score', color=silhouette_color)
        ax2.tick_params(axis='y', labelcolor=silhouette_color)
        title = f'K-means Elbow Method and Silhouette Analysis {title_suffix}'.strip()
    else:
        title = f'K-means Elbow Method {title_suffix}'.strip()
    
    plt.title(title)
    if show_grid:
        ax1.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def plot_silhouette_analysis(X, cluster_labels, silhouette_scores,
                             plots_per_row=4, figsize_base=(20, 5),
                             title_suffix=''):
    """
    Creates a grid of silhouette analysis plots for different K values.
    
    Parameters:
    -----------
    X : array-like
        The input data used for clustering
    cluster_labels : dict
        Dictionary mapping K values to cluster labels array
    silhouette_scores : list
        Average silhouette scores for each K
    plots_per_row : int, default=4
        Number of silhouette plots to display per row
    figsize_base : tuple, default=(20, 5)
        Base figure size per row (width, height)
    title_suffix : str, default=''
        Additional text to append to the main title
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        The generated figure
    """
    K_values = list(cluster_labels.keys())
    n_clusters = len(K_values)
    
    # Calculate grid dimensions
    n_rows = (n_clusters + 1) // plots_per_row + ((n_clusters + 1) % plots_per_row > 0)
    n_cols = min(plots_per_row, n_clusters)
    
    # Adjust figure height based on number of rows
    figsize = (figsize_base[0], figsize_base[1] * n_rows)
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    if n_rows == 1 and n_cols == 1:  # Handle case with only one plot
        axes = np.array([axes])
    axes = axes.flatten() if n_rows * n_cols > 1 else [axes]
    
    plt.suptitle(f'Silhouette Analysis for K-means Clustering {title_suffix}'.strip(), 
                fontsize=16, y=0.98)
    
    # Create silhouette plots for each K
    for idx, k in enumerate(K_values):
        ax = axes[idx]
        
        # Get silhouette values
        cluster_labels_k = cluster_labels[k]
        silhouette_avg = silhouette_scores[idx]
        sample_silhouette_values = silhouette_samples(X, cluster_labels_k)
        
        # Plot silhouette
        y_lower = 10
        for i in range(k):
            ith_cluster_values = sample_silhouette_values[cluster_labels_k == i]
            ith_cluster_values.sort()
            size_cluster_i = ith_cluster_values.shape[0]
            y_upper = y_lower + size_cluster_i
            
            color = cm.nipy_spectral(float(i) / k)
            ax.fill_betweenx(np.arange(y_lower, y_upper), 0, ith_cluster_values,
                             facecolor=color, edgecolor=color, alpha=0.7)
            
            # Label cluster number
            ax.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))
            y_lower = y_upper + 10
        
        # Plot average silhouette score line
        ax.axvline(x=silhouette_avg, color="red", linestyle="--")
        
        # Set plot aesthetics
        ax.set_title(f"K={k}, Avg Silhouette={silhouette_avg:.3f}")
        ax.set_xlabel("Silhouette Coefficient")
        ax.set_ylabel("Cluster")
        ax.set_yticks([])  # Hide y-axis ticks
        ax.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])
        ax.set_xlim([-0.1, 1])
    
    # Hide any unused subplots
    for idx in range(len(K_values), len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout(rect=[0, 0, 1, 0.97])  # Adjust for the suptitle
    return fig

def plot_kmeans_pca_projections(X, cluster_labels, plots_per_row=4, 
                              figsize_base=(20, 5), title_suffix=''):
    """
    Creates a grid of PCA projections for clusters at different K values.
    
    Parameters:
    -----------
    X : array-like
        The input data used for clustering
    cluster_labels : dict
        Dictionary mapping K values to cluster labels array
    plots_per_row : int, default=4
        Number of PCA plots to display per row
    figsize_base : tuple, default=(20, 5)
        Base figure size per row (width, height)
    title_suffix : str, default=''
        Additional text to append to the main title
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        The generated figure
    """
    K_values = list(cluster_labels.keys())
    n_clusters = len(K_values)
    
    # Calculate grid dimensions
    n_rows = (n_clusters + 1) // plots_per_row + ((n_clusters + 1) % plots_per_row > 0)
    n_cols = min(plots_per_row, n_clusters)
    
    # Adjust figure height based on number of rows
    figsize = (figsize_base[0], figsize_base[1] * n_rows)
    
    # Perform PCA once
    pca = PCA(n_components=2).fit_transform(X)
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    if n_rows == 1 and n_cols == 1:  # Handle case with only one plot
        axes = np.array([axes])
    axes = axes.flatten() if n_rows * n_cols > 1 else [axes]
    
    plt.suptitle(f'PCA Projections of K-means Clusters {title_suffix}'.strip(), 
                fontsize=16, y=0.98)
    
    # Create PCA plots for each K
    for idx, k in enumerate(K_values):
        ax = axes[idx]
        
        # Get cluster labels
        cluster_labels_k = cluster_labels[k]
        
        # Create colors
        colors = cm.nipy_spectral(cluster_labels_k.astype(float) / k)
        
        # Plot PCA projection
        ax.scatter(pca[:, 0], pca[:, 1], marker='.', s=30, lw=0, alpha=0.7,
                  c=colors, edgecolor='k')
        
        # Set plot aesthetics
        ax.set_title(f"K={k}")
        ax.set_xlabel("Principal Component 1")
        ax.set_ylabel("Principal Component 2")
        ax.grid(True, alpha=0.3)
    
    # Hide any unused subplots
    for idx in range(len(K_values), len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout(rect=[0, 0, 1, 0.97])  # Adjust for the suptitle
    return fig

def visualize_clusters_2d_interactive(X_scaled, kmeans_labels, height=600, width=800, 
                                     random_state=42, title_suffix='', include_metrics=True,
                                     point_size=10, opacity=0.7, colorscale='Viridis',
                                     methods=None, max_samples=3000, perplexity=30,
                                     calculate_silhouette=True, calculate_ch=True, 
                                     calculate_db=True, use_parallel=True, 
                                     umap_neighbors=15, umap_min_dist=0.1):
    """
    Creates an interactive visualization of clusters using PCA, t-SNE, and UMAP projections.
    Optimized for performance with large datasets.
    
    Parameters:
    -----------
    X_scaled : array-like or DataFrame
        The input data, should be scaled and imputed
    kmeans_labels : array-like
        Cluster labels for each data point
    height : int, default=600
        Height of the plot in pixels
    width : int, default=800
        Width of the plot in pixels
    random_state : int, default=42
        Random state for reproducibility
    title_suffix : str, default=''
        Additional text to append to plot titles
    include_metrics : bool, default=True
        Whether to include cluster quality metrics in titles
    point_size : int, default=10
        Size of points in the scatter plot
    opacity : float, default=0.7
        Opacity of the points (0-1)
    colorscale : str, default='Viridis'
        Colorscale to use for the clusters (any valid Plotly colorscale)
    methods : list or None, default=None
        List of projection methods to use ['pca', 'tsne', 'umap']. 
        If None, uses all available methods.
    max_samples : int, default=3000
        Maximum number of samples to use for visualization. If dataset is larger,
        samples are randomly selected. Set to None to use all samples (can be slow).
    perplexity : int, default=30
        Perplexity parameter for t-SNE (lower values for smaller datasets)
    calculate_silhouette : bool, default=True
        Whether to calculate silhouette score (can be slow for large datasets)
    calculate_ch : bool, default=True
        Whether to calculate Calinski-Harabasz score
    calculate_db : bool, default=True
        Whether to calculate Davies-Bouldin score
    use_parallel : bool, default=True
        Whether to use parallel processing for t-SNE and UMAP
    umap_neighbors : int, default=15
        Number of neighbors for UMAP (lower values for more local structure)
    umap_min_dist : float, default=0.1
        Minimum distance for UMAP (lower values for tighter clusters)
        
    Returns:
    --------
    fig : plotly.graph_objects.Figure
        Interactive plotly figure with multiple tabs for different projections
    projections : dict
        Dictionary of projection coordinates
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import numpy as np
    import pandas as pd
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
    from sklearn.utils import resample
    import time
    import warnings
    
    # Start timer to provide feedback on processing time
    start_time = time.time()
    
    # Set default methods if not provided
    if methods is None:
        methods = ['pca', 'tsne', 'umap']
    else:
        methods = [m.lower() for m in methods]
    
    # Convert to numpy array if it's a DataFrame
    if isinstance(X_scaled, pd.DataFrame):
        feature_names = X_scaled.columns.tolist()
        original_data = X_scaled
        original_index = X_scaled.index
    else:
        original_data = X_scaled
        feature_names = [f"Feature {i+1}" for i in range(X_scaled.shape[1])]
        original_index = pd.RangeIndex(len(X_scaled))
    
    # Subsample data if necessary
    if max_samples is not None and len(original_data) > max_samples:
        print(f"Dataset has {len(original_data)} samples. Subsampling to {max_samples} for visualization...")
        
        # Stratified sampling to maintain cluster proportions
        X_array, kmeans_labels_array = resample(
            original_data, kmeans_labels, 
            n_samples=max_samples, 
            random_state=random_state, 
            stratify=kmeans_labels
        )
        
        if isinstance(original_data, pd.DataFrame):
            X_array = pd.DataFrame(X_array, columns=feature_names)
        
        # Create new index for the sampled data
        sampled_indices = np.random.choice(original_index, size=max_samples, replace=False)
    else:
        X_array = original_data
        kmeans_labels_array = kmeans_labels
        sampled_indices = original_index
    
    # Handle array conversion after potential sampling
    if isinstance(X_array, pd.DataFrame):
        X_values = X_array.values
    else:
        X_values = X_array
    
    # Calculate metrics if requested - with warning suppression for efficiency
    metrics_text = ""
    n_clusters = len(np.unique(kmeans_labels_array))
    
    if include_metrics and n_clusters > 1:
        metric_calculation_time = time.time()
        metrics_to_calculate = []
        
        if calculate_silhouette and len(X_values) <= 10000:
            metrics_to_calculate.append('silhouette')
        elif calculate_silhouette:
            print("Silhouette score calculation skipped for datasets > 10,000 points. Set calculate_silhouette=False to suppress this message.")
        
        if calculate_ch:
            metrics_to_calculate.append('ch')
        
        if calculate_db:
            metrics_to_calculate.append('db')
        
        metrics = {}
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            try:
                if 'silhouette' in metrics_to_calculate:
                    metrics['silhouette'] = silhouette_score(X_values, kmeans_labels_array)
                
                if 'ch' in metrics_to_calculate:
                    metrics['ch'] = calinski_harabasz_score(X_values, kmeans_labels_array)
                
                if 'db' in metrics_to_calculate:
                    metrics['db'] = davies_bouldin_score(X_values, kmeans_labels_array)
                
                metrics_parts = []
                if 'silhouette' in metrics:
                    metrics_parts.append(f"Silhouette: {metrics['silhouette']:.3f}")
                if 'ch' in metrics:
                    metrics_parts.append(f"CH: {metrics['ch']:.1f}")
                if 'db' in metrics:
                    metrics_parts.append(f"DB: {metrics['db']:.3f}")
                
                if metrics_parts:
                    metrics_text = "<br>" + " | ".join(metrics_parts)
                
                print(f"Metrics calculated in {time.time() - metric_calculation_time:.2f} seconds")
            
            except Exception as e:
                print(f"Warning: Could not calculate some metrics: {e}")
    
    # Create the projections
    projections = {}
    titles = []
    all_methods = []
    
    # Create figure
    fig = go.Figure()
    
    # Helper function to add a trace for a projection
    def add_scatter_trace(projection, name, var_explained=None):
        hover_text = [
            f"ID: {idx}<br>Cluster: {label}" 
            for idx, label in zip(sampled_indices, kmeans_labels_array)
        ]
        
        title = f"{name} Projection - {n_clusters} Clusters"
        if var_explained is not None:
            title += f" (var: {var_explained[0]:.2f}, {var_explained[1]:.2f})"
        title += metrics_text
        if title_suffix:
            title += f"<br>{title_suffix}"
        
        # Create a discrete colorscale with equal spacing between clusters
        discrete_colors = px.colors.qualitative.G10[:n_clusters] if n_clusters <= 10 else px.colors.qualitative.Alphabet[:n_clusters]
        if n_clusters > len(discrete_colors):
            # Fall back to generating more colors if we have many clusters
            import matplotlib.cm as cm
            import matplotlib.colors as mcolors
            cmap = cm.get_cmap(colorscale, n_clusters)
            discrete_colors = [mcolors.rgb2hex(cmap(i)) for i in range(n_clusters)]
        
        # Create a custom discrete colorscale where each cluster has its own distinct color
        discrete_colorscale = []
        for i in range(n_clusters):
            # Append the color at the start and end of each cluster's range
            # This creates a step function effect instead of a gradient
            discrete_colorscale.append([i/n_clusters, discrete_colors[i]])
            discrete_colorscale.append([(i+1)/n_clusters, discrete_colors[i]])
        
        fig.add_trace(
            go.Scatter(
                x=projection[:, 0],
                y=projection[:, 1],
                mode='markers',
                marker=dict(
                    size=point_size,
                    color=kmeans_labels_array,
                    colorscale=discrete_colorscale,
                    opacity=opacity,
                    showscale=True,
                    colorbar=dict(
                        title='Cluster',
                        titleside='right',
                        titlefont=dict(size=14),
                        tickvals=list(range(n_clusters)),
                        ticktext=list(range(n_clusters))
                    )
                ),
                text=hover_text,
                hoverinfo='text',
                name=name,
                visible=(name == all_methods[0] if all_methods else True)  # First method is visible initially
            )
        )
        return title
    
    # PCA projection (fastest, so do it first)
    if 'pca' in methods:
        pca_time = time.time()
        pca = PCA(n_components=2, random_state=random_state)
        pca_result = pca.fit_transform(X_values)
        projections['pca'] = pca_result
        pca_var = pca.explained_variance_ratio_
        all_methods.append('PCA')
        print(f"PCA completed in {time.time() - pca_time:.2f} seconds")
    
    # t-SNE projection (slower)
    if 'tsne' in methods:
        tsne_time = time.time()
        n_jobs = -1 if use_parallel else 1
        perplexity_value = min(perplexity, len(X_values) - 1)
        
        print(f"Running t-SNE with perplexity={perplexity_value}, n_jobs={n_jobs}...")
        try:
            tsne = TSNE(
                n_components=2, 
                random_state=random_state, 
                perplexity=perplexity_value,
                n_jobs=n_jobs,
                n_iter=1000
            )
            tsne_result = tsne.fit_transform(X_values)
            projections['tsne'] = tsne_result
            all_methods.append('t-SNE')
            print(f"t-SNE completed in {time.time() - tsne_time:.2f} seconds")
        except Exception as e:
            print(f"t-SNE failed: {e}. Try reducing dataset size or perplexity.")
    
    # UMAP projection (if available and requested)
    has_umap = False
    if 'umap' in methods:
        umap_time = time.time()
        try:
            import umap.umap_ as umap
            n_jobs = -1 if use_parallel else 1
            
            print(f"Running UMAP with n_neighbors={umap_neighbors}, min_dist={umap_min_dist}...")
            umap_model = umap.UMAP(
                n_components=2,
                random_state=random_state,
                n_neighbors=umap_neighbors,
                min_dist=umap_min_dist,
                n_jobs=n_jobs
            )
            umap_result = umap_model.fit_transform(X_values)
            projections['umap'] = umap_result
            has_umap = True
            all_methods.append('UMAP')
            print(f"UMAP completed in {time.time() - umap_time:.2f} seconds")
        except ImportError:
            print("UMAP not installed. To use UMAP, run: pip install umap-learn")
        except Exception as e:
            print(f"UMAP failed: {e}")
    
    # Add traces for each projection method
    if 'pca' in methods:
        titles.append(add_scatter_trace(pca_result, 'PCA', pca_var))
    if 'tsne' in methods and 't-SNE' in all_methods:
        titles.append(add_scatter_trace(tsne_result, 't-SNE'))
    if 'umap' in methods and has_umap:
        titles.append(add_scatter_trace(umap_result, 'UMAP'))
    
    # Create buttons for tab selection
    buttons = []
    
    # Create a button for each method
    for i, method in enumerate(all_methods):
        visibility = [i == j for j in range(len(all_methods))]
        buttons.append(
            dict(
                label=method,
                method="update",
                args=[
                    {"visible": visibility},
                    {"title": titles[i]}
                ]
            )
        )
    
    # Update layout
    fig.update_layout(
        updatemenus=[
            dict(
                active=0,
                buttons=buttons,
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.15,
                yanchor="top"
            ),
        ],
        height=height,
        width=width,
        title=dict(
            text=titles[0] if titles else f"Cluster Visualization - {n_clusters} Clusters {metrics_text}",
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(
            title="Dimension 1",
            gridcolor='rgba(200, 200, 200, 0.2)',
            showgrid=True
        ),
        yaxis=dict(
            title="Dimension 2",
            gridcolor='rgba(200, 200, 200, 0.2)',
            showgrid=True
        ),
        hovermode='closest',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    print(f"Total visualization time: {time.time() - start_time:.2f} seconds")
    
    # Return the figure and projections
    return fig, projections

def determine_optimal_k(X, k_range=(2, 15), methods=None, figsize=(15, 10), random_state=42):
    """
    Determine the optimal number of clusters for K-means using multiple methods.
    
    Parameters:
    -----------
    X : array-like
        The input data for clustering
    k_range : tuple, default=(2, 15)
        Range of k values to test (min, max)
    methods : list, default=None
        Methods to use for determining optimal k. Options:
        ['elbow', 'silhouette', 'calinski_harabasz', 'gap', 'bic']
        If None, uses ['elbow', 'silhouette', 'calinski_harabasz']
    figsize : tuple, default=(15, 10)
        Figure size for the plots
    random_state : int, default=42
        Random seed for KMeans
        
    Returns:
    --------
    optimal_k : int
        The suggested optimal number of clusters
    fig : matplotlib.figure.Figure
        The figure object containing the plots
    """
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score, calinski_harabasz_score
    import numpy as np
    import matplotlib.pyplot as plt
    
    if methods is None:
        methods = ['elbow', 'silhouette', 'calinski_harabasz']
    
    k_values = range(k_range[0], k_range[1] + 1)
    
    # Initialize storage for metrics
    inertias = []
    silhouette_scores = []
    calinski_scores = []
    
    # Calculate metrics for each k
    for k in k_values:
        # Fit KMeans
        kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        kmeans.fit(X)
        
        # Inertia (within-cluster sum of squares)
        inertias.append(kmeans.inertia_)
        
        # Only calculate silhouette for k >= 2
        if k >= 2:
            labels = kmeans.labels_
            silhouette_scores.append(silhouette_score(X, labels))
            calinski_scores.append(calinski_harabasz_score(X, labels))
        else:
            silhouette_scores.append(0)
            calinski_scores.append(0)
    
    # Create plots
    fig, axes = plt.subplots(len(methods), 1, figsize=figsize)
    if len(methods) == 1:
        axes = [axes]
    
    plot_idx = 0
    
    # Plot Elbow Method
    if 'elbow' in methods:
        ax = axes[plot_idx]
        ax.plot(k_values, inertias, 'bo-')
        ax.set_xlabel('Number of clusters (k)')
        ax.set_ylabel('Inertia')
        ax.set_title('Elbow Method')
        ax.grid(True)
        
        # Calculate elbow point using the maximum curvature
        curve = np.diff(np.diff(inertias))
        elbow_k = k_values[np.argmax(curve) + 1]
        ax.axvline(x=elbow_k, color='r', linestyle='--', 
                  label=f'Elbow point: k={elbow_k}')
        ax.legend()
        plot_idx += 1
    
    # Plot Silhouette Score
    if 'silhouette' in methods:
        ax = axes[plot_idx]
        ax.plot(k_values[1:], silhouette_scores[1:], 'go-')  # Start from k=2
        ax.set_xlabel('Number of clusters (k)')
        ax.set_ylabel('Silhouette Score')
        ax.set_title('Silhouette Method')
        ax.grid(True)
        
        # Find the k with maximum silhouette score
        sil_scores = np.array(silhouette_scores[1:])
        max_silhouette_k = k_values[1:][np.argmax(sil_scores)]
        ax.axvline(x=max_silhouette_k, color='r', linestyle='--', 
                  label=f'Max Silhouette: k={max_silhouette_k}')
        ax.legend()
        plot_idx += 1
    
    # Plot Calinski-Harabasz Index
    if 'calinski_harabasz' in methods:
        ax = axes[plot_idx]
        ax.plot(k_values[1:], calinski_scores[1:], 'mo-')  # Start from k=2
        ax.set_xlabel('Number of clusters (k)')
        ax.set_ylabel('Calinski-Harabasz Index')
        ax.set_title('Calinski-Harabasz Method')
        ax.grid(True)
        
        # Find the k with maximum Calinski-Harabasz index
        ch_scores = np.array(calinski_scores[1:])
        max_ch_k = k_values[1:][np.argmax(ch_scores)]
        ax.axvline(x=max_ch_k, color='r', linestyle='--', 
                  label=f'Max C-H Index: k={max_ch_k}')
        ax.legend()
        plot_idx += 1
    
    plt.tight_layout()
    
    # Determine the optimal k using voting
    votes = {}
    
    if 'elbow' in methods:
        if elbow_k not in votes:
            votes[elbow_k] = 0
        votes[elbow_k] += 1
    
    if 'silhouette' in methods:
        if max_silhouette_k not in votes:
            votes[max_silhouette_k] = 0
        votes[max_silhouette_k] += 1
    
    if 'calinski_harabasz' in methods:
        if max_ch_k not in votes:
            votes[max_ch_k] = 0
        votes[max_ch_k] += 1
    
    # Get the k with the most votes
    optimal_k = max(votes.items(), key=lambda x: x[1])[0]
    
    return optimal_k, fig

def determine_dbscan_eps(X, k=5, figsize=(10, 6)):
    """
    Determine the optimal epsilon parameter for DBSCAN using k-distance graph.
    
    Parameters:
    -----------
    X : array-like
        The input data for clustering
    k : int, default=5
        The number of nearest neighbors to consider
    figsize : tuple, default=(10, 6)
        Figure size for the plot
        
    Returns:
    --------
    eps : float
        The suggested epsilon parameter for DBSCAN
    fig : matplotlib.figure.Figure
        The figure object containing the k-distance plot
    """
    # Compute k-nearest neighbors
    neigh = NearestNeighbors(n_neighbors=k)
    neigh.fit(X)
    distances, _ = neigh.kneighbors(X)
    
    # Sort the distances to the kth nearest neighbor
    k_distances = distances[:, k-1]
    k_distances.sort()
    
    # Create the k-distance plot
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(range(len(k_distances)), k_distances)
    ax.set_xlabel('Points sorted by distance')
    ax.set_ylabel(f'Distance to {k}th nearest neighbor')
    ax.set_title('k-distance Graph for DBSCAN Parameter Selection')
    ax.grid(True)
    
    # Find the "elbow" in the k-distance plot
    # Calculate the second derivative to find the point of maximum curvature
    k_distances_array = np.array(k_distances)
    second_derivative = np.diff(np.diff(k_distances_array))
    elbow_index = np.argmax(second_derivative) + 1
    eps_suggestion = k_distances[elbow_index]
    
    # Mark the suggested epsilon value
    ax.axhline(y=eps_suggestion, color='r', linestyle='--',
              label=f'Suggested eps: {eps_suggestion:.4f}')
    ax.legend()
    
    return eps_suggestion, fig
