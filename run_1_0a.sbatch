#!/bin/bash
#SBATCH --job-name=task1_0a
#SBATCH --partition=gpu-redhat
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=06:00:00
#SBATCH --output=task1_0a_%j.out
#SBATCH --error=task1_0a_%j.err

set -uo pipefail
cd "$SLURM_SUBMIT_DIR"

echo "[$(date)] job $SLURM_JOB_ID on $(hostname)"
nvidia-smi -L || true

source "$HOME/miniforge3/etc/profile.d/conda.sh" || { echo "FATAL: conda.sh not found"; exit 1; }
conda activate vllm || { echo "FATAL: could not activate vllm env"; exit 1; }

export RESULTS_DIR=results_8b_16seed
export N_SEEDS=16
export MODEL_NAME=NousResearch/Meta-Llama-3.1-8B-Instruct
export OPENAI_BASE_URL=http://localhost:8000/v1
export OPENAI_API_KEY=EMPTY
export PROVIDER_TAG=local_vllm

echo "[$(date)] starting vLLM server..."
vllm serve "$MODEL_NAME" \
    --dtype float16 \
    --max-model-len 8192 \
    --port 8000 \
    > "vllm_server_${SLURM_JOB_ID}.log" 2>&1 &
SERVER_PID=$!

cleanup() {
    echo "[$(date)] tearing down vLLM server (PID $SERVER_PID)"
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "[$(date)] waiting for server..."
READY=0
for i in $(seq 1 120); do
    if curl -s http://localhost:8000/v1/models 2>/dev/null | grep -q '"id"'; then
        READY=1; echo "[$(date)] server ready (~$((i*10))s)"; break
    fi
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        echo "[$(date)] FATAL: server died during startup — see vllm_server_${SLURM_JOB_ID}.log"; exit 1
    fi
    sleep 10
done
[ "$READY" -eq 1 ] || { echo "[$(date)] FATAL: server not ready within timeout"; exit 1; }

echo "[$(date)] running task_1_0.py (N_SEEDS=$N_SEEDS, RESULTS_DIR=$RESULTS_DIR)"
python task_1_0.py
RC=$?
echo "[$(date)] harness exit code: $RC"

if [ "$RC" -eq 0 ]; then
    echo "[$(date)] building credit-gap figure..."
    python fig_credit_gap.py || echo "WARN: fig_credit_gap.py failed (JSON + trajectory still saved)"
fi

echo "[$(date)] done."
exit $RC
