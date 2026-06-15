#!/bin/bash
#
# FEDERAL TRIAL COUNSEL - UNLOCK SCRIPT
# Decrypts protected skill files
#
# Usage: ./unlock.sh
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ENCRYPTED_DIR="$ROOT_DIR/.encrypted"
OUTPUT_DIR="$HOME/.claude/skills"

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                               ║"
echo "║   ███████╗███████╗██████╗ ███████╗██████╗  █████╗ ██╗                        ║"
echo "║   ██╔════╝██╔════╝██╔══██╗██╔════╝██╔══██╗██╔══██╗██║                        ║"
echo "║   █████╗  █████╗  ██║  ██║█████╗  ██████╔╝███████║██║                        ║"
echo "║   ██╔══╝  ██╔══╝  ██║  ██║██╔══╝  ██╔══██╗██╔══██║██║                        ║"
echo "║   ██║     ███████╗██████╔╝███████╗██║  ██║██║  ██║███████╗                   ║"
echo "║   ╚═╝     ╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝                   ║"
echo "║                                                                               ║"
echo "║                    🔐 TRIAL COUNSEL UNLOCK SYSTEM 🔐                          ║"
echo "║                                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if encrypted files exist
if [ ! -d "$ENCRYPTED_DIR" ]; then
    echo "ERROR: No encrypted files found."
    echo "Please ensure you have the .encrypted directory."
    exit 1
fi

# Check for encrypted files
if [ ! -f "$ENCRYPTED_DIR/federal-trial-counsel.enc" ]; then
    echo "ERROR: federal-trial-counsel.enc not found."
    exit 1
fi

echo "Found encrypted Federal Trial Counsel skill."
echo ""

# Prompt for password
echo -n "Enter unlock password: "
read -s PASSWORD
echo ""
echo ""

if [ -z "$PASSWORD" ]; then
    echo "ERROR: Password cannot be empty."
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "Unlocking Federal Trial Counsel..."
echo ""

# Decrypt
if openssl enc -aes-256-cbc -d -salt -pbkdf2 -iter 100000 \
    -in "$ENCRYPTED_DIR/federal-trial-counsel.enc" \
    -out "/tmp/federal-trial-counsel.tar.gz" \
    -pass pass:"$PASSWORD" 2>/dev/null; then

    # Extract to skills directory
    tar -xzf "/tmp/federal-trial-counsel.tar.gz" -C "$OUTPUT_DIR"
    rm "/tmp/federal-trial-counsel.tar.gz"

    echo "✓ Federal Trial Counsel installed to $OUTPUT_DIR/federal-trial-counsel"
    echo ""
    echo "=============================================="
    echo "  UNLOCK COMPLETE"
    echo "=============================================="
    echo ""
    echo "The skill will auto-activate when Claude Code starts."
    echo ""
    echo "Features unlocked:"
    echo "  • 40+ Federal Causes of Action"
    echo "  • 19 Litigation Strategy Engines"
    echo "  • Twombly/Iqbal Pleading Engine"
    echo "  • MTD Risk Scoring (0-100)"
    echo ""
else
    echo "✗ Failed to decrypt (wrong password?)"
    rm -f "/tmp/federal-trial-counsel.tar.gz"
    exit 1
fi

echo "=============================================="
echo "  IMPORTANT LEGAL NOTICE"
echo "=============================================="
echo ""
echo "By unlocking this skill, you agree to:"
echo "  1. Use for PERSONAL purposes only"
echo "  2. NOT copy, distribute, or share"
echo "  3. Have all outputs reviewed by a licensed attorney"
echo "  4. Accept that this is NOT legal advice"
echo ""
