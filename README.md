# Rules Engine Template — retired

**This repository is archived and should not be used.** It was the third iteration of an
attempt to make deterministic, source-backed rules engines reproducible. The fourth
iteration replaced it, and is where the work continues.

| Use this instead | For |
|---|---|
| [`rules-kernel`](https://github.com/brandonifco/rules-kernel) | The ruleset-agnostic foundation an engine references: replay identity, provenance, and the unresolved-result contract. Published to nuget.org, `net8.0;net10.0`. |
| [`rules-factory`](https://github.com/brandonifco/rules-factory) | The method for turning a written ruleset into an engine, and the corpus map that method produces. |

## Why it was retired

Not because it was broken — though it was, in ways recorded in its closed issues. Because it
was **the wrong kind of artifact**.

It tried to be two things at once: the product skeleton an engine starts from, *and* the
thing that produces engines. Because both lived in one repository, its tooling could not
tell which role it was serving. Four of its eight invariant checks examined files that only
exist in a produced engine, found nothing, and reported `ok` — a gate reporting PASS while
proving nothing, in a repository whose central claim was that prose does not fail a build
but checks do.

The deeper problem was the model. A template is copied and then diverges. Two engines built
this way each grew their own random source, their own replay identity, their own scripted
test double; the second corrected mistakes in the first; and because each owned its copy,
none of those corrections could reach the other. A copied foundation cannot be fixed once.

The kernel is referenced, not copied. Both engines now depend on it.

## What it got right, and what carried forward

The determinism discipline, the source-boundary handling, the single canonical gate, the
decision-record culture, and the insistence that an invariant worth stating is worth a
check — all of it survived, and most of it is stricter now. The kernel's checker has nine
checks and 105 tests for the checks themselves, which is the part this repository never had.

Its failures carried forward too, as lessons with names:

- A check that examines nothing must say so — and its **exit code** must say so, not just its
  output.
- A citation is a promise. This repository shipped 61 references to files that did not
  exist, several inside runtime error messages handed to users.
- Enforcement and the documents it cites ship together, or neither ships.
- A test whose expectation is computed the same way as the thing it checks can only confirm
  that the code does what it does.

## What is still here

Everything, unchanged, at the commit it was archived on. The git history, the tooling, and
twenty closed issues that each say where their subject went. Nothing was deleted, because
the record of why a design was abandoned is worth more than the design.

The `deckardII` repository that produced it, and the extraction pipeline inside it, are
likewise intact.
