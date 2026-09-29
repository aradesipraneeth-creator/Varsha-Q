#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "============================================================"
echo "VARSHA-Q: RENDER SINGLE-SERVICE BUILD PIPELINE"
echo "============================================================"

echo "--> [1/3] Upgrading pip and installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "--> [2/3] Verifying and initializing baseline model weights..."
python scripts/train_all.py --synthetic --epochs 5

echo "--> [3/3] Checking frontend distribution..."
if [ ! -d "frontend/dist" ] || [ "$REBUILD_FRONTEND" = "true" ]; then
    if command -v npm &> /dev/null; then
        echo "Building Vite/React frontend..."
        cd frontend
        npm install
        npm run build
        cd ..
    else
        echo "Warning: npm not found in build environment."
    fi
else
    echo "Found pre-built frontend distribution in frontend/dist. Ready for static serving."
fi

echo "============================================================"
echo "VARSHA-Q BUILD FINISHED SUCCESSFULLY"
echo "============================================================"
