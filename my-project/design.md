**Student:** Kapil Tamang  
**Project:** B05 – Resilient Case Management Services  
**Assignment:** 1 – Problem and Markdown Foundation  
**Date:** November 6, 2026  
**Real-world setting:** Los Angeles County District Attorney's Office (LADA)  
**Document status:** Initial problem and scope draft

1. Problem and Scope

   Who Has the Problem?

    In both cases, the prosecution staff and designated case support personnel from LADA have to find and look over certain documents to be used as a basis in preparing criminal cases. These documents can include reports by police, charging documents, statements by witnesses, and other. Filing deputy district attorney while getting ready for a hearing, for example, will have to find proper documentation for his or her case, make sure that it is the proper version of the document that he or she needs for performing the current task, and access the document promptly. At the same time, intake clerks and paralegals have to use effective methods to locate and sort the records in question. IT systems administrators will have to take care of correct functioning of the corresponding computer systems.

    The direct end-user in my project will be an authorized prosecutor, who is in need for one particular case file. He/she requires a correct file to be provided, timely reaction time, and definite message, when the required file has not been found. My project is concerned with delivery of reliable content access through separate computing services and is not intended for delivery of legal conclusions or messages.

 *  Current WorkFlow and Documented Issues

    In the LADA Request for Proposal RFP-DA-IT01 dated September 29, 2026, the already existing system PIMS, which stands for Prosecutor Information Management System, is mentioned in Section 2.2 and was developed primarily for the management of charging documents and statistics. Moreover, the LADA RFP mentions other systems used in addition to PIMS such as eFolder, SharePoint databases, Notes/Domino Applications, ECER (Electronic Charge Evaluation Request) and Excel Spreadsheets. The problems include duplication or inconsistency of data entry and non-integration of applications and justice partners. They require a cloud based case management system. They are modernization and integration requirements not the evidence of a certain server problem or delay.

    Simplified representative process flow for accessing the document will be as follows: a staff member accesses the particular case file, retrieves the necessary document from a system/database, opens the document and views it for the purpose of preparing for the case. This is how the process can be defined; however, the RFP does not provide any confirmed process flow followed by all employees.

    If the data and all information is scattered throughout multiple different locations, then it is crucial for one to have the understanding of where the files are stored and how they can be retrieved. This is something that I am unaware of because it is not mentioned in the RFP, namely the physical location of the files, the number of servers, transfer rate, replication and what happens to the storage upon failure.

    https://camisvr.co.la.ca.us/LACoBids/BidLookUp/BidDetail?BidNumber=RFP-DA-IT01

*   The Specific Distributed-Systems Problem

    In this case, the distributed system is realized with the help of different programs or machines sending messages through the network. For instance, the document-access service can handle the request issued by the user, the metadata service can store information about the document version and its potential location, and the storage service can save the file. All these services function independently and may fail independently.

    I want to research three related questions. First, it is the question of location – how the access service locates the machine that contains the required document. Second, it is the question of performance – what time period is needed for the transfer of the whole file from the moment when the request was issued to the moment of the document delivery, if the first machine fails to respond. The third question concerns availability and consistency.

    Where there are two replicas of the same document kept in two servers, then it is likely that the document may still be retrieved even if one of the servers has failed. However, the replica might not have the latest version of the document. Just by accessing another server may not suffice in such cases. What is required is to verify whether the version present is the required one or not.

    My main research question can be put as:
    How can the small document access service restore the required version of the case file from the available storage node in case of partial failure? 

*   Concrete Scenario: One Prosecutor, One Document, One Failure

    Consider a fabricated case related to a criminal where the case number is LADA-DEMO-104. A prosecutor who has a hearing scheduled asks for the document DOC-104-01 with version 2 in PDF form. In the current student model, Storage Node A is responsible for supplying this document while Storage Node B should have a copy as a replica. A separate service called Document Access Service receives this request. The metadata database contains the document ID, version number, and location where the document is expected to be available.

    Under usual circumstances, the prosecutor asks for the version 2 of the document and the access service authenticates the simulated test identity, accesses the metadata, retrieves the file from Node A, verifies the document version and checksum, and supplies the file back to the requester. Time period from the moment when the access service received the request until the file is sent back will serve as retrieval latency.

    Now assume that Node A becomes unresponsive whereas the access service is still functioning. Once the access service times out or notices the failure, it tries to fetch version 2 from Node B. If Node B has the entire version 2 which is validated, the prosecutor receives the file along with the additional delay from detection and failover.

    If Node B has only version 1, then the system shall not return the file as version 2 without giving a proper explanation that the required version is not available. The copied file will be of any use only if its version meets the requirements.

    This is an example of a test case and not an actual failure of the LADA. The scenario is purposely kept simple enough to replicate with the fictional entries.


*   Where the Documents Will Be Stored in the Prototype

    In the case of the proposed prototype, PDFs and document metadata will not be stored in the same location. Storage Nodes A and Storage Node B will each store separate copies of the PDFs, whereas a PostgreSQL database will store the document metadata.

    Document metadata will include a reference to the document, version number, expected checksum, and the storage nodes which have copies of the documents. Using this information, the access service will determine the storage node to use and initiate file transfer via a network connection.

    Thus, for instance, if the prosecutor requires DOC-104-01, the access service will first use the metadata database to determine the document, then contact the appropriate storage node and request and get the PDF. It is important to note that accessing the metadata entry is different from transferring the document since the former will contain data about the latter.

    Node A and Node B will act as two separate services of storage. In the local simulation process, they may be executed as separate processes or containers on the same computer with separate directories for storing files persistently. The configuration may be taken as a failure of service or disruption in connection; however, it cannot be considered proof of the system's robustness against loss of complete laptop or building.

    The reason for this configuration is to examine the effects of document placement, network interaction, file transfer, and service failures on the document accessibility.

    This is a proposed student design and not the existing infrastructure of LADA.

*   Performance and Failure Questions to Investigate

    One aspect of measuring is how fast the retrieval process is from the various storage nodes. Retrieval time is measured by the time difference between when the Document Access Service receives a request until the complete document is received.

    As part of a future controlled experiment, I am going to use synthetic documents that have 1 MB, 10 MB, and 50 MB in size. The above values represent test inputs and not measurements of county case files. In each test, I will measure the time required to retrieve the whole document from Node A in normal circumstances and from Node B when Node A fails. In addition, I will check whether the retrieved document is the correct one and whether the request is successful.

    Replication delay is another important measure. Replication delay is defined as the time difference between storing version 2 of the document on Node A until a complete and verified version 2 on Node B becomes available. A large replication delay makes it more likely that the failover will retrieve an older version.

    In addition, I would like to see how a service can identify an unreachable node. Although a smaller timeout would enable quicker switching to another storage node, it could misinterpret slow response times as a failure. Conversely, a larger timeout would minimize unnecessary failover attempts while causing the user to wait for too long before the switch.

    Tests must be carried out before I make claims regarding milliseconds. The comparison will be made using the same files and conditions under which there will be one node versus two nodes.

*   Evidence, Assumptions, and Unknowns

    The most compelling evidence from a documentation standpoint would be from the official RFP from LADA. This document describes multiple aging applications, fragmented support systems, lack of integration, and the need for a new, cloud-based case management system. The section on purpose also describes performance, operational requirements, and disaster recovery as issues.

    This evidence shows the need to study the availability of documents in a case-management setting. It is not clear from this evidence whether LADA is experiencing the types of failure mentioned in my scenario with its document server.

    For the student model, I will assume that a document can be transferred between two storage services; one storage service may fail but the other one remains operational; version information about the document can be obtained; and a checksum is useful in validating the document contents.

    Unknowns in this case involve LADA's true location of the documents, server configuration, network latency, access time, replication strategy, and outage rate. My simulation will be used to verify the behavior of itself rather than the outage rate of the actual county systems.

    Using these assumptions and unknowns, I will guide future stages of my research and implementation process without stating any hypotheses as facts.

*   Stakeholders and Their Needs
    
    | Stakeholder | Document-related task | Main need |
    |---|---|---|
    | Prosecutor (primary user) | Request and review a case file before a hearing | Retrieve the correct version promptly, or receive a clear failure result |
    | Case intake clerk | Locate and organize case records | Dependable document identifiers and locations |
    | Paralegal / authorized support staff | Find materials for case preparation | Consistent access to relevant documents |
    | IT administrator | Diagnose unavailable services | Detect failed nodes and understand recovery behavior |
    | LADA as an organization | Coordinate case information across applications | Reliable, integrated access to case materials |

*   Workflow and Context Image

    Simulation of the student's model of distributed document access. Access service gets document identifier and version information and accesses the file either in the primary storage node or the replica, if the primary storage node is unavailable. The above scheme describes my system, not LADA's current infrastructure.

    The above scheme shows the distinction between the requesting user, the service that locates the documents, the metadata base, and two separate storage services.

    Also, the above scheme depicts the critical error condition. In case of unavailability of the primary storage node, the system may try to access the document from another node. However, the replica will be an acceptable node only in the case if it contains the required version of the file and passes the file integrity check.

    This process describes the interaction of different elements through the network to get access to the document.


*   My Small Semester I Contribution
    
    In the first semester, my contribution will be the design and specification of a failure-aware document retrieval function.

    I will outline one document request that includes a document ID and version required, one case of successful retrieval where node A is responding and one case of failed retrieval where node A is not responding and node B may or may not have the required version.

    I will describe the output that the user should get in each case and also discuss ways that can be used to measure retrieval time and version correctness.

    The scope will include one authorized user, some fictional PDF documents, one Document Access Service, one metadata database and two separate storage services.

    This contribution is more limited in scope compared to the development of a full document management system. It will help in investigating one realizable feature: obtaining the correct document version from an available node or informing that the requested version is not available.

    For this semester, I need to define the problem statement, define the behavior required, determine the technical questions and the plan for evaluation. The development of a prototype would be carried out in case there is enough time; however, the first assignment does not demand that I have a working system.



*   Larger Semester II Goal

    I will be creating independently operating storage services and Document Access Service, adding fictional PDF files to them, performing simulation of failure of the primary node and measuring the results of the retrieval.

    The system will enable Document Access Service to find documents, get files from storage nodes, check document versions and try to retrieve the document from replica node in case of failure of the primary node.

    I would test the difference between access through one node and access through two replicated nodes using the same test files.

    The major measures will be document retrieval successes, false version returns, normal retrieval latency, failure retrieval latency, failover delay and replica update delay.

    The objective of the comparison is to find out if keeping replicated copies of documents enhances access even in cases where there are node failures, as well as the costs incurred by replicating documents.

    The anticipated outcome of the experiment is an operational educational prototype, experimental data, and tradeoffs between document availability, performance, and consistency.

    The experiment is not meant to substitute LADA's real case management system.

*    Explicit Project Exclusions

    The project does not involve any actual criminal cases, any confidential information, or LADA infrastructure. All the documents and document IDs used are fictional.

    This project does not deal with court filings, prosecution decisions, evidence chain management, victim notifications, and authentication system development.

    The project does not aim at replacement of eFolder, PIMS, or any other existing software. It will not pretend to fulfill government security standards for production applications.

    Initially, the prototype will be concerned with document retrieval process, two separate storage nodes, simple replica verification, and impact of one storage service failure.

    The prototype is not aimed at guaranteeing document availability if both storage nodes, common metadata database, and whole host are unavailable.

    The first study is devoted to document retrieval process and one storage service failure rather than all possible disasters and enterprise storage systems.

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