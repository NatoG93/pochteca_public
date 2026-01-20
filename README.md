# 🦅 Pochteca Trading Bot

**Pochteca** is an advanced algorithmic trading system built on top of [Freqtrade](https://www.freqtrade.io/). This repository represents a production-ready implementation of a modular trading architecture designed for high-frequency crypto markets.

> **Note:** This is a portfolio release. Sensitive configurations and proprietary data have been excluded.

## 🚀 Features

- **Modular Strategy Engine**: Supports plug-and-play strategies (e.g., EMA Scalping, Momentum).
- **Automated Data Pipeline**: Webhook-triggered data updates and resampling.
- **Dockerized Architecture**: Fully containerized for consistent deployment.
- **Signal-Based Execution**: Extensible architecture for external signal integration (e.g., from TradingView or n8n).

## 📂 Project Structure

```
pochteca/
├── docs/               # Architecture, Security, and Flow documentation
├── src/                # Core logic and adapter scripts
├── user_data/
│   └── strategies/     # Python-based trading strategies
├── docker-compose.yml  # Container orchestration
└── updatedata.sh       # Data management utility
```

## 🛠️ Getting Started

### Prerequisites
- Docker Engine & Docker Compose
- Python 3.10+ (for local development)

### Quick Start
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/pochteca.git
    cd pochteca
    ```
2.  **Configure Environment**:
    ```bash
    cp .env.example .env
    # Edit .env with your dummy API keys for testing
    ```
3.  **Launch System**:
    ```bash
    docker compose up -d
    ```

## 📚 Documentation
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Security Policy](docs/SECURITY.md)
- [Signal Flows](docs/FLOWS.md)

## ⚖️ License
MIT License - See [LICENSE](LICENSE) for details.
