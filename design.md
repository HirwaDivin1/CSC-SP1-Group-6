

1. Problem and Scope

   Who Has the Problem?

    Both prosecutors and designated case support personnel at the Los Angeles County District Attorney's Office (LADA) are supposed to find and view various documents in preparation of criminal proceedings. Such documents may consist of police reports, charging papers, witness statements, and others. Filing deputy district attorney in the process of preparing for a hearing, for instance, will have to find the right document for the case, check that it is the right version needed for the task, and then access it without any undue delays. Intake clerks and paralegals, for their part, should have efficient methods of locating and arranging such records. Administrators of IT systems will have to maintain proper functioning of such systems.

    My immediate user in the project will be an authorized prosecutor, who requests one case document. He or she will need a right file, a decent response time, and a definitive message in case when the file could not be found. My project is not aimed at delivering legal verdicts or notifications; rather, it focuses on providing dependable access to document content through separate computing services.

 *  Current WorkFlow and Documented Issues

    The LADA Request for Proposal RFP-DA-IT01 on September 29, 2026, mentions in Section 2.2 the existing system called PIMS which stands for Prosecutor Information Management System and was initially designed mainly to manage charging documents and statistics. It also mentions the other systems that are involved such as eFolder, SharePoint databases, Notes/Domino Applications, ECER (Electronic Charge Evaluation Request), and Excel Spreadsheets. The issues include duplicity or inconsistencies in data entry and lack of integration of applications and justice partners. They seek a cloud-based case management system. They are modernization and integration requirements not evidence of a certain server problem or delay.

    simplified representative process flow of accessing a document is as follows: a staff member accesses a certain case file, locates the required document within an available system or database, opens the document and looks at it for the purpose of case preparation. This is how the process is described generally; however, the RFP does not publish a verified process followed by all employees.

    When data and associated details reside across various systems, it is vital to have knowledge of the storage location of the file requested and its retrieval process. The RFP does not provide me with the physical location of each file, the number of servers, transfer rate, replication process, and storage behavior when a failure occurs. I will assume that these are all unknown to me.

*   The Specific Distributed-Systems Problem

    The distributed system is implemented using separate programs or machines, which send messages through the network. For example, the document-access service can process the request from the user, the metadata service can keep information about the document version and possible locations, and the storage service can store the file itself. All three services operate independently and can crash independently.

    I would like to explore three interrelated problems. The first one is the problem of location — how the access service finds the machine that stores the required document. The second one is the problem of performance — how much time is needed to deliver the whole file from the moment when the request has been issued until the document delivery, in case the first machine does not reply. The third one is the problem of availability and consistency.

    If a document has been duplicated on two servers, there is a possibility that it will still be available when one of the servers fails. But the replica might not have the latest copy of the document yet. Just accessing a different server will thus not be enough. The system needs to check if the copy that is available corresponds to the desired version.

    My primary research question is as follows: How would a small document access service recover the needed version of a case file from the available storage node in case of partial failure?

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
