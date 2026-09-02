# Contributing to NER Studio

NER Studio is archived and no longer under active feature development. Contributions should normally be limited to correcting documentation, preserving historical context, or addressing clear repository issues. Forks are welcome for continued learning and development.

## Development Workflow

1. Make changes on `develop` or on a short-lived branch created from `develop`.
2. Keep each change focused and use clear commit messages.
3. Test the affected front-end or back-end area when the change touches executable code.
4. Open a pull request targeting `develop` for ordinary collaborative work.
5. After the changes on `develop` have been reviewed and confirmed stable, open a pull request from `develop` to `main`.
6. Use **Create a merge commit** when merging the two long-lived branches; do not repeatedly rebase `develop` and `main`.
7. Create release tags only from `main`.
8. Merge the updated `main` back into `develop` after each release so both branches share the release commit.

Direct pushes and force pushes to `main` are not part of the normal workflow.

## Pull Requests

- Describe what changed and why.
- Keep unrelated changes in separate pull requests.
- Update the English and Simplified Chinese documentation together when user-facing information changes.
- Do not present planned or incomplete functionality as implemented.
- Preserve the repository's archived status and accurately document known limitations.

## License

Unless explicitly stated otherwise, contributions submitted to this repository are provided under the repository's [MIT License](LICENSE).
