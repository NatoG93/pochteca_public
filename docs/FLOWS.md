# Signal Flows

This document outlines the flows for external signals triggering actions within the Pochteca system.

## 1. Data Update Flow
**Trigger**: Scheduled n8n workflow or manual trigger.
**Goal**: Ensure local data is fresh for analysis.

1.  **Source**: n8n sends POST request to `/update`.
2.  **Payload**:
    ```json
    {
      "timeframes": ["5m", "15m"],
      "days": 5
    }
    ```
3.  **Listener**: Validates payload and executes `updatedata.sh`.
4.  **Action**: `updatedata.sh` runs `freqtrade download-data`.
5.  **Output**: New data files in `user_data/data`.

## 2. Emergency Stop Flow (Conceptual)
**Trigger**: Market crash detected by external sentiment analyzer.
**Goal**: Halt trading immediately.

1.  **Source**: Sentiment Analysis Bot.
2.  **Payload**:
    ```json
    {
      "action": "force_exit",
      "reason": "sentiment_crash_detected"
    }
    ```
3.  **Listener**: Parses "force_exit".
4.  **Action**: Calls Freqtrade RPC `/forceexit`.
