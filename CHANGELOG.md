# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2024-12-04

### Added
- 📝 Created `SECRETS_CONFIGURATION_REQUIRED.md` - Comprehensive guide for GitHub Secrets configuration
- 🔧 Added `configure-secrets.sh` - Helper script for Docker Hub credential verification and setup guidance
- 📚 Enhanced documentation with exact configuration values and step-by-step instructions

### Changed
- 🔄 Updated README.md badges to use correct GitHub repository (janeTingl/telegram-115bot)
- 🔄 Updated git clone URL in README.md to reference correct repository
- 📦 Version bump to trigger Docker Hub workflow after Secrets configuration

### Fixed
- 🐛 Corrected GitHub Actions badge URL in README
- 🐛 Fixed repository references throughout documentation

## [1.0.0] - 2024-12-04

### Added
- 🎉 Initial release
- 🐳 Docker Hub auto-publish workflow with GitHub Actions
- 🏗️ Multi-architecture support (AMD64, ARM64)
- 🤖 Full-stack Telegram 115 Bot with FastAPI backend
- ⚛️ React 18 + TypeScript + Vite frontend
- 🔐 TOTP 2FA authentication
- 📁 115 Cloud storage integration
- 🎬 TMDB metadata integration
- 📺 Emby STRM generation
- 🌐 WebDAV support
- ⬇️ Offline download management

### Infrastructure
- ✅ GitHub Actions workflow for automated Docker builds
- ✅ Docker Compose configuration
- ✅ Nginx reverse proxy
- ✅ Supervisor process management
- ✅ SQLite database storage

---

## How to Use This Changelog

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities
