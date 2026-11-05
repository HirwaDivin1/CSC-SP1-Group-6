B05 – Resilient Case Management Services

Individual Project: Adaptive Referral State Reconciliation (ARSR)

Kapil Tamang

1. What problem are you investigating?

    My senior project deals with the issue of discovering receipt management related to maintaining correct discovery receipt records when an authorized evidence document is provided to the defense counsel, but problems with communication arise and/or the document is revised further. I choose to concentrate on the LA County District Attorney's Office (LADA) and one of its processes related to the discovery management process.

    In September 2026, LADA released Request for Proposals (RFP) RFP-DA-IT01 in order to find an updated, cloud-based Case Management System (CMS) that will substitute the obsolete applications. Section 2.2 describes problems with discovery compliance due to a fragmented IT infrastructure of the organization. Section 3.1 states that the new system should provide such features as Brady obligations, statutory discovery, workflow automation, document management, and audit. Section 9 also mentions discovery management and compliance tracking as the fields for the demonstration by the vendors. 
    
    https://camisvr.co.la.ca.us/LACoBids/BidLookUp/BidDetail?BidNumber=RFP-DA-IT01
   
    The discovery management process will be limited to one operation, that is, verification of the delivery of one approved discovery document that has been delivered to the defense lawyer’s office. The problem will occur if the two services, which deliver the document from the sender to the receiver, are separate entities and no acknowledgment of receipt takes place before updating the case management system.

    For instance, assume there is a fictitious criminal case referred to as LADA-104. The version 1 of an evidence document, which has been approved by the deputy district attorney for disclosure purposes, will be disclosed via the case management system through a delivery service. The receiving service will acknowledge receipt of the document.

    However, assume that receiving service gets version 1, but the acknowledgment is never sent due to the interruption of the network connection. During the interruption, the prosecutor agrees to version 2 of the disclosure. Once communication is restored, the system will get an old acknowledgment or try to send version 1.

    Without proper validation, the case management system will treat this acknowledgment as the approval of version 2. Duplicate delivery acknowledgments or undelivered disclosures are another consequence of lack of proper validation.

    My project addresses this particular technical issue, not the whole process of discovery. The following five features will help to handle one process of disclosure: version validation, reliable delivery, fail-safe delivery, deadline check, and audit log.

    The system will not verify if the evidence is to be disclosed according to the law, approve legal documents or whether technical acknowledgment can be considered a proof of service according to the law. These issues should be addressed by legal professionals.

2. Who or what is affected by it?

    The first party of interest is a Deputy District Attorney, tasked with overseeing the process of discovery disclosures at the Los Angeles County District Attorney’s Office. This individual will be tracking all documents prepared, approved, transmitted, and receipt confirmed.

    The other party of interest is defense counsel who requires access to the disclosed documents. Other individuals that may be affected by the process are discovery team members who are tasked with document preparation, tracking of the documents' transmission, and incomplete transmission activities.

    The RFP of the county identifies the need for compliance with discovery requirements and coordination with defense counsel among other capabilities required of the new case management system.

    https://camisvr.co.la.ca.us/LACoBids/BidLookUp/BidDetail?BidNumber=RFP-DA-IT01

    In this fictional example of the LADA-104 scenario, the prosecutor can notice that despite the recording of version 1 by the receiving service, it still remains unconfirmed. If later on, version 2 gets confirmed, the prosecutor would have to be able to differentiate the previous delivery attempt from the new one.

    An incorrect acknowledgment entry might necessitate the manual comparison of the document versions, checking of communication logs or contacting the receiver. Such actions can make the process of verification more delayed and repetitive.

    The issue concerns the reliability of the two software services that are part of the process. One of the services – case management service – stores the data on the disclosure requests and another – the receiving service – stores the data on the deliveries made. Being independent services, they can perform an operation even though the communication between them is interrupted.

    The purpose is to give prosecutors the correct technical information on each of the disclosure attempts, and not to automate their legal decisions.

3. What evidence do you currently have that it is a real problem?
    
    Source one is the RFP-DA-IT01 from the Los Angeles County District Attorney published on September 29, 2026. Section 2.2 states that LADA currently operates using an older Prosecutor Information Management System (PIMS) along with other software tools like eFolder, Electronic Charge Evaluation Request (eCER), Notes/Domino applications, SharePoint databases, and spreadsheet.

    Some of the existing challenges listed by the county are inconsistencies in data entry and integration and the lack of discovery compliance. All these challenges have been stated to be real problems with the organization and not assumptions for my project.

    Section 3.1 defines the need for a new system with the features related to discovery rules, automated workflow, document management and audit, while section 9 defines the need for discovery management and compliance tracking.

    https://camisvr.co.la.ca.us/LACoBids/BidLookUp/BidDetail?BidNumber=RFP-DA-IT01

    The next source provides the official documentation on transactions in PostgreSQL. It enables several database operations to be grouped into a single unit, and in the event that the transaction fails, its changes may be undone. The importance of this source is that there should not be any partial recordings of disclosures, delivery statuses, and audit activities in a single database.

    Unfortunately, a transaction in the case management database will not ensure the recording of the document in the separate receiving service database.

    https://www.postgresql.org/docs/current/tutorial-transactions.html

    The third source refers to the documentation from Microsoft regarding the Transactional Outbox pattern. In such a case, the problem of reliable communication between systems is solved by putting the outgoing messages in a local transaction with database changes. Another process delivers these messages, making it possible to recover from an incomplete communication.

    Another important fact provided by Microsoft is that messages can be delivered multiple times, and services need to deal with this. This gives technical proof for the importance of communication reliability and message duplicates.

    Another technical proof is provided by Camunda 8 documentation regarding job workers. Camunda enables retries for unfinished tasks and continuation of work after worker unavailability. Camunda's documentation also states that tasks may run several times which makes the application tolerate repetitions of operations.

    https://docs.camunda.io/docs/components/concepts/job-workers/

    While these sources confirm the technical threats mentioned above, I was unable to check that LADA had experienced such a problem with lost acknowledgment or an outdated version as mentioned in my example. I did not interview the employees of the county nor analyze the disclosure logs nor measure the system.

    I assume that delayed acknowledgments and changing the version of the document lead to inaccurate receipts if independently functioning services do not validate the initial request and document version.

    This evidence provides proof of the actual organizational need and risk of distributed systems. In order to find out if my approach improves the chosen workflow, experiments will have to be done.

4. What solutions already exist?

   There exist a number of technologies for each of the areas of reliable communication, data consistency, and workflow recovery. I will discuss the comparison between PostgreSQL transactions, Microsoft's Transactional Outbox, and Camunda 8.

    The PostgreSQL database transactions ensure the consistency of database operations inside one database. For instance, a transaction can create a disclosure request, save the document version after approval, and keep the corresponding audit event. In case of error during transaction execution, all operations can be undone.

    The main benefit is that the database changes are safeguarded against incomplete transactions. The disadvantage is that the transaction itself cannot synchronize two services. The successful saving into database doesn't guarantee that the service of the receiving defense counsel saved the document.

    https://www.postgresql.org/docs/current/tutorial-transactions.html

    The second approach is the Transactional Outbox pattern from Microsoft. The principle of this pattern involves storing outgoing events together with the business data. Later, a background job sends such events to some other service. In case of unavailability of communication, the messages can be delivered subsequently.

    Such an approach can help keep the request for approval until the availability of the service responsible for delivering it. The positive thing about it is that there is no risk of loss of the outgoing request after a successful operation in the database.

    Nevertheless, this pattern ensures at-least-once delivery, but not exactly-once delivery. So, it is possible to have duplicate messages, which need to be considered. Moreover, the reliable delivery of an acknowledgement of version 1 doesn’t mean the delivery of version 2.

    https://learn.microsoft.com/en-us/power-platform/architecture/reference-architectures/transactional-outbox-pattern

    Thirdly, Camunda 8 represents a workflow orchestration solution, which allows orchestrating operations, which are performed by different services. Workers in Camunda can complete tasks, detect errors, and retry incomplete operations. The solution allows persisting workflow state even when a worker becomes unavailable.

    For a disclosure of discovery workflow, Camunda may orchestrate communication, acknowledgments, and retries. The solution is good at managing workflows with multiple steps and restarting tasks in case of interruption.

    Nevertheless, the solution itself cannot automatically detect if a late acknowledgment concerns a certain approved version of the document. Also, the documentation for Camunda mentions the necessity of implementing idempotent workers, which means that re-execution of a certain task should not result in undesired behavior.

    https://docs.camunda.io/docs/components/concepts/job-workers/

    As part of my proposed Resilient Discovery Receipt Tracking System, I will conduct research on a specific recovery model which consists of five components.

    First, document version validation will tie the disclosure request to a correct document version that was approved. Secondly, the reliable delivery component will store requests during temporary communications failures. Third, the failure recovery component will analyze past delivery results and detect repeated requests prior to retransmission.

    Fourth, deadline management will notify authorized users about unconfirmed disclosure near a manually entered deadline. Fifth, the audit history component will track document versions, delivery attempts, acknowledgements, and recovery operations.

    All of these components are not individual new technologies. What my contribution will be is the combined use of these technologies to maintain the history of accurate version specific discovery receipts under controlled failure conditions.

    My goal is to find out whether adding version awareness to reliable delivery technology will result in any benefits. Until experimental evaluation is conducted, this will remain a proposed solution.  


6. What is the most important thing you still do not know?
    The most significant challenge is determining whether the version-aware acknowledgment reconciliation process will be able to handle discovery receipt statuses better than the traditional durable delivery and retry process when the acknowledgments are delayed or lost.

    There are systems which can help in storing outgoing requests and retrying operations if there is a failure. However, what needs to be determined is the way the system should function if a previous version of the document has been received, its acknowledgment delayed and the latest one approved.

    For instance, if version 1 has been successfully received before version 2 has been approved, then it will be crucial for the system to keep the historical data on version 1 without considering it as the receipt for version 2.

    In order to test this, I will develop a prototype which will include the case disclosure service and the defense receiving service. Both the services will maintain their own logs independently but will interact using API.

    There will be two types of implementation; one will be the normal process and the second will have version-aware acknowledgment verification and reconciliation before completion of receipt statuses.

    Both systems will work on the same fictitious documents under controlled circumstances. The test will simulate a lost acknowledgment, multiple retransmission requests, service interruption, and a delayed acknowledgment from an older version of a document.

    Some of the most significant variables will be errors in updating receipt status, unnecessary retransmissions, unresolved retransmissions requests, and recovery time. In addition, I will investigate the additional processing required due to version validation.

    It can be hypothesized that version-based reconciliation will minimize errors in updating receipt status when acknowledgments about different document versions arrive in wrong sequence.

    Nevertheless, one of the limitations will be whether the receiver is able to request any previous retransmission requests using some unique identifier. If this data is unavailable, the system will have to keep unresolved retransmission request and not be able to confirm delivery automatically.

    The experiment will show if the suggested approach is reliable enough or adds unnecessary complexity.


7. Your Individual Scope

    The particular discovery disclosure workflow that my individual project will examine is one workflow based on the discovery-compliance standards of the Los Angeles County District Attorney.

    The scope will include one fictional criminal case, one approved discovery document with its replacements, one service for delivering it to the defense, and one version-aware acknowledgment recovery procedure.

    Python with FastAPI will be used for the independent services, PostgreSQL for persistent records, and Docker Compose for running the services and simulating interruptions. One small React dashboard may present document versions, delivery statuses, acknowledgments, deadlines, and audit logs. The database will be queried using direct SQL queries.

    All five features will be implemented in this single disclosure workflow only. A full-blown criminal case management system, evidence analysis, decision-making about discovery requests, real connections with the court, and the actual delivery of sensitive criminal records will not be implemented. All the records and documents will be fictional.

    The primary comparison will be made between a standard reliable delivery and a reliable delivery enhanced with document version verification and acknowledgment reconciliation.

    The expected outcome would be a fully functional prototype of a distributed system and tests that would show how the data on receipts evolves under the conditions of disruptions, repetitions, and document updates.

    This research is manageable for a single student since the implementation will be restricted to only two main services, one discovery workflow, few database tables, and experimentation. Five additional features give the technical depth while not needing other criminal justice workflows.

    I want to find out if version aware acknowledgment recovery can increase the accuracy and reliability of the discovery receipts tracking process.
