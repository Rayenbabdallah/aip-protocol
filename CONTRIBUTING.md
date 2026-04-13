# Contributing to AIP

## Welcome

We are defining the foundation of how intelligence negotiates, structures, and commits to work natively. AIP is an open protocol. It belongs to everyone who builds on it. 

## Ways to Contribute

- **Implement AIP** in a new language (TypeScript, Rust, Go).
- **Build an agent** using AIP and share its interaction trace.
- **Open issues** resolving structural ambiguities or execution violations.
- **Propose primitives** or lifecycle extensions formally for v0.2.
- **Improve documentation** mapping out the standard clearer.

## Spec Contributions

The protocol defines the absolute bounds of agent interaction. Changes require precision.

- Changes to the spec require an issue first. Do not open a PR blindly.
- Label the issue specifically as `spec-proposal`.
- Describe structurally: what problem it solves, exactly what primitive or rule it affects, and what the alternative is.
- Spec changes demand open consensus and discussion before a pull request can be evaluated.

## Code Contributions

- Fork the repository locally.
- Create an intentional branch: `feature/your-feature` or `fix/your-fix`.
- Write exact tests for anything new you inject into the SDK natively.
- Run `pytest` ensuring execution boundaries hold before submitting.
- Submit a PR with a clean, clear description mapping your logic.

## Issue Labels

- `spec-proposal` — modifications to core AIP primitives or formal rules.
- `implementation` — building out a new language SDK natively.
- `bug` — something is functionally broken.
- `discussion` — open questions mapping unhandled logic vectors.
- `v0.2` — logic slated formally inside the candidate for the next version.

## Code of Conduct

Build in good faith. Disagree with ideas, not people. AIP's success is measured in agents connected.

## Governance

AIP v0.1 is authored by Rayen Ben Abdallah. 
v0.2 will be structurally shaped by the active working group natively. 

If you want a seat pushing logic at the table, simply open an issue titled `"AIP v0.2 working group"` to join.
