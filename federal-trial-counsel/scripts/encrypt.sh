#!/bin/bash
#
# FEDERAL TRIAL COUNSEL - ENCRYPTION SCRIPT
# For repository owner use only
#
# Usage: ./encrypt.sh <password>
#

set -e

if [ -z "$1" ]; then
    echo "Usage: ./encrypt.sh <password>"
    echo "This script encrypts skill files for secure distribution."
    exit 1
fi

PASSWORD="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=============================================="
echo "  FEDERAL TRIAL COUNSEL - ENCRYPTION"
echo "=============================================="
echo ""

# Create encrypted directory
mkdir -p "$ROOT_DIR/.encrypted"

# Files/folders to encrypt (exclude scripts, .git, .encrypted, README)
echo "Creating archive of skill files..."

# Create a temporary directory with files to encrypt
TEMP_DIR=$(mktemp -d)
mkdir -p "$TEMP_DIR/federal-trial-counsel"

# Copy relevant directories
for dir in assets modules references workflows; do
    if [ -d "$ROOT_DIR/$dir" ]; then
        cp -r "$ROOT_DIR/$dir" "$TEMP_DIR/federal-trial-counsel/"
    fi
done

# Copy key files
for file in SKILL.md MANIFEST.md; do
    if [ -f "$ROOT_DIR/$file" ]; then
        cp "$ROOT_DIR/$file" "$TEMP_DIR/federal-trial-counsel/"
    fi
done

# Copy scripts (except encrypt/unlock)
if [ -d "$ROOT_DIR/scripts" ]; then
    mkdir -p "$TEMP_DIR/federal-trial-counsel/scripts"
    for subdir in federal_pleading_engine courtlistener; do
        if [ -d "$ROOT_DIR/scripts/$subdir" ]; then
            cp -r "$ROOT_DIR/scripts/$subdir" "$TEMP_DIR/federal-trial-counsel/scripts/"
        fi
    done
fi

echo "Encrypting federal-trial-counsel..."

# Create tarball
tar -czf "/tmp/federal-trial-counsel.tar.gz" -C "$TEMP_DIR" federal-trial-counsel

# Encrypt with OpenSSL (AES-256-CBC)
openssl enc -aes-256-cbc -salt -pbkdf2 -iter 100000 \
    -in "/tmp/federal-trial-counsel.tar.gz" \
    -out "$ROOT_DIR/.encrypted/federal-trial-counsel.enc" \
    -pass pass:"$PASSWORD"

# Generate checksum
shasum -a 256 "$ROOT_DIR/.encrypted/federal-trial-counsel.enc" > "$ROOT_DIR/.encrypted/federal-trial-counsel.sha256"

# Cleanup
rm "/tmp/federal-trial-counsel.tar.gz"
rm -rf "$TEMP_DIR"

echo "  -> Created .encrypted/federal-trial-counsel.enc"
echo ""
echo "=============================================="
echo "  ENCRYPTION COMPLETE"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Commit the .encrypted folder"
echo "2. Share the password securely with authorized users"
echo ""
