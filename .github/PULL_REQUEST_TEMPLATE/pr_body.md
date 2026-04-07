## Summary

Adds the project README and supporting documentation files that were missing from the repository.

### Changes

- **`README.md`** – Full project documentation: features, tech stack, installation, configuration, project structure, usage guide, and a known-limitations/roadmap section that links to the open issues.
- **`.env.example`** – Template for required environment variables (`GITHUB_TOKEN`, `GITHUB_USERNAME`) so contributors know what to configure.
- **`.github/ISSUE_TEMPLATE/`** – Issue body files used to create the 6 code-review issues filed in this PR.

### Related Issues

This PR was created as part of a code-review pass. The issues found and filed are:

| # | Title |
|---|-------|
| #1 | [Bug] Card and edit GET routes return 500 when item ID does not exist |
| #2 | [Security] GitHub token accepted as plaintext form field in sync endpoint |
| #3 | [Bug] Timezone mismatch: standup cutoff uses `datetime.utcnow()` but SQLite stores local time |
| #4 | [Enhancement] Add input validation for enum fields (status, priority, severity) |
| #5 | [Performance] GitHub sync loads all records into memory for URL deduplication |
| #6 | [Enhancement] Add pagination to list views |

### Checklist

- [x] README covers all major features
- [x] Setup instructions are accurate
- [x] `.env.example` added with placeholder values
- [x] Known limitations / roadmap section lists all filed issues
