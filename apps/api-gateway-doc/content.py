"""Content of the API Gateway Enterprise Architecture Standard.

The document is authored as data. build_docx.py renders it, numbers it,
generates the requirement IDs and Appendix A.2, and checks it.

Inline markup:  **bold**   `code`   [[placeholder]] (highlighted)
Cross-refs:     {ch:CODE}  {sec:key}  {fig:key}  {tbl:key}

Requirement text must contain exactly one normative keyword
(shall / shall not / should / should not / may); the builder enforces this.
Modality rule used when converting the README:
  * shall / shall not  <- README "must", "required", "mandatory", "not permitted",
                          and boundary / Required items in the README capability summary
  * should / should not <- README "should" where it expresses a preference,
                          recommendation or "where appropriate"
  * may                <- README "can", "may", "optional"
Every place where this strengthens the README is marked with chg=... and is
listed in CHANGES.md.
"""

# ---------------------------------------------------------------------------
# Block constructors
# ---------------------------------------------------------------------------

def P(text):
    return {"t": "p", "text": text}


def H2(title, key, src):
    return {"t": "h2", "title": title, "key": key, "src": src}


def R(text, bullets=None, chg=None):
    return {"t": "req", "text": text, "bullets": bullets or [], "chg": chg}


def RAT(text):
    return {"t": "rat", "text": text}


def NOTE(text):
    return {"t": "note", "text": text}


def BUL(items):
    return {"t": "bul", "items": items}


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
    "version": "1.0",
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
]

# ---------------------------------------------------------------------------
# Chapters
# ---------------------------------------------------------------------------

CHAPTERS = []

# 1 -------------------------------------------------------------------------
CHAPTERS.append(CH("INT", "Introduction", [
    H2("Purpose", "purpose", [1]),
    P("This document defines the enterprise architecture, operating model, responsibilities and "
      "required capabilities of the API Gateway platform of [[Organization Name]]. It is the normative "
      "reference for the design and operation of the platform, for application teams that expose "
      "APIs through it, and for governance, security and audit stakeholders."),
    P("The API Gateway is an enterprise infrastructure layer positioned between API consumers and "
      "backend services. Its purpose is to provide a consistent, secure, observable and governed "
      "entry point for web traffic, while allowing application teams to manage their APIs "
      "independently within organizational guardrails."),
    P("The API Gateway is **not** a business-logic layer. The core principle of this document is:"),
    NOTE("**Application teams own their APIs and business policies. The infrastructure team owns the "
         "platform, its capabilities, and the technical guardrails around it.**"),

    H2("Scope", "scope", [2]),
    P("This document applies to the handling of web traffic to backend services through the API "
      "Gateway. The scope is intentionally expressed as web traffic, rather than by a fixed list of "
      "protocols, so that the architecture is not unnecessarily coupled to a specific application "
      "protocol."),
    R("The Platform shall support the exposure and management of web-based API traffic."),
    R("The Platform architecture should remain independent of any specific application protocol."),
    R("The Platform should be capable of supporting HTTP/HTTPS, GraphQL, gRPC and MCP APIs, and other "
      "web-based API technologies."),
    P("SOAP is outside the scope of this document."),
    P("The following are within the scope of this document:"),
    BUL(["WebSocket and streaming traffic.",
         "Service-to-service (east-west) traffic.",
         "Multi-tenant use of the Platform.",
         "Non-production environments."]),
    P("The following adjacent systems are outside the scope of this document, except for the "
      "boundaries defined in {ch:BND}: the Web Application Firewall (WAF), the organization's Load "
      "Balancer, the Identity Provider, the secrets-management solution, and the business logic of "
      "individual applications."),

    H2("Audience", "audience", []),
    BUL(["The Infrastructure Team, which owns and operates the Platform.",
         "Application Teams that design, expose and operate APIs through the Gateway.",
         "Information security, risk and audit stakeholders.",
         "Enterprise architecture and governance bodies."]),

    H2("Normative language", "normative", []),
    P("The key words below are used to indicate requirement levels. They are written in bold where "
      "they appear in a numbered requirement."),
    TBL("keywords", "Requirement levels",
        ["Keyword", "Level", "Meaning"],
        [["**shall**, **shall not**", "Mandatory", "An absolute requirement or prohibition."],
         ["**should**, **should not**", "Recommended",
          "There may be valid reasons to deviate in particular circumstances, but the implications "
          "must be understood and weighed before a different course is chosen."],
         ["**may**", "Optional", "The item is permitted but not required."]],
        [4.2, 3.0, 8.8]),
    P("These terms are used in accordance with BCP 14 (RFC 2119 and RFC 8174) and only when written "
      "in lower-case bold within a numbered requirement."),
    P("Each requirement carries an identifier of the form **GW-AAA-NNN**, where AAA identifies the "
      "subject area (the chapter) and NNN is a sequence number within it. Requirements apply to the "
      "Platform unless they name a different party. Paragraphs headed *Rationale* or *Note*, and shaded "
      "statements of principle, are informative and do not add requirements."),
    NOTE("**Capability and enablement.** Where this document requires the Platform to provide a "
         "capability (for example rate limiting, caching or schema validation), the capability must "
         "be available. Unless a requirement states otherwise, whether it is enabled for a specific "
         "API is decided by the Application Team according to the needs of that API."),

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
         ["Site", "A location or environment in which applications run and in which a Gateway may be "
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
    P("This chapter states the principles on which the remainder of the document is based."),

    H2("Central API entry point", "entry", [3]),
    R("APIs exposed for consumption outside their immediate service boundary shall be exposed through "
      "the API Gateway.",
      chg="README §3.1 said 'should'; strengthened to 'shall' (central enforcement point is the "
          "founding principle, §40 item 1)."),
    R("Direct exposure of an API that allows consumers to bypass the organization's authentication, "
      "authorization, rate-limiting, logging and security controls shall not be permitted.",
      chg="README §3.1 said 'should not be permitted'; strengthened together with GW-PRN-001."),
    RAT("The Gateway provides a consistent enforcement point for API access."),

    H2("Infrastructure, not business logic", "nobiz", [1]),
    R("The Gateway shall not implement application business logic."),
    R("The Platform should enable Application Teams to expose and manage APIs without requiring the "
      "Infrastructure Team to understand or implement the business logic of any application."),

    H2("Ownership", "owner", [3]),
    R("Application Teams shall own the APIs they expose through the Gateway, including API design, "
      "API contract, business semantics, consumers, access requirements, authorization requirements, "
      "versioning, deprecation, retirement, documentation and consumer lifecycle."),
    R("The Infrastructure Team shall own the Gateway platform, its capabilities and the technical "
      "guardrails around it."),
    R("The Infrastructure Team should not become the owner of an API solely because the API is "
      "implemented through the Gateway."),

    H2("Self-service with guardrails", "selfsvc", [3]),
    R("The Platform should operate on a model of self-service with guardrails."),
    R("Within organizational guardrails, the Platform should enable Application Teams to carry out the "
      "following themselves:",
      bullets=["Create APIs.", "Configure routes.", "Configure backend mappings.",
               "Configure authentication requirements.", "Configure authorization policies.",
               "Configure rate limits.", "Configure transformations.",
               "Configure caching where appropriate.", "Manage API versions.", "Manage consumers.",
               "Manage the API lifecycle."]),
    R("The Infrastructure Team should provide the Platform and enforce organizational requirements "
      "where technically appropriate."),
    NOTE("Not every organizational guideline needs to become a hard technical restriction. "
         "See {ch:GOV}."),

    H2("Summary of principles", "summary", [40]),
    P("The following principles summarize the architecture. Each is specified in the chapter or "
      "section indicated."),
    TBL("principles", "Summary of architectural principles",
        ["#", "Principle", "Specified in"],
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
    TBL("roles", "Roles",
        ["Role", "Description"],
        [["Application Team", "Owns an API and its business logic; defines requirements for access, "
                              "authorization, routing and rate limits; manages consumers and the "
                              "API lifecycle."],
         ["Infrastructure Team", "Owns and operates the Platform; provides the capabilities and "
                                 "guardrails through which Application Teams manage their APIs."],
         ["Governance body", "Defines API standards and policies for the organization "
                             "(see {sec:orggov})."]],
        [4.2, 11.8]),

    H2("Responsibility matrix", "matrix", [4]),
    R("Responsibilities shall be allocated between Application Teams and the Infrastructure Team as "
      "set out in {tbl:matrix}."),
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
    P("The Gateway distinguishes between two primary consumer categories. The categories describe the "
      "consumer and its identity model, not a specific product implementation."),
    TBL("consumercat", "Consumer categories",
        ["Category", "Consumer", "Identity model"],
        [["C2B (Consumer to Business)", "A human user",
          "Authenticates through the organization's IdP and receives a short-lived access token."],
         ["B2B (Business to Business)", "Another system or application",
          "Uses a client credential to obtain a short-lived access token from the IdP or token service."]],
        [4.4, 4.0, 7.6]),
    R("The Gateway should distinguish between C2B and B2B consumers."),
    R("The Gateway shall authenticate the consumers of the APIs it exposes.",
      chg="README §38 lists Authentication as 'Required' and §30.1 as a mandatory guardrail; "
          "expressed here as a 'shall'."),
    R("APIs without consumer authentication shall not be permitted.",
      chg="New requirement. The README does not say whether anonymous or public APIs are allowed; "
          "decided during review: not permitted."),
    NOTE("The lifetime of access tokens is defined by the owner of the Identity Provider and is outside "
         "the scope of this document."),

    H2("C2B authentication", "c2b", [5]),
    P("C2B represents access where the consumer is a human user."),
    R("C2B users should authenticate through the organization's Identity Provider."),
    R("C2B access should use short-lived access tokens issued by the organization's Identity Provider."),
    R("The Gateway shall validate the identity and the relevant claims presented by the consumer."),
    R("The Gateway may pass trusted identity information to the application, such as user ID, groups, "
      "roles, claims, scopes and other organizational identity attributes."),
    FIG("c2b", "fig_c2b.png", "C2B authentication and access flow",
        "Sequence diagram. The user authenticates with the Identity Provider and receives a short-lived "
        "access token. The user sends an API request with the token to the API Gateway. The Gateway "
        "validates the token and claims, enforces authorization and policies, and forwards an authorized "
        "request with trusted identity attributes to the backend."),

    H2("B2B authentication", "b2b", [6]),
    P("B2B represents access where the consumer is another system or application. The architecture "
      "avoids repeatedly sending long-lived credentials across the network. It therefore distinguishes "
      "between the client identity or credential used to obtain tokens, and the access token used to "
      "access APIs."),
    R("B2B clients should use a client credential to obtain a short-lived access token, and then present "
      "that access token for API access."),
    R("The long-lived client credential should not be used as the API access credential for every request."),
    R("Long-lived credentials should not be continuously transmitted across the network.",
      chg="README §40 item 8 referred to 'long-lived access tokens'. Corrected to 'credentials' to align "
          "with §6, which contrasts long-lived credentials with short-lived access tokens."),
    RAT("This model gives better control over credential exposure, token lifetime, revocation, "
        "rotation, auditing and authorization."),
    FIG("b2b", "fig_b2b.png", "B2B authentication and access flow",
        "Sequence diagram. The B2B client authenticates to the Identity Provider or token service with its "
        "client credential and receives a short-lived access token. The client sends an API request with "
        "the token to the API Gateway. The Gateway validates the token and claims, enforces authorization "
        "and policies, and forwards an authorized request with trusted identity attributes to the backend."),

    H2("Authorization", "authz", [7]),
    R("The Gateway shall enforce authorization at the API and operation level.",
      chg="README §7 said 'should'; strengthened because §38 lists Authorization as 'Required'."),
    R("Gateway authorization decisions may be based on the following:",
      bullets=["Identity", "Groups", "Roles", "Claims", "Scopes", "Policies", "Consumer identity"]),
    TBL("authzexample", "Example of operation-level authorization",
        ["Consumer", "Request", "Decision"],
        [["Consumer A", "GET /customers", "Allowed"],
         ["Consumer A", "DELETE /customers", "Denied"]],
        [5.0, 6.0, 5.0], first_bold=False),
    R("The application shall remain responsible for authorization decisions that require business context."),
    R("The Gateway shall not implement business authorization logic.",
      chg="README §7 said 'should not'; aligned with the 'shall not' in {sec:nobiz}."),
    TBL("authz_split", "Division of authorization decisions",
        ["Component", "Question answered"],
        [["Gateway", "Is this consumer allowed to call GET /customers/{id}?"],
         ["Application", "Is this user allowed to access customer #123?"]],
        [4.0, 12.0]),
]))

# 5 -------------------------------------------------------------------------
CHAPTERS.append(CH("TRF", "Traffic Management", [
    H2("Routing", "routing", [8]),
    R("The Gateway shall route requests to the appropriate backend."),
    R("The Gateway shall support the following methods of routing:",
      bullets=["Path-based routing", "Host-based routing", "API-based routing",
               "Operation-based routing", "Version routing"]),

    H2("Version routing", "vroute", [8]),
    R("The Gateway shall provide the technical capability to route traffic between API versions.",
      chg="README §8.1 said 'should'; strengthened because §38 lists Version Routing as 'Required'."),
    TBL("routeexample", "Example of version routing",
        ["Request path", "Backend"],
        [["/api/v1/customers", "Backend v1"], ["/api/v2/customers", "Backend v2"]],
        [8.0, 8.0], first_bold=False),
    R("The Application Team shall decide which versions exist, which consumers use each version, and "
      "when a version is deprecated and retired."),

    H2("Load balancing boundary", "lb", [9]),
    R("The Gateway shall not serve as the organization's general-purpose Load Balancer.",
      chg="README §9 said 'should not become'; strengthened because §38 lists Load Balancer as a "
          "'separate responsibility'."),
    R("Responsibilities should be divided between the Gateway and load-balancing infrastructure as set "
      "out in {tbl:lbsplit}."),
    TBL("lbsplit", "Division of responsibilities between the Gateway and load balancing",
        ["The Gateway handles", "Load-balancing infrastructure handles"],
        [[["API routing", "API-level policies", "API-level health checks", "API-level timeouts"],
          ["Distribution between backend instances", "Backend pool management",
           "Infrastructure-level traffic distribution", "Instance-level availability"]]],
        [8.0, 8.0], first_bold=False),
    R("The Gateway may integrate with load-balancing infrastructure where appropriate."),

    H2("Health checks", "health", [10]),
    R("The Gateway shall be able to determine whether a backend is available before routing traffic to it.",
      chg="README §10 said 'should'; strengthened because §38 lists Health Checks as 'Required'."),
    R("Gateway health checking shall support the following:",
      bullets=["HTTP health endpoints", "Configurable intervals", "Timeouts", "Failure thresholds",
               "Recovery thresholds", "Backend-specific configuration"],
      chg="README §10 said 'should support'; strengthened together with the previous requirement."),
    R("The Gateway shall use the result of health checks to make routing decisions."),
    R("The Application Team shall expose an appropriate health endpoint for its backend."),
    NOTE("Regular health checks apply to the backends of all API technologies. No protocol-specific "
         "health-check mechanism is defined."),

    H2("Timeouts", "timeouts", [11]),
    R("The Gateway shall enforce timeouts at the following levels:",
      bullets=["Connection timeout", "Backend response timeout", "Request timeout"],
      chg="README §11 says timeouts are 'a required Gateway capability' that 'should exist at appropriate "
          "levels, including' these; expressed as a 'shall'."),
    R("Timeouts should be configurable according to the characteristics of the API."),
    RAT("Timeouts protect both the Gateway and backend services from indefinitely hanging requests."),

    H2("Retry policy", "retry", [12]),
    R("Automatic retries should not be enabled by default."),
    RAT("Retries can create additional load against an already unhealthy backend and may cause "
        "unexpected application behavior. By default, when a backend request times out, the Gateway "
        "does not send the request again."),
    R("Automatic retries may be enabled for a specific use case only when all of the following "
      "conditions are met:",
      bullets=["The operation is known to be safe to repeat.", "The backend behavior is understood.",
               "The retry policy is explicitly defined.", "The additional load is acceptable."]),
    NOTE("The default position is: **Timeout: yes. Automatic retry: no.**"),

    H2("Rate limiting", "ratelimit", [13]),
    P("Rate limiting provides significant protection against accidental overload, excessive consumer "
      "usage, misbehaving applications, traffic spikes, resource exhaustion and abuse."),
    R("The Gateway shall provide rate limiting as a capability.",
      chg="README §13 calls it 'an important Gateway capability'; strengthened because §38 lists it as "
          "'Required capability'."),
    R("Rate limits may be applied based on the following:",
      bullets=["Consumer", "API", "Operation", "Client identity", "Token",
               "Other relevant attributes"]),
    TBL("rateexample", "Example of per-API rate limits for one consumer",
        ["Consumer", "API", "Limit"],
        [["Consumer A", "API A", "100 requests per second"],
         ["Consumer A", "API B", "20 requests per second"]],
        [5.0, 5.0, 6.0], first_bold=False),
    R("Rate limiting may be enabled for an API where appropriate."),
    NOTE("Rate limiting is not required to be enabled for every API."),
]))

# 6 -------------------------------------------------------------------------
CHAPTERS.append(CH("POL", "API Policy Capabilities", [
    H2("Transformation", "transform", [14]),
    RAT("Transformation can resolve many integration conflicts without requiring backend changes. "
        "For example, a consumer can use a new API format while the Gateway presents the legacy "
        "format to the backend."),
    R("The Gateway shall provide transformation as a capability.",
      chg="README §14 calls it 'a valuable Gateway capability'; strengthened because §38 lists it as "
          "'Required capability'."),
    R("The Gateway may perform technical transformations such as the following:",
      bullets=["Header manipulation", "Path rewriting", "Request mapping", "Response mapping",
               "Protocol-level adaptations", "Version compatibility transformations"]),
    R("Transformation should be used for technical compatibility."),
    R("Transformation shall not be used to implement business logic.",
      chg="README §14 said 'should be used for technical compatibility, not for implementing business "
          "logic'; the prohibition is aligned with GW-PRN-003."),

    H2("Caching", "cache", [15]),
    R("The Gateway shall provide caching as a capability.",
      chg="README §15 calls it 'an optional Gateway capability'; expressed as a capability the Platform "
          "shall provide (§38: 'Required capability'), enabled per API where appropriate."),
    R("Caching should be used only where it is safe and appropriate."),
    R("The caching configuration of an API should take the following into account:",
      bullets=["Cache TTL", "Cache key", "HTTP cache headers", "Authentication context",
               "Authorization context", "Data sensitivity", "Data freshness", "Cache invalidation"]),
    R("Caching shall not cause one consumer to receive data belonging to another consumer."),
    R("The Gateway shall not become a business-data store.",
      chg="README §15 said 'should not become'; strengthened to match the boundary in {sec:nobiz}."),
    R("Business-driven cache invalidation shall remain an application responsibility."),

    H2("Schema validation", "schema", [16]),
    R("The Gateway shall provide schema validation as a capability.",
      chg="README §16 calls it 'a useful Gateway capability'; strengthened because §38 lists it as "
          "'Required capability'."),
    R("The Gateway may validate the following:",
      bullets=["Request structure", "Response structure", "Required fields", "Data types",
               "Payload size", "API contract compliance"]),
    RAT("Schema validation provides an additional layer of protection for backend services."),
    R("Schema validation should not be used to implement business validation."),
    TBL("validation", "Technical validation versus business validation",
        ["Component", "Example of validation"],
        [["Gateway (technical)", "customer_id must be an integer."],
         ["Application (business)", "customer_id must belong to the authenticated user."]],
        [5.0, 11.0]),
]))

# 7 -------------------------------------------------------------------------
CHAPTERS.append(CH("LCY", "API Contract, Lifecycle and Developer Portal", [
    H2("API contract", "contract", [17]),
    R("Every API shall have a defined technical contract.",
      chg="README §17 said 'should'; strengthened because §38 lists API Documentation as 'Required'."),
    R("The contract should describe the following:",
      bullets=["Endpoints", "Methods", "Parameters", "Headers", "Request schemas", "Response schemas",
               "Error responses", "Authentication requirements", "Authorization requirements",
               "Versions"]),
    R("The contract should be version controlled as part of the API lifecycle."),

    H2("API lifecycle", "lifecycle", [18]),
    FIG("lifecycle", "fig_lifecycle.png", "API lifecycle",
        "Seven stages in sequence: Design, Development, Exposure, Operation, Change or Version, "
        "Deprecation and Retirement.", width_cm=16.0),
    R("The Application Team shall own the API lifecycle."),
    R("The Gateway shall provide the technical capabilities required to implement the API lifecycle."),

    H2("Deprecation", "deprec", [18]),
    R("When an API version is deprecated, the Application Team should do the following:",
      bullets=["Identify the consumers.", "Provide migration guidance.", "Define a retirement date.",
               "Monitor usage.", "Eventually remove access."]),

    H2("Consumer lifecycle", "consumerlc", [18]),
    R("The Application Team, as API owner, shall be responsible for the following:",
      bullets=["Adding consumers.", "Removing consumers.", "Changing consumer permissions.",
               "Reviewing unused consumers.", "Revoking access when it is no longer required."]),

    H2("Developer Portal", "portal", [19]),
    R("The Platform shall provide a Developer Portal.",
      chg="README §19 said 'should'; strengthened because §38 lists Developer Portal as 'Required'."),
    R("The Developer Portal should provide the following:",
      bullets=["API discovery", "API documentation", "API versions", "Authentication requirements",
               "Authorization requirements", "Usage information", "Access request information"]),
    R("The Developer Portal should give clear instructions on how to obtain authorization to consume an API."),
    P("The mechanism for issuing credentials or granting access depends on the organization's "
      "implementation and is not inherently a responsibility of the Gateway."),
    R("The API owner shall be responsible for the accuracy of the API documentation."),
]))

# 8 -------------------------------------------------------------------------
CHAPTERS.append(CH("CFG", "Configuration Management", [
    H2("Git as the source of truth", "git", [20]),
    R("API configuration shall be synchronized with Git.",
      chg="README §20 said 'should'; strengthened because §38 lists Git Integration as 'Required'."),
    R("Git shall serve as the source of truth for the following:",
      bullets=["API definitions", "Routes", "Policies", "Gateway configuration",
               "Version configuration", "Consumer configuration where appropriate"],
      chg="README §20 said 'should'; strengthened, together with the previous requirement."),
    R("Direct manual changes to production Gateway configuration should be avoided."),
    RAT("Using Git as the source of truth provides change history, review, auditability, rollback, "
        "reproducibility and consistency between environments."),

    H2("GitOps", "gitops", [21]),
    P("The preferred operating model is GitOps."),
    R("Changes to Gateway configuration should follow this sequence:",
      bullets=["Defined in Git.", "Reviewed.", "Validated.", "Approved.", "Deployed automatically."]),
    FIG("gitops", "fig_gitops.png", "Configuration change flow",
        "Flow diagram. A change is defined in Git as a pull request, reviewed, automatically validated, "
        "approved and automatically deployed to the API Gateway. Secrets management supplies secrets "
        "to the Gateway at deployment. Git records what was requested and approved; Gateway audit "
        "records what was executed."),
    R("Production should not depend on undocumented manual configuration."),
    R("The deployed state should be reproducible from the repository."),

    H2("Secrets", "secrets", [22]),
    R("Secrets, including passwords, private keys, API secrets, client secrets and long-lived "
      "credentials, shall not be stored in Git."),
    R("Secrets shall be stored in a dedicated secrets-management solution.",
      chg="README §22 said 'should'; strengthened because §38 lists Secrets Storage as a 'separate "
          "secure system'."),
    R("The deployment process should combine the configuration held in Git with the secrets held in the "
      "secrets-management solution to produce the runtime configuration."),
]))

# 9 -------------------------------------------------------------------------
CHAPTERS.append(CH("OBS", "Observability and Audit", [
    H2("Runtime logging", "logging", [23]),
    R("The Gateway shall provide centralized observability."),
    R("At a minimum, runtime logging shall record the following:",
      bullets=["Consumer identity", "API", "Operation", "Timestamp", "HTTP status", "Request result",
               "Latency", "Rejection reason", "Rate-limit information where relevant"],
      chg="README §23 said 'should'; strengthened because §38 lists Runtime Logs as 'Required'."),
    R("The Gateway should not log sensitive business payloads by default."),
    R("Which information is sensitive should be defined per API by the Application Team.",
      chg="New requirement, decided during review: sensitive information is defined per API, and payloads "
          "involving it are not logged."),
    R("Observability should integrate with the organization's existing logging and monitoring systems."),

    H2("Metrics", "metrics", [24]),
    R("The Gateway shall expose metrics for the following:",
      bullets=["Request volume", "Error rate", "Latency", "Backend latency", "Availability",
               "Rate limiting", "Authentication failures", "Authorization failures",
               "Backend failures", "Gateway health"],
      chg="README §24 said 'should'; strengthened because §38 lists Metrics as 'Required'."),
    R("Metrics should be available by the following dimensions:",
      bullets=["API", "Operation", "Consumer", "Backend", "Environment"]),

    H2("Audit", "audit", [25]),
    R("Audit logging shall be performed for all administrative and configuration activities."),
    R("Audit logs shall record at least the following:",
      bullets=["Who performed the action.", "What was changed.", "When it was changed.",
               "Which API or configuration was affected."],
      chg="README §25 said 'should'; strengthened because audit logging is stated to be mandatory."),
    R("Audit logs shall be sent to a centralized system outside the direct control of the person "
      "performing the operation.",
      chg="README §25 said 'should'; strengthened for the same reason."),
    P("Two complementary sources of evidence exist for each change, as set out in {tbl:evidence}."),
    TBL("evidence", "Sources of audit evidence",
        ["Source", "Evidence provided"],
        [["Git", "What change was requested and approved."],
         ["Gateway audit", "What was actually changed or executed."]],
        [4.0, 12.0]),
    NOTE("No retention period is defined for runtime logs or audit logs."),
]))

# 10 ------------------------------------------------------------------------
CHAPTERS.append(CH("AVL", "Availability and Deployment Architecture", [
    H2("Availability", "sla", [26]),
    R("The Platform shall provide at least 99.9% monthly availability during regular operation.",
      chg="README §26 said 'should'; strengthened because it is stated as an SLA. 'During regular "
          "operation' added by a review decision: planned maintenance is not counted."),
    P("Availability is measured during regular operation; planned maintenance is excluded from the "
      "calculation. This commitment applies to the Gateway platform and does not imply availability of "
      "backend applications."),
    NOTE("For information: 99.9% availability in a 30-day month allows approximately 43 minutes of "
         "unavailability during regular operation."),
    R("The Platform shall not contain a single point of failure.",
      chg="README §26 said 'should not'; strengthened because §38 lists High Availability as 'Required'."),
    R("The Platform shall provide the following:",
      bullets=["Multiple Gateway instances", "Failure tolerance", "Controlled upgrades",
               "Controlled resets", "Rollback capability", "Health-based traffic management"]),

    H2("Controlled reset", "reset", [27]),
    R("Gateway resets and restarts should be performed in a controlled manner."),
    R("Maintenance should be performed on a rolling basis."),
    R("A planned Gateway reset shall not intentionally prevent new requests from being served when "
      "redundant capacity is available."),
    NOTE("Existing sessions may be affected during a reset where this is technically unavoidable."),

    H2("Distributed deployment", "distributed", [28]),
    R("The Gateway should be deployed close to the applications it serves."),
    R("Where an application exists in multiple sites, the Gateway shall be available in each relevant site.",
      chg="README §28 said 'should'; strengthened because §38 lists Distributed Data Plane as 'Required'."),
    R("A failure or network partition affecting another site shall not prevent local APIs from operating.",
      chg="README §28 said 'should not'; strengthened for the same reason."),
    RAT("This reduces dependency on a remote site for local application traffic."),

    H2("Centralized management and distributed runtime", "mgmt", [29]),
    R("The Platform should combine a centralized Management Plane with a distributed Data Plane."),
    R("The Management Plane may be centralized."),
    R("The Data Plane shall be distributed.",
      chg="README §29 said 'should'; strengthened because §38 lists Distributed Data Plane as 'Required'."),
    R("The loss of the Management Plane shall not immediately stop already-configured API traffic.",
      chg="README §29 and §40 item 24 said 'should not'; strengthened as the defining property of a "
          "distributed Data Plane."),
    R("The Data Plane shall continue to operate indefinitely using its last known valid configuration "
      "while the Management Plane is unavailable.",
      chg="README §29 said 'should'; strengthened for the same reason. 'Indefinitely' added by a review "
          "decision (no time limit on running without the Management Plane)."),
    R("The Management Plane should be restorable within one hour.",
      chg="New requirement from a review decision (recovery time for the Management Plane)."),
    NOTE("New configuration changes may depend on the availability of the Management Plane."),
    FIG("distributed", "fig_distributed.png", "Centralized management with distributed Data Planes",
        "Diagram. A central Management Plane sends configuration to an API Gateway in Site A and an API "
        "Gateway in Site B. Each Gateway serves the application in its own site. If the Management Plane "
        "is unavailable, each Gateway continues to serve traffic using its last known valid configuration."),
]))

# 11 ------------------------------------------------------------------------
CHAPTERS.append(CH("GOV", "Governance and Exceptions", [
    H2("Governance model", "model", [30]),
    P("Governance combines three mechanisms, described in {tbl:mechanisms}. The overall principle is:"),
    NOTE("**Enforce what can safely and consistently be enforced; document and guide the rest.**"),
    TBL("mechanisms", "Governance mechanisms",
        ["Mechanism", "Purpose", "Enforcement"],
        [["Mandatory guardrails", "Requirements that can and should be technically enforced.",
          "Technically enforced by the Platform."],
         ["Standards", "The organization's preferred and consistent way of operating APIs.",
          "Technically enforced where practical."],
         ["Guidelines", "Decisions that cannot or should not be enforced by technology.",
          "Documented and guided; not enforced."]],
        [4.2, 7.0, 4.8]),

    H2("Mandatory guardrails", "guardrails", [30]),
    R("Requirements that are suitable for technical enforcement should be implemented as mandatory "
      "Gateway guardrails."),
    R("Mandatory guardrails should include the following:",
      bullets=["HTTPS at required boundaries", "Authentication", "Required logging",
               "Maximum request size", "Mandatory organizational policies"]),
    NOTE("Communication within the cluster, including between the Gateway and backend services, uses "
         "HTTP. No minimum TLS version and no maximum request size are defined by this document."),

    H2("Standards", "standards", [30]),
    R("Standards should define the organization's preferred and consistent way of operating APIs."),
    R("Where practical, standards should be technically enforced."),

    H2("Guidelines", "guidelines", [30]),
    P("Not every architectural or operational decision can or should be enforced by technology."),
    R("Decisions that are not suited to technical enforcement should remain guidelines."),
    P("Examples of guidelines include:"),
    BUL(["Recommended caching", "Recommended timeout values", "Recommended API versioning strategy",
         "Recommended use of transformation"]),

    H2("Organizational governance", "orggov", [31]),
    R("An organizational governance body should define API standards and policies."),
    R("The Infrastructure Team should implement the requirements defined by the governance body as "
      "Gateway capabilities and guardrails."),
    R("Where organizational governance is not yet mature, the Infrastructure Team may temporarily "
      "provide governance for the Gateway platform itself."),
    R("Interim governance of the Gateway platform shall not make the Infrastructure Team the owner of "
      "individual APIs."),
    NOTE("An organizational governance body has not yet been defined. Interim governance by the "
         "Infrastructure Team therefore applies."),

    H2("Exceptions", "exceptions", [32]),
    R("The Platform should support a controlled exception mechanism."),
    R("An exception should have the following:",
      bullets=["A documented reason.", "An identified owner.", "An appropriate approval.",
               "Risk considerations.", "An expiration or review date where appropriate."]),
    R("Exceptions should not become an alternative to proper architecture."),
]))

# 12 ------------------------------------------------------------------------
CHAPTERS.append(CH("BND", "Platform Boundaries", [
    H2("Boundary overview", "matrix2", [33, 34, 35, 36]),
    P("The Gateway is one component of a wider security and infrastructure architecture. "
      "{tbl:boundaries} summarizes the boundary between the Gateway and each adjacent component."),
    TBL("boundaries", "Boundaries between the Gateway and adjacent components",
        ["Adjacent component", "The Gateway is responsible for", "The adjacent component is responsible for"],
        [["WAF",
          ["Authentication", "Authorization", "Routing", "Rate limiting", "API policies",
           "Request controls", "Timeouts", "API-level transformations", "API contract validation",
           "API observability"],
          ["Attack signatures", "SQL injection detection", "Cross-site scripting detection",
           "Malicious payload detection", "Bot protection", "Other application security controls"]],
         ["Load Balancer",
          ["Consumer to API handling", "Authentication and authorization", "Rate limiting and policy",
           "Routing and transformation", "Observability"],
          ["Distribution between backend instances", "Backend pool management"]],
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
    R("The Gateway shall not attempt to become a WAF.",
      chg="README §33 said 'should therefore not attempt to become a WAF'; strengthened as a boundary "
          "(§38: 'Separate component')."),
    R("A WAF may be placed in front of the Gateway when the security architecture requires it."),

    H2("Gateway and Load Balancer", "lbb", [34]),
    R("The Gateway and the organization's Load Balancer may coexist."),
    R("The boundary between the Gateway and the Load Balancer should be clearly defined, as described "
      "in {sec:lb}."),

    H2("Gateway and Identity Provider", "idp", [35]),
    P("The Gateway does not need to be the organization's Identity Provider."),
    R("The Gateway shall consume identity and validate the tokens issued by the Identity Provider."),
    R("The Identity Provider shall remain responsible for user authentication, client authentication, "
      "token issuance and identity lifecycle."),

    H2("Gateway and application", "app", [36]),
    R("The Gateway shall provide infrastructure-level protection."),
    R("The application shall remain responsible for business authorization, business validation, "
      "business logic, data access control and business-level auditing."),
    P("The division of authorization decisions is illustrated in {tbl:authz_split}."),
]))

# 13 ------------------------------------------------------------------------
CHAPTERS.append(CH("VND", "Vendor Neutrality", [
    H2("Principle", "vprinciple", [37]),
    R("The Gateway architecture should minimize unnecessary vendor lock-in."),
    R("The following should remain conceptually independent of any specific product:",
      bullets=["API contracts", "API lifecycle", "Authentication model", "Authorization model",
               "GitOps workflow", "Governance model", "Observability requirements",
               "Deployment model"]),

    H2("Vendor-specific capabilities", "vspecific", [37]),
    R("Vendor-specific capabilities may be used when they provide significant value."),
    R("Vendor-specific capabilities that are used should be identified as implementation-specific."),
    P("The goal is not to guarantee zero migration effort. The goal is to ensure that:"),
    NOTE("**The organization's API architecture and policies are not unnecessarily defined by the "
         "implementation details of a single Gateway product.**"),
]))

# ---------------------------------------------------------------------------
# Appendices
# ---------------------------------------------------------------------------

CHAPTERS.append(CH("APA", "Capability Summary and Requirements Register", [
    H2("Capability summary", "capsummary", [38]),
    P("{tbl:capabilities} summarizes the status of each capability. "
      "**Required** means the Platform shall provide the capability and apply it. "
      "**Required capability** means the Platform shall provide the capability, and the Application "
      "Team decides whether to enable it for a given API. **Preferred** identifies the preferred "
      "operating model. The remaining entries identify responsibilities that lie outside the Gateway."),
    TBL("capabilities", "Capability summary",
        ["Capability", "Status", "Specified in"],
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

    H2("Requirements register", "register", []),
    P("The register lists every numbered requirement in this document. It is generated from the "
      "requirement text, so it always matches the body of the document."),
    {"t": "register"},
], appendix="A"))

CHAPTERS.append(CH("APB", "Operating Model", [
    P("{fig:operating_model} summarizes the operating model. Application Teams operate their APIs "
      "through the Platform by defining them in Git. The Infrastructure Team owns the Platform, which "
      "combines central management with a distributed Data Plane and enforces the capabilities "
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

CHAPTERS.append(CH("APC", "Open Issues and Decisions Pending", [
    P("The following items are not defined in this version of the document. They are recorded here "
      "so that they are resolved deliberately rather than by default."),
    TBL("openissues", "Open issues",
        ["ID", "Topic", "Decision or information required", "Related"],
        [["OI-01", "Capability enablement",
          "Confirm which capabilities are optional per API and which are mandatory guardrails for every "
          "API (for example rate limiting, caching and schema validation).", "{sec:normative}"],
         ["OI-02", "Requirement levels",
          "Review the requirements expressed as 'should', for example token-based B2B access, GitOps and "
          "the default retry position, to decide whether any should become 'shall'.", "{sec:normative}"],
         ["OI-03", "Consumer configuration in Git",
          "Define which consumer configuration is held in Git and which is managed at runtime.",
          "{sec:git}"],
         ["OI-04", "Governance body",
          "Define the organizational governance body, including its owner and mandate. Until then the "
          "Infrastructure Team provides interim governance for the Platform.", "{sec:orggov}"]],
        [1.6, 3.4, 8.2, 2.8], first_bold=True),
], appendix="C"))


# ---------------------------------------------------------------------------
# Change-log material (written to CHANGES.md by build_docx.py)
# ---------------------------------------------------------------------------

RESOLVED = [
    "**Required vs. optional.** README §13/§15/§16 called rate limiting, caching and schema validation "
    "optional, while §38 called them 'Required capability'. Resolved as: the Platform shall provide "
    "the capability; whether it is enabled for a given API is the Application Team's decision "
    "(Section 1.4, Appendix A). Confirm in OI-01.",
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
    "Section 1.3 Audience, 1.4 Normative language, 1.5 Definitions and abbreviations, 1.6 References.",
    "Requirement identifiers (GW-AAA-NNN) and the requirements register (Appendix A.2).",
    "Section 3.1 Roles table (roles are described in the README only implicitly).",
    "The 99.9% availability informative note (approx. 43 minutes per 30-day month).",
    "{ch:APC} Open issues and decisions pending (OI-01 to OI-04).",
    "Requirements and notes added from review decisions (listed in the next section).",
]

# Decisions taken while resolving the draft open issues. Each is recorded in the
# document as a requirement or note; the interpretation is stated so it can be checked.
DECISIONS = [
    ("Token lifetime", "Defined by the owner of the Identity Provider; the document says so "
                       "({sec:consumers}, note)."),
    ("Transport security", "Traffic inside the cluster, including Gateway to backend, uses HTTP; no minimum "
                           "TLS version is defined ({sec:guardrails}, note). 'HTTPS at required boundaries' is "
                           "kept as a guardrail example, without saying which boundaries."),
    ("Maximum request size", "No maximum is defined ({sec:guardrails}, note). 'Maximum request size' stays in "
                             "the README's list of guardrail examples."),
    ("Availability measurement", "99.9% applies during regular operation; planned maintenance is excluded "
                                 "({sec:sla})."),
    ("Management Plane", "The Data Plane runs on its last known configuration indefinitely, and the Management Plane should be restorable within one hour "
                         "({sec:mgmt})."),
    ("Retention", "No log or audit retention period is defined (note in {sec:audit})."),
    ("Sensitive payloads", "Payloads involving sensitive information should not be logged; what is "
                           "sensitive is defined per API by the Application Team ({sec:logging})."),
    ("Health checks beyond HTTP", "Read as: regular health checks apply to all API technologies, with no "
                                  "protocol-specific mechanism ({sec:health}, note). Please confirm this reading."),
    ("Anonymous APIs", "Not permitted (new requirement in {sec:consumers})."),
    ("Governance body", "Not yet defined; recorded in {sec:orggov} and kept open as OI-04."),
    ("Scope gaps", "Read 'yes' as: WebSocket/streaming, east-west traffic, multi-tenancy and "
                   "non-production environments are in scope ({sec:scope}). Please confirm this reading."),
]
