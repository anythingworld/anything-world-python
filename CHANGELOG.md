# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2024-01-22

- Add operam `extra_formats: bool` parameter to `is_animation_done()` and
  `get_animated_model()`. Now it's possible to get models processed faster
  if `extra_formats=True`, without having to wait for all formats being
  generated

## [0.1.1] - 2024-01-18

- Remove python-magic (and libmagic) dependency
- Create a general `utils` and remove code duplicates

## [0.1.0] - 2024-01-17

- Major split between async and sync APIs

## [0.0.2] - 2024-01-15

- Add support to `/animate` and `/find` requests

## [0.0.1] - 2023-12-20

- Add initial non-public implementation
