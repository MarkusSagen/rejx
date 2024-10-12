# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.1.0](https://github.com/MarkusSagen/rejx/pull/7) - 2024-10-12

New release, fixes bugs and adds new options for selection

### Added

- Two new flags for targeting hidden files with `rejx`:
    - `--include-hidden` to include hidden files when searching
    - `--exclude-hidden` to exclude hidden files when searching
- New flag, `--all`, to the fix and clean commands by @StephanLoor

### Fixed

- Bug in previous release, making it not possible to install (See #2)
