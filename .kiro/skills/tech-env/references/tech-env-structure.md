# tech-env.md Document Structure

Use this as the skeleton when producing the final document. Include only the sections that apply (greenfield vs brownfield). Remove placeholder comments before delivering.

## Minimal Format

For teams that need to start quickly. AI-DLC will ask clarifying questions for anything missing.

````markdown
# Technical Environment: [Project Name]

## Language and Package Manager

- **[Language] [version]**
- **[Package manager]** for all dependency management
- [Any version pinning or lockfile conventions]

## Web Framework

- **[Framework]** with [validation library] for request/response validation
- [Any adapter or deployment wrapper, e.g., Mangum for Lambda]

## Cloud and Deployment

- **[Cloud provider]**, [account structure], [region(s)]
- **[Deployment model]**: [e.g., Lambda behind API Gateway, ECS Fargate, etc.]
- **[IaC tool]** for all infrastructure

## Testing

- **[Test framework]** with [coverage tool] ([coverage target])
- **[Type checker]** [mode]
- **[Linter/formatter]**
- [Any additional test tools, e.g., moto, hypothesis, testcontainers]

## Do NOT Use

| Prohibited          | Reason              | Use Instead         |
| ------------------- | ------------------- | ------------------- |
| [library/service]   | [why]               | [alternative]       |

## Security Basics

- [Auth model — one line]
- [Secrets management — one line]
- [Input validation approach — one line]
- [Encryption requirements — one line]
- [Compliance standards — one line, or "None specific"]

## Example Code Patterns

[One endpoint example, one domain function example, one test example.
Must be working code, not pseudocode.]
````

## Comprehensive Format

For teams that want a complete reference. Follows the full Technical Environment
Document Guide structure.

````markdown
# Technical Environment: [Project Name]

## Project Technical Summary

- **Project Name**: [name]
- **Project Type**: [Greenfield / Brownfield]
- **Primary Runtime Environment**: [Cloud / On-Premises / Hybrid]
- **Cloud Provider**: [provider]
- **Target Deployment Model**: [Serverless / Containers / VMs / Hybrid]
- **Team Size**: [number and composition]
- **Team Experience**: [key skills relevant to tech choices]

## Programming Languages

### Required Languages

| Language   | Version   | Purpose   | Rationale   |
| ---------- | --------- | --------- | ----------- |
| [lang]     | [ver]     | [purpose] | [why]       |

### Permitted Languages

| Language   | Conditions for Use   |
| ---------- | -------------------- |
| [lang]     | [when approved]      |

### Prohibited Languages

| Language   | Reason   |
| ---------- | -------- |
| [lang]     | [why]    |

[Brownfield only: Existing Language Inventory table]

## Frameworks and Libraries

### Required Frameworks

| Framework/Library   | Version   | Domain   | Rationale   |
| ------------------- | --------- | -------- | ----------- |
| [framework]         | [ver]     | [domain] | [why]       |

### Preferred Libraries

| Library   | Purpose   | Use When   |
| --------- | --------- | ---------- |
| [lib]     | [purpose] | [when]     |

### Prohibited Libraries

| Library   | Reason   | Alternative   |
| --------- | -------- | ------------- |
| [lib]     | [why]    | [use instead] |

## Cloud Environment

### Service Allow List

| Service   | Approved Use Cases   | Constraints   |
| --------- | -------------------- | ------------- |
| [service] | [use cases]          | [limits]      |

### Service Disallow List

| Service   | Reason   | Alternative   |
| --------- | -------- | ------------- |
| [service] | [why]    | [use instead] |

## Preferred Technologies and Patterns

### Architecture Pattern

[Architecture style, deployment model, module boundaries — brief description]

### API Design Standards

- **Style**: [REST / GraphQL / gRPC]
- **Versioning**: [strategy]
- **Naming Convention**: [URL and JSON field conventions]
- **Error Format**: [standard error response structure with example]

### Data Patterns

- **Primary Data Store**: [store and access pattern]
- **Caching Strategy**: [approach]

## Security Requirements

### Authentication and Authorization

- **Auth Method**: [method]
- **Authorization Model**: [model]

### Data Protection

- **Encryption at Rest**: [approach]
- **Encryption in Transit**: [approach]
- **PII Handling**: [policy]

### Secrets Management

- **Storage**: [tool]
- **Prohibited Practices**: [list]

### Compliance

- **Standards**: [list or "None specific"]
- **Security Framework**: [framework name and version, or "Internal checklist"]

### Dependency Security

- **Scanning**: [tool and frequency]
- **License Policy**: [allowed and prohibited licenses]

## Testing Requirements

| Test Type        | Required   | Coverage Target   | Tooling   |
| ---------------- | ---------- | ----------------- | --------- |
| Unit             | [yes/no]   | [target]          | [tool]    |
| Integration      | [yes/no]   | [scope]           | [tool]    |
| End-to-End       | [yes/cond] | [scope]           | [tool]    |
| Contract         | [yes/cond] | [scope]           | [tool]    |
| Performance      | [yes/cond] | [scope]           | [tool]    |
| Security         | [yes/no]   | [scope]           | [tool]    |

### CI/CD Testing Gates

| Pipeline Stage   | Required Tests   | Failure Action   |
| ---------------- | ---------------- | ---------------- |
| Pre-commit       | [tests]          | [action]         |
| Pull Request     | [tests]          | [action]         |
| Pre-deploy       | [tests]          | [action]         |
| Post-deploy      | [tests]          | [action]         |

## Example Code Patterns

[Endpoint example, domain function example, test example.
Must be working code with corresponding tests.]

## Brownfield: Existing Technical Inventory

[Only for brownfield projects]

### What to Keep Unchanged

| Technology/Service   | Reason to Keep   |
| -------------------- | ---------------- |
| [tech]               | [why]            |

### What to Migrate

| Current   | Target   | Priority   | Approach   |
| --------- | -------- | ---------- | ---------- |
| [current] | [target] | [H/M/L]   | [how]      |

### What to Remove / Not Introduce

| Item   | Reason   | Removal Timeline   |
| ------ | -------- | ------------------ |
| [item] | [why]    | [when]             |

### Coexistence Rules

[How old and new patterns live together during transition]
````
