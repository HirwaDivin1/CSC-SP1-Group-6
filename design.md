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

    Let us consider an artificially constructed example that deals with a particular criminal, and the case number is LADA-DEMO-104. A prosecutor having hearings scheduled requests the document with the ID DOC-104-01, version 2, in PDF format. According to the current student model, Storage Node A is supposed to provide this document whereas Storage Node B is supposed to have the replica of this document. There is a special service called Document Access Service that receives this request. Metadata DB stores the ID, the version number of the document, and its location.

    In case of normal circumstances, the prosecutor is requesting the version 2 of the document, the access service verifies the simulated test identity, accesses the metadata, retrieves the file from Node A, checks the document version and checksum, and then sends back the file to the requester. The time period between receiving the request by the access service and sending the file back will be used for calculating the retrieval latency.

    In this situation, we assume that Node A goes down while access service is working properly. When access service timeout occurs and the failure is detected, it attempts to retrieve version 2 from Node B. In case Node B contains the complete version 2 that is valid, the prosecutor gets the file plus the delay associated with detecting and failing over.

    In case node B only has version 1, then the system should not give back the file as version 2 without explaining why it is unable to provide the requested version. The copied file will have no use if it does not satisfy the version requirements.

    This is an example of a test case and not the actual failure of LADA. This scenario is deliberately made simple enough to repeat using the fictitious entries.


*   Where the Documents Will Be Stored in the Prototype

    In the case of the proposed prototype, the PDFs and document metadata will not be stored in the same place. Storage Nodes A and Storage Node B will store copies of the PDFs separately while the metadata of the documents will be stored in a PostgreSQL database.

    The document metadata will contain the following information: a reference to the document, version number, expected checksum, and storage nodes holding copies of the documents. With the help of this information, the access service will be able to determine the storage node and start file transfer via the network connection.

    For example, in case the prosecutor needs DOC-104-01, the access service will first check the metadata database for the document, then connect to the right storage node and ask for and receive the PDF. It should be noted that there is a difference between accessing the metadata entry and transferring the document as the former will contain information about the latter.

    Node A and Node B would function as two distinct storage services. When it comes to the local simulation procedure, they can be run separately as processes or containers on the same computer having different directories for persistent file storage. The configuration may be treated as either failure of service or loss of connection; however, it cannot be seen as evidence of the system resilience in case of loss of the entire laptop or even building.

    The main idea behind this configuration was to study the impact of the mentioned factors on document availability.

    This is a proposed student design and not the existing infrastructure of LADA.

*   Performance and Failure Questions to Investigate

    Another element of measurement is the speed of retrieving data from all the different nodes in storage. Retrieval time is determined by the time taken between the time the Document Access Service receives the request and the time the entire document is received.

    For an experiment in the future, I will be using some synthetic documents that will have sizes of 1 MB, 10 MB, and 50 MB. These numbers above are the inputs for testing and not the actual sizes of the county case files. In all the tests, I will be timing the time needed to retrieve the entire document from node A normally and node B in case node A fails. Also, I will be determining whether the right document has been retrieved successfully.

    Replication delay is yet another crucial parameter to take into account. The definition of replication delay is the period of time from the moment when version 2 of the document is saved at Node A until a complete and checked version 2 at Node B is achieved. The big replication delay is very probable to cause failover to obtain the old version.

    Moreover, I would also like to know how a service will recognize that the node is no longer reachable. While a small timeout value will allow faster changing to another storage node, it might mistake slow response as failure, and vice versa – a bigger timeout will avoid unnecessary failover, but the user will wait too much for switching.

    However, tests should be conducted prior to any conclusions being made about milliseconds. Comparison will be done on the same files and under the same conditions where one node will be compared with two nodes.

*   Evidence, Assumptions, and Unknowns

    The strongest documentation evidence would come from the RFP from LADA itself. This document explains that there are multiple aging applications, lack of integration and need of a new cloud-based case management system due to fragmented support systems. The purpose section also indicates performance, operational requirements, and disaster recovery as the problems.

    Such an evidence indicates that it is important to analyze the availability of documents in case management environment. It is not quite clear from the provided evidence whether LADA is experiencing the kinds of problems in the scenario presented with their document server.

    Assuming a student model where the document may be transferred between two storage services; one storage service fails but the other one works; version information about the document is available; and finally a checksum is helpful for validation of the document contents.

    Unknowns for this problem include LADA's real location for the documents, the server configuration, network latency, access time, method of replication, and rate of outages. I'll use the simulation to test the correctness of itself as opposed to the rate of outages of the actual county systems.

    From these assumptions and unknowns, I will plan the rest of my research and implementation without forming any hypotheses into statements of fact.

*   Stakeholders and Their Needs
    
    | Stakeholder | Document-related task | Main need |
    |---|---|---|
    | Prosecutor (primary user) | Request and review a case file before a hearing | Retrieve the correct version promptly, or receive a clear failure result |
    | Case intake clerk | Locate and organize case records | Dependable document identifiers and locations |
    | Paralegal / authorized support staff | Find materials for case preparation | Consistent access to relevant documents |
    | IT administrator | Diagnose unavailable services | Detect failed nodes and understand recovery behavior |
    | LADA as an organization | Coordinate case information across applications | Reliable, integrated access to case materials |

*   Workflow and Context Image
    ![Distributed case-document access showing the prosecutor, Document Access Service, metadata database, and two storage nodes.](my-project/assets/architecture.png)
    
    Simulation of the model of document access for distributed documents of the student. The access service receives the identifier of the document and its version and accesses the document either in the primary storage node or in the replica, if the primary storage node is not available. This scheme illustrates my system, not the infrastructure of the LADA at the present moment.

    The scheme above demonstrates the difference between the requesting user, the service that finds the documents, the metadata base, and two separate storage services.

    Moreover, the scheme above illustrates the critical error situation. In case of unavailability of the primary storage node, the system can access the document from some other node. However, the replica can become the appropriate node only in case when it possesses the corresponding version of the document and passes the integrity check of the file.  

    This process is the interaction of various components via the network in order to gain access to the document.


*   My Small Semester I Contribution
    
    My contribution during the first semester will be to design and specify a failure aware document retrieval function.

    In this case, I will list one document request specifying the document ID and version required, one case where the document request is successful with Node A replying and another case where the document request is unsuccessful because node A does not reply but node B might have the requested version.

    In addition to describing the output the user is expected to receive in each case, I will explore some methods that can be employed to measure the retrieval time and version correctness.

    Scope will involve one authorized user, fictional PDF documents, Document Access Service, metadata database and two storage services.

    This contribution is less ambitious in scope than designing a whole document management system. This will aid the investigation of one realistic feature namely retrieving the right version of the document.

    In this case, in the present semester, I need to identify the problem statement, specify the desired behavior, determine technical questions and evaluation plan. The prototype development will be done if time permits but the first assignment does not require me to have any system developed yet.



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
