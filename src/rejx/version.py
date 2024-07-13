"""Return rejx version."""

from importlib import metadata  # pragma: no cover

# Used to automatically set version number from github actions
# as well as not break when being tested locally
try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
