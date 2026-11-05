Raian Pial

# A Distributed Tool for Coordinated Load and Resource Management

# **What problem are you investigating?**

I am investigating why an application can keep some servers busy while leaving capacity unused on others. This can happen when the part that sends requests does not take changes in available resources into account. My project will look at how to connect these decisions so the application finishes more useful work without becoming overloaded.

This topic comes from National Science Foundation (NSF) Award 2542973, “CAREER: Integrated Load and Resource Management for High-Utilization Datacenters,” led by Ahmed Saeed at Georgia Tech. His project connects overload control inside applications, server resource scheduling, and coordination between services. I will build a smaller version that connects deciding how much work to accept, assigning workers, and choosing where requests go. The original research also covers central processing unit (CPU) and graphics processing unit (GPU) scheduling; my prototype uses application-level worker assignments. My example is a number-processing application with two steps. Service A sorts a list of numbers, and Service B runs calculations on the sorted list and returns a summary. Each service has two copies, called replicas. A worker is a process that carries out a task. When the workload matches the workers available at each step, requests move through A and B without waiting long.

The problem appears when work is sent to a replica faster than it can finish it, even though another replica has room. For example, suppose one copy of B can finish five requests per second and the other can finish fifteen. Sending ten requests per second to each would make the first copy fall behind while the second has spare capacity. These numbers explain the situation; they are not results from my program.

There can also be too many workers assigned to A and too few to B. Moving an available worker from A to B could help, but the system must then update how much work each stage accepts and where it sends requests. If both copies of B are full, A should slow down accepting new work so unfinished results do not keep piling up. I will test whether connecting these decisions helps more requests finish on time.

I aim to implement separate server programs that communicate through network messages and perform real calculations. They will initially run on one computer. The project will measure their actual behavior, including delays and failures.

# **Who or what is affected by it?**

The immediate stakeholders are developers and administrators responsible for services that process requests through several stages. In the proposed example, an administrator needs to decide how many requests to admit and how many workers each stage should receive. A developer needs a clear explanation of why a request was delayed or rejected. Users experience the outcome through waiting times, failures, or successful results.

Google is a specific organization with documented experience of this problem. Its Site Reliability Engineering book explains that requests can have very different resource costs, making request counts alone an unreliable capacity measure. It describes resource-based overload protection and client-side throttling, where clients reduce outgoing work when a backend is rejecting requests. This provides an operational example of the need to coordinate demand with available capacity. It does not establish Google as a client for my project. 

For my prototype, the intended user is an administrator running a small data-processing service on limited hardware. This is a proposed user profile rather than a confirmed external partner. The administrator would use test results and logs to understand which stage limits performance and whether changing worker allocation helps. A successful prototype could provide a repeatable way to evaluate these choices before considering a larger deployment.

I will evaluate useful throughput, unused worker capacity, waiting times, rejected work, and controller overhead. Financial and energy savings will not be claimed without separate measurements.

# **What evidence do you currently have that it is a real problem?**

Google’s Site Reliability Engineering book explains that requests can use different amounts of resources. For example, a large processing task may need more time and memory than a small one. This means that sending the same number of requests to each server does not always give them equal workloads. This supports looking at available resources when deciding where requests should go.

Google also explains that overload can cause a system to complete less useful work. When requests arrive faster than they can be processed, more requests remain active or waiting, which can put additional pressure on memory and processing resources. Problems can spread if work from an overloaded or failed server is sent to other servers that cannot handle the extra traffic. In the proposed application, this is relevant because Service A could continue producing results faster than Service B can process them.

The research paper Overload Control for µs-scale RPCs with Breakwater provides another example. Breakwater uses credits issued by servers to control how much work clients can send. Its evaluation shows how this approach handles sudden increases in demand for services with very short requests. This provides evidence that controlling incoming work based on feedback from servers is useful, although it does not prove that the same results will occur in this project.

Together, these sources establish that uneven resource demands and overload are real problems. What still needs testing is whether the proposed coordination improves this particular application. Comparing it with fixed worker assignments and basic load balancing will show whether it completes more requests on time, reduces waiting, and leaves less worker capacity unused.

# **What solutions already exist?**

One existing approach is round-robin load balancing. NGINX documentation describes distributing requests among application servers in turn. This is easy to configure and offers a useful baseline. For my workload, however, equal request counts may represent unequal amounts of computation. My inference is that this approach can leave one replica occupied with expensive requests while another finishes cheaper work. 

A second approach is least-connections load balancing. NGINX sends a new request to the server with the fewest active connections, which can help when requests take different amounts of time. Connection count still does not directly describe memory requirements or the capacity of a later stage. For this experiment, its limitation is that selecting a less busy replica does not itself adjust worker allocation between A and B. This comparison concerns the routing methods, not every capability available in NGINX. 

A third approach is admission control and throttling. Google documents rejecting work as resource utilization approaches configured thresholds and reducing traffic at clients. These mechanisms can protect a backend, but selecting thresholds and deciding how quickly to recover admission remain important design choices for my experiment. 

Breakwater offers a more specialized admission mechanism: servers grant credits that permit clients to send work. This helps regulate arrivals before requests accumulate at the server. Its focus on very short requests makes implementation overhead especially important. I will use the paper to understand the design tradeoff, rather than claim to reproduce its algorithm or performance. 

My tentative solution will connect simple versions of these ideas. Each replica will report queue length, available worker slots, and estimated memory reservations. A central manager will route eligible work, while each server controller adjusts its own workers between stages within a fixed local total. Downstream congestion will reduce upstream admission. The deliverable will be a configurable tool with a controlled comparison of coordinated and separate decisions. I am not claiming that these mechanisms are new.

# **What is the most important thing you still do not know?**

The central uncertainty is whether keeping admission and routing aligned with worker allocation increases timely completions enough to justify coordination overhead. I will test steady traffic, bursts, mixed request sizes, and a more expensive second stage. Initial calibration will identify approximate service capacity, after which workloads will span below-capacity and overloaded conditions. Request processing will perform actual calculations and allocate real data structures.

The experiment will compare round-robin routing with fixed workers, least-connections routing with fixed workers, and the coordinated version. All versions will use the same tasks, hardware, total worker count, memory budget, queue bounds, and timeout rules. A fixed-allocation admission-control run will isolate dynamic allocation’s contribution. A controlled test will change worker assignments midway through a run, comparing updated admission and routing against unchanged settings. This directly tests allocation–traffic mismatch.

Measurements will include completed requests per second, median response time, and the 95th-percentile response time, below which 95 percent of measured responses fall. I will also report worker busy/idle time, rejections, timeouts, queue lengths, and the percentage of all offered requests completed within a deadline selected before comparison. Reporting successful-response latency alone could make aggressive rejection appear beneficial. Outcomes will therefore be separated by request type and terminal status.

An automated test script will generate arrivals on a preset schedule rather than waiting for each response before sending the next request. It will record offered and actual send rates to detect limitations in the traffic generator. Runs will include warm-up, a measured interval, and a defined drain period. Repeated trials with recorded random seeds will show variability. Unique request identifiers and known expected outputs will support checks for missing responses, duplicates, and incorrect calculations.

Failure tests will stop one server program and check that the manager stops routing new work to it after a timeout. Interrupted requests will receive explicit failure outcomes; automatic retry and guaranteed recovery are outside this scope. Separate checks will verify queue bounds, reservations, fixed worker totals, and reassignment only after task completion. Results may support slower worker adjustments, revised admission limits, or retaining fixed allocation if coordination provides no consistent benefit.

# **Your Individual Scope**

I will build a Python tool consisting of a request manager, two independent server programs, and a test client. Each server will own a copy of A and B, separate queues, and a local controller. Python’s multiprocessing module will support workers executing actual tasks. Workers will finish their current task before being reassigned between stages within that server.

The programs will communicate through Transmission Control Protocol (TCP) sockets using localhost and different ports. Python’s socket documentation explains that localhost connections are restricted to the same machine. Components will exchange serialized requests, results, and capacity reports without relying on shared application memory between servers. Configurable host addresses will allow later deployment across computers, although that deployment will not be claimed as tested. 

For thrust one, a reusable admission wrapper will check processing slots and estimated memory requirements together. Estimates for two task sizes will be calibrated and compared with observed process memory. Queue payloads and process overhead must also fit the budget. These are application-managed limits, not operating-system-enforced memory isolation or transparent instrumentation of arbitrary software.

For thrust two, each local controller will divide its fixed worker pool between A and B, updating admission limits with the allocation. A minimum for each stage and a waiting period between changes will limit overcorrection. Worker counts approximate resource scheduling at the application level; they do not reserve processor cores or implement operating-system or GPU scheduling. Microsecond decisions are outside scope.

For thrust three, the manager will select eligible replicas across the two server programs. Service A’s output will be forwarded to an available B replica. Reports of downstream congestion will reduce upstream admission, providing backpressure. Periodic health checks and connection timeouts will identify unavailable processes. Local admission checks will remain authoritative because capacity reports can become outdated.

Development and testing will require no virtual machines, Docker, or paid cloud services. Artificially generated requests will exercise real computation, memory allocation, and socket communication. This is a local deployment of a distributed-systems tool, not evidence of performance across independent physical servers. All components share hardware and an operating system, so tests cannot establish resilience to whole-machine failures or real network partitions. The central manager will also remain a single point of failure.

The project excludes automatic cluster expansion and full reproduction of the NSF research. Its limited service chain and rule-based controls make incremental implementation practical. Deliverables will include source code, startup instructions, automated tests, comparison graphs, and measured limitations. The investigation will establish whether this implementation improves timely completions under its tested conditions.

# **References**

1\. National Science Foundation. Award 2542973\. CAREER: Integrated Load and Resource Management for High-Utilization Datacenters.

https\://www\.nsf.gov/awardsearch/show-award/?AWD\_ID=2542973

2\. Saeed, Ahmed. NSF CAREER project description. Georgia Tech.

https\://saeed.github.io/career/index.html

3\. Saeed, Ahmed. Curriculum vitae. Funding entry for NSF Award 2542973\.

https\://saeed.github.io/files/cv.pdf

4\. Forero Cuervo, Alejandro. “Handling Overload.” Site Reliability Engineering, Chapter 21\. Google, 2016\.

https\://sre.google/sre-book/handling-overload/

5\. Ulrich, Mike. “Addressing Cascading Failures.” Site Reliability Engineering, Chapter 22\. Google, 2016\.

https\://sre.google/sre-book/addressing-cascading-failures/

6\. Cho, Inho, Ahmed Saeed, Joshua Fried, Seo Jin Park, Mohammad Alizadeh, and Adam Belay. “Overload Control for µs-scale RPCs with Breakwater.” 14th USENIX Symposium on Operating Systems Design and Implementation, 2020, pp. 299–314.

https\://www\.usenix.org/conference/osdi20/presentation/cho

7\. NGINX. “Using nginx as HTTP load balancer.” Official documentation.

https\://nginx.org/en/docs/http/load\_balancing.html

8\. Python Software Foundation. “multiprocessing — Process-based parallelism.” Python documentation.

https\://docs.python.org/3/library/multiprocessing.html

9\. Python Software Foundation. “Socket Programming HOWTO.” Python documentation.

https\://docs.python.org/3/howto/sockets.html

*Source verification note: The NSF award page was unavailable during preparation. The award number and title were cross-checked against the investigator’s curriculum vitae; descriptions of the research thrusts rely on his project page. Other linked sources were consulted on November 4, 2026\.*