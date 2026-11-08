# B05 – Distributed Criminal Case Document Access and Failure Recovery

Student: Kapil Tamang  
Project: B05 – Resilient Case Management Services  
Last updated: November 8, 2026  
Document status: Proposed — initial draft for review

## Progress Note

This draft identifies prosecutors and authorized case staff at the Los Angeles County District Attorney's Office (LADA) as people who could benefit from reliable access to criminal case documents. I reviewed LADA's RFP-DA-IT01 to understand its legacy applications and integration challenges. I also reviewed PostgreSQL documentation on replication and high availability. I narrowed my contribution to investigating how a small distributed system can retrieve the correct document from another storage node when the primary node becomes unavailable. I have not implemented the prototype or collected performance measurements. My next step is to define a repeatable retrieval test for normal operation and a simulated failure.

## Contents

1. [Problem research and scope](#1-problem-research-and-scope)
2. [Requirements and system specification](#2-requirements-and-system-specification)
3. [Alternatives and selected solution](#3-alternatives-and-selected-solution)
4. [Architectural design](#4-architectural-design)
5. [Component design and interfaces](#5-component-design-and-interfaces)
6. [Data structure design](#6-data-structure-design)
7. [Algorithm design and execution](#7-algorithm-design-and-execution)
8. [Failures and security](#8-failures-and-security)
9. [Implementation and feasibility](#9-implementation-and-feasibility)
10. [Testing and verification](#10-testing-and-verification)
11. [Operation, maintenance, and future work](#11-operation-maintenance-and-future-work)
12. [Revision history and references](#12-revision-history-and-references)

## 1. Problem Research and Scope

### Problem and Affected People

I am investigating how criminal case documents can remain accessible when stored across independent computer services. Prosecutors, paralegals, and case intake clerks need to retrieve police reports, charging documents, and other case materials while preparing criminal cases.

The primary user is a prosecutor who needs the correct version of a document before a hearing. If its storage service is unavailable, or the only accessible copy is outdated, the prosecutor may not be able to retrieve the required file. My proposed contribution is a small distributed retrieval mechanism that locates an available copy and checks its version before returning it.

### Stakeholders and Needs

| Stakeholder | Task | Need |
|---|---|---|
| Prosecutor | Retrieve case documents | Fast access to the correct document version |
| Case intake clerk | Organize case records | Reliable document identifiers and locations |
| Paralegal | Prepare case materials | Consistent access to required files |
| IT administrator | Maintain storage services | Detect failures and restore document access |

### Current Workflow

LADA's RFP-DA-IT01 reports that the office uses the legacy Prosecutor Information Management System (PIMS) alongside eFolder, SharePoint, Notes/Domino, eCER, and spreadsheets. The RFP identifies fragmented systems, duplicate data entry, and limited integration. [1]

In a representative workflow, an authorized employee identifies a criminal case, locates a document in the relevant application or repository, and retrieves it for case preparation. This is a simplified assumed workflow, not a verified description of every LADA employee's steps. The RFP does not specify exactly where files are physically stored, the number of storage nodes, or current retrieval times.

### Concrete Scenario

Illustrative scenario, not a measured incident: A prosecutor preparing for a hearing requests police report `DOC-104-01`, version 2, for fictional case `LADA-DEMO-104`.

In my proposed prototype, Storage Node A holds the primary copy and Storage Node B maintains a replica. A Document Access Service receives the request and checks metadata about the document's version and location. Normally, it retrieves version 2 from Node A and returns the file.

Suppose Node A stops responding. The access service tries Node B. If Node B has a complete, verified version 2, the document can still be returned. If Node B has only version 1, the service must report that the required version is unavailable instead of silently returning an outdated file. This illustrates partial failure, replication, availability, and consistency in a distributed system.

### Workflow Image

![An authorized prosecutor requests a case document from a Document Access Service, which checks document metadata, retrieves the verified version from Storage Node A during normal operation, or uses Storage Node B as a replica after a primary-node failure.](assets/document-access-architecture.png)

*Figure 1. Proposed distributed case-document access and failure-recovery workflow. A prosecutor requests a document through a central service that checks metadata and retrieves the required version from a primary node or verified replica. This is a student simulation, not LADA's current architecture.*

### Evidence

LADA's official RFP-DA-IT01, dated September 29, 2026, documents legacy applications, fragmented information systems, limited integration, and the need for a modern cloud-based case management system with performance and disaster-recovery considerations. [1] It does **not** confirm that the county has experienced the specific storage failure in my example.

PostgreSQL's high-availability documentation describes database replication and standby approaches. [2] This helps me understand existing techniques, although replicating PostgreSQL records is not the same as replicating PDF files.

Assumptions to test: two independently running storage services can hold copies of a fictional document; one service may fail while the other remains available; and document versions and checksums can help verify a returned copy. I have not interviewed LADA staff or measured its storage performance.

### Six-Week Contribution (Semester I)

I will investigate one bounded operation: retrieving a required document from an available storage node when the primary node is unavailable. The initial model will have one test user, a few fictional PDF files, one access service, one metadata store, and two separate storage services. I will describe normal retrieval, primary-node failure, replica verification, and the outcomes the user should receive.

I will plan measurements of retrieval time, successful requests, and correct-version returns. A small proof of concept may be developed if time allows. The first assignment focuses on understanding and scoping the problem, not completing an enterprise storage system.

### Semester II Scope

The larger goal is to implement a working distributed document-retrieval prototype with basic replication, failure detection, version checking, and failover. I will compare single-node retrieval with two-node replicated retrieval using the same synthetic files and failure conditions. Measures will include retrieval latency, successful retrieval rate, failover delay, replication delay, and wrong-version outcomes. Results will describe the behavior of the prototype, not LADA's production systems.

### Exclusions

- Real criminal case records, confidential data, and connections to actual LADA infrastructure.
- Integration with real courts, police databases, or government cloud services.
- Prosecution decisions, court filing, evidence chain of custody, and victim notifications.
- A complete case management platform, full authentication system, or production security certification.
- Guarantees of access if both storage nodes, the shared metadata store, or the entire host computer fail.
- Datacenter-scale deployment or physical disaster recovery in the initial student prototype.

## 2. Requirements and System Specification

Work to come — Assignment 2. Define inputs, outputs, correctness rules, response-time criteria, and acceptance checks.

## 3. Alternatives and Selected Solution

Work to come — Assignments 2–3. Compare a single-node baseline with replicated document storage and justify the selected approach.

## 4. Architectural Design

Work to come — Assignment 3. Specify running components, network messages, deployment boundaries, and service dependencies.

## 5. Component Design and Interfaces

Work to come — Assignment 3. Define responsibilities, request and response formats, errors, and repeated-call behavior.

## 6. Data Structure Design

Work to come — Assignment 4. Define document identifiers, version metadata, checksums, replica locations, and persistent records.

## 7. Algorithm Design and Execution

Work to come — Assignment 4. Add retrieval and failover pseudocode, including normal and interrupted executions.

## 8. Failures and Security

Work to come — Assignment 4. Analyze node failures, stale replicas, network delays, authorization, and excluded failure conditions.

## 9. Implementation and Feasibility

Work to come — Assignments 3–6. Document development tools, local setup, implementation status, and a small feasibility experiment.

## 10. Testing and Verification

Work to come — Assignments 4–6. Specify reproducible tests and report observed retrieval, failover, and replication performance.

## 11. Operation, Maintenance, and Future Work

Work to come — Assignments 4–6. Describe monitoring, diagnosis, recovery, maintenance, limitations, and Semester II milestones.

## 12. Revision History and References

### Revision History

| Revision date | Change to my design | Reason and evidence |
|---|---|---|
| November 8, 2026 | Defined stakeholders, document-retrieval scenario, small contribution, exclusions, and workflow image | Assignment 1; informed by LADA's RFP and course Chapters 1–4 |

### One Open Question

| Open question | Why it matters | Next action |
|---|---|---|
| How can the access service verify that Node B contains the required current document version when Node A fails, without adding excessive retrieval delay? | A replica might be available but outdated, and returning it as current would be incorrect. | Investigate version checks and compare normal and failover retrieval in a controlled test. |

### References

1. Los Angeles County District Attorney's Office. *Request for Proposals RFP-DA-IT01 – Case Management System Solution* (September 29, 2026), especially Sections 2.1, 2.2, and 3.0. https://camisvr.co.la.ca.us/LACoBids/BidLookUp/BidDetail?BidNumber=RFP-DA-IT01
2. PostgreSQL Documentation. *High Availability, Load Balancing, and Replication*. https://www.postgresql.org/docs/current/high-availability.html
3. GitHub Docs. *Basic Writing and Formatting Syntax*. https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax
4. Course handbook. *Chapters 1–4: Distributed Systems and Software Design Foundations*. Instructor-provided reading.
