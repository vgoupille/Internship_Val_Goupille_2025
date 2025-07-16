"""
BacSC: A general workflow for bacterial single-cell RNA sequencing data analysis
"""

from .ClusterDE import (
    call_de,
    construct_synthetic_null,
    generate_nb_data_copula,
)

from .NB_est import (
    estimate_overdisp_nb,
    fit_nbinom,
    negbin_mean_to_numpy,
)

from .scTransform import SCTransform
from .countsplit import countsplit_adata, select_n_pcs_countsplit
from .clustering_opt import (
    modularity,
    cpm,
    mod_weighted,
    cluster_train_test,
    find_optimal_clustering_resolution,
)

# Import the scDEED module itself
from . import scDEED
from .scDEED import (
    scDEED as scDEED_function,  # Rename to avoid conflict
    create_permuted_data_scdeed,
    embed_data_scDEED,
    calculate_reliability_scores,
    scdeed_parameter_selection,
)
from .util import (
    convert_to_dense_counts,
    filter_outliers,
    is_outlier,
    rotate_umap,
    find_opt_umap_rotation,
)
from .util_probe import (
    prep_probe_BacSC_data,
    grouped_var_agg,
)
