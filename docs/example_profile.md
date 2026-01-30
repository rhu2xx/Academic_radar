# Academic Radar - Example Research Profile

This file shows what a generated research profile looks like.

```json
{
  "core_task": "Spatiotemporal forecasting on dynamic graph structures",
  "mathematical_framework": "Graph signal processing, recurrent neural networks, attention mechanisms, Bayesian inference",
  "pain_points": [
    "Memory bottlenecks with long sequence modeling",
    "High computational cost for real-time inference",
    "Difficulty capturing long-range dependencies"
  ],
  "domain_keywords": [
    "traffic prediction",
    "traffic flow",
    "road networks",
    "congestion",
    "transportation"
  ],
  "methodologies": [
    "Graph Convolutional Networks",
    "LSTM",
    "Attention mechanisms",
    "Temporal modeling"
  ],
  "created_at": "2026-01-30T12:00:00Z",
  "source_papers": [
    "data/user_papers/traffic_gnn_paper.pdf",
    "data/user_papers/spatiotemporal_forecasting.pdf"
  ]
}
```

## How It's Used

The Abstractor agent takes this profile and generates queries like:

### Direct Queries (Same domain)
- "traffic prediction graph neural networks attention"
- "road network spatiotemporal forecasting"

### Abstracted Queries (Cross-domain)
- "sparse dynamic graph sequence modeling" (finds papers on social networks, molecular dynamics, etc.)
- "long-range dependencies recurrent models" (finds papers on NLP, video analysis, etc.)

### Solution-Seeking Queries (Targeting pain points)
- "memory efficient sequence models long context"
- "real-time inference optimization graph networks"
- "low-rank approximation temporal data"

The magic happens when papers from **video compression** or **protein folding** use the same mathematical techniques to solve your **traffic prediction** constraints!
