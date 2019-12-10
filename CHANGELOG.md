# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) (sort of. It's early days, and there may be some breaking changes released under a minor version increment).

## [0.10.0] - 2019-12-03

### Fixed

- WebSocket connection is creating on instantiation and only recreated if calls are failing (was: connection created per call)

### Added

- Exponential backoff: retry a configurable number of times, wait time between grows exponentially
