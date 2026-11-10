
# B05 – Distributed Criminal Case Document Storage, Access, and Failure Recovery

Student: Kapil Tamang  
Project: B05 – Resilient Case Management Services  
Last updated: November 9, 2026  
Document status: Assignment 1 draft

## Progress Note

I reviewed the Los Angeles County District Attorney's Office (LADA) case management system Request for Proposals (RFP) and Chapters 1–4 of the course handbook. The RFP describes several older applications and integration challenges. I narrowed my individual B05 contribution to investigating how criminal case documents are stored, located, accessed, transferred, replicated, and recovered across independent services.

I identified the main stakeholders, developed a fictional case scenario, and prepared a workflow diagram. I also reviewed PostgreSQL's high-availability documentation to better understand replication and data availability. My next step is to define testable requirements and determine how to measure document retrieval and transfer time. The prototype and performance measurements are planned work.

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

I am investigating how criminal case documents can be stored, located, accessed, viewed, and transferred across multiple independent servers in a distributed system. I also want to understand how the system maintains access to the correct documents when one storage server becomes unavailable.

At the Los Angeles County District Attorney's Office, prosecutors, case intake clerks, and paralegals use criminal case documents such as police reports and charging documents for filing preparation, case review, and hearings. These users need to locate and retrieve the correct document version without unnecessary delays.

My project focuses on understanding where documents are stored, how their locations are recorded, how authorized users retrieve and view them, and how long documents take to transfer between services. I will also investigate how document copies are synchronized and how another storage node can provide access when the primary node fails.

The goal is to investigate a small distributed document-access mechanism that supports reliable storage, efficient retrieval, document-version correctness, and continued availability during individual storage-node failures.

### Stakeholders and Needs

| Stakeholder | Task | Need |
|---|---|---|
| Prosecutor | Locate, retrieve, and view criminal case documents | Timely access to the correct document version |
| Case intake clerk | Store and organize case records | Reliable document identifiers and storage locations |
| Paralegal | Retrieve supporting case documents | Dependable access to required files |
| IT administrator | Maintain document storage and access services | Identify server failures and restore document availability |

### Current Workflow

LADA's official RFP-DA-IT01 describes its Prosecutor Information Management System (PIMS) and supporting applications, including eFolder, SharePoint, Notes/Domino, and eCER. The RFP identifies fragmented applications, duplicate data entry, and limited integration between systems. It calls for a modern, integrated, cloud-based case management system. [1]

A typical document-access task begins when an authorized employee identifies a criminal case and locates the required document in the appropriate application or repository. The employee then retrieves and reviews the document for case preparation.

My project investigates how this process could work within a proposed distributed system where different services are responsible for document storage, location, retrieval, replication, and recovery. The investigation will focus on five connected areas.

### 1. Document Storage

The first part of my project focuses on understanding where criminal case documents are stored within a distributed system.

In my proposed prototype, Storage Node A contains the primary PDF document, while Storage Node B maintains another copy. The actual document files are saved within the storage services.

A separate metadata database records information such as the document ID, version number, checksum, and storage-node locations.

This allows the Document Access Service to identify where a requested document is stored without requiring the prosecutor to know the physical server or file path.

I want to investigate how document storage locations are organized and how the system determines which server contains a particular document.

### 2. Document Location and Access

The second part focuses on how authorized users locate, retrieve, and view stored documents.

For example, a prosecutor may request a police report using its document ID and required version number.

The Document Access Service receives the request, checks the simulated user's authorization, and queries the metadata database to determine which storage node contains the requested document.

The service then contacts an available storage node, retrieves the file, and returns the PDF so the prosecutor can open and view it.

This part of the project investigates how separate services communicate to provide access to documents without requiring users to manually search individual servers.

### 3. Document Transfer and Performance

The third part focuses on how documents move between storage services and how long retrieval and transfer operations take.

When a document is requested, the Document Access Service communicates with the metadata database and the selected storage node. The file must then be transferred over the network before the user can view it.

I want to investigate the time required to retrieve a complete document and the time required to copy a document from one storage node to another.

I plan to test fictional PDF documents of approximately 1 MB, 10 MB, and 50 MB to compare retrieval and transfer times under controlled conditions.

These measurements will help evaluate how document size and distributed communication affect retrieval performance.

### 4. Replication and Synchronization

The fourth part focuses on maintaining document copies across different storage nodes.

In my proposed system, Storage Node A contains the primary document, and Storage Node B maintains a replicated copy.

When a document is created or updated on Node A, the updated version must be copied to Node B.

The system will use document metadata, version numbers, and checksums to determine whether the replica contains the required document.

I want to investigate how long replication takes and how the system can identify outdated copies.

This is important because having multiple copies does not guarantee that every storage node contains the latest correct version.

### 5. Failure Recovery and Availability

The fifth part focuses on what happens when a storage node becomes unavailable.

If Storage Node A stops responding, the Document Access Service attempts to locate and retrieve the requested document from Storage Node B.

Before returning the document, the service verifies that Node B contains the correct version.

If Node B contains the requested version, the user can continue accessing the document. If Node B only contains an outdated version, the system reports that the required version is unavailable instead of returning the wrong file.

I want to investigate how this recovery process affects document availability and retrieval time.

This will allow me to compare normal document retrieval with retrieval during a simulated storage-node failure.

### Concrete Scenario

Consider a fictional criminal case identified as LADA-DEMO-104.

A prosecutor preparing for a hearing needs to view police report DOC-104-01, version 2.

In the proposed prototype, the report is stored on Storage Node A. The metadata database records the document ID, version number, and locations of available copies.

When the prosecutor requests the report, the Document Access Service checks the metadata database to identify where the document is stored.

During normal operation, the service retrieves version 2 from Node A, transfers the PDF, and returns it to the prosecutor for viewing.

The system also maintains a replicated copy on Storage Node B. When the report is updated, the system attempts to synchronize the updated version between the storage nodes.

Now consider what happens if Storage Node A becomes unavailable.

Instead of immediately failing the request, the Document Access Service attempts to retrieve the document from Storage Node B.

If Node B contains a complete, verified version 2, the prosecutor can still retrieve the correct police report.

If Node B contains only version 1, the service reports that the requested version is unavailable.

This fictional scenario demonstrates the complete distributed document workflow, including storage, location, access, retrieval, replication, synchronization, and failure recovery.

It also provides a way to investigate document transfer time, version correctness, and availability during an individual storage-node failure.

### Workflow Image

Proposed distributed criminal case document workflow showing an authorized prosecutor, Document Access Service, metadata database, Storage Node A, Storage Node B, replication, document retrieval, and failure recovery.](my-project/assets/architecture.png

*Figure 1. Proposed distributed criminal case document storage, access, and failure recovery workflow. An authorized user requests a document through the Document Access Service. The service checks the metadata database to locate the correct version, retrieves the file from Storage Node A during normal operation, and returns it for viewing. Documents are replicated to Storage Node B, which can provide a verified copy when Node A becomes unavailable. This diagram represents a proposed student prototype, not LADA's current infrastructure.*

### Evidence and Existing Approach

LADA's official RFP provides evidence of a real organizational need to modernize case-management applications and improve integration between existing systems. It identifies multiple applications, including PIMS, eFolder, and SharePoint, that support case-related information management. [1]

This provides the real-world context for investigating how documents can be stored, located, and retrieved reliably across independent services.

PostgreSQL's official high-availability documentation describes replication and standby database techniques that support data availability. [2]

I will use these concepts as a starting point for understanding distributed storage and recovery while distinguishing database replication from the replication of actual PDF documents.

My proposed approach uses a Document Access Service, a metadata database, and two independent storage nodes.

The metadata database records document identifiers, versions, and storage locations, while the storage nodes maintain the actual files.

This architecture is a proposed student simulation intended to investigate document storage, access, transfer performance, replication, and failure recovery.

### Six-Week Contribution (Semester I)

My individual contribution during Semester I is to investigate and design a small distributed document storage and retrieval mechanism.

I will focus on one complete document workflow: storing a fictional PDF, recording its location, locating it through metadata, retrieving and viewing it, transferring it between storage services, maintaining a replicated copy, and attempting recovery when the primary node becomes unavailable.

The initial scope includes one simulated authorized user, a small set of fictional documents, one Document Access Service, one metadata database, and two independently running storage services.

I will describe the expected behavior of each operation and define how to measure document retrieval time, transfer time, replica-update delay, and version correctness.

A small proof of concept may be developed if time permits.

My goal during Semester I is to establish a clear and testable distributed-systems design rather than implement an entire criminal case management platform.

### Semester II Scope

In Semester II, I plan to implement a working prototype that demonstrates document storage, location, retrieval, transfer, replication, and failure recovery across two independent storage nodes.

The prototype will allow fictional PDF documents to be stored and retrieved through the Document Access Service.

I will use a metadata database to track document identifiers, versions, and storage locations.

I will also implement document replication between Storage Node A and Storage Node B and simulate storage-node failures to observe how retrieval behaves when the primary node becomes unavailable.

I plan to compare a single-node baseline with the replicated approach.

The evaluation will measure document retrieval latency, transfer time between storage nodes, replica-update delay, successful retrieval rate, failover delay, and whether the correct document version was returned.

These experiments will help me understand the tradeoffs between performance, reliability, availability, and consistency in a distributed document storage system.

### Exclusions

- The project will focus on document storage, location, access, retrieval, transfer, replication, synchronization, and failure recovery rather than developing a complete case management system.
- The initial prototype will use fictional criminal case documents instead of confidential records.
- Direct integration with external court systems, police databases, and government production systems is outside the initial scope.
- Legal decision-making, case prosecution workflows, victim notifications, and other administrative functions will not be implemented.
- Large-scale production deployment and advanced disaster recovery will be considered future extensions rather than part of the initial prototype.

2. Requirements and Success Criteria

    Work to come in a later assignment.

    This section will define formal requirements and measurable acceptance criteria for document retrieval, availability, version correctness, and response time.

3. Existing Approaches and Comparison

    Work to come in a later assignment.

    This section will compare a basic single-node storage approach with a two-node replicated approach to examine the differences in availability, performance, and reliability.

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
