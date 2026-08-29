# VPN Subscription for Karing

Auto-updating VPN subscription with Warp+ protection and DNS leak prevention.

## Features

- Auto-update every hour via GitHub Actions
- 150 working servers from 100+ sources
- Warp+ data protection
- AmneziaFree backup
- DNS leak protection
- AdGuard ad blocking
- Russian apps bypass VPN
- Encrypted subscription support

## Setup

### 1. GitHub Secrets

Go to Settings -> Secrets and variables -> Actions -> New repository secret:

| Secret | Description |
|--------|-------------|
| `WARP_PRIVATE_KEY` | Your Warp+ private key |
| `WARP_RESERVED` | Warp+ reserved (e.g. `0,0,0`) |
| `SUB_PASSWORD` | Subscription encryption password |

### 2. Get Warp+ Key

1. Install 1.1.1.1 app
2. Get license key from settings
3. Use WG key generator to get private key

### 3. Karing Import

Add subscription URL:
