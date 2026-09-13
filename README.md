# Rules Engine Template

A reusable starter for deterministic, source-backed tabletop rules engines.

The template provides:

- a deterministic .NET 10 Core project;
- replay-compatibility and random-source primitives;
- test infrastructure;
- exact SDK pinning;
- authoritative-source provenance and hash verification;
- bounded PDF source extraction;
- configurable rules-surface detection;
- repository invariant checks;
- local/CI validation parity;
- pull-request policy and rules-conformance gates.

The template intentionally starts with no authoritative rules corpus configured. A new project declares its own sources and rules surfaces after initialization.

## Create a new rules engine

On GitHub, open `brandonifco/rules-engine-template` and choose **Use this template**.

Clone the new repository and enter it:

```bash
git clone https://github.com/OWNER/REPOSITORY.git
cd REPOSITORY
```

Install the repository-pinned .NET SDK:

```bash
./scripts/bootstrap-dotnet.sh
```

Initialize the project identity:

```bash
PATH="$PWD/.dotnet:$PATH" ./scripts/init-rules-engine.py \
  --project-id my-rules \
  --project-name "My Rules Engine" \
  --project-prefix MyRules \
  --repo OWNER/REPOSITORY
```

The initializer is intentionally single-use. It replaces the template identity, renames the Core and test projects, updates project references, writes `framework.json`, and refreshes dependency lock files.

Arguments:

- `--project-id`: lowercase machine identifier matching `[a-z][a-z0-9-]*`
- `--project-name`: human-readable project name
- `--project-prefix`: identifier-style .NET namespace/project prefix
- `--repo`: GitHub repository in `OWNER/REPOSITORY` form

## Verify the new repository

Inspect the local development environment:

```bash
./scripts/doctor.sh
```

Run the canonical merge-equivalent validation gate:

```bash
./scripts/validate.sh full
```

For a faster inner loop:

```bash
./scripts/validate.sh fast
```

`validate.sh full` is the repository's single definition of an acceptable change. CI invokes the same gate rather than maintaining a separate build recipe.

## Configure the authoritative rules corpus

Source-backed rules work requires `.github/source-manifest.json`.

Example for one rulebook:

```json
{
  "schemaVersion": 1,
  "sources": [
    {
      "sourceId": "core-rules",
      "authority": 1,
      "title": "Core Rules",
      "edition": "Example Edition",
      "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
      "pdfPageCount": 300,
      "pageNumbering": {
        "printedPageEqualsPdfPageMinus": 12
      },
      "envVar": "CORE_RULES_PDF"
    }
  ]
}
```

The committed manifest identifies the authoritative source but never contains the local PDF path.

Configure your own local copy with either the manifest's environment variable:

```bash
export CORE_RULES_PDF=/absolute/path/to/core-rules.pdf
```

or a gitignored `source.local.json` in the primary checkout:

```json
{
  "core-rules": "/absolute/path/to/core-rules.pdf"
}
```

Then verify the configured file against the committed SHA-256:

```bash
tools/source-slice.py --source-id core-rules --verify-only
```

A hash mismatch is a hard failure. Do not change the manifest merely to make a different printing or scan pass.

## Extract bounded source packets

Use `tools/source-slice.py` to extract only the pages needed for the current rules task.

By PDF page:

```bash
tools/source-slice.py \
  --source-id core-rules \
  --pages 45-48 \
  --output /tmp/core-rules-45-48.txt
```

By printed page number:

```bash
tools/source-slice.py \
  --source-id core-rules \
  --printed-pages 33-36 \
  --output /tmp/core-rules-33-36.txt
```

For tables, add `--layout`. Use `--expect REGEX` when a known heading or term must appear in the slice.

Source packets are ephemeral review inputs. Do not commit extracted rulebook text or PDFs to the repository.

If the manifest declares exactly one source, `--source-id` may be omitted. With multiple sources it is required.

## Declare the rules surface

The bare template has no project-specific rules surface.

Create `.github/rules-surface-paths.txt` and list repository-relative paths whose changes require rules-conformance handling.

Example:

```text
src/MyRules.Rules/
src/MyRules.Data/
tests/MyRules.Rules.Tests/
```

Rules:

- one literal repository-relative path per line;
- blank lines are ignored;
- lines beginning with `#` are ignored;
- a trailing `/` matches the directory and all descendants;
- an entry without a trailing `/` matches one exact file;
- globs and regular expressions are not supported;
- `.github/source-manifest.json` is always part of the rules surface;
- `packages.lock.json` is excluded from rules-surface classification.

## Development workflow

For each change:

1. define scope and acceptance criteria in an Issue;
2. extract only the authoritative pages needed for rules work;
3. implement the smallest coherent change;
4. add or update tests;
5. run `./scripts/validate.sh full`;
6. open a pull request using `.github/pull_request_template.md`;
7. provide exact source locators for rules changes;
8. record required conformance verdicts for rules-surface changes;
9. merge only after repository gates are green.

The pull-request template also requires determinism impact, known limitations, agent provenance, and explicit confirmation that unrelated changes are absent.

## Determinism

Treat changes to any of the following as compatibility-sensitive:

- random-number consumption;
- ordering;
- serialization;
- replay identity;
- source-baseline identity;
- state transitions.

An apparently harmless extra random draw can change every later result. Preserve deterministic behavior deliberately and test it directly.

## Source boundary

The authoritative source files remain outside Git.

The repository may contain source identity and metadata, hashes, page-count and page-number mapping, derived code and structured data, tests, citations, and provenance.

The repository must not contain source PDFs, local absolute paths to those PDFs, committed source-extraction packets, or large copied sections of source text.

## Updating the template

Changes to the reusable framework should be made in `brandonifco/rules-engine-template`, validated there, and versioned deliberately.

A consuming rules-engine repository should evolve independently after initialization rather than pulling arbitrary template changes into an active rules implementation.
