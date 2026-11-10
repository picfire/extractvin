# idle approach

Personal instructions for agents working on idle projects:
code style rules, approaches to working with the code, and tools.

## Agent Role

- Primary areas of expertise: architecture, security, systems programming, and web services.
- Preferred stack: Linux, Python, Rust, TypeScript, PostgreSQL, and SQLite.
- Communicate in English, concisely and specifically; avoid awkward literal translations.
- Verify hypotheses against source code and distinguish assumptions from facts.

## General Rules

- After each stage, briefly report the result and the next planned stage. If the work is
  complete and there is no next stage, say so explicitly.

### Security

- Security is one of the project's key requirements.
- The application must ensure not only that its code runs safely and reliably, but also
  that the data it handles remains safe.
- Prevent errors that could lead to compromise. Report critical issues in the same
  session, emphasizing their demonstrably possible consequences.
- Do not expose confidential data in results, errors, or diagnostics.

### Scope

- General rules apply regardless of programming language. The Python section applies to
  Python code, the Rust section to Rust code, and the Django section to Django projects.
- This document defines personal project standards. Explicit task requirements and
  clarifications in the project's `AGENTS.md` take precedence over its general rules and
  defaults. If a conflict remains unresolved, ask the owner rather than changing the
  rules independently.
- Apply these rules to new code and code touched by the task. Bring nearby code into
  compliance only when necessary for the task; perform broad reorganizations only after
  the owner's approval.

### Working With Changes

- Follow the project's conventions and structure. Check its `AGENTS.md`, `README.md`,
  documents in `docs/`, and existing code for project-specific details.
- Stay within the task's scope; propose unrelated fixes before making them.
- If you notice typos in code or comments, propose correcting them.
- When fixing a bug, preserve all other observable behavior.
- Always disclose backward-incompatible changes explicitly.

### Compatibility for Projects Not Yet Public - WIP

- Backward-compatibility commitments begin only after the project owner explicitly
  declares them. Until then, do not add compatibility layers, version formats or data
  structures, or tests for old releases. Once compatibility is declared, preserve it
  within a major application version; incompatible changes require a major version
  increment and checks against examples of previously supported formats. Introduce
  versioning for schemas, formats, and interfaces only with the project owner's approval.

### Architecture

#### Modules and Reuse

- Organize primitives and operations into logically distinct modules for protocols,
  transport, file handling, validation, logging, and application workflows. Do not put
  everything in an entry point or an unstructured `utils` module; do not split code
  without a reason.
- Do not duplicate code. Extract shared behavior only when it is actually reused.

#### State, Resources, and Errors

- Group related state, resources, and operations into classes or structures when
  appropriate. Classes and structures may serve as namespaces when they group related
  data and methods.
- Importing a module or creating an object must not unexpectedly access the network,
  start processes, modify files, or launch background work. State initialization and
  argument validation are acceptable; perform external actions explicitly.
- Release resources on normal completion, errors, and cancellation.
- Validate inputs at system boundaries. Do not suppress errors; distinguish expected
  errors from programming errors. Handle errors where the operation can be completed
  correctly, its state preserved, and the result reported. Do not add implicit retries
  for dangerous actions.
- Justify performance changes with measurements, while preserving reliability and
  functionality.

### Dependencies and Portability

- Do not tie a package to the repository location, a developer's working directory,
  specific hardware, or a particular runtime environment.
- Prefer the standard library and already-adopted dependencies. Do not add a library or
  custom implementation that duplicates an existing one. Keep development tools separate
  from runtime dependencies.
- Do not include environment files (`.env`), caches, dumps, temporary results, secrets,
  or other sensitive information in distributions.

### CLI

The rules in this subsection apply only to packages with a command-line interface.

- After adding a command, verify that it runs from an unrelated working directory.
- Keep the CLI responsible only for arguments, command selection, user interaction,
  result presentation, and exit codes.
- Lower layers must not depend on the CLI.
- Send CLI diagnostics to stderr. Send data intended for programs (such as JSON) to
  stdout without log messages mixed in. Help and confirmation prompts belong in the CLI.

### Logging and Progress

- Choose log levels by meaning: `DEBUG`, `INFO`, `WARNING`, and `ERROR`.
- Keep application progress notifications separate from diagnostics. Structured events
  or progress callbacks are acceptable for GUI and web interfaces; do not derive progress
  by parsing logs.
- Configure log handlers and formats at the entry point. Library code must not reconfigure
  global logging.
- CLI and log messages must be in English. Do not log secrets or complete data, including
  binary data.
- If a project requires mandatory logging or auditing, its completeness must not depend
  on the diagnostic logging level or handlers.

### Code Style

- Use double quotes for string literals.

#### Names

- Use meaningful names. Never use single-letter variable names. Examples: `s` → `source`,
  `i` → `idx`, `p` → `path`, `u1` → `user_1`, and `r2` → `response_2`.
- Start function and method names with a verb and express an action, such as
  `filter_known_fields`, `read_database`, or `create_empty_entry`. Use `is_`, `has_`,
  `can_`, or `should_` for predicates, such as `is_valid_image_path`.

#### Imports

- Imports usually belong at the top of a module. A justified exception is a circular
  import.

#### Blank Lines and Logical Blocks

- Separate logical sections inside functions and methods with one blank line (LF).
- Do not use two or more consecutive blank lines in code.

#### Comments and Docstrings

- Write comments and documentation in clear, standard language, using little slang.
- Comments should explain non-obvious constraints and reasons, not repeat the code.
- Remove outdated comments.
- Document public methods in plain language.

### Development Tools

- Do not use obsolete tools when suitable newer tools are available.
- Run linters and formatters only when the owner directly requests it, including
  check-only modes.
- Do not reformat code you did not touch.

### Documentation

- Write descriptions in simple language accessible to a broad audience.

#### README

- The file should briefly but fully describe the project's functionality and the value it
  provides.
- Avoid excessive detail, including technical detail.
- If extended documentation exists, link to it from the README.
- If no extended documentation exists, the README may include examples of basic tools
  provided by the application.
- Do not use relative links: the README may be displayed where source files are unavailable.
- Do not use absolute filesystem paths.

#### User Documentation

- Store user documentation in `docs/`.
- It must include:
  - Minimum dependency requirements (for example, Python 3.15+).
  - Brief installation instructions, no longer than two or three lines.
- It may explain how to contribute to the project.
- A separate quickstart section may address a basic user need in a minimal form and then
  grow step by step in complexity.
- When API documentation is needed, prefer automated documentation tools such as
  `mkdocs-apidescribed-plugin`.

#### INSTALL

- The file should briefly describe how to install the application.

#### CONTRIBUTING

- The file should briefly describe ways to contribute to the application.
- It is important to state that contributors, including agents, must follow `IDLE.md`.

#### LICENSE

- The file must contain the license text.
- Unless otherwise specified, use the BSD 3-Clause license.


### Testing

- Do not duplicate existing tests or tests already provided by used libraries,
  frameworks, or applications.

#### Structure and Scenarios

- For new standalone packages, keep tests in `tests/`; mirror the package module
  hierarchy in test file locations, except for the package root.
- Group tests by public behavior.
- Do not write separate tests for private methods.
- Find existing tests by checking the test tool configuration and the actual project
  structure, not only `tests/`. The rule for locating new tests does not limit where you
  search.
- Cover successful, failing, and boundary scenarios, especially failures before writing,
  partial completion, cancellation, and resource release.
- Aim for a small, fast test suite. Avoid excessive or duplicate checks; combine similar
  cases when that remains clear. Review and extend existing tests where appropriate and
  consistent with the other rules.
- Keep conditional logic inside test functions to an absolute minimum.
- Separate setup, action, and assertions with blank lines; Arrange/Act/Assert comments are
  optional. Test names should explain the scenario without being verbose.
- For errors, check the type and meaningful message text.
- Do not write tests for tests or tests for documentation.

#### Fixtures, Data, and Time

- Review and reuse existing fixtures; use parametrization for variants. Choose the
  smallest necessary scope and data volume.
- Do not create a fixture for one-time use, except for resource management, environment
  setup, or guaranteed cleanup.
- Small data may live directly in a test. Store larger data in a nearby `datafixtures`
  subdirectory.
- If time or randomness affects a result, control it by replacing the dependency. Do not
  use real waits to test timers or durations.
- Do not weaken production checks for the sake of a test.

#### Isolation and Substitutions

- The general test suite must not depend on execution order, physical hardware, external
  networks, or privileges.
- Automated tests must not require administrative privileges, modify working system
  directories, logs, or services, or affect user sessions. Substitute external
  interactions and third-party services, or run them in an isolated test environment
  that does not affect the working system or user data.
- Make broad use of substitutes for external processes and system interfaces, including
  command results, access errors, and disappearing external objects. Substitute external
  interactions, but not the calculations, validation, serialization, or application
  decisions being tested.
- Unit tests must not create real external connections, including HTTP/TLS; substitute
  those interactions.
- Integration tests verify real interactions among the components under test in isolation.
  Temporary local servers and other necessary isolated components are acceptable.
- Check response and error handling.

#### Test Suite Boundaries

- Do not create a separate heavy-test suite within the general suite.
- Check the same public behavior locally and in CI.
- Do not introduce additional test infrastructure, including VM checks, coverage, or
  Hypothesis, unless the task requires it. Preserve the project's existing test
  infrastructure.
- End-to-end tests may live in a separate, explicitly invoked suite. Do not include them
  in the general test run locally or in CI.
- Do not test internal mechanisms of third-party build or installation tools.

### Files

- Every edited text file must end with exactly one terminating LF, with no extra blank
  lines or trailing whitespace.

### Checks and Reporting

- After making changes, run relevant checks and report their actual results. If a check was
  not run, say so explicitly; do not present it as successful.

## Python

### Packaging

#### Structure and Dependencies

- Package new standalone applications as portable Python 3.12+ projects with a `src`
  layout and `pyproject.toml`, using `hatchling` rather than setuptools for builds.

#### Distributions and Support Files

- Include the package, required runtime resources, metadata, and licenses in the wheel.
  Include source files and everything needed to build in the sdist: `pyproject.toml`,
  files used to build the README, licenses, build scripts, and resources. Do not include
  tests or test data in the wheel or sdist.
- Do not track `uv.lock` in VCS for libraries and applications installed from packages.
  For web services deployed from a repository, track `uv.lock` for reproducible
  deployment. Do not include `uv.lock` in the wheel or sdist.

### CLI

- Use a command in `[project.scripts]` as the entry point, for example
  `<package>.cli:main`. Do not create `main.py` or `__main__.py`; a `main()` function in
  `cli.py` is acceptable.
- Lower layers must not depend on `argparse.Namespace`, `input`, or `print`.

### Logging and Progress

- Use the standard `logging` module and module-level loggers such as
  `logging.getLogger(__name__)` for diagnostics, rather than `print` or custom callbacks.
- Use deferred formatting for logging:
  `logger.info("Read %d bytes", size)`. Use f-strings for ordinary string construction.

### Code Style

#### Names and Types

- Name properties (`@property`) and pytest fixtures as data or resources.
- Annotate arguments and return values for all functions and methods, including private
  ones. Use keyword-only parameters when they prevent confusion.
- Add `from __future__ import annotations` only when deferred annotations are needed, for
  example to refer to not-yet-defined types or imports guarded by `TYPE_CHECKING`. Do not
  add it to every module by habit.

#### Imports

- Use absolute imports for external dependencies and relative imports within the
  application. `import *` is prohibited.
- Lazy imports are acceptable for a specific reason, such as allowing help and library
  imports to work without an optional backend.

#### Language Features and Practices

- Prefer `pathlib.Path` for paths, retaining low-level `os` operations when descriptor-level
  guarantees are needed.
- Store repeated reads of the same attribute (or attribute chain) or unchanged dictionary
  value in a variable when that improves readability. If the dictionary may have changed,
  read its current value again.
- Use the `:=` (walrus) operator when it avoids repeated computation and improves
  readability, both in loops and comprehensions. For example:
  `names = {name_ for name in names_all if (name_ := name.strip())}`.

#### Blank Lines and Logical Blocks

- Leave exactly one blank line before `with`, `for`, `while`, and `if` blocks, and before
  `elif` and `else`. This also applies to the first block after a function declaration
  and to nested blocks.
- Leave exactly one blank line before `except`. After blocks and `raise`, leave one blank
  line if more code follows in the function. Do not add an extra blank line at the end of
  a file; the single terminating LF rule applies.

#### Strings

- For ordinary value conversion and formatting, use f-strings instead of `str()`,
  `format()`, or the `%` operator. The exception is deferred formatting for `logging`
  messages, as described above.

#### Files

- Do not leave `.py` files containing only comments; `__init__.py` is the exception.

### Development Tools

#### makeapp

- For local development, use [makeapp](https://pypi.org/project/makeapp/): run `ma tools`
  and `ma tests` from the specific package directory. Do not use makeapp in CI; run tests
  with pytest.
- For local work and CLI development, install from the package directory with
  `ma up --tool`. Run the command directly by name. Do not describe alternative
  installation methods or manual environment management in user instructions.

#### Formatting

- When Python formatting is explicitly requested, use Ruff with the package settings.
  Keep lines to 129 characters or fewer, or follow a stricter package formatter limit.

### Testing

#### Environment and Tools

- Use pytest as the test framework. For file-based data, use `pytest-datafixtures`; for
  mocking HTTP responses from external systems when using `requests`, use
  `pytest-responsemock` and its `response_mock` fixture; for Django applications, use
  `pytest-djangoapp`; and for controlling calendar time, use `time-machine` (the import
  and pytest fixture are both named `time_machine`). These are development dependencies,
  separate from application runtime dependencies.

#### Structure and Scenarios

- For example, `src/pkg/model/config.py` corresponds to `tests/pkg/model/test_config.py`.
- Add test docstrings only for non-obvious cases.
- Check exceptions with `pytest.raises(..., match=...)`.

#### Fixtures, Data, and Time

- Put shared fixtures in `conftest.py`. When variants need names, use
  `pytest.param(..., id="name")`.
- Request fixtures through test parameters rather than importing fixture functions.
- Create callable fixtures when flexible argument passing is needed; these fixtures must
  return a callable object.
- Store large saved samples in `tests/datafixtures/` and read them with
  `pytest-datafixtures`.
- Use `tmp_path` for files and `caplog` for logs.
- Do not use `time-machine` 3.x to replace monotonic clocks. Replace the required monotonic
  time source separately in the code under test, not globally.

#### Test Suite Boundaries

- Check the package's wheel/sdist contents and installation when relevant to the task,
  for example when changing package resources or entry points.

## Rust

### State, Resources, and Errors

- In production code, return expected errors through `Result` and propagate them with `?`.
  Do not use `panic!`, `unwrap`, or `expect` for invalid input or external operation errors.
- Release resources through ownership and `Drop`. If the result of an operation matters,
  return it explicitly; cleanup in `Drop` is not a substitute for error handling.

### Code Style

- Prefer `Path` and `PathBuf` for paths, retaining low-level operations where descriptor
  guarantees are needed.
- The prohibition on single-letter variable names does not apply to type parameters or
  lifetimes.
- Data access methods may be named after the data or resource. Preserve standard Rust
  constructor and method names.

### Testing

- Do not create a directory for a single module; use one file instead of a directory
  containing only `mod.rs` when that is sufficient.
- Run checks with `cargo test` and `cargo check` from the specific package directory.

## Django

### Models

- Do not access foreign keys from model `__str__()` methods.

### URLs and Namespaces

- Set `app_name` in `urls.py` to create a namespace.
- Define hierarchical URLs directly in `urlpatterns` as a nested tree such as
  `path("prefix/", include([path(...), ...]))`: place child `path` entries inside
  `include`, not in a flat list or intermediate variables such as `limits_patterns`.

### Migrations

- Create and regenerate schema-change migrations with Django commands.
- For authored data migrations and special `RunPython` or `RunSQL` operations, create an
  empty migration with `makemigrations --empty`, then add the required operations and
  transformation code.
- Do not rewrite already-applied migrations without the owner's approval, unless the
  project explicitly allows regenerating initial migrations during development.
- Use Django's built-in migration tools; do not create a separate automated test suite for
  the migration mechanism. Test custom data-transformation logic.

### Testing

- Do not use `django.test.TestCase` for Django tests. Use pytest.
- In Django tests, do not hardcode internal URLs; obtain them with `reverse()`. Do not
  call `reverse()` repeatedly; create and use `url_*` fixtures.
- When using fixtures that count database queries, keep the expected query count current:
  verify actual values rather than inventing numbers.

----

Source and current version: https://gist.github.com/idlesign/206cad37df9a9cfbe1a366ff6dc1bd06
