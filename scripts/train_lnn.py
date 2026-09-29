"""
VARSHA-Q LNN & GNN Training Scripts
"""
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

import torch
import torch.nn as nn
import torch.optim as optim
from backend.app.data.demo_provider import DemoProvider
from backend.app.ml.lnn_model import LiquidNeuralNetwork
from backend.app.ml.gnn_model import GraphNeuralNetwork, SpatiotemporalFusion

def train_spatiotemporal():
    print("Training Continuous-Time Liquid Neural Network & Spatial Graph Neural Network...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    provider = DemoProvider(random_seed=42)
    demo_sample = provider.generate_scenario_data("ACTIVE_MONSOON", seed=42)

    lnn = LiquidNeuralNetwork(input_dim=8, hidden_dim=32, num_layers=2).to(device)
    gnn = GraphNeuralNetwork(node_in_dim=7, hidden_dim=32, num_layers=2).to(device)
    fusion = SpatiotemporalFusion(d_temp=32, d_spat=32, d_fused=32).to(device)
    head = nn.Linear(32, 1).to(device)

    optimizer = optim.AdamW(list(lnn.parameters()) + list(gnn.parameters()) + list(fusion.parameters()) + list(head.parameters()), lr=0.005)
    criterion = nn.MSELoss()

    t_seq = torch.tensor(demo_sample["temporal_sequences"], dtype=torch.float32, device=device)
    s_feat = torch.tensor(demo_sample["spatial_features"], dtype=torch.float32, device=device)
    adj = torch.tensor(demo_sample["adjacency_matrix"], dtype=torch.float32, device=device)
    targets = torch.tensor(demo_sample["observed_rainfall"], dtype=torch.float32, device=device).unsqueeze(-1)

    for ep in range(15):
        optimizer.zero_grad()
        h_t = lnn(t_seq)
        h_s = gnn(s_feat, adj)
        fused = fusion(h_t, h_s)
        pred = head(fused)
        loss = criterion(pred, targets)
        loss.backward()
        optimizer.step()

    out_path = BASE_DIR / "models" / "spatiotemporal_weights.pt"
    torch.save({
        "lnn": lnn.state_dict(),
        "gnn": gnn.state_dict(),
        "fusion": fusion.state_dict(),
        "head": head.state_dict()
    }, out_path)
    print(f"Saved spatiotemporal model weights to {out_path}")

if __name__ == "__main__":
    train_spatiotemporal()
