"""Content of the API Gateway Enterprise Architecture Standard (version 1.2 onward: continuous prose).

The document is authored as data. build_docx.py renders it, numbers it and checks it.

Inline markup:  **bold**   *italic*   `code`   [[placeholder]] (highlighted)
Cross-refs:     {ch:CODE}  {sec:key}  {fig:key}  {tbl:key}

Wording rule used when converting the README:
  * must / must not      <- README "must", "required", "mandatory", "not permitted",
                            and Required / separate items in the README capability summary
  * should / recommended <- README "should" where it expresses a preference or recommendation
  * can / may            <- README "can", "may", "optional"
  * present tense        <- README statements of fact ("The application remains responsible...")
Any paragraph that departs from the README's wording carries chg=..., which is listed
in CHANGES.md against its section.
"""

# ---------------------------------------------------------------------------
# Block constructors
# ---------------------------------------------------------------------------

def P(text, chg=None):
    return {"t": "p", "text": text, "chg": chg}


def H2(title, key, src):
    return {"t": "h2", "title": title, "key": key, "src": src}


def NOTE(text, chg=None):
    return {"t": "note", "text": text, "chg": chg}


def BUL(items, chg=None):
    return {"t": "bul", "items": items, "chg": chg}


def TBL(key, caption, headers, rows, widths, first_bold=True):
    return {"t": "tbl", "key": key, "caption": caption, "headers": headers,
            "rows": rows, "widths": widths, "first_bold": first_bold}


def FIG(key, image, caption, alt, width_cm=16.0):
    return {"t": "fig", "key": key, "image": image, "caption": caption, "alt": alt,
            "width_cm": width_cm}


def CH(code, title, blocks, appendix=None, src=None):
    return {"code": code, "title": title, "blocks": blocks, "appendix": appendix, "src": src or []}


# ---------------------------------------------------------------------------
# Document metadata (placeholders are highlighted in the output)
# ---------------------------------------------------------------------------

META = {
    "title": "API Gateway Enterprise Architecture Standard",
    "subtitle": "Architecture and Operating Model",
    "version": "1.2",
    "status": "Draft",
    "date": "21 September 2026",
    "date_iso": "2026-09-21",
    "org": "[[Organization Name]]",
    "doc_id": "[[Document ID]]",
    "classification": "[[Classification]]",
    "owner": "[[Document owner, Infrastructure Team]]",
    "author": "[[Author]]",
    "review_cycle": "[[Review cycle, e.g. annual]]",
    "effective": "[[Effective date]]",
    "next_review": "[[Next review date]]",
}

# Revision history, oldest first. To issue a new version: add an entry here, set
# META["version"] to match, rebuild, then archive (see PLAN.md).
REVISIONS = [
    {"version": "1.0", "date": "2026-09-21", "author": "[[Author]]",
     "desc": "First issue (draft). Converted from the architecture and operating-model notes "
             "(README.md); review decisions recorded."},
    {"version": "1.1", "date": "2026-09-21", "author": "[[Author]]",
     "desc": "Draft. Settles three open issues (all three optional capabilities stay optional per API; "
             "consumer configuration in Git defined; Security Managers approve exceptions) "
             "and makes the security core mandatory."},
    {"version": "1.2", "date": "2026-09-21", "author": "[[Author]]",
     "desc": "Draft. Rewritten as continuous prose: numbered requirements and the "
             "requirements register removed; obligations expressed in plain must / should / can wording."},
]

# ---------------------------------------------------------------------------
# Chapters
# ---------------------------------------------------------------------------

CHAPTERS = []

# 1 -------------------------------------------------------------------------
CHAPTERS.append(CH("INT", "Introduction", [
    H2("Purpose", "purpose", [1]),
    P("This document sets out the enterprise architecture and operating model of the API Gateway "
      "platform of [[Organization Name]]. It is the reference for the design and operation of the "
      "platform, for the application teams that expose APIs through it, and for the security, risk, "
      "audit and governance functions that oversee it."),
    P("The API Gateway is an enterprise infrastructure layer positioned between API consumers and "
      "backend services. It gives the organization a consistent, secure, observable and governed entry "
      "point for web traffic, and it allows application teams to manage their own APIs independently, "
      "within organizational guardrails. The API Gateway is not a business-logic layer. The principle "
      "behind the whole document is a division of ownership:"),
    NOTE("**Application teams own their APIs and business policies. The infrastructure team owns the "
         "platform, its capabilities, and the technical guardrails around it.**"),

    H2("Scope", "scope", [2]),
    P("The Gateway handles web traffic to backend services. The scope is deliberately defined as web "
      "traffic, not as a fixed list of protocols, so that the architecture is not coupled to any one "
      "application protocol. The platform is intended to support HTTP/HTTPS, GraphQL, gRPC and MCP, "
      "together with other web-based API technologies. WebSocket and streaming traffic, "
      "service-to-service (east-west) traffic, multi-tenant use of the platform and non-production "
      "environments are also within scope. SOAP is outside the scope of this document."),
    P("The following adjacent systems are outside the scope of this document, except for the boundaries "
      "described in {ch:BND}: the Web Application Firewall (WAF), the organization's Load Balancer, the "
      "Identity Provider, the secrets-management solution, and the business logic of individual "
      "applications."),

    H2("Audience", "audience", []),
    P("The document is written for the Infrastructure Team, which owns and operates the platform; for "
      "the Application Teams that design, expose and operate APIs through it; for information-security, "
      "risk and audit stakeholders; and for enterprise-architecture and governance bodies."),

    H2("How to read this document", "normative", []),
    P("The document is written as continuous text. Where it says that something must or must not be "
      "done, the rule is mandatory. Where it says that something should be done, or is recommended, it "
      "describes expected practice from which a team can depart for a good reason, provided it "
      "understands the consequences. Where it says that something can or may be done, it is optional. "
      "Statements that describe what the Gateway or a team does, for example that the Gateway validates "
      "the access token, set out how the platform is required to operate. The words are used in the "
      "sense of BCP 14 (RFC 2119 and RFC 8174)."),
    NOTE("**Capability and enablement.** Where this document says that the platform provides a "
         "capability, for example rate limiting, caching or schema validation, the capability must be "
         "available. Unless the text says otherwise, whether it is enabled for a specific API is decided "
         "by the Application Team according to the needs of that API."),

    H2("Definitions and abbreviations", "defs", []),
    TBL("defs", "Definitions and abbreviations",
        ["Term", "Definition"],
        [["Access token", "A short-lived credential issued by the Identity Provider that a consumer "
                          "presents to access an API."],
         ["API Gateway (Gateway)", "The infrastructure layer between API consumers and backend "
                                   "services at which access, security and operational policies for "
                                   "API traffic are enforced."],
         ["API Platform (Platform)", "The complete capability operated by the Infrastructure Team: the "
                                     "Gateway Data Plane, the Management Plane, GitOps integration and "
                                     "the Developer Portal."],
         ["Application Team", "The team that owns an API, its contract and its business logic."],
         ["B2B", "Business to Business: access where the consumer is another system or application."],
         ["C2B", "Consumer to Business: access where the consumer is a human user."],
         ["Client credential", "A long-lived credential that a B2B client uses to obtain access tokens."],
         ["Consumer", "A user or system that calls an API through the Gateway."],
         ["Data Plane", "The Gateway runtime instances that process API traffic."],
         ["Developer Portal", "The portal through which APIs are discovered, documented and access "
                              "to them is requested."],
         ["GitOps", "An operating model in which configuration is defined in Git and changes are "
                    "reviewed, validated, approved and deployed automatically."],
         ["Guardrail", "An organizational requirement that is technically enforced by the Platform."],
         ["Guideline", "Recommended practice that is documented but not technically enforced."],
         ["IdP", "Identity Provider: the organization's system that authenticates users and clients "
                 "and issues tokens."],
         ["Infrastructure Team", "The team that owns and operates the Platform."],
         ["Load Balancer", "Infrastructure that distributes traffic between instances of a backend."],
         ["Management Plane", "The management layer used to configure and manage Gateways; also "
                              "referred to as the control plane or central management."],
         ["Security Managers", "The team [[team name]] designated by the organization to approve "
                               "exceptions to this document."],
         ["Site", "A location or environment in which applications run and in which a Gateway can be "
                  "deployed."],
         ["Source of truth", "The single authoritative location from which the deployed state is derived."],
         ["Standard", "The organization's defined, consistent way of operating APIs."],
         ["TTL", "Time to live: the period for which a cached item is considered valid."],
         ["WAF", "Web Application Firewall: a control that protects applications against "
                 "application-layer attacks."]],
        [4.2, 11.8]),

    H2("References", "refs", []),
    BUL(["BCP 14: RFC 2119, Key words for use in RFCs to Indicate Requirement Levels, and RFC 8174, "
         "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words.",
         "[[Organizational information-security policy]]",
         "[[Organizational API governance standards, when issued]]"]),
]))

# 2 -------------------------------------------------------------------------
CHAPTERS.append(CH("PRN", "Architectural Principles", [
    P("This chapter states the principles on which the rest of the document rests."),

    H2("Central API entry point", "entry", [3]),
    P("APIs that are exposed for consumption outside their immediate service boundary must be exposed "
      "through the API Gateway. Exposing such an API directly, so that consumers can bypass the "
      "organization's authentication, authorization, rate-limiting, logging and security controls, is "
      "not permitted. The Gateway is therefore the consistent enforcement point for API access.",
      chg="README §3.1 said 'should' and 'should not be permitted'; expressed as 'must' and 'is not "
          "permitted' because a central enforcement point is the founding principle (§40 item 1)."),

    H2("Infrastructure, not business logic", "nobiz", [1]),
    P("The Gateway is infrastructure, not business logic, and it does not implement application "
      "business logic. The platform is intended to let Application Teams expose and manage APIs without "
      "requiring the Infrastructure Team to understand or implement the business logic of any "
      "application."),

    H2("Ownership", "owner", [3]),
    P("Application Teams own the APIs they expose through the Gateway. Ownership covers the design and "
      "contract of the API, its business semantics, its consumers, the access and authorization "
      "requirements that apply to it, versioning, deprecation and retirement, documentation, and the "
      "consumer lifecycle. The Infrastructure Team owns the Gateway platform, its capabilities and the "
      "technical guardrails around it. The Infrastructure Team should not become the owner of an API "
      "merely because that API is implemented through the Gateway."),

    H2("Self-service with guardrails", "selfsvc", [3]),
    P("The preferred operating model is self-service with guardrails. Within organizational guardrails, "
      "Application Teams should be able to create APIs, configure routes and backend mappings, configure "
      "authentication requirements and authorization policies, set rate limits, configure "
      "transformations, configure caching where appropriate, manage API versions and consumers, and "
      "manage the API lifecycle themselves. The Infrastructure Team provides the platform and, where it "
      "is technically appropriate, enforces organizational requirements. Not every organizational "
      "guideline needs to become a hard technical restriction; {ch:GOV} explains how the different "
      "kinds of rule are handled."),

    H2("Summary of principles", "summary", [40]),
    P("The principles are summarized in {tbl:principles}, with the place where each is developed."),
    TBL("principles", "Summary of architectural principles",
        ["#", "Principle", "Developed in"],
        [["1", "The Gateway is the central enforcement point for APIs exposed beyond their service "
               "boundary.", "{sec:entry}"],
         ["2", "The Gateway is infrastructure, not business logic.", "{sec:nobiz}"],
         ["3", "Application Teams own their APIs; the Infrastructure Team owns the Platform.",
          "{sec:owner}"],
         ["4", "Self-service is provided within organizational guardrails.", "{sec:selfsvc}"],
         ["5", "C2B access uses short-lived access tokens issued by the organizational IdP.",
          "{sec:c2b}"],
         ["6", "B2B access separates the client credential used to obtain tokens from the access token "
               "used to reach APIs; long-lived credentials are not transmitted with every request.",
          "{sec:b2b}"],
         ["7", "Routing, version routing and health checks belong in the Gateway; load balancing "
               "between backend instances remains a separate responsibility.",
          "{sec:routing}, {sec:lb}, {sec:health}"],
         ["8", "Timeouts are required; automatic retries are not enabled by default.",
          "{sec:timeouts}, {sec:retry}"],
         ["9", "Rate limiting protects services and enforces consumption policies.", "{sec:ratelimit}"],
         ["10", "Transformation, caching and schema validation are available capabilities, enabled "
                "where appropriate and never used to implement business logic.", "{ch:POL}"],
         ["11", "WAF functionality remains separate from the Gateway.", "{sec:waf}"],
         ["12", "Git is the source of truth for API configuration; production changes follow a "
                "controlled GitOps process; secrets are never stored in Git.", "{ch:CFG}"],
         ["13", "Audit logging is mandatory for administrative and configuration changes.", "{sec:audit}"],
         ["14", "The Platform provides at least 99.9% monthly availability.", "{sec:sla}"],
         ["15", "Gateways are deployed at the sites where applications run; centralized management is "
                "combined with a distributed runtime, and loss of the Management Plane does not "
                "immediately stop configured API traffic.", "{sec:distributed}, {sec:mgmt}"],
         ["16", "Governance combines enforceable guardrails with standards and guidelines.", "{ch:GOV}"],
         ["17", "The architecture remains as vendor agnostic as reasonably possible.", "{ch:VND}"]],
        [1.0, 11.0, 4.0], first_bold=False),
    P("The overall objective is to provide a secure, highly available, observable, governed and "
      "self-service API platform while keeping the ownership boundary clear:"),
    NOTE("**The infrastructure team provides and protects the road. The application team owns where "
         "the road goes and what happens at the destination.**"),
]))

# 3 -------------------------------------------------------------------------
CHAPTERS.append(CH("ROL", "Roles and Responsibilities", [
    H2("Roles", "roles", [4]),
    P("Four roles appear throughout the document, and {tbl:roles} describes them."),
    TBL("roles", "Roles",
        ["Role", "Description"],
        [["Application Team", "Owns an API and its business logic; defines requirements for access, "
                              "authorization, routing and rate limits; manages consumers and the "
                              "API lifecycle."],
         ["Infrastructure Team", "Owns and operates the Platform; provides the capabilities and "
                                 "guardrails through which Application Teams manage their APIs."],
         ["Governance body", "Defines API standards and policies for the organization "
                             "(see {sec:orggov})."],
         ["Security Managers", "Approve exceptions to this document (see {sec:exceptions})."]],
        [4.2, 11.8]),

    H2("Responsibility matrix", "matrix", [4]),
    P("{tbl:matrix} sets out how responsibilities are allocated between Application Teams and the "
      "Infrastructure Team."),
    TBL("matrix", "Responsibility matrix",
        ["Area", "Application Team", "Infrastructure Team"],
        [["API design", "Owns", "Provides platform support"],
         ["API contract", "Owns", "Provides platform capability"],
         ["Business logic", "Owns", "Not responsible"],
         ["Consumers", "Owns", "Provides platform capability"],
         ["Authorization policy", "Defines the requirement", "Provides enforcement"],
         ["Authentication platform", "Consumes", "Provides"],
         ["Routing", "Defines the destination", "Provides the capability"],
         ["Rate limiting", "Defines the requirement", "Provides the capability"],
         ["Health checks", "Defines the appropriate endpoint and behavior", "Provides the capability"],
         ["Gateway platform", "Consumes", "Owns"],
         ["Availability of the Gateway", "—", "Owns"],
         ["GitOps platform", "Consumes", "Provides"],
         ["Logging platform", "Consumes", "Provides"],
         ["Audit", "Participates", "Owns the platform"],
         ["WAF", "Separate capability", "Separate responsibility"],
         ["Load balancing", "Application and platform architecture", "Provides Gateway integration"]],
        [4.6, 5.9, 5.5]),
]))

# 4 -------------------------------------------------------------------------
CHAPTERS.append(CH("IAM", "Identity, Authentication and Authorization", [
    H2("Consumer categories", "consumers", [5]),
    P("The Gateway distinguishes between two primary categories of consumer, described in "
      "{tbl:consumercat}. The categories describe the consumer and its identity model, not a specific "
      "product."),
    TBL("consumercat", "Consumer categories",
        ["Category", "Consumer", "Identity model"],
        [["C2B (Consumer to Business)", "A human user",
          "Authenticates through the organization's IdP and receives a short-lived access token."],
         ["B2B (Business to Business)", "Another system or application",
          "Uses a client credential to obtain a short-lived access token from the IdP or token service."]],
        [4.4, 4.0, 7.6]),
    P("The Gateway authenticates the consumers of the APIs it exposes, and APIs without consumer "
      "authentication are not permitted.",
      chg="README §38 lists Authentication as 'Required' and §30.1 as a mandatory guardrail, so it is "
          "stated as an obligation. 'APIs without consumer authentication are not permitted' is new: "
          "the README does not say whether anonymous or public APIs are allowed; decided during review."),
    NOTE("The lifetime of access tokens is defined by the owner of the Identity Provider and is "
         "outside the scope of this document."),

    H2("C2B authentication", "c2b", [5]),
    P("C2B represents access where the consumer is a human user. C2B users must authenticate through "
      "the organization's Identity Provider (IdP) and must use the short-lived access tokens that it "
      "issues. The Gateway validates the identity and the relevant claims presented with each request. "
      "It can pass trusted identity information on to the application, such as the user ID, groups, "
      "roles, claims, scopes and other organizational identity attributes. {fig:c2b} shows the flow.",
      chg="README §5.1 said 'should' for both the IdP and the short-lived tokens; made mandatory by a "
          "review decision (security core)."),
    FIG("c2b", "fig_c2b.png", "C2B authentication and access flow",
        "Sequence diagram. The user authenticates with the Identity Provider and receives a short-lived "
        "access token. The user sends an API request with the token to the API Gateway. The Gateway "
        "validates the token and claims, enforces authorization and policies, and forwards an authorized "
        "request with trusted identity attributes to the backend."),

    H2("B2B authentication", "b2b", [6]),
    P("B2B represents access where the consumer is another system or application. To avoid sending "
      "long-lived credentials across the network again and again, the architecture separates two "
      "things: the client credential, which a B2B client uses only to obtain a token, and the "
      "short-lived access token, which it presents to reach APIs. A B2B client must use its client "
      "credential to obtain a short-lived access token from the Identity Provider or token service, "
      "and must present that token, not the long-lived credential, when it calls an API. Long-lived "
      "credentials must not be transmitted with every request. This gives better control over "
      "credential exposure, token lifetime, revocation, rotation, auditing and authorization. "
      "{fig:b2b} shows the flow.",
      chg="README §6 called this 'the preferred model' ('should'), and §40 item 8 spoke of 'long-lived "
          "access tokens'; made mandatory by a review decision (security core), and 'tokens' corrected "
          "to 'credentials' to agree with §6."),
    FIG("b2b", "fig_b2b.png", "B2B authentication and access flow",
        "Sequence diagram. The B2B client authenticates to the Identity Provider or token service with its "
        "client credential and receives a short-lived access token. The client sends an API request with "
        "the token to the API Gateway. The Gateway validates the token and claims, enforces authorization "
        "and policies, and forwards an authorized request with trusted identity attributes to the backend."),

    H2("Authorization", "authz", [7]),
    P("The Gateway enforces authorization at the API and operation level. For example, a consumer can "
      "be allowed to call GET /customers and denied DELETE /customers. Gateway authorization decisions "
      "can be based on identity, groups, roles, claims, scopes, policies and consumer identity.",
      chg="README §7 said 'should enforce'; stated as an obligation because §38 lists Authorization as "
          "'Required'."),
    P("The application remains responsible for authorization decisions that require business context, "
      "and the Gateway does not implement business authorization logic. The two questions differ: the "
      "Gateway asks whether this consumer is allowed to call GET /customers/{id}, while the "
      "application asks whether this user is allowed to access customer #123.",
      chg="README §7 said the Gateway 'should not' implement business authorization logic; aligned with "
          "the statement in Section 2.2 that the Gateway does not implement business logic."),
]))

# 5 -------------------------------------------------------------------------
CHAPTERS.append(CH("TRF", "Traffic Management", [
    H2("Routing", "routing", [8]),
    P("The Gateway routes each request to the appropriate backend. It supports path-based, host-based, "
      "API-based, operation-based and version routing."),

    H2("Version routing", "vroute", [8]),
    P("Routing between API versions is an important Gateway capability, and the Gateway provides the "
      "technical means to do it. For example, requests to /api/v1/customers can be routed to one "
      "backend and requests to /api/v2/customers to another. The decisions about versions stay with the "
      "Application Team, which decides which versions exist, which consumers use each one, and when a "
      "version is deprecated and retired.",
      chg="README §8.1 said 'should provide the technical capability'; stated as an obligation because "
          "§38 lists Version Routing as 'Required'."),

    H2("Load balancing boundary", "lb", [9]),
    P("The Gateway is not the organization's general-purpose Load Balancer and must not be used as one. "
      "The Gateway handles API routing, API-level policies, API-level health checks and API-level "
      "timeouts. A dedicated Load Balancer, or the application infrastructure, handles the distribution "
      "of traffic between backend instances, backend pool management, infrastructure-level traffic "
      "distribution and instance-level availability. The Gateway can integrate with load-balancing "
      "infrastructure where appropriate.",
      chg="README §9 said 'should not become'; strengthened to 'must not' because §38 lists Load "
          "Balancer as a 'separate responsibility'."),

    H2("Health checks", "health", [10]),
    P("The Gateway must be able to determine whether a backend is available before it routes traffic to "
      "it. It does this with regular health checks, which apply to the backends of all API "
      "technologies; no protocol-specific mechanism is defined. Health checking supports HTTP health "
      "endpoints, configurable intervals and timeouts, failure and recovery thresholds, and "
      "backend-specific configuration. The Application Team is responsible for exposing an appropriate "
      "health endpoint for its backend, and the Gateway uses the result to make its routing decisions.",
      chg="README §10 said 'should'; strengthened because §38 lists Health Checks as 'Required'. The "
          "sentence that health checks are regular and apply to all API technologies records a review "
          "decision, which is still to be confirmed."),

    H2("Timeouts", "timeouts", [11]),
    P("Timeouts are a required Gateway capability. The Gateway enforces a connection timeout, a backend "
      "response timeout and a request timeout, which protects both the Gateway and the backend services "
      "from requests that hang indefinitely. Timeouts should be configurable according to the "
      "characteristics of each API.",
      chg="README §11 says timeouts are 'a required Gateway capability' that 'should exist at "
          "appropriate levels, including' these three; stated as an obligation."),

    H2("Retry policy", "retry", [12]),
    P("Automatic retries should not be enabled by default. A retry can add load to a backend that is "
      "already unhealthy and can cause unexpected application behavior, so when a backend request "
      "times out the Gateway does not send it again. A retry can be enabled for a specific use case, "
      "but only when the operation is known to be safe to repeat, the behavior of the backend is "
      "understood, the retry policy is explicitly defined, and the additional load is acceptable."),
    NOTE("The default position is: **Timeout: yes. Automatic retry: no.**"),

    H2("Rate limiting", "ratelimit", [13]),
    P("Rate limiting protects against accidental overload, excessive consumer usage, misbehaving "
      "applications, traffic spikes, resource exhaustion and abuse. The Gateway provides it as a "
      "capability. Limits can be applied per consumer, API, operation, client identity, token or other "
      "relevant attribute; for example, one consumer can be allowed 100 requests per second on one API "
      "and 20 on another. Rate limiting is optional for each API and is not required for every API, "
      "but it is recommended where it can help protect the API or its backend.",
      chg="README §13 calls it 'an important Gateway capability' and says it 'can be enabled where "
          "appropriate'. §38 lists it as 'Required capability'. A review decision keeps it fully "
          "optional per API and recommended where it can help."),
]))

# 6 -------------------------------------------------------------------------
CHAPTERS.append(CH("POL", "API Policy Capabilities", [
    H2("Transformation", "transform", [14]),
    P("Transformation is a valuable Gateway capability because it can resolve many integration "
      "conflicts without changes to the backend. For example, a consumer can use a new API format while "
      "the Gateway presents the legacy format to the backend. The Gateway provides transformation as a "
      "capability and can perform technical transformations such as header manipulation, path "
      "rewriting, request and response mapping, protocol-level adaptations and version-compatibility "
      "transformations. Transformation is for technical compatibility; it must not be used to "
      "implement business logic.",
      chg="README §14 calls it 'a valuable Gateway capability' (§38: 'Required capability'), and says "
          "transformation 'should be used for technical compatibility, not for implementing business "
          "logic'; the prohibition is aligned with Section 2.2."),

    H2("Caching", "cache", [15]),
    P("The Gateway provides caching as a capability. Caching is optional for each API, and it is "
      "recommended where it can help and where it is safe and appropriate. The cache configuration of an "
      "API should take into account the cache TTL and key, HTTP cache headers, the authentication and "
      "authorization context, data sensitivity, data freshness and invalidation. Caching must never "
      "cause one consumer to receive data that belongs to another. The Gateway does not act as a "
      "business-data store, and business-driven cache invalidation remains an application "
      "responsibility.",
      chg="README §15 calls it 'an optional Gateway capability' that should be used 'only where it is "
          "safe and appropriate' (§38: 'Required capability'). A review decision keeps it fully optional "
          "per API and recommended where it can help. 'Does not act as a business-data store' strengthens "
          "README's 'should not become'."),

    H2("Schema validation", "schema", [16]),
    P("The Gateway provides schema validation as a capability. It can validate request and response "
      "structure, required fields, data types, payload size and compliance with the API contract, and "
      "so gives backend services an additional layer of protection. Schema validation is optional for "
      "each API and is recommended where it can help protect the backend. It should not be used to "
      "implement business validation: the Gateway can check that customer_id is an integer, but only "
      "the application can check that customer_id belongs to the authenticated user.",
      chg="README §16 calls it 'a useful Gateway capability' (§38: 'Required capability'). A review "
          "decision keeps it fully optional per API and recommended where it can help protect the backend."),
]))

# 7 -------------------------------------------------------------------------
CHAPTERS.append(CH("LCY", "API Contract, Lifecycle and Developer Portal", [
    H2("API contract", "contract", [17]),
    P("Every API must have a defined technical contract, and the contract should be version controlled "
      "as part of the API lifecycle. It should describe the endpoints, methods, parameters, headers, "
      "request and response schemas, error responses, authentication and authorization requirements, "
      "and versions.",
      chg="README §17 said 'should'; strengthened to 'must' because §38 lists API Documentation as "
          "'Required'."),

    H2("API lifecycle", "lifecycle", [18]),
    P("The API lifecycle runs from design through development, exposure and operation, and then change "
      "or versioning, deprecation and retirement, as shown in {fig:lifecycle}. The Application Team owns "
      "the lifecycle. The Gateway provides the technical capabilities needed to carry it out."),
    FIG("lifecycle", "fig_lifecycle.png", "API lifecycle",
        "Seven stages in sequence: Design, Development, Exposure, Operation, Change or Version, "
        "Deprecation and Retirement.", width_cm=16.0),

    H2("Deprecation", "deprec", [18]),
    P("When an API version is deprecated, the Application Team should identify its consumers, provide "
      "migration guidance, define a retirement date and monitor usage, and should eventually remove "
      "access to it."),

    H2("Consumer lifecycle", "consumerlc", [18]),
    P("The Application Team, as API owner, is responsible for adding and removing consumers, changing "
      "their permissions, reviewing consumers that are no longer used, and revoking access when it is "
      "no longer required."),

    H2("Developer Portal", "portal", [19]),
    P("The Platform provides a Developer Portal. The portal should offer API discovery, documentation, "
      "versions, authentication and authorization requirements, usage information and access-request "
      "information, and it should give clear instructions on how to obtain authorization to consume an "
      "API. How credentials are issued or access is granted depends on the organization's "
      "implementation and is not inherently a responsibility of the Gateway. The API owner is "
      "responsible for the accuracy of the API documentation.",
      chg="README §19 said 'should provide a Developer Portal'; stated as an obligation because §38 "
          "lists Developer Portal as 'Required'."),
]))

# 8 -------------------------------------------------------------------------
CHAPTERS.append(CH("CFG", "Configuration Management", [
    H2("Git as the source of truth", "git", [20]),
    P("API configuration is synchronized with Git, and Git is the source of truth for API definitions, "
      "routes, policies, Gateway configuration, version configuration and consumer configuration. "
      "Consumer configuration means the consumer's identity, its entitlements (the APIs and operations "
      "it can use) and its rate limits. Consumer credentials are never held in Git; see {sec:secrets}. "
      "Direct manual changes to production Gateway configuration should be avoided. Working from Git "
      "provides change history, review, auditability, rollback, reproducibility and consistency "
      "between environments.",
      chg="README §20 said 'should be synchronized' and 'should serve as the Source of Truth'; stated as "
          "obligations because §38 lists Git Integration as 'Required'. 'Consumer configuration where "
          "appropriate' is defined by a review decision as identity, entitlements and rate limits."),

    H2("GitOps", "gitops", [21]),
    P("The preferred operating model is GitOps. A change is defined in Git, reviewed, validated, "
      "approved and deployed automatically, as shown in {fig:gitops}. Production must not depend on "
      "undocumented manual configuration, and the deployed state should be reproducible from the "
      "repository.",
      chg="README §21 said production 'should not' depend on undocumented manual configuration; made "
          "mandatory by a review decision (security core)."),
    FIG("gitops", "fig_gitops.png", "Configuration change flow",
        "Flow diagram. A change is defined in Git as a pull request, reviewed, automatically validated, "
        "approved and automatically deployed to the API Gateway. Secrets management supplies secrets "
        "to the Gateway at deployment. Git records what was requested and approved; Gateway audit "
        "records what was executed."),

    H2("Secrets", "secrets", [22]),
    P("Secrets, including passwords, private keys, API secrets, client secrets and long-lived "
      "credentials, must not be stored in Git. They are held in a dedicated secrets-management "
      "solution, and the deployment process should combine the configuration in Git with the secrets "
      "in that solution to produce the runtime configuration.",
      chg="README §22 said secrets 'should be stored in a dedicated secrets-management solution'; "
          "stated as an obligation because §38 lists Secrets Storage as a 'separate secure system'."),
]))

# 9 -------------------------------------------------------------------------
CHAPTERS.append(CH("OBS", "Observability and Audit", [
    H2("Runtime logging", "logging", [23]),
    P("The Gateway provides centralized observability. As a minimum, runtime logs record the consumer "
      "identity, the API and operation, the timestamp, the HTTP status, the result of the request, the "
      "latency, the reason for any rejection and, where relevant, rate-limit information. The Gateway "
      "should not log sensitive business payloads by default. Which information is sensitive is "
      "defined per API by the Application Team, and the payloads of an API that involves sensitive "
      "information should not be logged. Observability should integrate with the organization's "
      "existing logging and monitoring systems.",
      chg="README §23 said runtime logging 'should provide' these fields; stated as an obligation "
          "because §38 lists Runtime Logs as 'Required'. That sensitivity is defined per API is a review "
          "decision."),

    H2("Metrics", "metrics", [24]),
    P("The Gateway exposes metrics for request volume, error rate, latency, backend latency, "
      "availability, rate limiting, authentication failures, authorization failures, backend failures "
      "and Gateway health. Metrics should be available by API, operation, consumer, backend and "
      "environment.",
      chg="README §24 said 'should expose'; stated as an obligation because §38 lists Metrics as "
          "'Required'."),

    H2("Audit", "audit", [25]),
    P("Audit logging is mandatory for all administrative and configuration activities. An audit record "
      "states who performed the action, what was changed, when it was changed, and which API or "
      "configuration was affected. Audit logs are sent to a centralized system outside the direct "
      "control of the person performing the operation. Two complementary sources of evidence exist for "
      "every change: Git shows what change was requested and approved, and the Gateway audit shows "
      "what was actually changed or executed. No retention period is defined for runtime logs or audit "
      "logs.",
      chg="README §25 said audit logs 'should record' these details and 'should be sent' to a central "
          "system; stated as obligations because audit logging is described as mandatory."),
]))

# 10 ------------------------------------------------------------------------
CHAPTERS.append(CH("AVL", "Availability and Deployment Architecture", [
    H2("Availability", "sla", [26]),
    P("The Platform provides at least 99.9% monthly availability during regular operation. Planned "
      "maintenance is excluded from the calculation. The commitment applies to the Gateway platform and "
      "does not imply the availability of backend applications. For information, 99.9% availability in "
      "a 30-day month allows approximately 43 minutes of unavailability during regular operation."),
    P("The Platform must not contain a single point of failure. To achieve this it provides multiple "
      "Gateway instances, tolerance of failures, controlled upgrades and resets, rollback capability "
      "and health-based traffic management.",
      chg="README §26 said the platform 'should provide' 99.9% and 'should not contain a single point of "
          "failure'; stated as obligations (SLA; §38 lists High Availability as 'Required'). 'During "
          "regular operation' and the exclusion of planned maintenance are review decisions."),

    H2("Controlled reset", "reset", [27]),
    P("Gateway resets and restarts should be performed in a controlled manner, and maintenance should "
      "be performed on a rolling basis. A planned reset must not intentionally prevent new requests "
      "from being served when redundant capacity is available. Existing sessions can be affected during "
      "a reset where this is technically unavoidable."),

    H2("Distributed deployment", "distributed", [28]),
    P("The Gateway should be deployed close to the applications it serves. Where an application exists "
      "in more than one site, the Gateway must be available in each relevant site, so that local "
      "applications do not depend on a remote site. A failure or a network partition that affects "
      "another site must not prevent local APIs from operating.",
      chg="README §28 said 'should' for both statements; strengthened to 'must' because §38 lists "
          "Distributed Data Plane as 'Required'."),

    H2("Centralized management and distributed runtime", "mgmt", [29]),
    P("The preferred architecture combines centralized management with a distributed runtime. The "
      "Management Plane can be central, while the Data Plane is distributed. The loss of the Management "
      "Plane must not immediately stop API traffic that is already configured: the Data Plane "
      "continues to operate, indefinitely, on its last known valid configuration while the Management "
      "Plane is unavailable, although new configuration changes can depend on the Management Plane being "
      "available. The Management Plane should be restorable within one hour. {fig:distributed} shows "
      "the arrangement.",
      chg="README §29 and §40 item 24 said 'should'; strengthened to 'must' because §38 lists "
          "Distributed Data Plane as 'Required'. 'Indefinitely' and 'restorable within one hour' are "
          "review decisions."),
    FIG("distributed", "fig_distributed.png", "Centralized management with distributed Data Planes",
        "Diagram. A central Management Plane sends configuration to an API Gateway in Site A and an API "
        "Gateway in Site B. Each Gateway serves the application in its own site. If the Management Plane "
        "is unavailable, each Gateway continues to serve traffic using its last known valid configuration."),
]))

# 11 ------------------------------------------------------------------------
CHAPTERS.append(CH("GOV", "Governance and Exceptions", [
    H2("Governance model", "model", [30]),
    P("Governance combines three mechanisms: mandatory guardrails, standards and guidelines. The "
      "overall principle is:"),
    NOTE("**Enforce what can safely and consistently be enforced; document and guide the rest.**"),

    H2("Mandatory guardrails", "guardrails", [30]),
    P("Requirements that are suited to technical enforcement should be implemented as mandatory Gateway "
      "guardrails. Examples are HTTPS at required boundaries, authentication, required logging, a "
      "maximum request size and mandatory organizational policies. Communication within the cluster, "
      "including between the Gateway and backend services, uses HTTP. No minimum TLS version and no "
      "maximum request size are defined by this document."),

    H2("Standards", "standards", [30]),
    P("Standards define the organization's preferred and consistent way of operating APIs. Where it is "
      "practical, standards should be technically enforced."),

    H2("Guidelines", "guidelines", [30]),
    P("Not every architectural or operational decision can or should be enforced by technology. "
      "Decisions that are not suited to technical enforcement remain guidelines. Examples are "
      "recommended caching, recommended timeout values, the recommended API versioning strategy and the "
      "recommended use of transformation."),

    H2("Organizational governance", "orggov", [31]),
    P("The preferred long-term model is for an organizational governance body to define API standards "
      "and policies, which the Infrastructure Team then implements as Gateway capabilities and "
      "guardrails. An organizational governance body has not yet been defined. Until it is, the "
      "Infrastructure Team can provide governance for the Gateway platform itself. This does not make "
      "the Infrastructure Team the owner of individual APIs."),

    H2("Exceptions", "exceptions", [32]),
    P("The Platform should support a controlled exception mechanism. An exception should have a "
      "documented reason, an identified owner, approval from the Security Managers, a statement of the "
      "risks involved, and an expiration or review date where appropriate. Exceptions should not "
      "become an alternative to proper architecture.",
      chg="README §32 said 'an appropriate approval'; a review decision names the approver: the "
          "Security Managers."),
]))

# 12 ------------------------------------------------------------------------
CHAPTERS.append(CH("BND", "Platform Boundaries", [
    H2("Boundary overview", "matrix2", [33, 34, 35, 36]),
    P("The Gateway is one component of a wider security and infrastructure architecture. "
      "{tbl:boundaries} summarizes the boundary between the Gateway and each adjacent component, and "
      "the sections that follow explain each boundary."),
    TBL("boundaries", "Boundaries between the Gateway and adjacent components",
        ["Adjacent component", "The Gateway is responsible for", "The adjacent component is responsible for"],
        [["WAF",
          ["Authentication", "Authorization", "Routing", "Rate limiting", "API policies",
           "Request controls", "Timeouts", "API-level transformations", "API contract validation",
           "API observability"],
          ["Attack signatures", "SQL injection detection", "Cross-site scripting detection",
           "Malicious payload detection", "Bot protection", "Other application security controls"]],
         ["Load Balancer",
          ["Authentication", "Authorization", "Rate limiting", "API policy", "Routing",
           "Transformation", "Observability"],
          ["Distribution between backend instances", "Backend pool management",
           "Infrastructure-level traffic distribution", "Instance-level availability"]],
         ["Identity Provider",
          ["Consuming identity", "Validating tokens", "Enforcing API authorization",
           "Passing trusted identity information downstream"],
          ["User authentication", "Client authentication", "Token issuance", "Identity lifecycle"]],
         ["Application",
          ["Infrastructure-level protection"],
          ["Business authorization", "Business validation", "Business logic", "Data access control",
           "Business-level auditing"]]],
        [3.2, 6.4, 6.4]),

    H2("Gateway and WAF", "waf", [33]),
    P("The Gateway is not a WAF and must not attempt to become one. Protection against application-layer "
      "attacks, such as attack signatures, SQL injection and cross-site scripting detection, malicious "
      "payload detection and bot protection, belongs to the WAF. A WAF can be placed in front of the "
      "Gateway when the security architecture requires it.",
      chg="README §33 said the Gateway 'should therefore not attempt to become a WAF'; strengthened to "
          "'must not' as a boundary (§38: 'Separate component')."),

    H2("Gateway and Load Balancer", "lbb", [34]),
    P("The Gateway and the organization's Load Balancer can coexist, and the boundary between them "
      "should be clearly defined, as described in {sec:lb}."),

    H2("Gateway and Identity Provider", "idp", [35]),
    P("The Gateway does not need to be the organization's Identity Provider. The Identity Provider is "
      "responsible for user authentication, client authentication, token issuance and the identity "
      "lifecycle. The Gateway consumes identity, validates tokens, enforces API authorization and "
      "passes trusted identity information downstream."),

    H2("Gateway and application", "app", [36]),
    P("The Gateway provides infrastructure-level protection. The application remains responsible for "
      "business authorization, business validation, business logic, data access control and "
      "business-level auditing. In short, the Gateway asks whether a client is allowed to call an API, "
      "and the application asks whether that client is allowed to access a specific record."),
]))

# 13 ------------------------------------------------------------------------
CHAPTERS.append(CH("VND", "Vendor Neutrality", [
    H2("Principle", "vprinciple", [37]),
    P("The Gateway architecture should minimize unnecessary vendor lock-in. API contracts, the API "
      "lifecycle, the authentication and authorization models, the GitOps workflow, the governance "
      "model, observability requirements and the deployment model should remain conceptually "
      "independent of any specific product."),

    H2("Vendor-specific capabilities", "vspecific", [37]),
    P("Vendor-specific capabilities can be used when they provide significant value, and they should "
      "then be identified as implementation-specific. The goal is not to guarantee zero migration "
      "effort. The goal is to ensure that:"),
    NOTE("**The organization's API architecture and policies are not unnecessarily defined by the "
         "implementation details of a single Gateway product.**"),
]))

# ---------------------------------------------------------------------------
# Appendices
# ---------------------------------------------------------------------------

CHAPTERS.append(CH("APA", "Capability Summary", [
    P("{tbl:capabilities} summarizes the status of each capability. **Required** means that the "
      "Platform provides the capability and applies it. **Required capability** means that the "
      "Platform provides the capability and the Application Team decides whether to enable it for a "
      "given API. **Preferred** identifies the preferred operating model. The remaining entries "
      "identify responsibilities that lie outside the Gateway."),
    TBL("capabilities", "Capability summary",
        ["Capability", "Status", "Described in"],
        [["API routing", "Required", "{sec:routing}"],
         ["Version routing", "Required", "{sec:vroute}"],
         ["Health checks", "Required", "{sec:health}"],
         ["Timeouts", "Required", "{sec:timeouts}"],
         ["Automatic retry", "Not recommended by default", "{sec:retry}"],
         ["Authentication", "Required", "{sec:consumers}, {sec:c2b}, {sec:b2b}"],
         ["Authorization", "Required", "{sec:authz}"],
         ["Rate limiting", "Required capability", "{sec:ratelimit}"],
         ["Transformation", "Required capability", "{sec:transform}"],
         ["Caching", "Required capability", "{sec:cache}"],
         ["Schema validation", "Required capability", "{sec:schema}"],
         ["API documentation", "Required", "{sec:contract}, {sec:portal}"],
         ["Developer Portal", "Required", "{sec:portal}"],
         ["Git integration", "Required", "{sec:git}"],
         ["GitOps", "Preferred operating model", "{sec:gitops}"],
         ["Audit logs", "Required", "{sec:audit}"],
         ["Runtime logs", "Required", "{sec:logging}"],
         ["Metrics", "Required", "{sec:metrics}"],
         ["High availability", "Required", "{sec:sla}"],
         ["Distributed Data Plane", "Required", "{sec:distributed}"],
         ["Centralized management", "Preferred", "{sec:mgmt}"],
         ["WAF", "Separate component", "{sec:waf}"],
         ["Load Balancer", "Separate responsibility", "{sec:lb}, {sec:lbb}"],
         ["Business logic", "Application responsibility", "{sec:nobiz}, {sec:app}"],
         ["Secrets storage", "Separate secure system", "{sec:secrets}"],
         ["Vendor neutrality", "Architectural principle", "{ch:VND}"]],
        [5.0, 5.6, 5.4]),
], appendix="A", src=[38]))

CHAPTERS.append(CH("APB", "Operating Model", [
    P("{fig:operating_model} summarizes the operating model. Application Teams operate their APIs "
      "through the Platform by defining them in Git. The Infrastructure Team owns the Platform, which "
      "combines central management with a distributed Data Plane and provides the capabilities "
      "described in this document. Organizational governance defines the standards that the Platform "
      "implements as guardrails."),
    FIG("operating_model", "fig_operating_model.png", "API Gateway operating model",
        "Diagram. The Application Team defines API definitions, consumers, authorization policy, rate "
        "limits, versioning, documentation and lifecycle as code in Git. Git and GitOps deploy the "
        "approved configuration to the API Gateway Platform, owned by the Infrastructure Team, which "
        "provides authentication, authorization, routing, health checks, timeouts, rate limiting, "
        "transformation, caching, schema validation, logging and audit through a distributed Data Plane "
        "with a Gateway per site in front of backend services. Central Management, the Management "
        "Plane, configures the platform. Organizational governance and standards are implemented as "
        "guardrails through the Management Plane.", width_cm=14.5),
], appendix="B", src=[39]))

CHAPTERS.append(CH("APC", "Open Issues", [
    P("One item is not yet defined in this version of the document and is recorded here so that it is "
      "resolved deliberately rather than by default."),
    P("**Governance body.** The organizational governance body has not been defined, including its "
      "owner and mandate. Until it is, the Infrastructure Team provides interim governance for the "
      "Platform and the Security Managers approve exceptions. See {sec:orggov} and {sec:exceptions}."),
], appendix="C"))


# ---------------------------------------------------------------------------
# Change-log material (written to CHANGES.md by build_docx.py)
# ---------------------------------------------------------------------------

RESOLVED = [
    "**Required vs. optional.** README §13/§15/§16 called rate limiting, caching and schema validation "
    "optional, while §38 called them 'Required capability'. Resolved as: the Platform provides the "
    "capability; whether it is enabled for a given API is the Application Team's decision "
    "(Section 1.4, Appendix A). Confirmed during review: all three stay fully optional per API and are "
    "recommended where they can help.",
    "**Credentials vs. tokens.** README §40 item 8 said long-lived 'access tokens' should not be "
    "transmitted; §6 makes the distinction between long-lived client credentials and short-lived "
    "access tokens. Corrected to 'credentials' (Section 4.3).",
    "**Structure.** README §5.1 (C2B) was an orphan and B2B was a separate top-level section (§6); both "
    "now sit under Chapter 4. §33–§36 were titled 'Security Boundary' although §34 (load balancer) and "
    "§36 (application) are not security topics; retitled 'Platform Boundaries' (Chapter 12).",
    "**Duplicates merged.** Load-balancer boundary (§9, §34), the Gateway/application authorization split "
    "(§7, §36), Git as source of truth and GitOps (§20, §21), the two near-identical distributed-runtime "
    "diagrams (§28, §29), and the 26 closing principles (§40) versus §3, are each stated once.",
    "**Terminology.** 'Control plane', 'management layer', 'management plane' and 'central management' "
    "are unified as 'Management Plane'; 'the platform', 'the API platform' and 'the Gateway platform' "
    "are unified as 'the Platform' / 'the Gateway' as defined in Section 1.5.",
]

NEW_CONTENT = [
    "Cover page, document control, revision history, approval table, contents and lists of figures/tables.",
    "Section 1.3 Audience, 1.4 How to read this document, 1.5 Definitions and abbreviations, 1.6 References.",
    "Section 3.1 Roles (roles are described in the README only implicitly).",
    "The 99.9% availability informative note (approx. 43 minutes per 30-day month).",
    "Security Managers role, defined as the team that approves exceptions ({sec:exceptions}).",
    "{ch:APC} Open issues (the governance body).",
    "Statements added from review decisions (listed in the next section).",
]

# Decisions taken while resolving the draft open issues. Each is recorded in the
# document; the interpretation is stated so it can be checked.
DECISIONS = [
    ("Token lifetime", "Defined by the owner of the Identity Provider; the document says so "
                       "({sec:consumers}, note)."),
    ("Transport security", "Traffic inside the cluster, including Gateway to backend, uses HTTP; no minimum "
                           "TLS version is defined ({sec:guardrails}). 'HTTPS at required boundaries' is "
                           "kept as a guardrail example, without saying which boundaries."),
    ("Maximum request size", "No maximum is defined ({sec:guardrails}). 'Maximum request size' stays in "
                             "the README's list of guardrail examples."),
    ("Availability measurement", "99.9% applies during regular operation; planned maintenance is excluded "
                                 "({sec:sla})."),
    ("Management Plane", "The Data Plane runs on its last known configuration indefinitely, and the "
                         "Management Plane should be restorable within one hour ({sec:mgmt})."),
    ("Retention", "No log or audit retention period is defined ({sec:audit})."),
    ("Sensitive payloads", "Payloads involving sensitive information should not be logged; what is "
                           "sensitive is defined per API by the Application Team ({sec:logging})."),
    ("Health checks beyond HTTP", "Read as: regular health checks apply to all API technologies, with no "
                                  "protocol-specific mechanism ({sec:health}). Please confirm this reading."),
    ("Anonymous APIs", "Not permitted ({sec:consumers})."),
    ("Governance body", "Not yet defined; recorded in {sec:orggov} and kept open ({ch:APC})."),
    ("Scope gaps", "Read 'yes' as: WebSocket/streaming, east-west traffic, multi-tenancy and "
                   "non-production environments are in scope ({sec:scope}). Please confirm this reading."),
    ("Exception approval", "Exceptions are approved by the Security Managers, a defined team ({sec:exceptions}). "
                           "The team's name is a placeholder to fill in ({sec:defs})."),
    ("Capability enablement", "Rate limiting, caching and schema validation stay fully optional per API and "
                              "are recommended where they can help ({sec:ratelimit}, {sec:cache}, {sec:schema})."),
    ("Consumer configuration in Git", "Git holds consumer identity, entitlements (APIs and operations) and "
                                      "rate limits; credentials are never in Git ({sec:git}). Not answered: "
                                      "whether consumers can also be created at runtime, for example through "
                                      "the Developer Portal."),
    ("Security core made mandatory", "C2B use of the IdP with short-lived tokens, the B2B token exchange, no "
                                     "long-lived credential on every request, and no reliance on undocumented "
                                     "manual production configuration are now mandatory (see the change table "
                                     "above). Other 'should' statements are unchanged."),
]
