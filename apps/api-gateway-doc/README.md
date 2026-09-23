# API Gateway — Enterprise Architecture & Operating Model

> **Status:** source notes for the official document, current as of version 1.0 (2026-09-21).
> The official document is `API_Gateway_Enterprise_Architecture_Standard.docx`; every issued version is in `versions/`.
> Where the two differ (wording, merged sections), see `CHANGES.md`.

## 1. Purpose

The API Gateway is an enterprise infrastructure layer positioned between API consumers and backend services.

Its purpose is to provide a consistent, secure, observable, and governed entry point for web traffic while allowing application teams to manage their APIs independently within organizational guardrails.

The API Gateway is **not a business-logic layer**.

The core principle is:

> **Application teams own their APIs and business policies. The infrastructure team owns the platform, its capabilities, and the technical guardrails around it.**

The platform should enable application teams to expose and manage APIs without requiring the infrastructure team to understand or implement the business logic of each application.

---

# 2. Scope

The API Gateway is intended to handle **web traffic** to backend services.

The architecture should not be unnecessarily coupled to a specific application protocol.

The platform should be capable of supporting technologies such as:

* HTTP/HTTPS
* GraphQL
* gRPC
* MCP
* Other web-based API technologies

SOAP is outside the intended scope.

The following are within scope:

* WebSocket and streaming traffic
* Service-to-service (east-west) traffic
* Multi-tenant use of the platform
* Non-production environments

The scope is intentionally expressed as **web traffic** rather than defining the platform around a fixed list of protocols.

---

# 3. Core Principles

## 3.1 Central API Entry Point

APIs exposed for consumption outside their immediate service boundary should be exposed through the API Gateway.

Direct exposure that allows consumers to bypass the organization's authentication, authorization, rate limiting, logging, and security controls should not be permitted.

The Gateway therefore provides a consistent enforcement point for API access.

APIs without consumer authentication (anonymous APIs) are not permitted.

---

## 3.2 Self-Service with Guardrails

The preferred operating model is:

> **Self-Service with Guardrails**

Application teams should be able to:

* Create APIs
* Configure routes
* Configure backend mappings
* Configure authentication requirements
* Configure authorization policies
* Configure rate limits
* Configure transformations
* Configure caching where appropriate
* Manage API versions
* Manage consumers
* Manage API lifecycle

The infrastructure team should provide the platform and enforce organizational requirements where technically appropriate.

Not every organizational guideline needs to become a hard technical restriction.

---

## 3.3 Application Ownership

The application team owns the API.

This includes:

* API design
* API contract
* Business semantics
* Consumers
* Access requirements
* Authorization requirements
* Versioning
* Deprecation
* Retirement
* Documentation
* Consumer lifecycle

The infrastructure team should not become the owner of the API simply because the API is implemented through the Gateway.

---

# 4. Responsibility Model

| Area                    | Application Team                      | Infrastructure Team          |
| ----------------------- | ------------------------------------- | ---------------------------- |
| API design              | Owner                                 | Platform support             |
| API contract            | Owner                                 | Platform capability          |
| Business logic          | Owner                                 | Not responsible              |
| Consumers               | Owner                                 | Platform capability          |
| Authorization policy    | Defines requirement                   | Provides enforcement         |
| Authentication platform | Consumes                              | Provides                     |
| Routing                 | Defines destination                   | Provides capability          |
| Rate limiting           | Defines requirement                   | Provides capability          |
| Health checks           | Defines appropriate endpoint/behavior | Provides capability          |
| Gateway platform        | Consumer                              | Owner                        |
| Availability of Gateway | —                                     | Owner                        |
| GitOps platform         | Consumer                              | Provides                     |
| Logging platform        | Consumes                              | Provides                     |
| Audit                   | Participates                          | Platform owner               |
| WAF                     | Separate capability                   | Separate responsibility      |
| Load Balancing          | Application/platform architecture     | Provides Gateway integration |

---

# 5. Authentication and Consumer Model

The API Gateway should distinguish between two primary consumer categories:

* **C2B — Consumer to Business**
* **B2B — Business to Business**

These categories describe the consumer and its identity model, rather than a specific product implementation.

---

## 5.1 C2B

C2B represents access where the consumer is a human user.

The user must authenticate through the organization's Identity Provider (IdP).

The expected model is:

```text
User
  |
  | Authenticate
  v
Identity Provider
  |
  | Short-lived Access Token
  v
API Gateway
  |
  | Authorized request
  v
Backend
```

C2B access must use **short-lived access tokens** issued by the organization's IdP.

The lifetime of the access tokens is defined by the owner of the Identity Provider and is not defined here.

The API Gateway validates the identity and relevant claims.

The application may receive trusted identity information such as:

* User ID
* Groups
* Roles
* Claims
* Scopes
* Other organizational identity attributes

---

# 6. B2B Authentication

B2B represents access where the consumer is another system or application.

The architecture should avoid repeatedly sending long-lived credentials across the network.

Instead, the system should distinguish between:

1. **Client identity / credentials used to obtain tokens**
2. **Access tokens used to access APIs**

Conceptually:

```text
B2B Client
   |
   | Client authentication
   v
Identity Provider / Token Service
   |
   | Short-lived Access Token
   v
API Gateway
   |
   v
Backend
```

The long-lived client credential must not be used as the API access credential for every request.

The required model is:

> **Use a client credential to obtain an access token, then use the access token for API access.**

This provides better control over:

* Credential exposure
* Token lifetime
* Revocation
* Rotation
* Auditing
* Authorization

---

# 7. Authorization

The API Gateway should enforce authorization at the API and operation level.

Examples:

```text
Consumer A -> GET /customers
Consumer A -> Allowed

Consumer A -> DELETE /customers
Consumer A -> Denied
```

Authorization can be based on:

* Identity
* Groups
* Roles
* Claims
* Scopes
* Policies
* Consumer identity

The application remains responsible for authorization decisions that require business context.

For example:

```text
Gateway:
    Is this consumer allowed to call GET /customers/{id}?

Application:
    Is this user allowed to access customer #123?
```

The Gateway should not implement business authorization logic.

---

# 8. Routing

The API Gateway is responsible for routing requests to the appropriate backend.

This includes support for:

* Path-based routing
* Host-based routing
* API-based routing
* Operation-based routing
* Version routing

---

## 8.1 Version Routing

Routing requests to different API versions is an important Gateway capability.

For example:

```text
/api/v1/customers -> Backend v1

/api/v2/customers -> Backend v2
```

The Gateway should provide the technical capability to route traffic between versions.

The application team remains responsible for deciding:

* Which versions exist
* Which consumers use each version
* When a version is deprecated
* When a version is retired

---

# 9. Load Balancing Boundary

The API Gateway should **not become the organization's general-purpose Load Balancer**.

The responsibility should be separated.

The Gateway handles:

* API routing
* API-level policies
* API-level health checks
* API-level timeouts

A dedicated Load Balancer or application infrastructure handles:

* Distribution between backend instances
* Backend pool management
* Infrastructure-level traffic distribution
* Instance-level availability

The Gateway may integrate with Load Balancing infrastructure where appropriate.

---

# 10. Health Checks

Health checks are an important API Gateway capability.

The Gateway should be able to determine whether a backend is available before routing traffic to it.

Health checks should support:

* HTTP health endpoints
* Configurable intervals
* Timeouts
* Failure thresholds
* Recovery thresholds
* Backend-specific configuration

The application is responsible for exposing an appropriate health endpoint.

The Gateway is responsible for using the result to make routing decisions.

Regular health checks apply to the backends of all API technologies. No protocol-specific health-check mechanism is defined.

---

# 11. Timeouts

Timeouts are a required Gateway capability.

Timeouts should exist at appropriate levels, including:

* Connection timeout
* Backend response timeout
* Request timeout

Timeouts protect both the Gateway and backend services from indefinitely hanging requests.

Timeouts should be configurable according to the characteristics of the API.

---

# 12. Retry Policy

Automatic retries should **not be enabled by default**.

Retries can create additional load against an already unhealthy backend and may cause unexpected application behavior.

For example:

```text
Client
  |
  | Request
  v
Gateway
  |
  | Request
  v
Backend
  |
  | Timeout
  X

Gateway does NOT automatically retry by default.
```

Retries may be considered for specific use cases only when:

* The operation is known to be safe
* The backend behavior is understood
* The retry policy is explicitly defined
* The additional load is acceptable

The default position is:

> **Timeout: Yes. Automatic Retry: No.**

---

# 13. Rate Limiting

Rate limiting is an important Gateway capability.

It can provide significant protection against:

* Accidental overload
* Excessive consumer usage
* Misbehaving applications
* Traffic spikes
* Resource exhaustion
* Abuse

Rate limiting can be applied based on:

* Consumer
* API
* Operation
* Client identity
* Token
* Other relevant attributes

Example:

```text
Consumer A
    |
    +-- API A: 100 req/s
    |
    +-- API B: 20 req/s
```

Rate limiting is a capability that can be enabled where appropriate. It is fully optional per API, and recommended where it can help protect the API or its backend.

It does not necessarily need to be enabled for every API.

---

# 14. Transformation

Transformation is a valuable Gateway capability because it can solve many integration conflicts without requiring backend changes.

The Gateway may perform technical transformations such as:

* Header manipulation
* Path rewriting
* Request mapping
* Response mapping
* Protocol-level adaptations
* Version compatibility transformations

For example:

```text
Consumer
    |
    | New API format
    v
API Gateway
    |
    | Legacy backend format
    v
Backend
```

Transformation should be used for **technical compatibility**, not for implementing business logic.

---

# 15. Caching

Caching can be provided as an optional Gateway capability.

Caching is fully optional per API. It should be used where it can help and where it is safe and appropriate.

The Gateway should consider:

* Cache TTL
* Cache key
* HTTP cache headers
* Authentication context
* Authorization context
* Data sensitivity
* Data freshness
* Cache invalidation

Caching must not cause one consumer to receive data belonging to another consumer.

The Gateway should not become a business-data store.

Business-driven cache invalidation remains an application responsibility.

---

# 16. Schema Validation

Schema validation is a useful Gateway capability for validating API contracts.

The Gateway may validate:

* Request structure
* Response structure
* Required fields
* Data types
* Payload size
* API contract compliance

Schema validation provides an additional layer of protection for backend services.

However, it should not be used to implement business validation.

Schema validation is fully optional per API, and recommended where it can help protect the backend.

For example:

```text
Gateway:
    "customer_id must be an integer"

Application:
    "customer_id must belong to the authenticated user"
```

The first is technical validation.

The second is business logic.

---

# 17. API Contract

Every API should have a defined technical contract.

The contract should describe:

* Endpoints
* Methods
* Parameters
* Headers
* Request schemas
* Response schemas
* Error responses
* Authentication requirements
* Authorization requirements
* Versions

The contract should be treated as part of the API lifecycle and should be version controlled.

---

# 18. API Lifecycle

The API lifecycle should include:

```text
Design
  |
Development
  |
Exposure
  |
Operation
  |
Change / Version
  |
Deprecation
  |
Retirement
```

The application team owns the lifecycle.

The Gateway provides the technical capabilities required to implement the lifecycle.

---

## 18.1 Deprecation

When an API version is deprecated:

* Consumers should be identified
* Migration guidance should be provided
* A retirement date should be defined
* Usage should be monitored
* Access should eventually be removed

---

## 18.2 Consumer Lifecycle

The API owner is responsible for:

* Adding consumers
* Removing consumers
* Changing consumer permissions
* Reviewing unused consumers
* Revoking access when it is no longer required

---

# 19. Developer Portal

The API platform should provide a Developer Portal.

The Portal should provide:

* API discovery
* API documentation
* API versions
* Authentication requirements
* Authorization requirements
* Usage information
* Access request information

The Portal should provide clear instructions on **how to obtain authorization to consume an API**.

The exact mechanism for issuing credentials or granting access depends on the organization's implementation and is not inherently a responsibility of the Gateway itself.

The API owner is responsible for the accuracy of API documentation.

---

# 20. Git as the Source of Truth

API configuration should be synchronized with Git.

Git should serve as the **Source of Truth** for:

* API definitions
* Routes
* Policies
* Gateway configuration
* Version configuration
* Consumer configuration (consumer identity, entitlements to APIs and operations, and rate limits)

Consumer credentials are never stored in Git.

Direct manual changes to production Gateway configuration should be avoided.

The desired model is:

```text
Git
 |
 | Pull Request
 v
Validation
 |
 | Approved
 v
Deployment
 |
 v
API Gateway
```

This provides:

* Change history
* Review
* Auditability
* Rollback
* Reproducibility
* Consistency between environments

---

# 21. GitOps

The preferred operating model is GitOps.

Changes should be:

1. Defined in Git
2. Reviewed
3. Validated
4. Approved
5. Automatically deployed

Production must not depend on undocumented manual configuration.

The deployed state should be reproducible from the repository.

---

# 22. Secrets

Secrets must not be stored in Git.

This includes:

* Passwords
* Private keys
* API secrets
* Client secrets
* Long-lived credentials

Secrets should be stored in a dedicated secrets-management solution.

The deployment process should combine:

```text
Git
+
Secrets Management
=
Runtime Configuration
```

---

# 23. Observability

The API Gateway must provide centralized observability.

At minimum, runtime logging should provide:

* Consumer identity
* API
* Operation
* Timestamp
* HTTP status
* Request result
* Latency
* Rejection reason
* Rate-limit information where relevant

The Gateway should not log sensitive business payloads by default.

Which information is sensitive is defined per API by the application team. Payloads of APIs that involve sensitive information should not be logged.

Observability should integrate with the organization's existing logging and monitoring systems.

---

# 24. Metrics

The Gateway should expose metrics for:

* Request volume
* Error rate
* Latency
* Backend latency
* Availability
* Rate limiting
* Authentication failures
* Authorization failures
* Backend failures
* Gateway health

Metrics should be available by dimensions such as:

* API
* Operation
* Consumer
* Backend
* Environment

---

# 25. Audit

Audit logging is mandatory for administrative and configuration activities.

Audit logs should record at least:

* Who performed the action
* What was changed
* When it was changed
* Which API or configuration was affected

Audit logs should be sent to a centralized system outside the direct control of the person performing the operation.

There should be two complementary sources of evidence:

```text
Git
 |
 +-- What change was requested and approved

Gateway Audit
 |
 +-- What was actually changed/executed
```

No retention period is defined for runtime logs or audit logs.

---

# 26. Availability

The API Gateway platform should provide at least:

> **99.9% monthly availability during regular operation**

Availability is measured during regular operation; planned maintenance is excluded from the calculation.

This SLA applies to the Gateway platform and does not imply availability of backend applications.

The platform should not contain a single point of failure.

Requirements include:

* Multiple Gateway instances
* Failure tolerance
* Controlled upgrades
* Controlled resets
* Rollback capability
* Health-based traffic management

---

# 27. Controlled Reset

Gateway resets and restarts should be performed in a controlled manner.

The platform should maintain availability for new requests during maintenance.

Existing sessions may be affected during a reset where technically unavoidable.

However:

> **A planned Gateway reset must not intentionally prevent new requests from being served when redundant capacity is available.**

Rolling maintenance should be preferred.

---

# 28. Distributed Deployment

The API Gateway should be deployed close to the applications it serves.

If an application exists in multiple sites, the Gateway should be available in each relevant site.

For example:

```text
             Central Management
                    |
          +---------+---------+
          |                   |
       Site A              Site B
          |                   |
     Gateway A           Gateway B
          |                   |
      App A               App B
```

This reduces dependency on a remote site for local application traffic.

A failure or network partition affecting another site should not prevent local APIs from operating.

---

# 29. Centralized Management + Distributed Runtime

The preferred architecture is:

> **Centralized Management + Distributed Runtime**

The control/management layer may be centralized.

The data plane should be distributed.

The loss of the central management layer should not immediately stop already-configured API traffic.

The Gateway data plane should continue operating using its last known valid configuration, and should be able to do so indefinitely.

The management plane should be restorable within one hour.

New configuration changes may depend on management-plane availability.

Conceptually:

```text
                Control Plane
                     |
          +----------+----------+
          |                     |
       Site A                 Site B
          |                     |
     Gateway A              Gateway B
          |                     |
       App A                  App B
```

---

# 30. Governance Model

Governance should combine three mechanisms.

## 30.1 Mandatory Guardrails

Requirements that can and should be technically enforced should become mandatory Gateway guardrails.

Examples:

* HTTPS at required boundaries
* Authentication
* Required logging
* Maximum request size
* Mandatory organizational policies

Communication within the cluster, including between the Gateway and backend services, uses HTTP. No minimum TLS version and no maximum request size are defined.

---

## 30.2 Standards

Standards define the organization's preferred and consistent way of operating APIs.

Where practical, standards should be technically enforced.

---

## 30.3 Guidelines

Some decisions should remain guidelines.

This is important because not every architectural or operational decision can or should be enforced by technology.

Examples may include:

* Recommended caching
* Recommended timeout values
* Recommended API versioning strategy
* Recommended transformation usage

The overall principle is:

> **Enforce what can safely and consistently be enforced; document and guide the rest.**

---

# 31. Organizational Governance

The preferred long-term model is for an organizational governance body to define API standards and policies.

The infrastructure team should then implement those requirements as Gateway capabilities and guardrails.

If organizational governance is not yet mature, the infrastructure team may temporarily provide governance for the Gateway platform itself.

This does not make the infrastructure team the owner of individual APIs.

An organizational governance body has not yet been defined.

---

# 32. Exceptions

The platform should support a controlled exception mechanism.

An exception should:

* Have a documented reason
* Have an identified owner
* Have approval from the security managers
* Include risk considerations
* Have an expiration or review date where appropriate

Exceptions should not become an alternative to proper architecture.

---

# 33. Security Boundary: API Gateway vs WAF

The API Gateway and WAF serve different purposes.

### API Gateway

Responsible for:

* Authentication
* Authorization
* Routing
* Rate limiting
* API policies
* Request controls
* Timeouts
* API-level transformations
* API contract validation
* API observability

### WAF

Responsible for application-layer attack protection such as:

* Attack signatures
* SQL injection detection
* Cross-site scripting detection
* Malicious payload detection
* Bot protection
* Other application security controls

The API Gateway should therefore **not attempt to become a WAF**.

A WAF may exist before the API Gateway when required by the security architecture.

---

# 34. Security Boundary: API Gateway vs Load Balancer

The API Gateway should not replace the organization's Load Balancer.

### API Gateway

Focuses on:

```text
Consumer
   |
   v
API
   |
   +-- Authentication
   +-- Authorization
   +-- Rate Limit
   +-- Policy
   +-- Routing
   +-- Transformation
   +-- Observability
```

### Load Balancer

Focuses on:

```text
Gateway
   |
   +---- Backend Instance 1
   +---- Backend Instance 2
   +---- Backend Instance 3
```

The two capabilities can coexist and should have clearly defined boundaries.

---

# 35. Security Boundary: API Gateway vs Identity Provider

The API Gateway does not need to be the organization's Identity Provider.

The Identity Provider is responsible for:

* User authentication
* Client authentication
* Token issuance
* Identity lifecycle

The API Gateway is responsible for:

* Consuming identity
* Validating tokens
* Enforcing API authorization
* Passing trusted identity information downstream

---

# 36. Security Boundary: API Gateway vs Application

The API Gateway provides infrastructure-level protection.

The application remains responsible for:

* Business authorization
* Business validation
* Business logic
* Data access control
* Business-level auditing

For example:

```text
Gateway:
    "Is this client allowed to call this API?"

Application:
    "Is this client allowed to access this specific record?"
```

---

# 37. Vendor Agnostic Architecture

The API Gateway architecture should minimize unnecessary vendor lock-in.

The following should remain conceptually independent from a specific product:

* API contracts
* API lifecycle
* Authentication model
* Authorization model
* GitOps workflow
* Governance model
* Observability requirements
* Deployment model

Vendor-specific capabilities may be used when they provide significant value, but they should be identified as implementation-specific.

The goal is not to guarantee zero migration effort.

The goal is to ensure that:

> **The organization's API architecture and policies are not unnecessarily defined by the implementation details of a single Gateway product.**

---

# 38. Required Capabilities Summary

| Capability             | Requirement                |
| ---------------------- | -------------------------- |
| API Routing            | Required                   |
| Version Routing        | Required                   |
| Health Checks          | Required                   |
| Timeouts               | Required                   |
| Automatic Retry        | Not recommended by default |
| Authentication         | Required                   |
| Authorization          | Required                   |
| Rate Limiting          | Required capability        |
| Transformation         | Required capability        |
| Caching                | Required capability        |
| Schema Validation      | Required capability        |
| API Documentation      | Required                   |
| Developer Portal       | Required                   |
| Git Integration        | Required                   |
| GitOps                 | Preferred operating model  |
| Audit Logs             | Required                   |
| Runtime Logs           | Required                   |
| Metrics                | Required                   |
| High Availability      | Required                   |
| Distributed Data Plane | Required                   |
| Centralized Management | Preferred                  |
| WAF                    | Separate component         |
| Load Balancer          | Separate responsibility    |
| Business Logic         | Application responsibility |
| Secrets Storage        | Separate secure system     |
| Vendor Neutrality      | Architectural principle    |

"Required capability" means the platform must provide the capability; whether it is enabled for a given API is decided by the application team. Rate limiting, caching and schema validation are fully optional per API and recommended where they can help.

---

# 39. API Gateway Operating Model

The resulting operating model can be summarized as follows:

```text
                         Organization
                              |
                 Governance / Standards
                              |
                              v
                         API Platform
                              |
              +---------------+---------------+
              |                               |
        Central Management               Git / GitOps
              |                               |
              +---------------+---------------+
                              |
                    Distributed Data Plane
                     /                    \
                    /                      \
               Site A                    Site B
                 |                          |
             API Gateway                API Gateway
                 |                          |
              Backend                    Backend
```

Application teams operate their APIs through the platform:

```text
Application Team
      |
      +-- API Definition
      +-- Consumers
      +-- Authorization Policy
      +-- Rate Limits
      +-- Versioning
      +-- Documentation
      +-- Lifecycle
      |
      v
   Git / GitOps
      |
      v
 API Gateway Platform
      |
      +-- Authentication
      +-- Authorization
      +-- Routing
      +-- Health Checks
      +-- Timeout
      +-- Rate Limiting
      +-- Transformation
      +-- Caching
      +-- Schema Validation
      +-- Logging
      +-- Audit
      |
      v
   Backend Services
```

---

# 40. Final Principles

The enterprise API Gateway architecture is based on the following principles:

1. **The API Gateway is a central enforcement point for APIs.**
2. **The Gateway is infrastructure, not business logic.**
3. **Application teams own their APIs.**
4. **The infrastructure team owns the Gateway platform.**
5. **Self-Service should be provided within organizational guardrails.**
6. **C2B must use short-lived user access tokens issued by the organizational IdP.**
7. **B2B must separate client credentials used for token acquisition from access tokens used for API access.**
8. **Long-lived credentials must not be continuously transmitted across the network.**
9. **Routing and version routing belong in the Gateway.**
10. **Load balancing between backend instances remains a separate responsibility.**
11. **Health checks are a required Gateway capability.**
12. **Timeouts are required; automatic retries should not be enabled by default.**
13. **Rate limiting is an important capability for protecting services and enforcing consumption policies.**
14. **Transformation can solve many technical integration conflicts without changing applications.**
15. **Caching and schema validation are available capabilities and should be enabled where appropriate.**
16. **WAF functionality remains separate from the API Gateway.**
17. **Git should be the source of truth for API configuration.**
18. **Production changes should be performed through a controlled GitOps process.**
19. **Secrets must never be stored in Git.**
20. **Audit logging is mandatory for administrative and configuration changes.**
21. **The platform should provide at least 99.9% monthly availability.**
22. **Gateway deployment should be distributed across sites where applications are deployed.**
23. **Centralized management should be combined with a distributed runtime.**
24. **Loss of the management plane should not immediately stop already-configured API traffic.**
25. **Governance should combine enforceable guardrails with standards and guidelines.**
26. **The architecture should remain as vendor agnostic as reasonably possible.**

The overall objective is to provide a **secure, highly available, observable, governed, and self-service API platform** while keeping the ownership boundary clear:

> **The infrastructure team provides and protects the road. The application team owns where the road goes and what happens at the destination.**
