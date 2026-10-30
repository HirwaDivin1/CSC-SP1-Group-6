# **Distributed Document Processing: Reliable Recovery and Provenance Tracking**

## **What problem are we investigating?**

The problem I am investigating is how distributed document-processing systems can reliably process files when multiple computers or software workers are involved, particularly when unexpected failures interrupt the processing of documents. Many organizations collect and process information from different sources, including reports, spreadsheets, databases, and other digital records. These documents often need to be cleaned, converted into a standard format, or analyzed before the information can be used. When large numbers of documents must be processed, the work can be divided among multiple software workers to improve efficiency. However, this introduces challenges related to communication, task coordination, failure recovery, and data consistency.

This problem relates to distributed computing because different software components are responsible for completing parts of the processing operation. A typical system might contain a central server that receives documents, a task queue that distributes processing jobs, and multiple workers that complete those jobs independently. Once a worker finishes processing a document, it saves the output and informs the system that the task is complete. Under normal conditions, this allows multiple documents to be processed simultaneously. However, problems can occur when a worker crashes, loses communication, or fails to confirm that it has completed its assigned task.

For example, consider an organization that receives hundreds of CSV and JSON documents containing records that must be converted into a consistent format. Under normal conditions, a document is submitted to the system, assigned to a worker, processed, and saved. The worker then sends a confirmation indicating that the job is complete. However, suppose the worker successfully saves the processed document but crashes before sending the confirmation. The task queue may assume that the job was not completed and assign it to another worker. If the second worker processes the same document again, the system could create duplicate outputs or perform unnecessary repeated work.

Another problem is keeping track of where processed information originally came from. This information is called *data provenance*. It includes details about the original document, the processing steps performed, and the resulting output. If a system does not maintain accurate provenance records, users may have difficulty determining which source produced a particular result or whether a document was processed more than once. The World Wide Web Consortium (W3C) defines a provenance model for describing the relationships between data, processing activities, and the agents responsible for those activities (W3C, 2013).

My project will investigate how to improve the reliability of a distributed document-processing system by combining failure recovery, duplicate-output prevention, and provenance tracking. The main focus will be ensuring that interrupted processing jobs can be recovered without creating multiple accepted outputs for the same logical task. Instead of simply simulating these conditions, I plan to build a small working application in which independent software workers communicate with a central service and process actual document files.

The project will focus on CSV and JSON documents, simple data transformations, and failures involving individual processing workers. It will not attempt to develop an entire enterprise document-management platform or support every possible document format.

## **Who or what is affected by it?**

This problem affects organizations and individuals that depend on automated systems to process large collections of information. Examples include government agencies, research institutions, businesses, and organizations that regularly receive reports or datasets from different sources. These organizations may rely on document-processing pipelines to prepare information for analysis, reporting, or storage. When processing jobs fail or produce inconsistent results, the information provided to users may become incomplete, duplicated, or difficult to verify.

For example, consider a research organization that collects environmental reports from several locations. Each report contains measurements that must be converted into a common format before analysts can compare the results. If a worker crashes while processing one of these reports, the system must determine whether the document was successfully processed or whether the task needs to be repeated. If the system produces multiple accepted outputs for the same report, analysts may accidentally count the same information more than once. This could lead to inaccurate summaries or require additional time to identify and remove duplicate records.

Data analysts and researchers are particularly affected because they depend on consistent information when performing calculations and making decisions. System administrators are also affected because they must monitor processing jobs, investigate failures, and determine which tasks need to be restarted. Developers responsible for maintaining these systems must ensure that communication failures do not cause documents to be lost or incorrectly processed.

The processing infrastructure itself is affected as well. Repeating tasks unnecessarily consumes computing resources, including processing time, memory, and storage. When many documents are being processed simultaneously, repeated work can reduce the system's overall efficiency. These problems become more important as the number of workers and incoming documents increases.

Provenance is another important concern for the people using the processed information. Research by Chapman and colleagues (2024) discusses how detailed provenance can help explain the transformations performed within data-processing pipelines. Without a reliable processing history, users may have difficulty understanding how an output was created or determining whether it can be trusted.

Addressing these issues is important because organizations need both accurate processing results and a reliable way to recover when failures occur. My project will focus on improving these capabilities within a small distributed system rather than assuming that adding more workers automatically makes document processing reliable.

## **What evidence do you currently have that it is a real problem?**

The challenges associated with distributed document processing have been documented in research and in technical documentation for existing distributed messaging systems. When work is divided among multiple independent processes, communication failures can create uncertainty about whether a task was completed. As a result, reliable systems must consider both how tasks are distributed and how their results are recorded.

RabbitMQ is a messaging system that supports communication between applications and processing workers. Its reliability documentation explains that messages can be delivered more than once when failures interrupt communication or prevent acknowledgments from reaching the message broker. A message broker is software that receives messages and distributes them to the appropriate consumers. Acknowledgments allow a worker to confirm that it has handled a message. When a message is not acknowledged before a worker disconnects, it may be delivered again to another worker (RabbitMQ, n.d.).

This behavior helps prevent unfinished tasks from being permanently lost, but it also creates the possibility of repeated execution. For example, a worker may complete a document transformation and save the output while the acknowledgment is still pending. If the worker then crashes, the task may be assigned again even though its result already exists. RabbitMQ therefore recommends that applications be designed to handle repeated message deliveries safely.

The Celery task-processing framework also documents this problem. Celery supports distributing tasks among worker processes and can acknowledge tasks after execution. However, its documentation explains that late acknowledgments may allow a task to execute more than once if a worker fails. This is why Celery recommends designing tasks to be *idempotent*, meaning that repeating the same operation does not create additional unintended effects (Celery, 2026).

The importance of provenance has also been established through technical standards and academic research. The W3C PROV model describes how the origins and transformations of information can be represented. In addition, Chapman and colleagues (2024) examine how detailed provenance records can support understanding and explaining data transformations. These sources demonstrate that tracking the history of processed information is an established technical concern, rather than simply an optional feature.

Existing tools such as OpenLineage also demonstrate that software systems can record metadata about processing jobs, their executions, and the datasets they use or produce. This provides a practical example of how provenance-related information can be collected during data processing.

Although these sources establish that repeated processing and provenance tracking are genuine technical challenges, they do not prove that a particular organization has experienced the exact failure described in my project. I have not yet developed the application, measured duplicate outputs, or tested recovery after worker crashes.

At this stage, I am assuming that a basic processing system without duplicate-output protection may produce repeated results when an already completed task is assigned again. I also expect that maintaining processing records will improve recovery and traceability, although doing so may introduce additional database operations and processing overhead. These assumptions will need to be tested.

The main evidence still missing is experimental data showing how the proposed implementation behaves during normal operation and controlled failures. By building the system and deliberately interrupting workers at different stages, I will be able to determine whether the proposed improvements prevent duplicate outputs and how they affect overall processing performance.

## **What solutions already exist?**

Several existing technologies support distributed task processing and failure recovery. Two important approaches are message-queue-based processing and workflow orchestration. Both allow work to be managed across multiple software components, but they provide different levels of coordination and have different limitations.

Message-queue-based processing uses a system such as RabbitMQ to distribute jobs among available workers. Instead of sending every document directly to one processing program, the application creates a message describing the work that needs to be completed. Workers receive these messages, perform the required operations, and acknowledge completion. This approach supports asynchronous processing, meaning that the document-submission service does not need to wait for every document to finish processing before accepting more work.

One advantage of message queues is that they separate the application receiving documents from the workers processing them. Additional workers can be added when more processing capacity is needed. RabbitMQ also supports acknowledgments and message redelivery, which help unfinished jobs become available again after certain failures. However, the message queue does not automatically guarantee that a task will produce only one accepted output. If a worker completes its operation but fails before acknowledging the message, the same job may be processed again.

Another approach is workflow orchestration, which uses software to coordinate processing tasks, track their status, and manage dependencies. Apache Airflow is an example of a workflow-management system used to organize data-processing pipelines. It allows developers to define workflows containing multiple tasks and control how those tasks are executed. This is useful when document processing involves several dependent stages, such as validation, transformation, and report generation.

Workflow orchestration provides more features for monitoring and organizing complex processing operations. However, these systems may introduce additional configuration and infrastructure requirements. They also do not eliminate every problem associated with repeated task execution. The operations performed by individual tasks still need to be designed so that retries do not produce incorrect results.

A related approach is persistent job tracking. In this design, the application records each processing job in a database, including its unique identifier, processing status, and output information. Before accepting a processed result, the system checks whether that logical job already has a completed result. This can help prevent duplicate outputs even when the processing task is executed more than once. The design must ensure that checking and recording completion are coordinated safely, rather than allowing two workers to independently accept the same result.

Provenance systems provide another useful capability. OpenLineage defines a model for collecting information about jobs, individual executions, and the datasets involved in processing. This can help users determine which input data contributed to a particular output. However, recording provenance alone does not prevent repeated processing or recover unfinished tasks. It is mainly concerned with describing how data was produced.

For my project, I plan to build a smaller system that combines reliable task distribution with persistent job tracking and basic provenance records. The main comparison will be between a baseline implementation that relies on message acknowledgments and a proposed implementation that also uses unique job identifiers, database-enforced output uniqueness, and processing-history records.

The goal is not to replace existing technologies such as RabbitMQ or Airflow. Instead, it is to investigate whether a limited, application-level improvement can prevent duplicate outputs and preserve document history under the specific failure conditions being tested.

## **What is the most important thing you still do not know?**

The most important question I still need to investigate is whether persistent job tracking and duplicate-output prevention can improve recovery from worker failures without introducing excessive processing overhead.

Existing documentation explains why tasks may be delivered more than once and why applications should safely handle retries. However, the effectiveness of a particular solution depends on how it is implemented and what types of failures occur. For example, recording task status in a database may prevent a repeated job from creating another accepted output, but the additional database operations could increase processing time. There may also be situations where two workers attempt to complete the same job at nearly the same time.

To investigate this question, I plan to develop a small distributed document-processing application using Python. The application will include an ingestion server that receives documents, a task queue that distributes processing jobs, and two independent workers that transform files. A database will record job identifiers, processing statuses, source information, and output records.

The first version will serve as a baseline. It will use task acknowledgments to manage work but will not include the proposed database-enforced duplicate-output protection. The improved version will use persistent job records and a uniqueness rule that permits only one accepted result for each logical processing job. It will also record the source document and transformation used to create each output.

The experiment will use a collection of generated CSV and JSON documents containing sample records. Both versions of the system will receive the same document batches and perform the same transformations. I plan to test normal operation, worker failures during processing, and failures that occur after an output has been saved but before the worker acknowledges completion.

The main measurements will include the percentage of jobs completed successfully, the number of missing or duplicate accepted outputs, recovery time after a worker failure, total processing time, and the completeness of provenance records. I will also compare processing throughput, meaning the number of documents completed per second, to determine whether the additional tracking operations reduce performance.

To make the comparison fair, both implementations will use the same document sizes, worker counts, and processing operations. Failure conditions will be introduced at predetermined points so the behavior can be reproduced. I will also repeat experiments to check whether the results are consistent.

One important distinction is that a worker may execute the same transformation more than once even if the improved system prevents duplicate results from being accepted. Therefore, the project will measure duplicate execution attempts separately from duplicate saved outputs. The initial goal is not to guarantee that work is physically executed only once, but to make repeated execution safe for the selected document-processing operations.

The results will influence the eventual design. If persistent tracking prevents duplicate outputs while adding only a small processing delay, it would support using the improved approach. If performance decreases significantly, I may need to simplify the stored records or reduce unnecessary database operations. The final design decision will depend on the experimental results rather than assuming that the proposed method is always better.

## **Project Scope**

My individual project will focus on designing, implementing, and evaluating a simplified distributed document-processing system that supports reliable recovery and provenance tracking. The main goal is to determine whether application-level job tracking can prevent duplicate outputs when worker failures cause processing tasks to be repeated.

The application will be developed using Python and the FastAPI framework. A central ingestion service will accept document uploads and create processing jobs. A message queue, potentially implemented using RabbitMQ, will distribute those jobs to two independent worker processes. SQLite or PostgreSQL will be used to store processing records, depending on the concurrency requirements identified during development.

The system will accept two document formats: CSV and JSON. Each document will undergo one predefined transformation, such as standardizing field names and producing a cleaned output. Keeping the transformation simple will allow the investigation to focus on the reliability of the distributed processing system instead of the complexity of interpreting document contents.

Each logical processing job will receive a unique identifier. The database will store the document's source information, processing status, output location, and completion time. The improved version will prevent multiple accepted outputs from being committed for the same job. It will also store basic provenance information connecting the source document, processing operation, and resulting output.

The proposed application will contain a submission component, a task-distribution component, two workers, and a shared database. These components will run as separate software processes and communicate using network interfaces or message passing. This provides an actual small distributed application rather than a simulation that only represents hypothetical workers.

Testing will focus on worker crashes, interrupted acknowledgments, repeated task deliveries, and normal processing performance. The system will be evaluated using controlled document batches and repeatable failure scenarios. Results will be collected in tables and graphs to compare the baseline and improved implementations.

The project will not include advanced document recognition, machine-learning models, support for large numbers of file formats, complex access-control systems, or deployment across multiple cloud regions. It will also exclude failures of every component occurring simultaneously. These areas would expand the project beyond the main research question.

A possible future extension would involve adding more workers or supporting additional document transformations. However, the initial scope will remain limited to two workers, two document formats, one transformation, and a small number of controlled failure scenarios.

This project is manageable for one student because its main components can be developed and tested locally using established Python libraries and open-source tools. The document-processing operations are intentionally simple, and the system does not require physical hardware, paid cloud services, or a large computing environment. The limited scope also allows enough time to implement the baseline, develop the proposed improvement, test failure recovery, and explain the results.

Overall, the project will provide a practical investigation into reliability challenges in distributed document-processing systems. By building and comparing two working implementations, I hope to determine how persistent job tracking and provenance records can improve recovery and result consistency when processing workers experience failures.

## **References**

1. RabbitMQ. *Reliability Guide*. RabbitMQ Documentation.  
   [https\://www\.rabbitmq.com/docs/reliability](https://www.rabbitmq.com/docs/reliability)  
2. RabbitMQ. *Consumer Acknowledgements and Publisher Confirms*. RabbitMQ Documentation.  
   [https\://www\.rabbitmq.com/docs/confirms](https://www.rabbitmq.com/docs/confirms)  
3. Celery Project. *Tasks*. Celery 5.6 Documentation.  
   [https\://docs.celeryq.dev/en/stable/userguide/tasks.html](https://docs.celeryq.dev/en/stable/userguide/tasks.html)  
4. World Wide Web Consortium (W3C). (2013). *PROV Model Primer*. W3C Working Group Note.  
   [https\://www\.w3.org/TR/prov-primer/](https://www.w3.org/TR/prov-primer/)  
5. Chapman, A., Lauro, L., Missier, P., & Torlone, R. (2024). *Supporting Better Insights of Data Science Pipelines with Fine-grained Provenance*. ACM Transactions on Database Systems, 49(2), Article 6\.  
   [https\://doi.org/10.1145/3644385](https://doi.org/10.1145/3644385)  
6. OpenLineage. *OpenLineage Specification: Job, Run, and Dataset Metadata*. OpenLineage Documentation.  
   [https\://openlineage.io/docs/spec/object-model/](https://openlineage.io/docs/spec/object-model/)  
7. Apache Software Foundation. *Best Practices*. Apache Airflow Documentation.  
   [https\://airflow.apache.org/docs/apache-airflow/stable/best-practices.html](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)

