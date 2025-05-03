# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2023-11-01

### Added
- Implemented advanced templates for specific use cases (code refactoring, API design, etc.)
- Added tagging system for prompts with search and filtering capabilities
- Added user profile management with account settings
- Added prompt editing functionality
- Added confirmation dialog for prompt deletion
- Added pagination for prompt lists
- Added Flask-Limiter for rate limiting API endpoints
- Added Flask-Caching for improved performance
- Added Flask-Mail for email notifications
- Added database migrations with Flask-Migrate
- Added unit tests for models and utilities
- Added CSRF protection for all forms
- Added proper API error handling

### Changed
- Refactored application to use Flask Blueprint pattern
- Improved project structure with separate directories for routes, models, etc.
- Implemented factory pattern for application creation
- Enhanced configuration management with environment-specific settings
- Updated templates to use Bootstrap 5 for responsive design
- Improved database models with proper indexing for better performance

### Fixed
- Fixed empty advanced_templates.html file
- Fixed missing validation in prompt save function
- Fixed security issues with hardcoded secret key in development mode
- Fixed lack of error handling in API endpoints
- Fixed sorting and filtering issues in prompt lists

## [1.0.0] - 2023-10-01

### Added
- Initial release of PromptCrafter
- Basic prompt generation with structured and natural language formats
- User registration and authentication system
- Prompt saving and sharing functionality
- Public prompt browsing
- Basic API for prompt generation

### Changed


### Fixed


### Security


## [0.0.1] 

- Initial release of Prompt crafter System


<!-- Versions -->
[unreleased]: https://github.com/FIBA00/promptCrafteraider_V2/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/FIBA00/promptCrafter/compare/v0.0.1...v1.0.0
[0.0.1]: https://github.com/FIBA00/promptCrafter/releases/tag/v0.0.1