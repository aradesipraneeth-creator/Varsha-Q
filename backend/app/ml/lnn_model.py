"""
VARSHA-Q Liquid Neural Network (LNN) Temporal Dynamics Model
Implements continuous-time Liquid Time-Constant (LTC) recurrent dynamics based on Hasani et al. (2021).
Captures evolving atmospheric and precipitation sequence memory using non-linear ODE integration.

Mathematical Formulation:
dx(t)/dt = - [ 1/tau + f(x(t), u(t)) ] * x(t) + A * f(x(t), u(t))
where tau is the base time constant, u(t) is meteorological input vector,
f(...) is non-linear synaptic conductance, and x(t) is hidden liquid state.
"""
import torch
import torch.nn as nn
from typing import Tuple, Optional


class LiquidCell(nn.Module):
    """
    A single Liquid Time-Constant (LTC) cell with input-dependent time constant.
    Continuous-time dynamics discretized via semi-implicit Euler integration:
    x[t + dt] = (x[t] + dt * A * f_in) / (1 + dt * (1/tau + f_in))
    """
    def __init__(self, input_dim: int, hidden_dim: int, dt: float = 0.5):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.dt = dt

        # Base time-constant parameter (strictly positive via softplus)
        self.tau_raw = nn.Parameter(torch.ones(hidden_dim) * 0.5)

        # Synaptic conductance network: computes dynamic leak & drive from (input, state)
        self.w_input = nn.Linear(input_dim, hidden_dim, bias=True)
        self.w_state = nn.Linear(hidden_dim, hidden_dim, bias=False)

        # Reversal potential / driving ceiling A
        self.reversal_potential = nn.Parameter(torch.ones(hidden_dim) * 2.0)

        # Output projection
        self.activation = nn.Tanh()

    def forward(self, u_t: torch.Tensor, x_t: torch.Tensor) -> torch.Tensor:
        """
        u_t: (batch_size, input_dim) - Current meteorological inputs at time t
        x_t: (batch_size, hidden_dim) - Liquid state at time t
        Returns: x_{t+1} of shape (batch_size, hidden_dim)
        """
        tau = torch.nn.functional.softplus(self.tau_raw) + 0.05
        leak_base = 1.0 / tau

        # Dynamic conductance f(x_t, u_t)
        conductance = torch.sigmoid(self.w_input(u_t) + self.w_state(x_t))

        # Semi-implicit Euler integration step
        numerator = x_t + self.dt * (self.reversal_potential * conductance)
        denominator = 1.0 + self.dt * (leak_base + conductance)
        x_next = self.activation(numerator / denominator)

        return x_next


class LiquidNeuralNetwork(nn.Module):
    """
    Multi-layer Liquid Neural Network for temporal rainfall & atmospheric sequence encoding.
    Input shape: (batch_size, sequence_length, input_dim)
    Output shape: (batch_size, hidden_dim) - Temporal representation at final timestep
    """
    def __init__(self, input_dim: int = 8, hidden_dim: int = 32, num_layers: int = 2, dt: float = 0.5):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.dt = dt

        self.cell1 = LiquidCell(input_dim, hidden_dim, dt=dt)
        if num_layers > 1:
            self.cell2 = LiquidCell(hidden_dim, hidden_dim, dt=dt)
        else:
            self.cell2 = None

        self.layer_norm = nn.LayerNorm(hidden_dim)
        self.dropout = nn.Dropout(0.1)

    def forward(self, x_seq: torch.Tensor, init_state: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        x_seq: (batch_size, seq_len, input_dim)
        Returns: latent temporal embedding of shape (batch_size, hidden_dim)
        """
        batch_size, seq_len, _ = x_seq.shape
        device = x_seq.device

        h1 = torch.zeros(batch_size, self.hidden_dim, device=device)
        h2 = torch.zeros(batch_size, self.hidden_dim, device=device) if self.cell2 is not None else None

        # Step through continuous-time dynamic trajectory
        for t in range(seq_len):
            u_t = x_seq[:, t, :]
            h1 = self.cell1(u_t, h1)
            if self.cell2 is not None:
                h2 = self.cell2(h1, h2)

        final_rep = h2 if h2 is not None else h1
        final_rep = self.layer_norm(final_rep)
        return self.dropout(final_rep)
