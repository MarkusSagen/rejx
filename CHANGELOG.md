# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.1.0](https://github.com/MarkusSagen/rejx/pull/9) - 2024-10-12

New release, fixes bugs and adds new options for selection

### Added

- New `tree` command as an alias for `ls --view tree`
- Two new flags for targeting hidden files with `rejx`:
    - `--include-hidden` to include hidden files when searching
    - `--exclude-hidden` to exclude hidden files when searching
- New flag, `--all`, to the fix and clean commands by @StephanLoor

### Changed

- Refactored `find_rej_files` function to accept a path parameter
- Updated `fix`, `diff`, `ls`, and `clean` commands to use a consistent interface
- Enhanced README with more detailed usage examples
- Consistent `path` argument across all commands
- Improved error handling and user feedback
- The `--all` flag now works with a specified directory path

### Fixed

- Bug in previous release, making it not possible to install (See #2)
- Make consistent behaviour for the commands in rejx
- Improved handling of non `.rej` files in various commands
- Better error messages when invalid paths are provided
- Remove logs incorrectly suggesting that changes could be applied from non-rejx files
- Bug with duplicate logging when setting up rich logger
