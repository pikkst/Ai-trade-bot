# Frontend npm Audit Exceptions

This document records known frontend dependency vulnerabilities that are accepted for the MVP phase.

## Accepted Exceptions

### esbuild (moderate)

- **Package**: esbuild <=0.24.2
- **Advisory**: GHSA-67mh-4wv8-2f99
- **Exploitability**: Enables websites to send requests to the dev server and read responses
- **Remediation**: Upgrade vite to >=8.2.0 (breaking change; tracked for M002+)

### react-router (moderate)

- **Package**: react-router 6.0.0 - 7.17.0
- **Advisory**: GHSA-wrjc-x8rr-h8h6 (open redirect via backslash), GHSA-337j-9hxr-rhxg (arbitrary constructor injection)
- **Exploitability**: Requires user interaction with crafted links or SSR hydration
- **Remediation**: Upgrade react-router to >=7.18.0 (tracked for M002+)

### react-router-dom (moderate)

- **Package**: react-router-dom 6.0.0-alpha.0 - 7.17.0
- **Advisory**: Depends on vulnerable react-router versions
- **Exploitability**: Inherited from react-router
- **Remediation**: Resolved by upgrading react-router to >=7.18.0

### vite (high)

- **Package**: vite <=6.4.2
- **Advisory**: Depends on vulnerable esbuild versions
- **Exploitability**: Inherited from esbuild; requires dev server interaction
- **Remediation**: Upgrade vite to >=8.2.0 (breaking change; tracked for M002+)

## Policy

- Severity threshold for CI: moderate and above
- Exceptions are time-bounded and reviewed quarterly
- New vulnerabilities must be assessed within 7 days of discovery
