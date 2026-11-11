# Distributed SSH Blocklist for Research Campuses

**Author:** Hirwa Divin Iradukunda  
**Course:** CSC 59866  
**Selected project and option:** Distributed SSH blocklist across independent research campuses (motivated by NSF award 2613277)  
**Current assignment:** 1  
**Friday commit deadline:** November 6, 2026, at 11:59 p.m. New York time  
**Monday presentation:** November 9, 2026, at 6:30 p.m. New York time  
**Last updated:** November 7, 2026  
**Document status:** Proposed

## Progress note

This week I changed projects. My earlier idea, a ransomware tripwire on one machine, was not clearly distributed, so I moved to a blocklist that campuses share directly with each other, with no central operator. The instructor approved this direction on November 5 and asked me to call it a distributed blocklist rather than a replicated one, since copying the list is only one part of it.

To check that the problem is real, I replayed six days of public honeypot data. Sharing bans between sites stopped noticeably more attacker attempts than local bans alone, but requiring two or three sites to agree removed much of that gain, while a one-hour delay in sharing barely mattered. The main open issue is whether agreement keeps enough benefit to justify its safety. Next, in Assignment 2, I will write requirements and compare local bans, a central hub and k-of-n agreement.

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

For a system administrator protecting a research campus's SSH login servers, password-guessing attempts arrive all day, and scientific institutions face such attacks with limited cybersecurity expertise and resources [1]. Each campus blocks attackers with its own tools, such as fail2ban [8], so an address that one campus has already caught must start over at the next campus before it is banned there too; guessing spread across many attacking addresses is also hard to spot by looking at one address at a time [3], and attackers have moved between HPC sites using stolen SSH credentials [2]. The consequence is attacker attempts reaching servers that another campus had already stopped. Sharing bans through one central hub would fix that, but a single mistake or compromise at the hub, or at one member, could then lock researchers out at every campus at once. Requiring several campuses to agree before a ban is safer, but it bans fewer attackers. My project will investigate that trade-off by building a distributed blocklist with no central operator, in which a ban applies once k of n campuses report the same address, and by measuring how much protection it keeps compared with local bans and a central hub.

| Stakeholder | What they do today | What they need from a shared blocklist |
|---|---|---|
| Campus security or HPC system administrator (for example at CUNY's HPC center) | Runs local tools such as fail2ban on SSH login servers | Fewer attempts reaching servers, and control over which other sites' reports are trusted |
| Researchers and students who log in over SSH | Log in with a password, for example through CUNY HPCC's gateway (Documented: see Evidence) | Not to be locked out because another campus made a mistake |
| A participating campus as an organization | Decides what security data it can share | To share block decisions without giving raw logs to a single outside operator |
| Regional network or consortium (for example NYSERNet) | Connects member campuses (Documented: CUNY is a member) | A sharing scheme that does not need it to run and defend a central service (Assumed) |

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
| 09:00 | 203.0.113.7 fails 5 logins at Campus A | A bans it | A bans it and reports to hub; hub tells B and C | A bans it and sends a signed report to B and C; 1 of 2 needed reports |
| 09:20 | Same address tries Campus B | B receives the attempts until its own threshold | Already blocked at B | B receives the attempts until its own threshold, then reports; with 2 reports, A, B and C all ban it |
| 09:40 | Same address tries Campus C | C receives the attempts until its own threshold | Already blocked at C | Already blocked at C |
| 10:00 | Campus C misconfigures its detector and reports 198.51.100.20, a shared address used by many researchers | Only C blocks those users | Hub pushes the ban to everyone: users locked out at A, B and C | One report is not enough, so only C blocks them |

Table 2. The same events under three sharing approaches. Addresses use reserved documentation ranges.

![An attacker sends failed SSH logins to Campus A. A's detector bans the address and A's blocklist node sends signed reports to the nodes at Campus B and Campus C. B and C ban the address once k of n campuses have reported it, so the attacker's later attempt at Campus B is blocked.](assets/blocklist_workflow.png)

Figure 1. Proposed workflow. Each campus keeps its own detector and adds a blocklist node. Nodes exchange signed reports directly, with no central server, and each applies a ban once k of n campuses agree. Editable source: [assets/blocklist_workflow.dot](assets/blocklist_workflow.dot).

**Evidence:**

| Claim | Label | Source |
|---|---|---|
| Scientific institutions face advanced attacks with limited security expertise and resources | Documented | NSF award 2613277 abstract [1] |
| Attackers moved between HPC sites using compromised SSH credentials in 2020 | Documented | EGI CSIRT [2] |
| Distributed SSH password guessing spread over many sources is real and hard to see from one source | Documented | Javed and Paxson [3] |
| Sharing bans between honeypot nodes cut attempts reaching SSH by 27.7–37.7% at k = 1, but only 9.0–19.4% at k = 2 (all 33 nodes); on 5 nodes outside the main sensor pool, 7.0–12.2% at k = 1 and 1.3% at k = 2 | Observed | Pilot replay of CyberLab data [4]; [evidence/pilot](evidence/pilot/README.md) |
| Delaying shared bans by one hour changed the k = 1 result by at most one percentage point | Observed | Same pilot replay |
| CUNY is a NYSERNet member | Documented | NYSERNet membership page [5] |
| CUNY HPCC users off the CSI campus log in to one gateway with a password; the page does not mention MFA | Documented (page last edited January 3, 2025) | CUNY HPCC wiki [6] |
| Campuses would prefer a shared blocklist with no central operator | Assumed | Part of the illustrative use case; not studied in this project |
| Mistaken or poisoned shared bans are a real concern | Documented (vendor) | CrowdSec describes defenses against false positives and data poisoning [7] |

Table 3. Evidence for the problem. The pilot used honeypot data: attackers only, six days, one operator, and 88% of events from one sensor pool, so it cannot measure wrongly blocked users. See [evidence/pilot/README.md](evidence/pilot/README.md) for limits.

**Six-week contribution:** One working path on 3 virtual machines, one node per simulated campus: a node turns a local fail2ban ban into a report to the other nodes, and each node applies the ban once k of n campuses have reported the same address. fail2ban is reused rather than built.

- Normal case: with k = 2, an address caught at two campuses is banned at the third before it arrives there.
- Adverse case: one campus wrongly reports a shared address (the 10:00 row of Table 2); with k = 2, no other campus bans it.
- Baseline: the same inputs with local bans only.

**Semester II scope:**

- Signed reports, withdrawal of a report, and ban expiry.
- Recovery after network splits: a cut-off node keeps its local bans and ends up with the same list as the others after it reconnects.
- A central-hub baseline, so all three approaches run on the same inputs.
- A replay of public honeypot data on 3–5 nodes, with measurements of attempts stopped, how many users one bad or mistaken site can lock out, recovery time, and network and resource overhead, at different values of k.
- Ways to reduce the cost of agreement, such as per-site trust or shorter expiry, if time allows.

**Exclusions:**

- Logins with stolen but valid passwords: they can succeed on the first try, so no ban is triggered.
- Attackers that rotate to a new address for every attempt.
- Working with or deploying on CUNY, NYSERNet or any real campus network; they are an illustrative use case, and all testing uses virtual machines and replayed public data.
- Private matching of addresses (for example secure multiparty computation); reports name the address in the clear among members.
- Open membership: the set of campuses and their signing keys is fixed in advance.
- Building a new attack detector.

> **Open question:** Can k-of-n agreement keep enough of the benefit of sharing to be worth its safety, or does a simpler approach (local bans or a hub) perform as well? See Section 12.

## 2 Requirements and system specification

*Work to come in Assignment 2 (due November 13).*

## 3 Alternatives and selected solution

*Work to come: draft in Assignment 2, complete in Assignment 3 (due November 20). Planned comparison: local bans only (baseline), central hub, and k-of-n agreement with no central operator.*

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

| Open question | Why it matters | Next action |
|---|---|---|
| Does k-of-n agreement keep enough of the benefit of sharing? | In the pilot, k = 2 kept roughly a third to a half of the k = 1 benefit on all nodes, and almost none on the 5 nodes outside the main pool | Define the comparison in Assignment 2; repeat the replay with expiry and revocation |
| Is honeypot data a fair stand-in for campus SSH traffic? | The pilot has only attackers, so it cannot show how many legitimate users a wrong ban affects | Look for public data or a synthetic model of legitimate logins during Assignment 2 |

**Assistance and reuse:**

I used an AI assistant (Claude) to help find and check sources, to write the pilot analysis scripts in [evidence/pilot](evidence/pilot/README.md), and to draft the tables, Figure 1 and the text of this section, which I reviewed and edited. The project choice, scope and open questions are my own and were approved by the instructor. The pilot reuses the CyberLab honeynet dataset under the CC BY 4.0 license [4]. The prototype will reuse fail2ban [8] as the local detector.

### References

All sources accessed November 4–6, 2026. Pilot data: CyberLab dataset version 1.0, daily files February 10–15, 2020.

1. National Science Foundation, "CICI: TCR: Cyber Threat Triage and Investigation for Scientific Institutions via Adaptive Deployable Provenance Analysis and Agentic AI-Based Threat Intelligence," award 2613277, Arizona State University, 2026. Supports: scientific institutions face advanced attacks with limited security resources. <https://www.nsf.gov/awardsearch/show-award?AWD_ID=2613277>
2. EGI CSIRT, "Attacks on multiple HPC sites," 2020. Supports: attackers hopped between HPC sites using compromised SSH credentials. <https://csirt.egi.eu/attacks-on-multiple-hpc-sites/>
3. M. Javed and V. Paxson, "Detecting Stealthy, Distributed SSH Brute-Forcing," ACM CCS 2013. Supports: distributed SSH password guessing is real and hard to detect per source; existing detection approach. <https://www.icir.org/vern/papers/dist-ssh-det.ccs13.pdf>
4. CyberLab honeynet dataset, Zenodo record 3687527, CC BY 4.0. Data for the pilot replay. <https://zenodo.org/records/3687527>
5. NYSERNet, "Membership." Supports: CUNY is a member. <https://nysernet.org/membership>
6. CUNY HPCC, "How to Login." Page last edited January 3, 2025. Supports: users off the CSI campus log in with a password through the `chizen.csi.cuny.edu` gateway, and the HPC systems accept connections only from the CSI campus. Accessed November 4, 2026; the site was unreachable on November 5, when the archived copy of October 10, 2025 was checked instead. <https://wiki.csi.cuny.edu/cunyhpc/index.php/How_to_Login> (archived: <https://web.archive.org/web/20251010024427/https://wiki.csi.cuny.edu/cunyhpc/index.php/How_to_Login>)
7. CrowdSec, "The CrowdSec Data." Existing approach: shared blocklist with central consensus and defenses against false positives and poisoning. <https://crowdsec.net/our-data>
8. fail2ban. Existing local detector, reused in this project. <https://github.com/fail2ban/fail2ban>
9. M. Burkhart et al., "SEPIA: Privacy-Preserving Aggregation of Multi-Domain Network Events and Statistics," USENIX Security 2010. Related work on correlating events across organizations privately. <https://static.usenix.org/events/sec10/tech/full_papers/Burkhart.pdf>

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
