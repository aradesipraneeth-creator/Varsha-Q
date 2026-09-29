"""
VARSHA-Q Graph Neural Network (GNN) Spatial Model & Spatiotemporal Fusion
Models spatial adjacency, elevation gradients, and marine-terrestrial boundaries across Indian districts.
Fuses LNN temporal trajectories with GNN spatial neighborhoods into a joint spatiotemporal embedding.
"""
import torch
import torch.nn as nn
from typing import Optional, Tuple


class SpatialGraphConv(nn.Module):
    """
    Symmetric normalized spatial graph convolution with self-loops:
    H^{(l+1)} = Activation( D^{-1/2} A_hat D^{-1/2} H^{(l)} W + H^{(l)} W_{res} )
    """
    def __init__(self, in_features: int, out_features: int, dropout: float = 0.1):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features

        self.weight = nn.Linear(in_features, out_features, bias=False)
        self.res_weight = nn.Linear(in_features, out_features, bias=True)
        self.activation = nn.LeakyReLU(0.1)
        self.layer_norm = nn.LayerNorm(out_features)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, adj_norm: torch.Tensor) -> torch.Tensor:
        """
        x: (num_nodes, in_features)
        adj_norm: (num_nodes, num_nodes) - Normalized adjacency matrix with self-loops
        Returns: (num_nodes, out_features)
        """
        # Message passing over spatial neighbors
        support = self.weight(x)  # (N, out_features)
        out = torch.matmul(adj_norm, support)  # (N, out_features)

        # Residual skip connection
        out = out + self.res_weight(x)
        out = self.layer_norm(out)
        out = self.activation(out)
        return self.dropout(out)


class GraphNeuralNetwork(nn.Module):
    """
    Multi-layer Spatial GNN for district graph processing.
    Input:
      node_features: (num_nodes, node_in_dim)
      adj_matrix: (num_nodes, num_nodes)
    Output:
      spatial_embeddings: (num_nodes, hidden_dim)
    """
    def __init__(self, node_in_dim: int = 7, hidden_dim: int = 32, num_layers: int = 2):
        super().__init__()
        self.num_layers = num_layers
        self.conv1 = SpatialGraphConv(node_in_dim, hidden_dim)
        if num_layers > 1:
            self.conv2 = SpatialGraphConv(hidden_dim, hidden_dim)
        else:
            self.conv2 = None

    @staticmethod
    def normalize_adjacency(adj: torch.Tensor) -> torch.Tensor:
        """
        Computes symmetric normalized adjacency: D_hat^{-1/2} A_hat D_hat^{-1/2}
        where A_hat = A + I
        """
        N = adj.size(0)
        adj_hat = adj + torch.eye(N, device=adj.device)
        deg = torch.sum(adj_hat, dim=1)
        deg_inv_sqrt = torch.pow(deg.clamp(min=1e-5), -0.5)
        d_mat = torch.diag(deg_inv_sqrt)
        return torch.matmul(torch.matmul(d_mat, adj_hat), d_mat)

    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        adj_norm = self.normalize_adjacency(adj)
        h = self.conv1(x, adj_norm)
        if self.conv2 is not None:
            h = self.conv2(h, adj_norm)
        return h


class SpatiotemporalFusion(nn.Module):
    """
    Documented Joint Spatiotemporal Fusion Layer:
    Fuses LNN temporal representation (capturing time-series rainfall evolution)
    with GNN spatial representation (capturing district topological neighborhood).

    Mathematical Formulation:
    H_temp: (N_districts, D_temp)
    H_spat: (N_districts, D_spat)

    Gating factor:
    G = sigmoid( Linear([H_temp, H_spat]) ) in [0, 1]

    Fused representation:
    Z_ST = LayerNorm( G * Proj_temp(H_temp) + (1 - G) * Proj_spat(H_spat) )
    """
    def __init__(self, d_temp: int = 32, d_spat: int = 32, d_fused: int = 32):
        super().__init__()
        self.proj_temp = nn.Linear(d_temp, d_fused)
        self.proj_spat = nn.Linear(d_spat, d_fused)

        # Adaptive gating mechanism
        self.gate_fc = nn.Sequential(
            nn.Linear(d_temp + d_spat, d_fused),
            nn.ReLU(),
            nn.Linear(d_fused, d_fused),
            nn.Sigmoid()
        )
        self.layer_norm = nn.LayerNorm(d_fused)
        self.head = nn.Sequential(
            nn.Linear(d_fused, d_fused),
            nn.GELU(),
            nn.Linear(d_fused, d_fused)
        )

    def forward(self, h_temporal: torch.Tensor, h_spatial: torch.Tensor) -> torch.Tensor:
        """
        h_temporal: (N_nodes, D_temp)
        h_spatial: (N_nodes, D_spat)
        Returns: (N_nodes, D_fused)
        """
        concat = torch.cat([h_temporal, h_spatial], dim=-1)
        gate = self.gate_fc(concat)

        fused = gate * self.proj_temp(h_temporal) + (1.0 - gate) * self.proj_spat(h_spatial)
        fused = self.layer_norm(fused)
        out = fused + self.head(fused)
        return out
