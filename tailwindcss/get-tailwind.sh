#! /usr/bin/env bash

cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null

TAILWIND_EXTRA_VERSION=$(cat VERSION)
TAILWIND_EXTRA_BASE_URL=https://github.com/dobicinaitis/tailwind-cli-extra/releases/download/${TAILWIND_EXTRA_VERSION}/tailwindcss-extra

arch=$(uname -a | tr '[:upper:]' '[:lower:]')

if [[ $arch == *"linux"* && $arch == *"x86_64"* ]]; then
    ARCH_SPECIFIER="linux-x64"
elif [[ $arch == *"linux"* && $arch == *"arm64"* ]]; then
    ARCH_SPECIFIER="linux-arm64"
elif [[ $arch == *"darwin"* && $arch == *"x86_64"* ]]; then
    ARCH_SPECIFIER="macos-x64"
elif [[ $arch == *"darwin"* && $arch == *"arm64"* ]]; then
    ARCH_SPECIFIER="macos-arm64"
else
    echo "Unsupported platform '$(uname -a)'"
    exit 1
fi

echo "Downloading tailwindcss extra ${TAILWIND_EXTRA_VERSION} for ${ARCH_SPECIFIER}"
curl -sLo tailwindcss ${TAILWIND_EXTRA_BASE_URL}-${ARCH_SPECIFIER}
chmod +x tailwindcss