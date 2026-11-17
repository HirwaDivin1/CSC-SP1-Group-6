
# B05 – Distributed Criminal Case Document Storage, Access, and Failure Recovery

Student: Kapil Tamang  
Project: B05 – Resilient Case Management Services  
Last updated: November 9, 2026  
Document status: Assignment 1 draft

## Progress Note

 I expanded the requirements for my distributed criminal case document storage and retrieval project. I defined five functional requirements covering document storage, retrieval, replication, failure recovery, and invalid requests. I also added correctness rules and proposed measurable targets for retrieval time, replication time, and failover performance. Using my workflow diagram, I compared a simple single-node storage approach with a two-node replicated approach to identify their differences in availability, performance, and complexity. I reviewed the LADA case management system RFP and PostgreSQL's high-availability documentation to support the project context and comparison. My next step is to evaluate the alternatives further and select a final design in Assignment 3. Implementation and performance testing have not yet been completed.

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

I am investigating how criminal case documents can be stored, located, accessed, viewed, and transferred across independent servers. At LADA, prosecutors, case intake clerks, and paralegals need police reports and other case documents for filing preparation, case review, and hearings. They need timely access to the correct document version.

My project focuses on where a document is stored on a server, how its location is recorded, how authorized users retrieve and view it, and how long retrieval and transfer take. I will also investigate how document copies are kept up to date and how a verified copy can be retrieved if the primary storage node fails. Failure recovery is one part of the complete storage-to-viewing workflow.

### Stakeholders and Needs

| Stakeholder | Task | Need |
|---|---|---|
| Prosecutor | Retrieve documents for hearings | Timely access to the correct version |
| Case intake clerk | Store and organize records | Reliable document IDs and storage locations |
| Paralegal | Prepare supporting case materials | Dependable access to required files |
| IT administrator | Maintain document access services | Detect failures and restore access |

### Current Workflow

LADA's official RFP-DA-IT01 describes its Prosecutor Information Management System (PIMS) and supporting tools, including eFolder, SharePoint, Notes/Domino, and eCER. The RFP identifies fragmented applications, duplicate data entry, and limited integration, and calls for a modern, integrated case management system. [1]

A typical task involves identifying a case, finding its document in the appropriate application, retrieving it, and reviewing it. My proposed design examines the full process through independent services: store the PDF on a node, record its ID and location, retrieve it for viewing, measure transfer time, maintain another copy, and recover access if a node becomes unavailable. This is a student design, not a description of LADA's current storage architecture.

### Concrete Scenario

Consider fictional case LADA-DEMO-104. Police report DOC-104-01, version 2, is stored on Storage Node A, with a replicated copy on Storage Node B. In the prototype, the file could be saved under a path such as `cases/LADA-DEMO-104/DOC-104-01/v2.pdf`. A metadata database records its document ID, version, checksum, and storage locations.

A prosecutor requests the report. The Document Access Service checks the simulated user's authorization, locates the document through metadata, retrieves it from Node A, and returns the PDF for viewing. I plan to measure the retrieval time and the time required to copy updates to Node B.

If Node A stops responding, the service tries Node B. When Node B has a complete, verified version 2, the request can succeed. If it has only version 1, the service reports that the required version is unavailable rather than returning an outdated report. This scenario connects storage, location, access, transfer, replication, version correctness, and failure recovery.

### Workflow Image

![Distributed criminal case document workflow showing an authorized user, Document Access Service, metadata database, two storage nodes, replication, and failover.](my-project/assets/arch.png)

*Figure 1. Proposed distributed document workflow. The access service uses metadata to locate the file, retrieves it from Node A during normal operation, and returns it for viewing. Node B stores a replica and can provide a verified copy if Node A is unavailable. This is a student prototype, not LADA's current infrastructure.*

### Evidence and Existing Approach

The LADA RFP establishes a need to modernize and integrate case-management applications. Its discussion of PIMS, eFolder, and related tools provides the real-world setting for investigating dependable access to case documents. [1]

PostgreSQL's high-availability documentation describes database replication and standby techniques. [2] I will study these ideas while distinguishing metadata replication from copying actual PDFs. My proposed system uses a Document Access Service, a metadata database for IDs, versions, and locations, and two file-storage nodes.

### Six-Week Contribution (Semester I)

I will investigate and design one small document workflow: store a fictional PDF, record its location, retrieve and view the requested version, transfer an updated copy to another node, and handle a primary-node failure. The scope includes one simulated authorized user, a small set of fictional PDFs, one Document Access Service, one metadata database, and two storage services.

I will define expected results for normal retrieval, replica updates, and node failure, and plan measurements for retrieval time, transfer time, replication delay, and version correctness. A small proof of concept may be developed if time permits. The goal is a manageable, testable design, not a complete case-management system.

### Semester II Scope

In Semester II, I plan to implement the Document Access Service and two storage nodes, store and replicate fictional PDFs, and simulate a node failure. I will compare a single-node baseline with the replicated design using different file sizes. I plan to measure retrieval latency, file transfer time, replica-update delay, failover delay, successful retrieval rate, and document-version correctness to evaluate performance and reliability tradeoffs.

### Exclusions

- The project focuses on document storage, location, viewing, retrieval, transfer, replication, and failure recovery rather than a complete case management system.
- The prototype will use fictional PDF documents instead of confidential criminal case records.
- Direct integration with courts, police databases, and government production systems is outside the initial scope.
- Legal decision-making, prosecution workflows, victim notifications, and other administrative functions will not be implemented.
- Large-scale production deployment and advanced disaster recovery are future possibilities, not part of the initial prototype.

2. Requirements and Success Criteria


## 2. Requirements and System Specification

### System Overview

The proposed system will allow authorized users to store, locate, retrieve, and view criminal case documents across independent storage nodes. The Document Access Service will communicate with a PostgreSQL metadata database to identify document IDs, versions, checksums, and storage locations.

Under normal operation, the system will retrieve documents from Storage Node A. Storage Node B will maintain a replicated copy that can be used when the primary storage node becomes unavailable. The system must verify that the retrieved document matches the requested version before returning it to the user.

The following requirements define the expected behavior of the proposed prototype. All performance targets are proposed and have not yet been measured.

### Functional Requirements

| Requirement ID | Requirement | Acceptance Check |
|---|---|---|
| FR-01 | The system shall store a fictional PDF on Storage Node A and record its document ID, version, checksum, and storage location in the metadata database. | Upload `DOC-104-01` version 2 and verify that the PDF exists on Node A and its metadata record contains the correct information. |
| FR-02 | The system shall allow an authorized user to request a document by ID and version and retrieve it from an available storage node. | Request `DOC-104-01` version 2 while Node A is online. Verify that the requested PDF is returned and can be viewed. |
| FR-03 | The system shall transfer document updates from Storage Node A to Storage Node B and verify that the replicated copy is complete. | Store version 2 on Node A, replicate it to Node B, and compare the document version and checksum on both nodes. |
| FR-04 | The system shall retrieve a verified document from Storage Node B when Storage Node A becomes unavailable. | Stop Node A and request version 2. Verify that Node B supplies the correct document when an identical verified copy exists. |
| FR-05 | The system shall reject unauthorized document requests and report an error when the requested document or correct version is unavailable. | Test an unauthorized user and request version 2 when only version 1 is available. Verify that neither request returns a document. |

### Correctness Rules

**CR-01 – Document Version Correctness**

The system must return only the document version requested by the authorized user. A document is valid for retrieval only when its ID, version, and checksum match the information recorded in the metadata database.

For example, if a prosecutor requests `DOC-104-01` version 2 and Storage Node B contains only version 1, the system must not return version 1 as a replacement. Instead, it must report that the requested version is unavailable.

**CR-02 – Replica Integrity**

A replicated document must match the original document's content before it is marked as verified. The system will use a SHA-256 checksum to compare the original PDF with its replicated copy. If the checksums do not match, the replica must not be returned as a valid document.

### Measurable Quality Targets

The following values are proposed targets for a small prototype running on a controlled local test environment. They are not measured performance results.

| Quality ID | Quality Target (Proposed) | Measurement and Acceptance Check |
|---|---|---|
| QT-01 | Normal document retrieval should complete within 2 seconds for a 1 MB PDF. | Perform 20 requests while Node A is online and measure the time from request submission until the full PDF is received. At least 19 should complete within 2 seconds. |
| QT-02 | Replication of a 1 MB PDF should complete within 3 seconds. | Perform 20 replication operations and measure the time from the start of the transfer until Node B has a verified copy. At least 19 should complete within 3 seconds. |
| QT-03 | Retrieval through Node B after Node A becomes unavailable should complete within 5 seconds. | Perform 20 requests with Node A intentionally unavailable and a verified copy already on Node B. At least 19 should complete within 5 seconds. |
| QT-04 | Every successful retrieval must return the requested document version with a matching checksum. | Test normal retrieval, failover retrieval, and outdated-replica cases. No test may return an incorrect document as successful. |

### Ordinary Input and Output Example

**Normal Operation**

Input:

- User: Authorized Prosecutor
- Case ID: `LADA-DEMO-104`
- Document ID: `DOC-104-01`
- Requested version: 2
- Storage Node A: Available
- Storage Node B: Available

Expected Output:

- Status: Success
- Document: `DOC-104-01` version 2
- Retrieved from: Storage Node A
- Verification: Version and checksum match
- Result: PDF returned for viewing

The Document Access Service authenticates the simulated user, searches the metadata database, identifies the correct storage location, and retrieves the requested document from Node A.

### Unsuccessful Case

Input:

- User: Authorized Prosecutor
- Document ID: `DOC-104-01`
- Requested version: 2
- Storage Node A: Unavailable
- Storage Node B: Contains only version 1

Expected Output:

- Status: Document unavailable
- Reason: Requested version 2 is not available on a verified storage node
- Result: No document returned

The service must not return version 1 because it does not match the requested version. This test checks whether the system preserves document correctness during a storage-node failure.

### Assumptions

The prototype assumes that a small collection of fictional PDF documents will be used for testing. The Document Access Service will communicate with two independently operated storage services over a simulated or local network. PostgreSQL will store document metadata, including document IDs, versions, checksums, and storage locations.

User authorization will be simulated rather than connected to a real government identity system. The initial tests assume that the metadata database and Document Access Service remain available while individual storage-node failures are introduced. Replication will be tested after each document update, and a copy will be considered valid only after verification.

### Constraints

The system will use one Document Access Service, one PostgreSQL metadata database, and two storage nodes. All documents will be fictional, and no confidential criminal case information will be used.

The project will focus on storage, retrieval, document transfer, replication, version correctness, and recovery from a storage-node failure. It will not implement an entire criminal case management system or integrate directly with government databases.

A failure of the metadata database, simultaneous failure of both storage nodes, automatic conflict resolution for concurrent updates, and large-scale disaster recovery are outside the initial prototype scope.

The performance measurements will depend on the test environment, file sizes, and simulated network conditions. The proposed targets may be revised after initial experiments.


## 3. Alternatives and Selected Solution

### Overview

This section compares two possible approaches for storing, retrieving, and recovering criminal case documents across storage servers. The first approach uses a single storage node as a simple baseline. The second approach uses two independent storage nodes with replication and failure recovery.

Both approaches will be compared against the requirements defined in Section 2, including document storage, retrieval, version correctness, transfer time, and availability during a storage-node failure. The final design will be selected in Assignment 3.

### Approach 1: Single-Node Document Storage (Baseline)

The first approach stores all fictional criminal case documents on one storage node. The Document Access Service uses the PostgreSQL metadata database to locate the requested PDF and retrieve it from that node.

When an authorized prosecutor requests a document, the service checks the metadata database, identifies the correct document version, retrieves the file, verifies its checksum, and returns it for viewing.

This approach is simple to implement because it requires only one storage location. It also avoids the additional work of transferring files between servers and keeping replicated copies synchronized.

However, if the storage node becomes unavailable, the system cannot retrieve the document. Even if the metadata database remains operational, the actual PDF remains inaccessible until the storage node is restored.

This approach provides a useful baseline for measuring normal retrieval performance, but it does not satisfy the replication and failure-recovery requirements.

### Approach 2: Two-Node Replicated Document Storage

The second approach stores the original document on Storage Node A and maintains a replicated copy on Storage Node B.

The Document Access Service retrieves document locations and versions from PostgreSQL. During normal operation, it retrieves the requested PDF from Node A. When a document is updated, the system transfers a copy to Node B and verifies that the replicated content matches the original.

If Node A becomes unavailable, the service attempts to retrieve the requested document from Node B. Before returning the PDF, it verifies that the document ID, version, and checksum match the requested information.

This approach provides an alternative storage location when the primary node fails. It also allows the prototype to measure replication time, document transfer time, and retrieval performance during normal operation and failure recovery.

However, replication introduces additional complexity. Document updates must be transferred correctly, both copies must remain consistent, and the system must avoid returning outdated or incomplete files.

For example, if Node A contains version 2 but Node B contains only version 1, the system must not return version 1 when version 2 is requested. Instead, it must report that the requested version is unavailable.

### Comparison of the Two Approaches

| Evaluation Criteria | Approach 1: Single Node | Approach 2: Two Nodes |
|---|---|---|
| FR-01: Document storage and metadata | Supported | Supported |
| FR-02: Authorized document retrieval | Supported while node is available | Supported while a valid copy is available |
| FR-03: Document replication | Not supported | Supported by design |
| FR-04: Recovery from primary-node failure | Not supported | Supported if Node B has a verified copy |
| FR-05: Invalid and unauthorized request handling | Can be implemented | Can be implemented |
| CR-01: Correct document version | Can be checked | Requires checking primary and replica versions |
| CR-02: Replica integrity | Not applicable | Requires checksum verification |
| QT-01: Normal retrieval within 2 seconds | To be measured | To be measured |
| QT-02: Replication within 3 seconds | Not supported | To be measured |
| QT-03: Failover retrieval within 5 seconds | Not supported | To be measured |
| QT-04: Version and checksum correctness | Can be tested for normal retrieval | Can be tested for normal and failover retrieval |
| Implementation complexity | Lower | Higher |
| Availability during Node A failure | Document unavailable | Document may be available through Node B |

### Evaluation Plan

Both approaches will be tested using the same fictional PDF documents and the same local test environment. Initial tests will use 1 MB PDF files, with additional file sizes considered during Semester II.

For the single-node approach, I will store a document, record its metadata, retrieve the requested version, and measure retrieval time. I will then stop the storage node and attempt to retrieve the document again to observe the failure behavior.

For the two-node approach, I will repeat the normal retrieval test and then transfer the document to Storage Node B. I will verify that both copies contain the same version and matching checksums.

After replication, I will stop Storage Node A and request the document again. The system should retrieve the verified copy from Storage Node B when available.

The experiments will measure document retrieval latency, file transfer time, replication delay, failover retrieval time, and version correctness. These measurements will help determine whether the additional complexity of replication provides sufficient benefits.

### Evidence Supporting the Approaches

The Los Angeles County District Attorney's Office RFP-DA-IT01 describes the need to modernize and integrate its case management applications. This provides the real-world motivation for investigating reliable access to criminal case documents across separate services. The proposed storage architecture is a student design rather than a description of LADA's existing infrastructure. [1]

PostgreSQL's high-availability documentation describes replication, standby servers, and failure recovery in database systems. These concepts help explain how additional copies and recovery mechanisms can improve availability while introducing synchronization challenges. [2]

In this project, PostgreSQL will store document metadata, including document IDs, versions, checksums, and locations. The actual PDF files will be copied between storage services separately. PostgreSQL database replication alone does not automatically replicate externally stored PDF files.

### Preliminary Assessment

The single-node approach is easier to implement and provides a useful baseline for measuring normal document retrieval. However, it does not provide an alternative storage location when its only node fails.

The two-node approach requires additional work for document replication, synchronization, and verification. However, it provides the possibility of retrieving a correct document from another storage node when the primary node becomes unavailable.

Both approaches will be evaluated using the same functional requirements and proposed performance targets. The final design decision will be made in Assignment 3 after considering reliability, implementation complexity, feasibility, and the results of further analysis.

4. System Architecture

    Work to come in a later assignment.

    This section will describe the placement of the Document Access Service, metadata database, storage nodes, and communication interfaces in greater detail.

5. Component Responsibilities

    Work to come in a later assignment.

    This section will explain the responsibilities of individual services and describe how they communicate during document requests and storage failures.

6. Data Structures and Persistent Storage

    Work to come in a later assignment.

    This section will define document identifiers, version records, storage locations, checksums, and persistent metadata structures.

7. Algorithms and Pseudocode

    Work to come in a later assignment.

    This section will describe the document retrieval process, storage-node failure detection, replica selection, and version verification.

8. Implementation Plan

    Work to come in a later assignment.

    This section will explain the proposed software technologies, development environment, implementation steps, and milestones.

9. Testing and Evaluation

    Work to come in a later assignment.

    This section will define formal testing procedures for retrieval latency, network delays, storage-node failures, replication delays, and document-version correctness.

10. Risks, Limitations, and Security

    Work to come in a later assignment.

    This section will discuss authorization, document integrity, confidentiality, system availability, and the limitations of the local simulation.

11. Progress Note and Open Question

    Progress Note – November 6, 2026

    For Assignment 1, I read Chapters 1-4 of the course handbook and studied the Los Angeles County District Attorney's Office RFP-DA-IT01. This RFP enabled me to establish a problem documented in terms of a fragmented legacy case management application and a lack of integration between these systems.

    Originally, I was contemplating pursuing a more general case management project, but I decided to concentrate on a single specific distributed systems problem of obtaining a right document from the primary storage system.

    My main stakeholders were prosecutors and authorized case support staff, and I created a fictional scenario about obtaining a document by a prosecutor with a storage node failure.

    I additionally proposed an architecture that includes a Document Access Service, metadata database, and two separate storage nodes. The first workflow shows how documents can be found and retrieved under normal conditions as well as how retrieval can be attempted from a different node in case the main node fails.

    I defined the personal contributions for Semester I, the implementation goal for Semester II, and the project exclusions.

    So far, I have performed the initial problem investigation and set the project boundaries. I have not implemented the system and measured its performance.  

    Open Problem

    In a scenario where Storage Node A is down, what mechanism would allow the Document Access Service to ascertain that Storage Node B actually holds the most recent version of a case document and not an old replica?

    This issue is significant in light of the fact that storing multiple versions of the document can enhance availability, but the documents may not have identical versions.

    For example, if Node A crashes before replication occurs, Node B may actually hold an old version of the document. Using this version to provide the document will yield an erroneous answer.

    What I have to do is learn more about document versioning, integrity checking, and replica selection.

12. Sources and Existing Approaches

    Source 1: Los Angeles County District Attorney's Office

    Title: Request for Proposals RFP-DA-IT01 – Case Management System Solution

    Publication Date: September 29, 2026

    Relevant Sections: 2.1, 2.2, and 3.0

    Link: https://camisvr.co.la.ca.us/LACoBids/BidLookUp/BidDetail?BidNumber=RFP-DA-IT01

    This is the primary source for the real-world problem. The RFP describes LADA's legacy case management environment, supporting applications such as PIMS and eFolder, fragmented information systems, and integration difficulties.

    It also establishes the county's interest in implementing a modern, cloud-based case management system and identifies performance, integration, and disaster recovery as important concerns.

    The RFP provides evidence of the organizational need but does not directly establish the storage-node failure described in my hypothetical scenario.

    Source 2: PostgreSQL Documentation

    Topic: High Availability, Load Balancing, and Replication

    Link: https://www.postgresql.org/docs/current/high-availability.html

    The documentation outlines the current methods for database replication and high availability. It provides some insight into how persistent information can be duplicated between systems and the role of standby systems in recovery.

    Database replication using PostgreSQL is distinct from PDF replication. My proposed prototype will use PostgreSQL for document metadata while exploring PDF replication.

    Source 3: Course Handbook

    Name of source: Chapters 1-4 – Distributed Systems & Software Design Fundamentals

    Source: Class materials provided by the professor.

    These chapters cover communicating processes, client/server systems, persistence of data, partial failures, software design, Markdown for documentation, evidence labels, and narrowing down the scope of a student project.
