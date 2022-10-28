# Contributing to mafic

Thank you for your interest in contributing to mafic! We welcome contributions from the community. This document outlines the process to help get your contribution accepted.

## I Have a Question

For questions and support, please use the [Discussions Page](https://github.com/ooliver1/mafic/discussions).

## I Found a Bug

Please report bugs to [The Issues Page](https://github.com/nextcord/nextcord/issues/new/choose). Before reporting a bug, please do the following:

- Search the issue tracker to see if someone has already reported the bug.
- If your issue involves a traceback, please include **all** of it. It contains important information that can help us diagnose the problem including where the issue occured.

- Please provide as much information as possible about your issue. The issue template will help you with this, but more details are listed here
  - A **short summary** of your issue. This is a quick overview of what your issue is about.
  - Reproduction steps. This is a list of steps that can be followed to **reproduce the issue**. If you can, please provide a **minimal** code example that we can run to reproduce the issue.
  - Expected results. What did you **expect to happen?** This helps us see if your bug is, actually a bug.
  - Actual results. What happened instead. Do not use **"it doesn't work"** as a description. This is not helpful. Instead, explain what happened such as "<> error was thrown", "the music stopped playing", etc.
  - Information **about your environment.** This includes your operating system, Python version, version of mafic, version of lavalink, and any other relevant information.

Without providing this information, solving your issue is harder, and may be impossible, so please help us help you.

## Creating a Pull Request

Please make sure your PRs are properly scoped. This means that your PR should only contain one feature or bug fix. If you want to add multiple features or bug fixes, please submit multiple PRs.

Here is some helpful information and guidelines to contribute:

### Installing Dependencies Locally

Mafic uses [Poetry](https://python-poetry.org/) for dependency management. You may either install it globally, with `pipx`, or use a virtual environment. If you are using a virtual environment, you will need to install Poetry in that environment.

To install globally: <https://python-poetry.org/docs/#installing-with-the-official-installer>
To install in a virtual environment: <https://python-poetry.org/docs/#installing-manually>

To install the dependencies, run `poetry install` in the root directory of the project.

### Code Style

We use [Black](https://github.com/psf/black) for code formatting, [Isort](https://github.com/pycqa/isort) for import sorting, [Flake8](https://github.com/PyCQA/flake8) for code style linting, [Slotscheck](https://github.com/ariebovenberg/slotscheck) and several other [pre-commit hooks](https://github.com/pre-commit/pre-commit-hooks) for linting.

To use all of these at once, after [installing](#installing-dependencies-locally), you can simply run `task lint` in the root directory of the project, or `python -m task lint` (`py -m` etc) if that does not work.

If you want `pre-commit` to run automatically whenever you commit, you can use `task pre-commit`.

### Type Annotations

Mafic uses [Pyright](https://github.com/microsoft/pyright) for type checking. To use it, run `task pyright` in the root directory of the project, or `python -m task pyright` (`py -m` etc) if that does not work.

If type annotations are new to you, here is a [guide](https://decorator-factory.github.io/typing-tips/) to help you with it.

## Commits

Mafic follows the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) style. This means that your commit messages and PR titles should be formatted in a specific way. This is to help us generate changelogs and release notes, whilst also helping us review your pull requests as we can see what each commit does.

Your commit messages should be in the present (imperative, 2nd person) tense, such as `Add`, not `Added`.

Examples include:

```txt
feat: add support for some feature
```

```txt
refactor(track)!: use a different method to get track info

This is a breaking change because the method used to get track info has changed.
```

```txt
fix(node): use a different method to connect to the node

This fixes an issue where the node would not connect if the host was an IPV6 address.

Co-Authored-By: Some Person <email@example.com>
```

More specifically, we use the [Angular Types List](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#type) for commit types. This means that your commit messages should be formatted like this:

```txt
<type>([scope]): <subject>
[BLANK LINE]
[body]
[BLANK LINE]
[footer]
```

> **Note**
> The type and subject are mandatory.

### Type

`<type>` is one of the following:

- **build**: Changes that affect the build system or external dependencies
- **ci**: Changes to our CI configuration files and scripts such as GitHub Actions
- **docs**: Documentation only changes
- **feat**: A new feature
- **fix**: A bug fix
- **perf**: A code change that improves performance
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc)
- **test**: Adding missing tests or correcting existing tests

### Scope

`[scope]` is the name of the module affected (as perceived by the person reading the changelog generated from commit messages). Scope is not required when the change affects multiple modules. Some examples are:

- `node.py` - `node` is the scope
- `track.py` - `track` is the scope
- `typing/` - `typing` is the scope
- `utils/` - `utils` is the scope

## Subject

The subject should be a short summary of the commit, the body can be used for more info, so do not cram so much into the subject. Ideally this should be 50 characters or less, but it is not a hard limit, 72 characters is fine if necessary.

## Body

The body is an optional long description about the commit, this can be used to explain the motivation for the change, and can be used to give more context about the change. It is not required, but it is recommended.

## Footer

The footer contains optional metadata about the commit. These are sometimes added by git or similar tools, and examples include `Co-authored-by`, `Signed-off-by`, `Fixes`.
