# Distributed SSH Blocklist for Research Campuses

**Author:** Hirwa Divin Iradukunda  
**Course:** CSC 59866  
**Selected project and option:** Distributed SSH blocklist across independent research campuses (motivated by National Science Foundation (NSF) award 2613277)  
**Current assignment:** 2  
**Friday commit deadline:** November 13, 2026, at 11:59 p.m. New York time (extended to November 15)  
**Monday presentation:** November 16, 2026, at 6:30 p.m. New York time  
**Last updated:** November 15, 2026  
**Document status:** Proposed

## Progress note

> - **What changed:** My main work was writing the Section 2 specification and starting Section 3 to compare local bans, a central hub, and k-of-n. Earlier, I narrowed the six-week scope to one operation with one normal and one adverse case on 3 campus VMs, deferring signing, withdrawal, expiry, and honeypot replay to Semester II. I also redrew Figure 1 for k=2 without signed reports, and fixed citations ([3] on November 9; [1] on November 9 and 13) after rechecking sources rather than from oral feedback.
> - **What I learned:** Writing requirements showed that safety (C1) and useful progress (F2) must both be tested, because a node that never bans anything would still pass C1.
> - **Main open issue:** A central hub could also wait for k campuses, leaving the real difference as who does the counting.
> - **Next step:** Choose the approach and draw the architecture in Assignment 3.

## Contents

- [1 Problem research and scope](#1-problem-research-and-scope)
- [2 Requirements and system specification](#2-requirements-and-system-specification)
- [3 Alternatives and selected solution](#3-alternatives-and-selected-solution)
- [4 Architectural design](#4-architectural-design)
- [5 Component design and interfaces](#5-component-design-and-interfaces)
- [6 Data structure design](#6-data-structure-design)
- [7 Algorithm design and execution](#7-algorithm-design-and-execution)
- [8 Failures and security](#8-failures-and-security)
- [9 Implementation and feasibility](#9-implementation-and-feasibility)
- [10 Testing and verification](#10-testing-and-verification)
- [11 Operation maintenance and future work](#11-operation-maintenance-and-future-work)
- [12 Revision history and references](#12-revision-history-and-references)

## 1 Problem research and scope

**Problem and affected people:**

For a system administrator protecting a research campus's SSH (Secure Shell) login servers, password-guessing attempts arrive all day, and scientific institutions face advanced cyber attacks with limited cybersecurity expertise and resources [1]. Each campus blocks attackers with its own tools, such as fail2ban [8], so an address that one campus has already caught must start over at the next campus before it is banned there too; guessing spread across many attacking addresses is also hard to spot by looking at one address at a time [3], and attackers have moved between high-performance computing (HPC) sites using stolen SSH credentials [2]. The consequence is attacker attempts reaching servers that another campus had already stopped. Sharing bans through one central hub would fix that, but a single mistake or compromise at the hub, or at one member, could then lock researchers out at every campus at once. Requiring several campuses to agree before a ban is safer, but it bans fewer attackers. My project will investigate that trade-off by building a distributed blocklist with no central operator, in which a ban applies once k of n campuses report the same address, and by measuring how much protection it keeps compared with local bans and a central hub.

| Stakeholder | What they do today | What they need from a shared blocklist |
|---|---|---|
| Campus security or HPC system administrator (for example at the City University of New York (CUNY) High Performance Computing Center (HPCC)) | Runs local tools such as fail2ban on SSH login servers | Fewer attempts reaching servers, and control over which other sites' reports are trusted |
| Researchers and students who log in over SSH | Log in with a password, for example through CUNY HPCC's gateway (Documented: see Evidence) | Not to be locked out because another campus made a mistake |
| A participating campus as an organization | Decides what security data it can share | To share block decisions without giving raw logs to a single outside operator |
| Regional network or consortium (for example NYSERNet, the New York State Education and Research Network) | Connects member campuses (Documented: CUNY is a member) | A sharing scheme that does not need it to run and defend a central service (Assumed) |

Table 1. Stakeholders and needs. CUNY's HPC center and NYSERNet are an illustrative use case; the project does not involve them, so their needs here are assumptions.

**Current workflow:**

1. An attacker's address sends failed SSH logins to Campus A's login server.
2. Campus A's detector (for example fail2ban) reads the authentication log and bans the address after a threshold, such as 5 failures in an hour.
3. Campus B and Campus C learn nothing, so the same address must reach their thresholds again before they ban it there too.
4. If campuses share through a central hub instead, every member applies whatever the hub sends, including mistakes.

The difficulty occurs at step 3 (no sharing) or step 4 (sharing that depends on one operator).

**Concrete scenario (illustrative):**

| Time | Event | Local bans only | Central hub | k-of-n, k = 2 |
|---|---|---|---|---|
| 09:00 | 203.0.113.7 fails 5 logins at Campus A | A bans it | A bans it and reports to hub; hub tells B and C | A bans it and sends a report to B and C; 1 of 2 needed reports |
| 09:20 | Same address tries Campus B | B receives the attempts until its own threshold | Already blocked at B | B receives the attempts until its own threshold, then reports; with 2 reports, A, B and C all ban it |
| 09:40 | Same address tries Campus C | C receives the attempts until its own threshold | Already blocked at C | Already blocked at C |
| 10:00 | Campus C misconfigures its detector and reports 198.51.100.20, a shared address used by many researchers | Only C blocks those users | Hub pushes the ban to everyone: users locked out at A, B and C | One report is not enough, so only C blocks them |

Table 2. The same events under three sharing approaches. Addresses use reserved documentation ranges.

![With k = 2. An attacker sends failed SSH logins to Campus A; A's detector bans the address and A's node reports it to the nodes at B and C. Later the attacker fails logins at Campus B; B's detector bans it and B's node reports it to C. With reports from two campuses, C's node bans the address, so the attacker's later attempt at Campus C is blocked before it starts.](assets/blocklist_workflow.png)

Figure 1. Proposed workflow with k = 2 of n = 3 (the normal case). Each campus keeps its own detector and adds a blocklist node. Nodes exchange reports directly, with no central server; a single report is not enough, so C bans the address only after both A and B have reported it. For readability, B's report to A is not drawn. Editable source: [assets/blocklist_workflow.dot](assets/blocklist_workflow.dot).

**Evidence:**

| Claim | Label | Source |
|---|---|---|
| Scientific institutions face advanced cyber attacks with limited cybersecurity expertise and resources | Documented | NSF award 2613277 abstract [1] |
| Attackers moved between HPC sites using compromised SSH credentials in 2020 | Documented | The computer security incident response team (CSIRT) of EGI, a European federation of research computing centers [2] |
| Distributed SSH password guessing spread over many sources is real and hard to see from one source | Documented | Javed and Paxson [3] |
| Sharing bans between honeypot nodes cut attempts reaching SSH by 27.7–37.7% at k = 1, but only 9.0–19.4% at k = 2 (all 33 nodes); on 5 nodes outside the main sensor pool, 7.0–12.2% at k = 1 and 1.3% at k = 2; ranges cover three fail2ban-style thresholds (5 per hour, 10 and 30 per 24 hours) | Observed | Pilot replay of CyberLab data [4]; [evidence/pilot](evidence/pilot/README.md) |
| Delaying shared bans by one hour changed the k = 1 result by at most one percentage point | Observed | Same pilot replay |
| CUNY is a NYSERNet member | Documented | NYSERNet membership page [5] |
| CUNY's High Performance Computing Center (HPCC) users off the College of Staten Island (CSI) campus log in to one gateway with a password; the page does not mention multi-factor authentication | Documented (page last edited January 3, 2025) | CUNY HPCC wiki [6] |
| Campuses would prefer a shared blocklist with no central operator | Assumed | Part of the illustrative use case; not studied in this project |
| Mistaken or poisoned shared bans are a real concern | Documented (vendor) | CrowdSec describes defenses against false positives and data poisoning [7] |

Table 3. Evidence for the problem. The pilot used honeypot data: attackers only, six days, one operator, and 88% of events from one sensor pool, so it cannot measure wrongly blocked users. See [evidence/pilot/README.md](evidence/pilot/README.md) for limits.

**Six-week contribution:** One working path on 3 campus virtual machines, one node per simulated campus, plus 1 test machine that plays the attacker: a node turns a local fail2ban ban into a report to the other nodes, and each node applies the ban once k of n campuses have reported the same address. fail2ban is reused rather than built.

- Normal case: with k = 2, an address caught at two campuses is banned at the third before it arrives there.
- Adverse case: one campus wrongly reports a shared address (the 10:00 row of Table 2); with k = 2, no other campus bans it.
- Baseline: the same inputs with local bans only.
- Supporting checks: reports from non-members are ignored (F4 in Section 2), and local bans keep working when other nodes are unreachable (C2 in Section 2).
- One timing measurement for the proposed quality target (Q1 in Section 2).

**Semester II scope:**

- Signed reports, withdrawal of a report, and ban expiry.
- Recovery after network splits: a cut-off node ends up with the same shared list as the others after it reconnects.
- A central-hub baseline, so all three approaches run on the same inputs.
- A replay of public honeypot data on 3–5 nodes, with measurements of attempts stopped, how many users one bad or mistaken site can lock out, recovery time, and network and resource overhead, at different values of k.
- Ways to reduce the cost of agreement, such as per-site trust or shorter expiry, if time allows.

**Exclusions:**

- Logins with stolen but valid passwords: they can succeed on the first try, so no ban is triggered.
- Attackers that rotate to a new address for every attempt.
- Working with or deploying on CUNY, NYSERNet or any real campus network; they are an illustrative use case, and all testing uses virtual machines and replayed public data.
- Private matching of addresses (for example secure multiparty computation, as in SEPIA [9]); reports name the address in the clear among members.
- Open membership: the set of member campuses and their network addresses is fixed in advance.
- Building a new attack detector.

> **Open question:** Can k-of-n agreement keep enough of the benefit of sharing to be worth its safety, or does a simpler approach (local bans or a hub) perform as well? See Section 12.

## 2 Requirements and system specification

This section specifies the six-week working path from Section 1. A **campus** is one participant; in the prototype each campus is one virtual machine running SSH (Secure Shell, the remote login service), fail2ban and a blocklist **node**. **n** is the number of member campuses (3 in the prototype) and **k** is how many different campuses must report an address before every node bans it (k = 2 unless stated). A **report** says "campus X banned address Y at time T". A **ban** means the campus refuses SSH connections from that address.

| ID | Required behavior and conditions | Acceptance check | Design and test reference |
|---|---|---|---|
| F1 | When fail2ban on a campus bans an address, that campus's node sends a report to every other member node | Make a test address fail 5 logins at Campus A; check that the nodes at B and C each record a report from A for that address | Planned; design in Sections 5 and 7 |
| F2 | When a node holds reports for the same address from at least k different campuses, counting its own campus's local ban as one of them, it bans that address | With k = 2, cause bans at A and then B; check that C refuses an SSH connection from the address before the address has tried C | Planned; normal case in Section 1 |
| F3 | An operator can list the shared bans a node has applied, with the campuses whose reports caused each one | After the F2 check, the list on C shows the address with A and B | Planned |
| F4 | A node ignores reports from senders that are not configured members, and records that it ignored them | Send a report from the test machine, which is not a member; check that no node counts it and that each node's log shows it was ignored | Planned |
| C1 | With k of 2 or more, no node bans an address because of reports from fewer than k different campuses; repeated reports from one campus count once | Use a test command at C's node to send the same report for 198.51.100.20 three times; check that A and B do not ban it (adverse case in Section 1) | Planned; adverse case in Section 1 |
| C2 | Losing contact with other nodes never removes a campus's own fail2ban bans or stops it from adding new ones | Stop the nodes at B and C; check that A's existing bans remain, then make a test address fail 5 logins at A and check that A bans it | Planned |
| Q1 | Proposed target, not measured: at least 95 of 100 test addresses reported by k campuses are banned at every running node within 5 seconds after the k-th report is sent, with one new address every 2 seconds, its k reports sent by a test command at k campus nodes (each sending node counts its test report as its own campus's report), on the 3 campus virtual machines in one local virtual network | Record when each k-th report is sent and when each node adds the ban, with clocks synchronized; an address never banned counts as a miss | Target only; measured in Assignment 5 |

Table 4. Initial requirements. F = functional requirement, C = correctness rule, Q = quality target. No requirement has passed yet; every check is a planned procedure.

C1 alone could be met by a node that never bans anything, so F2 is needed to show useful progress. The 5-second value in Q1 is a provisional choice: in the pilot, delaying shared bans by a whole hour changed the result by at most one percentage point (Table 3, measured at k = 1 only), so a few seconds leaves a wide margin. The target mainly checks that the prototype's sharing works promptly and reliably; it may be revised after the first measurement.

**Inputs and outputs:**

| Case | Input | Expected output |
|---|---|---|
| Ordinary (normal case) | k = 2, n = 3. 09:00: fail2ban at A bans 203.0.113.7. 09:20: fail2ban at B bans the same address | After B's report, C bans 203.0.113.7; C's list shows it with reports from A and B; an SSH attempt from it at C is refused |
| Unsuccessful (adverse case) | k = 2, n = 3. C's detector is misconfigured and C reports 198.51.100.20, a shared address, three times | A and B record one report from C, which is fewer than 2, and do not ban; researchers using that address can still log in at A and B |
| Unsuccessful (non-member) | A fourth virtual machine, not in the member list, reports 203.0.113.99 | No node counts the report; each node logs that it ignored a report from a non-member |

All addresses come from ranges reserved for documentation, so no real host is involved.

**Assumptions:**

| Assumption | Label | How to check |
|---|---|---|
| fail2ban can run a custom command each time it bans an address, receiving that address | Documented: fail2ban's action files define an `actionban` command that receives `<ip>` [10] | Configure such an action on one virtual machine and confirm it runs with the banned address |
| The three campus machines and the test machine can reach each other over the local virtual network | Assumed | Connect from each machine to the others' SSH and node ports before building further |
| An attacker uses the same address at every campus during an attack | Assumed (the pilot made the same assumption about pseudonymized addresses) | Accepted without a direct check. Consistent with the pilot: at a 5-per-hour threshold, 4,439 of 6,316 detected attacking addresses were seen at two or more nodes [evidence/pilot](evidence/pilot/README.md). Attackers that change address on every attempt are excluded in Section 1 |
| The machines' clocks agree closely enough to time Q1 | Assumed | Check clock synchronization status on each machine before measuring |
| The test machine can send traffic from a range of documentation addresses (such as 203.0.113.0 to 203.0.113.255) on the virtual network | Assumed | Assign several such addresses to the test machine and confirm a campus machine's SSH log shows each as the source |

**Constraints:**

- Six weeks of part-time work by one student.
- One laptop running 4 virtual machines: 3 campus machines and 1 test machine that sends the test logins and the non-member report.
- Only public or synthetic data and documentation-range test addresses; no real campus systems or user accounts.
- fail2ban is reused as the detector; no new detector is built.
- Reports are not signed in the six-week prototype; membership is checked against a fixed list of member addresses. Until signing is added in Semester II, a machine on the network that fakes a member's address could send false reports; F4 only shows that honest non-members are ignored.
- Programming language and messaging method are chosen in Assignment 3.

## 3 Alternatives and selected solution

*Draft in Assignment 2; the choice and decision records follow in Assignment 3 (due November 20).*

| Approach and source | Useful behavior | Limitation | Evidence or assumption |
|---|---|---|---|
| Local bans only (simple baseline): each campus runs fail2ban alone [8] | Nothing to build or trust beyond the campus's own detector | Every campus must detect the same attacker again | Documented: fail2ban bans addresses that cause repeated authentication errors [8]. Observed: the pilot measured this baseline (Table 3) |
| Central hub: every campus sends reports to one server, which forwards them to all members; a hub service such as CrowdSec also filters reports by consensus [7] | One detection protects every member quickly | The hub's operator must be trusted by everyone; a hub that forwards every report spreads one campus's mistake to all | Documented: CrowdSec describes central consensus and defenses against false positives [7]. Assumed: the forward-everything behavior describes the simple hub in Table 2 |
| k-of-n with no central operator: each node counts reports from different campuses and bans once k agree | No single operator; one mistaken campus cannot ban an address everywhere when k is 2 or more | Bans fewer attackers; every node must keep its own count and member list | Observed: the pilot's k = 2 result (Table 3). Assumed: the safety benefit, until C1 is tested |

Table 5. Approaches considered.

| Criterion (requirement) | Local bans only | Central hub | k-of-n, no central operator |
|---|---|---|---|
| Attacker caught at one campus is blocked at the others (F1, F2; judgment) | No | Yes, after the first report | Only after k campuses report it |
| One campus's mistaken report affects other campuses (C1; judgment) | No | Yes, if the hub forwards every report | No, when k is 2 or more |
| Local bans continue when other campuses are unreachable (C2; judgment) | Yes | Yes, but sharing stops while the hub is down | Yes; sharing continues only if at least k nodes can still reach each other |
| An operator can see which campuses caused each ban (F3; judgment) | Only the campus's own bans | The hub knows who reported; members see what it forwards | Each node keeps the reports behind its own bans |
| Reports from non-members are ignored (F4; judgment) | Not applicable: nothing is shared | The hub checks membership once for everyone | Every node checks the member list itself |
| Bans reach every node within seconds (Q1; judgment) | Not applicable: nothing is shared | Candidate: two network hops, through the hub | Candidate: one hop, but only after the k-th report |
| Who must be trusted | Nobody outside the campus | The hub operator | Any k members acting together |
| Messages for one detection, with n campuses | 0 | 1 to the hub, then n − 1 from it | n − 1 from the reporting campus |
| Fewer attempts than local bans in the pilot (all 33 nodes / 5 outside the main pool) | Baseline | 27.7–37.7% / 7.0–12.2%, inferred: a hub that forwards every report behaves like sharing with k = 1 | 9.0–19.4% / 1.3% with k = 2 |
| Prototype effort | Small: configure fail2ban | Medium: one server plus a client at each campus | Largest: each node keeps counts and a member list |

Table 6. Comparison against the requirements. The pilot row is Observed for local bans and k-of-n (Table 3); the hub figures are inferred from the k = 1 result, since no hub was run. Rows marked judgment, and the trust, message and effort rows, come from how each approach works, not from measurements. The k-of-n entries for one mistaken campus and for trust assume members cannot fake each other's addresses; without signing (Section 2, Constraints), one member could do so and reach k alone.

**Choice and reason:** Not final until Assignment 3. The comparison shows the main trade-off: the hub blocks the most attackers, while k-of-n limits the harm one campus can do. It also exposes an open question: a hub could count reports and require k campuses too, so the real difference from k-of-n may be only who does the counting and who must be trusted.

## 4 Architectural design

*Work to come in Assignment 3 (due November 20).*

## 5 Component design and interfaces

*Work to come in Assignment 3 (due November 20).*

## 6 Data structure design

*Work to come in Assignment 4 (due November 27).*

## 7 Algorithm design and execution

*Work to come in Assignment 4 (due November 27).*

## 8 Failures and security

*Work to come in Assignment 4 (due November 27).*

## 9 Implementation and feasibility

*Work to come: begin in Assignment 3, report in Assignments 5 and 6. Early evidence so far: [pilot replay](evidence/pilot/README.md).*

## 10 Testing and verification

*Work to come: plan in Assignment 4, results in Assignments 5 and 6.*

## 11 Operation maintenance and future work

*Work to come: draft in Assignment 4, complete in Assignment 6.*

## 12 Revision history and references

| Revision date | Change to my design | Reason and evidence |
|---|---|---|
| November 5, 2026 | Replaced the ransomware tripwire proposal with a distributed SSH blocklist | The instructor found the earlier idea not clearly distributed; the new direction was approved on November 5 |
| November 7, 2026 | First version of Section 1, workflow figure and pilot evidence | Assignment 1 (committed after the November 6 deadline) |
| November 9, 2026 | Corrected the wording of the claims cited to [1] and [3], one sentence of the pilot method, and the progress note length | Rechecked each source against its claim; the progress note limit is 100–150 words |
| November 11, 2026 | Narrowed the six-week contribution to one working path with one normal and one adverse case; moved signed reports, withdrawal, expiry and the honeypot replay to Semester II | Chapter 4 asks for one important operation, a small input set, a normal case and one adverse case in the six weeks |
| November 15, 2026 | Added the initial Section 2 specification (Table 4, inputs and outputs, assumptions, constraints) and the Section 3 draft comparison (Tables 5 and 6). In Section 1: redrew Figure 1 for the k = 2 normal case; removed "signed" from Figure 1, Table 2 and the exclusions; named the test machine, the supporting checks and the Q1 timing measurement in the six-week contribution; shortened the Semester II network-split bullet; stated the three thresholds in Table 3's pilot row; corrected the claim cited to [1]; cited SEPIA [9] in the exclusions; expanded abbreviations. In Section 12: corrected the outside-pool k = 2 wording and updated the next actions of the existing open questions ("revocation" became "withdrawal"); added an open question about a hub that requires k campuses; updated the assistance statement for the Section 2 and 3 drafts; aligned the wording of reference [1] with Section 1; added reference [10] and extended the access dates | Assignment 2; signing moved to Semester II on November 11 |

| Open question | Why it matters | Next action |
|---|---|---|
| Does k-of-n agreement keep enough of the benefit of sharing? | In the pilot, k = 2 kept roughly a third to a half of the k = 1 benefit on all nodes, and about a tenth to a fifth on the 5 nodes outside the main pool | Compared in Section 3 (Table 6); repeat the replay with expiry and withdrawal in Semester II |
| Would a hub that also requires k campuses give the same safety with less effort? | If so, the difference from my approach is only who does the counting and who must be trusted | Decide in Assignment 3 when choosing the approach |
| Is honeypot data a fair stand-in for campus SSH traffic? | The pilot has only attackers, so it cannot show how many legitimate users a wrong ban affects | Not resolved yet; look for public data or a synthetic model of legitimate logins before the Semester II replay |

**Assistance and reuse:**

I used an AI assistant (Claude) to help find and check sources, to write the pilot analysis scripts in [evidence/pilot](evidence/pilot/README.md), and to draft the tables, Figure 1, the Section 2 and 3 drafts and the text of this section, which I reviewed and edited. The project choice, scope and open questions are my own and were approved by the instructor. The pilot reuses the CyberLab honeynet dataset under the Creative Commons Attribution 4.0 (CC BY 4.0) license [4]. The prototype will reuse fail2ban [8] as the local detector.

### References

All sources accessed November 4–13, 2026. Pilot data: CyberLab dataset version 1.0, daily files February 10–15, 2020.

1. National Science Foundation, "CICI: TCR: Cyber Threat Triage and Investigation for Scientific Institutions via Adaptive Deployable Provenance Analysis and Agentic AI-Based Threat Intelligence," award 2613277, Arizona State University, 2026. Supports: scientific institutions face advanced cyber attacks with limited cybersecurity expertise and resources. <https://www.nsf.gov/awardsearch/show-award?AWD_ID=2613277>
2. EGI CSIRT, "Attacks on multiple HPC sites," 2020. Supports: attackers hopped between HPC sites using compromised SSH credentials. <https://csirt.egi.eu/attacks-on-multiple-hpc-sites/>
3. M. Javed and V. Paxson, "Detecting Stealthy, Distributed SSH Brute-Forcing," ACM CCS 2013. Supports: distributed SSH password guessing is real and hard to detect per source; existing detection approach. <https://www.icir.org/vern/papers/dist-ssh-det.ccs13.pdf>
4. CyberLab honeynet dataset, Zenodo record 3687527, CC BY 4.0. Data for the pilot replay. <https://zenodo.org/records/3687527>
5. NYSERNet, "Membership." Supports: CUNY is a member. <https://nysernet.org/membership>
6. CUNY HPCC, "How to Login." Page last edited January 3, 2025. Supports: users off the CSI campus log in with a password through the `chizen.csi.cuny.edu` gateway, and the HPC systems accept connections only from the CSI campus. Accessed November 4, 2026; the site was unreachable on November 5, when the archived copy of October 10, 2025 was checked instead. <https://wiki.csi.cuny.edu/cunyhpc/index.php/How_to_Login> (archived: <https://web.archive.org/web/20251010024427/https://wiki.csi.cuny.edu/cunyhpc/index.php/How_to_Login>)
7. CrowdSec, "The CrowdSec Data." Existing approach: shared blocklist with central consensus and defenses against false positives and poisoning. <https://crowdsec.net/our-data>
8. fail2ban. Existing local detector, reused in this project. <https://github.com/fail2ban/fail2ban>
9. M. Burkhart et al., "SEPIA: Privacy-Preserving Aggregation of Multi-Domain Network Events and Statistics," USENIX Security 2010. Related work on correlating events across organizations privately. <https://static.usenix.org/events/sec10/tech/full_papers/Burkhart.pdf>
10. fail2ban, `config/action.d/dummy.conf` (example action file), accessed November 13, 2026. Supports: an action's `actionban` command runs on each ban and receives the banned address as `<ip>`, which is how a node can learn of local bans. <https://github.com/fail2ban/fail2ban/blob/master/config/action.d/dummy.conf>

### Supporting media and evidence

- [assets/blocklist_workflow.png](assets/blocklist_workflow.png): Figure 1, the proposed workflow; source in [assets/blocklist_workflow.dot](assets/blocklist_workflow.dot).
- [evidence/pilot/README.md](evidence/pilot/README.md): pilot replay method, results, limits and run instructions; scripts and raw output in the same folder.

### Final document check

- [ ] Terms and examples make the project understandable to a beginner.
- [ ] All twelve sections contain project-specific content.
- [ ] Requirements connect to design and tests.
- [ ] Architecture, components, data, and algorithms agree.
- [ ] Targets and plans are separate from observations.
- [ ] Tables, images, pseudocode, references, and evidence links render correctly.
- [ ] Images have alternative text, captions, and readable labels.
- [ ] Run instructions and evidence support reproduction.
- [ ] I am prepared to present my work and orally review the same selected group mate.
- [ ] Remaining work and maintenance needs are explicit.
- [ ] Instructional placeholders are removed from the final submission.
