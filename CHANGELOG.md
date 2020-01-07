# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) (sort of. It's early days, and there may be some breaking changes released under a minor version increment).

## [0.14.0] - 2019-12-26

Boxing Day update!

### Changed

- Added named parameter `connection_retries` to `MarianClient`, default value is `10`
- Added named parameter `max_wait_time_between_connection_attempts` to `MarianClient`, default value is `300`
- When instantiating a `MarianClient` instance, if we receive a `ConnectionRefusedError`, attempt to reconnect `connection_retries` times, with exponential backoff, maxing out at `max_wait_time_between_connection_attempts`.
- This means in the default case, if Marian Server is unavailable, we will try to connect, wait 1 second, try to connect again, wait 2 seconds, try to connect again, wait 4 seconds, ... then 8, 16, 32, 64, 128, 256, 300, then actually fail, for a total wait time of 811 seconds.

## [0.13.0] - 2019-12-11

### Fixed

- `install_requires` wasn't bringing in a needed package; hardocding fixes this.

### Changed

- `build_release.sh` now accepts a second parameter: the string `minor` or `patch`. This determines how the version is bumped. As a reminder, the first parameter is the PyPi credential file location, default is `~/.pypirc`.

## [0.11.0] - 2019-12-10

### Fixed

- Bug ENG-6268. Backing off after timeout was causing a backlog of messages, so next time the connection was used, the client received stale messages.

### Added

- Tests for this bug. It involves spinning up a WebSocket echo server, which is done with node and a shell script. Sorry.

### Changed

- Now MIT Licensed!

## [0.10.0] - 2019-12-03

### Fixed

- WebSocket connection is creating on instantiation and only recreated if calls are failing (was: connection created per call)

### Added

- Exponential backoff: retry a configurable number of times, wait time between grows exponentially
