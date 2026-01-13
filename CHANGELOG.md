# Changelog

All notable changes to AUTOFLOW OS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- BRAIN module v2.0 with improved diagnostics
- Push notifications for clients
- Cross-reference catalog expansion
- Voice input for mechanics

---

## [1.0.0] - 2025-01-15

### Added
- **RECEPTION Module**
  - Conversational client qualification
  - Automatic slot booking
  - 1C integration for appointments
  - SMS/Telegram notifications

- **CRM Module**
  - Multi-criteria client search
  - Client card with full history
  - Fleet management
  - Balance tracking

- **WAREHOUSE Module**
  - Part search by article/OEM
  - Real-time inventory display
  - Basic cross-reference
  - Reservation system

- **Core Features**
  - Role-based access control (client/manager/mechanic/admin)
  - 1C:Enterprise integration via REST API
  - PostgreSQL database with SQLAlchemy ORM
  - Redis caching layer
  - Docker deployment support

- **Documentation**
  - Full API documentation
  - Deployment guide
  - User guide
  - Commercial proposal template

### Security
- JWT-based authentication
- Role-based access control
- Input validation with Pydantic
- SQL injection protection

---

## [0.9.0] - 2024-12-01 (Beta)

### Added
- Initial RECEPTION module implementation
- Basic CRM functionality
- 1C connector prototype
- Telegram bot framework

### Fixed
- Connection pooling issues
- FSM state persistence
- Cyrillic encoding in 1C responses

---

## [0.5.0] - 2024-10-15 (Alpha)

### Added
- Project structure
- Basic Telegram bot
- Database schema design
- CI/CD pipeline

---

## Version History

| Version | Date | Status |
|---------|------|--------|
| 1.0.0 | 2025-01-15 | ✅ Current |
| 0.9.0 | 2024-12-01 | Beta |
| 0.5.0 | 2024-10-15 | Alpha |

---

[Unreleased]: https://github.com/username/autoflow-os/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/username/autoflow-os/compare/v0.9.0...v1.0.0
[0.9.0]: https://github.com/username/autoflow-os/compare/v0.5.0...v0.9.0
[0.5.0]: https://github.com/username/autoflow-os/releases/tag/v0.5.0
