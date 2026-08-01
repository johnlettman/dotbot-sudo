<div align="center">
  <h1>Dotbot Sudo Plugin<br>
  <sub><sup><code>dotbot-sudo</code></sup></sub></h1>
</div>

[![License][shield-license]][url-license]
![Programming Language][shield-language]
[![CI Results][shield-ci]][url-ci]
[![codecov][shield-codecov]][url-codecov]

A plugin for [Dotbot][url-dotbot] that runs a group of Dotbot directives with
root privileges through `sudo`.

Originally created by [DrDynamic][url-drdynamic], this repository maintains the
plugin and its development workflow.

## Prerequisites

This plugin requires [Dotbot][url-dotbot], `sudo`, and Python 3.10 or newer.

## Installation

Add [dotbot-sudo][url-repo] as a submodule to your dotfiles repository:

```bash
git submodule add https://github.com/johnlettman/dotbot-sudo.git
```

Pass the plugin file to Dotbot with `--plugin`:

```bash
dotbot --plugin path/to/dotbot-sudo/sudo.py
```

## Usage

Add the `sudo` directive to your Dotbot YAML configuration. Its value is a list
of ordinary Dotbot tasks:

```yaml
- sudo:
    - clean:
        - /root/.cache
    - shell:
        - echo "running as root"
```

The nested Dotbot process inherits the terminal, so commands such as package
managers can prompt for credentials or package-build confirmations normally.

## Details

| Option | Required | Description |
|--------|----------|-------------|
| `sudo` | Yes | A list of Dotbot directives to execute with root privileges. |

The plugin preserves the current Dotbot defaults and forwards loaded plugin
arguments to the nested invocation.

## Development

Install the development environment with Poetry, then run:

```bash
make install-deps
make lint
make test
make check-generated-requirements
```

Generated requirement files come from `pyproject.toml` and are checked in CI.

[url-dotbot]: https://github.com/anishathalye/dotbot
[url-drdynamic]: https://github.com/DrDynamic/dotbot-sudo
[url-repo]: https://github.com/johnlettman/dotbot-sudo
[url-license]: https://github.com/johnlettman/dotbot-sudo/blob/master/LICENSE
[url-ci]: https://github.com/johnlettman/dotbot-sudo/actions/workflows/ci.yml
[url-codecov]: https://app.codecov.io/gh/johnlettman/dotbot-sudo

[shield-license]: https://img.shields.io/badge/License-MIT-green?style=for-the-badge
[shield-language]: https://img.shields.io/github/languages/top/johnlettman/dotbot-sudo?style=for-the-badge
[shield-ci]: https://img.shields.io/github/actions/workflow/status/johnlettman/dotbot-sudo/ci.yml?style=for-the-badge&label=CI
[shield-codecov]: https://img.shields.io/codecov/c/github/johnlettman/dotbot-sudo?style=for-the-badge
