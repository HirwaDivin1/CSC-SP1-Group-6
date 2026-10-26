

B05 – Resilient Case Management Services
Individual Project Scope: Resilient Case Synchronization
Student: Kapil Tamang
Course: Distributed Systems Senior Project
Assignment: Problem Understanding Paper


1. What problem are you investigating?

The research problem in question is the ability of various organizations to exchange information on their cases in case of crashes or disconnections in the computer systems. Case Management System (CMS) is a program that assists organizations in managing their files, allocation of tasks, monitoring the progress, and solving cases. Such systems are utilized in government bodies, courts, hospitals, and corporations. The exchange of information between multiple services may result in important changes being missed, duplicated, or delayed.

An example from real life is the Los Angeles County District Attorney's Office. In September 2026, the County issued a Request for Proposal (RFP), identified as RFP-DA-IT01, for a new cloud-based case management solution to replace several legacy solutions and integrate with courts and other justice organizations. For instance, let us assume a prosecutor is entering an update to a criminal case but the service that is supposed to share this information is not operational. The prosecutor’s system may be able to save the update but the other organization will still have outdated data. It is a hypothetical example and not any known incident involving Los Angeles County.

2. Who or what is affected by it?

The issue could possibly impact prosecutors, court workers, agencies dealing with justice, administrators, and clients. They all rely on the accuracy of information to conduct their regular business. In case one of the agencies receives out-of-date information, it would be difficult for the workers to make decisions based on the available data, and they might end up spending extra time confirming the status.
For instance, when a prosecutor changes case information but other authorized services fail to get such information, the receiving service will work with old case information. This can cause a lot of confusion and delay. The issue is even more serious as far as the computers are concerned because there will be different versions of the same information in the different services that are not connected.

3. What evidence do you currently have that it is a real problem?

The primary source is the official proposal of the District Attorney’s Office of Los Angeles County. According to the County, there is a need for replacement of several legacy case management systems with an advanced one that would be able to communicate with the court system and other departments. It demonstrates that there is really a need for integration and modernization. Nevertheless, the proposal does not indicate any communication problems.
The next source is PostgreSQL's documentation on transactions. Transactions are groups of database actions that either execute completely or not at all to prevent any partially completed database update. However, a transaction in one database does not necessarily mean that information is transferred to an external service.
The documentation for Microsoft Transactional Outbox describes the importance of keeping critical messages safe in case of communication failures between services. The Camunda 8 documentation also describes the idea of retrying incomplete tasks in case workers become unavailable. Both of these documents prove that message delivery and task retrying are established technical problems. I haven’t measured the failure rate or tried a prototype yet. My hypothesis is that verifying update versions and monitoring delivery may help in communication between case management services.

4. What solutions already exist?
A number of different solutions already exist for dealing with reliability issues in distributed systems. In the PostgreSQL database, there are database transactions that maintain consistency of related changes in the database. In Microsoft's Transactional Outbox solution, the database change and the related outbound message are stored together, enabling the latter to be sent even in case another service was unavailable at the moment. Camunda 8 is a workflow engine which coordinates services and retries incomplete work.	
Each approach has strengths and limitations. PostgreSQL transactions protect database operations but do not automatically synchronize separate agencies. The Transactional Outbox pattern helps preserve pending messages, but duplicate processing and message ordering still require attention. Camunda helps manage workflows and recovery, but it introduces additional complexity and does not automatically prevent repeated operations. My goal is to understand how these existing methods could support reliable case synchronization.

5. What is the most important thing you still do not know?

The primary concern for me here is how to find out if the new updates have been received by the various services and processed by them successfully following an error. Another aspect of my concern is how to avoid duplication of the updates in case of retrying any operations that have already been successful. While existing solutions cover aspects of these issues, I still do not know what approach should be used for my specific requirements.

This can be tested by constructing a little test with a District Attorney's Office, court, and another judicial institution with the help of fictional cases. I would cut off one service from the rest, pass some updates of the case, and connect the service again to see the results. It would be possible to compare two schemes of updating — one without recovery and another with logging pending updates and checking their versions. The number of lost updates, double actions, wrong version of cases, and the time of recovery can be measured.
Your Individual Scope

Scope of my individual project is Resilient Case Synchronization. I will be concentrating on making sure that case information synchronization can take place even if the connection is disrupted in some way. The project from Los Angeles County District Attorney will be the practical example for me, but I won't try to create their case management system.

My possible solution is a Case Update Verification and Recovery Mechanism that tracks update identifiers, checks whether services received the latest information, and attempts to recover missing updates without creating duplicates. I may use Python, FastAPI, PostgreSQL, and simulated network failures to investigate this approach. I will exclude real criminal case records, legal decision-making, and direct integration with government systems. This narrower scope makes the project manageable for one student. My goal is to test whether the proposed approach improves reliability rather than assume it is already the best solution.


References

Los Angeles County District Attorney's Office. Case Management System Solution, RFP-DA-IT01.
https://camisvr.co.la.ca.us/LACoBids/BidLookUp/BidDetail?BidNumber=RFP-DA-IT01
PostgreSQL Global Development Group. PostgreSQL Documentation: Transactions.
https://www.postgresql.org/docs/current/tutorial-transactions.html
Microsoft Learn. Implement the Transactional Outbox Pattern by Using Azure Cosmos DB.
https://learn.microsoft.com/en-us/azure/architecture/databases/guide/transactional-out-box-cosmos
Camunda. Camunda 8 Documentation: Job Workers.
https://docs.camunda.io/docs/components/concepts/job-workers/
