# Changelog

## [1.0.0] - 2024-05-22

### Added
FEATURE: Migrated static site to a dynamic Python Flask application.
FEATURE: Integrated PostgreSQL database (Supabase) for data persistence.
FEATURE: Implemented secure Admin Dashboard with password protection.
FEATURE: Added client-side image cropping (Cropper.js) and binary storage (BYTEA).
FEATURE: Redesigned UI with a modern Dark/Orange theme and Inter typography.
FEATURE: Implemented interactive Neural Network background animation using Canvas API.
FEATURE: Added Skeleton Loading state for profile image to improve UX.

### Fixed
FIX: Removed hardcoded API credentials and implemented environment variable configuration.
FIX: Optimized image serving with HTTP caching headers (24h cache).
FIX: Resolved responsive layout issues on mobile devices for the skills grid.
FIX: Standardized project structure to follow Flask conventions (templates/static).
