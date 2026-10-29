B05 – Resilient Case Management Services

Individual Project: Adaptive Referral State Reconciliation (ARSR)

Kapil Tamang

1. What problem are you investigating?

    The problem under examination is the issue of coordination of mental health referral procedures by various organizations in respect to the clients who take     part in criminal proceedings, specifically clients in detention who may require mental health treatment. Case Management System (CMS) is computer software used by organizations in the process of managing the information about the records, assignments, cases, and coordination of services. In my project, I study the case where mental health referrals, appointments, and other information have to be coordinated by separate organizations.   

    One practical example of such an environment is the Los Angeles County District Attorney's Office. On September 2026, Los Angeles County issued an RFP (Request for Proposals) RFP-DA-IT01 that seeks an innovative cloud-based case management system to replace the outdated application system and interface with the court systems. Los Angeles County has mental health diversion programs that provide assistance to qualifying candidates to get treatment and community services. These programs require interaction between different organizations each having its own set of roles and different computer systems.

    https://camisvr.co.la.ca.us/LACoBids/BidLookUp/BidDetail?BidNumber=RFP-DA-IT01

    To cite an illustration, consider a situation whereby an individual in custody has received approval for a mental health diversion program. A case manager refers the individual to a treatment facility, which subsequently sets up an appointment with the facility. Normally, the facility would confirm the appointment, the case manager would get the confirmation, and everything would proceed as per the approved plan. But what if the treatment plan of the individual was altered, while at the same time another case manager sought the same appointment? What if, besides that, the computer system of the facility crashed?

    There are three related problems that could emerge from such a scenario. One, the original referral may become obsolete due to changes in the situation. Two, both organizations might assume that they had booked the same appointment. Three, when the provider’s database becomes operational again, it will process either an outdated request or perform an action that has already been performed. These are failure situations, not incidents at Los Angeles County.

    The aim of my research is how individual services may identify obsolete referrals, arrange scarce treatment sessions and resume incomplete processes without making wrong entries. I am not researching how to ascertain whether an individual is eligible for mental health diversion or which medical care he needs. This decision must remain with relevant legal and medical specialists.

2. Who or what is affected by it?

    It is possible that the problem may affect people who are involved in cases of crimes, which requires mental health treatment, prosecution, defense, courts, corrections, case managers, and providers of the treatment. Every entity will have its responsibility; however, they might require the information from one another to be able to perform their tasks. In case the referral is outdated or the appointment was wrongly entered, the concerned personnel may take more time to understand what is happening, thereby causing delay to the client.

    For instance, consider the scenario where a treatment facility first accepts a referral of a patient who is transitioning from incarceration into a community setting. In cases where there are changes in the patient’s situation but no new information is conveyed to the case manager, the previously accepted treatment plan could still be recorded as having been confirmed. The treatment facility can then proceed to prepare for the treatment that is supposed to be reviewed, while another coordinator can be trying to use the same available time for treatment.

    The ODR programs offered by Los Angeles County have programs that help individuals access treatment, housing, and community support. The ODR Housing program offered by Los Angeles offers case management to help individuals transition from custody into the community. This shows that coordination among the courts, case managers, and treatment organizations plays an important role within the current process.

    In addition, the issue also influences the reliability of the computer systems. Information is stored by different firms in their own way, and one system may still be operational when another one is not. Therefore, at some point, the computer systems can have conflicting information regarding the referral, booking of an appointment, or the completion of a task.

3. What evidence do you currently have that it is a real problem?
    
    The first piece of evidence I have chosen comes from the official proposal by the Los Angeles County District Attorney’s office on how the new case management system can be developed. It mentions that the County wants to replace several outdated applications with an up-to-date integrated cloud-based system which will be able to manage criminal cases and exchange information with other justice organizations. It is evidence of the need for modernization and integration. But it doesn’t show that these failures occurred at all.

    https://camisvr.co.la.ca.us/LACoBids/BidLookUp/BidDetail?BidNumber=RFP-DA-IT01

    Another significant source is the Legal Policies Manual of the Los Angeles County District Attorney. It mentions mental health diversion and specifies that those eligible will be treated with an alternative method based on certain legal criteria. The County’s Office of Diversion and Reentry has records of programs that involve treatment organizations, housing, and case management.

    Technical documentation offers further information about the problems that may arise from the unreliability of distributed systems. According to PostgreSQL, database transactions can ensure that related operations are performed as a whole or not at all in case of failure in performing one operation. According to Transactional Outbox documentation by Microsoft, messages can be stored in case communication between services is not successful.

    These references confirm the fact that inconsistency in databases, reliable message delivery, and recovery of tasks are technical issues. But personally, I haven’t experienced these kinds of breakdowns in Los Angeles County, or conducted interviews or experiments. My theory is that the amendments made to the mental health referral process, conflicting reservations, and temporary malfunctioning of services can cause inconsistency in information if several organizations work independently.

4. What solutions already exist?

    Various technologies already developed can help solve various aspects of this challenge. The following three solutions include Camunda 8, the Transactional Outbox Pattern developed by Microsoft, and PostgreSQL database transactions. These solutions have their reliability features; however, they cover different coordination aspects.

    First, there is Camunda 8, a workflow management system which helps to coordinate activities of the services. For instance, in the referral workflow, one may create a referral, ask for an appointment, get confirmation, and mark it as complete. Camunda is able to monitor the workflow status and allow the task to be retried by a different worker when the previous one fails. The primary advantage of using Camunda is coordination of processes that consist of several stages and several independent services. The disadvantage is that retry does not guarantee that the referral remains valid.

    Another pattern is that of Transactional Outbox by Microsoft. In this method, the change made to the database and the corresponding outgoing event are bundled together within the same transaction. Then another service receives the event through another process. In case the transmission is unsuccessful, the event is kept pending until the transmission is made at a later point in time. This would be helpful in the scenario where there is a need to refer a patient to another organization. However, keeping the message pending does not necessarily mean the information is up-to-date.

    The third technique is that of using database transactions in the PostgreSQL database. This technique involves carrying out multiple database operations as one whole operation. For instance, using the database transaction along with the right constraints, a treatment provider can avoid conflicting appointment bookings in its database. The database rolls back any changes if an operation fails to commit. However, database transactions cannot synchronize appointment bookings between different organizations.

    The research approach I propose is Adaptive Referral State Reconciliation (ARSR). Rather than developing yet another referral management application, I would like to explore a coordination protocol that analyzes the current state of referrals, status of appointment reservations and operations that have already been performed to find out what needs to be done in case of failure. The contribution of such an approach is in combining all three decisions into one process of recovery.

5. What is the most important thing you still do not know?

    The biggest question that still remains for me is whether one coordination approach is enough to ensure that the information on referral and appointments remains accurate in cases where several changes take place almost simultaneously through independent service. For instance, I am unsure about how often an old confirmation of referral might clash with a new treatment schedule and also how the service should be restarted.

    I would also like to see if there will be any benefit from verifying the current states of the referral and reservations before trying to perform an action compared to using a normal durable workflow. Even though there exist technologies that support transactionality, retrials, and message durability, I have not seen any benefit of my coordination principles yet.

    In order to respond to this question, I could create a small simulation that includes District Attorney case service, mental health coordination service, and treatment provider service. Based on made-up data, I would simulate three scenarios, such as referral change after acceptance, two appointment requests at once, and provider service failure while processing.

    I will compare a basic workflow using persistent tasks and retry with my suggested state-aware coordination system. Both the workflows will be subjected to the same simulation failures. I will measure stale confirmations, conflicting reservations, double actions, referrals not resolved, and recovery time. This data will assist me in determining if my suggested system is better or unnecessarily complex.

    If there are few mistakes in confirmation and fewer reservation conflicts based on the results, I could explore the process further. In case there is no difference in results, then I will revise its coordination rules. However, I do acknowledge that the simulated system may not reflect all challenges faced by the organizations in reality.

6. Your Individual Scope
    The scope of my individual project is going to be ARSR in B05 – Resilient Case Management Services.

    My individual mechanism is going to study three interrelated functionalities. First, it is going to discover referrals that should be revalidated in case some important conditions have changed. Second, it is going to coordinate virtual treatment appointments to avoid conflicting confirmed appointments. Third, it is going to restore unfinished referral tasks in case of a crash of the provider's service while verifying that it is still valid.

    I plan to use Python, FastAPI, PostgreSQL, as well as separately running services that are going to simulate the network, as well as its failures. The data that is going to be used is not going to contain any actual cases, appointments, criminal activity, or medical data.

    The objective of the research is to create and test a coordination mechanism that would ensure accurate exchange of information among the services at all times in changing situations and in case of failures. The project is doable for one person since the focus is set on three simulated services, referral process, and experimentation.

    The desired result will be a tested prototype and the comparative analysis to show whether ARSR offers any advantages in the given situation. I will consider it a proposed solution until the results prove its effectiveness.
