#!/bin/bash
if [ $# -eq 0 ]; then
    # Default behavior if no args provided
    ARGS="--timeframe 5m 15m 30m 1h 4h --timerange 20260111-"
else
    # Use provided args
    ARGS="$@"
fi

echo "Running download-data with args: $ARGS"
docker compose run --rm freqtrade download-data $ARGS
