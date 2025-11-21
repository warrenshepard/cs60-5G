#!/usr/bin/env bash
#
# Warren Shepard and Nand Patel
# Dartmouth CS60 25F Final Project
# 20 Nov 2025
# 
# Starts all the core services in out mock 5G network.
# 
# AI Statement: ChatGPT for syntax.
#   Also figured out that we need to run the services as modules so that imports work correctly.
#   We also used chatGPT to write the cleanup() function as we were having trouble with that.
#   Specifically, we were having problems with shutting down processes on all ports.

set -e
cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"

pids=()

start_service() {
  name="$1"
  module="$2"
  echo "[run.sh] starting $name"
  python -m "$module" &
  pids+=($!)
}

start_service "NRF"          services.nrf.main
start_service "Policy"       services.policy.main
start_service "SMF"          services.smf.main
start_service "UPF"          services.upf.main
start_service "AMF"          services.amf.main
start_service "Application"  services.application.main
start_service "BaseStation"  services.base_station.main

cleanup() {
  echo
  echo "[run.sh] stopping services..."
  for pid in "${pids[@]}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
  wait || true
  echo "[run.sh] all services stopped."
}

trap cleanup INT TERM EXIT

echo "[run.sh] all services started. Press Ctrl+C to stop."
wait