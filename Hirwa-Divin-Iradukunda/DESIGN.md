# Distributed SSH Blocklist for Research Campuses

**Author:** Hirwa Divin Iradukunda  
**Course:** CSC 59866  
**Selected project and option:** Distributed SSH blocklist across independent research campuses (motivated by National Science Foundation (NSF) award 2613277)  
**Current assignment:** 3  
**Commit deadline:** November 22, 2026, at 11:59 p.m. New York time  
**Monday presentation:** November 23, 2026, at 6:30 p.m. New York time  
**Last updated:** November 21, 2026  
**Document status:** Proposed

## Progress note

> - **What changed:** Selected a k-of-n approach with no central operator (Section 3, two decision records), drafted the architecture (Figures 2 and 3), specified the `receive_report` contract (Section 5), and added the feasibility experiment and minimal path (Section 9). Moved report expiry (F5) back into the six-week build following Assignment 1 feedback on report currency and lost agreement. Incorporated Assignment 2 feedback by adding a k=2 hub comparison (Table 6), separating local detections from shared bans, and defining a 100-millisecond clock tolerance.
> - **What I learned:** From the feasibility experiment ([evidence/feasibility](evidence/feasibility/README.md)), fail2ban counts matching log lines rather than login attempts (banning after three failed logins) and runs its hook when local bans end.
> - **Main open issue:** Whether 24 hours is a sensible report lifetime and whether to prototype in containers instead of virtual machines.
> - **Next step:** Define the report records, counting algorithm, and failure behavior in Assignment 4.

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

**Six-week contribution:** One working path on 3 campus virtual machines, one node per simulated campus, plus 1 test machine that plays the attacker: a node turns a local fail2ban ban into a report to the other nodes, each node applies the ban once k of n campuses have current reports for the same address, and it lifts the ban when fewer than k current reports remain because reports expire. fail2ban is reused rather than built.

- Normal case: with k = 2, an address caught at two campuses is banned at the third before it arrives there.
- Adverse case: one campus wrongly reports a shared address (the 10:00 row of Table 2); with k = 2, no other campus bans it.
- Expiry case: each report counts for a fixed lifetime (24 hours, provisional); when a report expires and fewer than k current reports remain, every node lifts the shared ban (F5 in Section 2).
- Baseline: the same inputs with local bans only.
- Supporting checks: an operator can list each shared ban with the campuses behind it (F3 in Section 2), reports from non-members are ignored (F4), and local bans keep working when other nodes are unreachable (C2 in Section 2).
- One timing measurement for the proposed quality target (Q1 in Section 2).

**Semester II scope:**

- Signed reports and withdrawal of a report.
- Recovery after network splits: a cut-off node ends up with the same shared list as the others after it reconnects.
- A central-hub baseline, so all three approaches run on the same inputs.
- A replay of public honeypot data on 3–5 nodes, with measurements of attempts stopped, how many legitimate users one bad or mistaken site can lock out (using synthetic legitimate logins from the shared address in Table 2, kept separate from the attack-only results), the time until a wrongly banned address can log in again, and network and resource overhead, at different values of k.
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

This section specifies the six-week working path from Section 1. A **campus** is one participant; in the prototype each campus is one virtual machine running SSH (Secure Shell, the remote login service), fail2ban and a blocklist **node**. **n** is the number of member campuses (3 in the prototype) and **k** is how many different campuses must report an address before every node bans it (k = 2 unless stated). A **report** says "campus X banned address Y at time T"; it is **current** for a fixed lifetime after T, the expiry interval (24 hours unless stated; see F5). A **ban** means the campus refuses SSH connections from that address. There are two kinds of ban. A **local ban** is a detection: fail2ban's own `sshd` jail at that campus caught the address. A **shared ban** is enforcement: a node installed it because it holds reports from k campuses. Only local bans become reports and count toward k. A shared ban is never reported, so it can never be counted as another independent detection. In the C1 and Q1 checks, a test command at a node stands in for that campus's local ban.

| ID | Required behavior and conditions | Acceptance check | Design and test reference |
|---|---|---|---|
| F1 | When fail2ban on a campus bans an address, that campus's node sends a report to every other member node | Make failed logins from a test address at Campus A until fail2ban bans it; check that the nodes at B and C each record a report from A for that address | Planned; ban hook and report sender in Table 7, steps 1–2 of the Section 4 trace |
| F2 | When a node holds current reports for the same address from at least k different campuses, counting its own campus's local ban as one of them, it bans that address | With k = 2, cause bans at A and then B; check that C refuses an SSH connection from the address before the address has tried C, and that A and B receive no report from C for it | Planned; `receive_report` in Section 5 (`banned` outcome, example 1) |
| F3 | An operator can list the shared bans a node has applied, with the campuses whose reports caused each one | After the F2 check, the list on C shows the address with A and B | Planned; list command in Table 7 |
| F4 | A node ignores reports from senders that are not configured members, and records that it ignored them | Send a report from the test machine, which is not a member; check that no node counts it and that each node's log shows it was ignored | Planned; `not_member` outcome in Table 8, example 3 |
| F5 | When fewer than k campuses hold current reports for an address, every node that applied a shared ban for it lifts that ban; a node's own fail2ban bans are not affected | With the report lifetime set to 60 seconds for the test and k = 2, cause bans at A and, 20 seconds later, at B; check that C bans the address, that C lifts the ban within 5 seconds after A's report expires (60 seconds after it was made), and that the test machine reaches C's SSH password check again, while A's and B's own local bans for the address remain | Planned; expiry timer in Table 7, example 4 in Section 5 |
| C1 | With k of 2 or more, no node bans an address because of reports from fewer than k different campuses; repeated reports from one campus count once, and only local bans are reported | Use a test command at C's node to send the same report for 198.51.100.20 three times; check that A and B do not ban it (adverse case in Section 1) | Planned; `duplicate` outcome in Table 8, example 2 |
| C2 | Losing contact with other nodes never removes a campus's own fail2ban bans or stops it from adding new ones | Stop the nodes at B and C; check that A's existing bans remain, then make failed logins from a test address at A and check that fail2ban at A bans it | Planned; hook time limit in Decision 2, step 5 of the Section 9 path |
| Q1 | Proposed target, not measured: at least 95 of 100 test addresses reported by k campuses are banned at every running node within 5 seconds after the k-th report is sent, with one new address every 2 seconds, its k reports sent by a test command at k campus nodes (each sending node counts its test report as its own campus's report), on the 3 campus virtual machines in one local virtual network | Record when each k-th report is sent and when each node adds the ban. Before and after the run, record each machine's clock offset (the "System time" line of `chronyc tracking`). Two machines can differ by the sum of their offsets, so an address banned within 5 seconds plus or minus the sum of the two largest recorded offsets is uncertain. Uncertain addresses are measured once more; any still uncertain count as misses, so clock error cannot make the target pass. An address never banned counts as a miss | Target only; measured in Assignment 5 |

Table 4. Initial requirements. F = functional requirement, C = correctness rule, Q = quality target. No requirement has passed yet; every check is a planned procedure.

C1 alone could be met by a node that never bans anything, so F2 is needed to show useful progress. Together they set the six-week targets for wrong and missed bans: no shared ban caused by one campus's reports (C1), and no more than 5 of 100 addresses reported by k campuses left unbanned or late (Q1). How many legitimate logins a mistaken ban blocks needs synthetic legitimate traffic and is measured in Semester II. fail2ban counts matching log lines rather than login attempts (Section 9), so the checks say "until fail2ban bans it" instead of giving a number of logins. The 5-second value in Q1 is a provisional choice: in the pilot, delaying shared bans by a whole hour changed the result by at most one percentage point (Table 3, measured at k = 1 only), so a few seconds leaves a wide margin. The target mainly checks that the prototype's sharing works promptly and reliably; it may be revised after the first measurement. The 24-hour report lifetime in F5 is also provisional and a judgment: it matches the longest window among the pilot's thresholds (10 or 30 failures per 24 hours), so a report keeps counting while an attacker moves between campuses, and a mistaken report stops counting within a day. The Semester II replay will compare other lifetimes.

**Inputs and outputs:**

| Case | Input | Expected output |
|---|---|---|
| Ordinary (normal case) | k = 2, n = 3. 09:00: fail2ban at A bans 203.0.113.7. 09:20: fail2ban at B bans the same address | After B's report, C bans 203.0.113.7; C's list shows it with reports from A and B; an SSH attempt from it at C is refused |
| Unsuccessful (adverse case) | k = 2, n = 3. C's detector is misconfigured and C reports 198.51.100.20, a shared address, three times | A and B record one report from C, which is fewer than 2, and do not ban; researchers using that address can still log in at A and B |
| Ordinary (report expiry) | Continuing the ordinary case with a 24-hour lifetime: at 09:00 the next day, A's report expires | Each node now holds one current report (B's), fewer than 2, so A, B and C lift their shared bans for 203.0.113.7; fail2ban's own local bans are unaffected |
| Unsuccessful (non-member) | A fourth virtual machine, not in the member list, reports 203.0.113.99 | No node counts the report; each node logs that it ignored a report from a non-member |

All addresses come from ranges reserved for documentation, so no real host is involved.

**Assumptions:**

| Assumption | Label | How to check |
|---|---|---|
| fail2ban can run a custom command each time it bans an address, receiving that address | Documented [10]; Observed in the feasibility experiment (Section 9) | Checked in a container on November 17; repeat on the campus virtual machines |
| The three campus machines and the test machine can reach each other over the local virtual network | Assumed | Connect from each machine to the others' SSH and node ports before building further |
| An attacker uses the same address at every campus during an attack | Assumed (the pilot made the same assumption about pseudonymized addresses) | Accepted without a direct check. Consistent with the pilot: at a 5-per-hour threshold, 4,439 of 6,316 detected attacking addresses were seen at two or more nodes [evidence/pilot](evidence/pilot/README.md). Attackers that change address on every attempt are excluded in Section 1 |
| Each machine's clock is within 100 milliseconds of a common time source (kept by chrony, a standard clock-synchronization service) (provisional tolerance), so any two machines differ by at most 200 milliseconds, close enough to time Q1 and the F5 check and to expire reports | Assumed | Each virtual machine synchronizes its clock with chrony from the same source; record each machine's offset with `chronyc tracking` before and after every timing check, and repeat the check if any offset is over 100 milliseconds |
| The test machine can send traffic from a range of documentation addresses (such as 203.0.113.0 to 203.0.113.255) on the virtual network | Assumed | Assign several such addresses to the test machine and confirm a campus machine's SSH log shows each as the source |

**Constraints:**

- Six weeks of part-time work by one student.
- One laptop running 4 virtual machines: 3 campus machines and 1 test machine that sends the test logins and the non-member report.
- Only public or synthetic data and documentation-range test addresses; no real campus systems or user accounts.
- fail2ban is reused as the detector; no new detector is built.
- Reports are not signed in the six-week prototype; membership is checked against a fixed list of member addresses. Until signing is added in Semester II, a machine on the network that fakes a member's address could send false reports; F4 only shows that honest non-members are ignored.
- The node is written in Python 3 using only its standard library, and nodes send reports to each other as JSON (JavaScript Object Notation, a plain-text data format) over HTTP (Hypertext Transfer Protocol, the protocol web servers use) (Section 4). A compiled language such as Go is a possible later improvement.

## 3 Alternatives and selected solution

| Approach and source | Useful behavior | Limitation | Evidence or assumption |
|---|---|---|---|
| Local bans only (simple baseline): each campus runs fail2ban alone [8] | Nothing to build or trust beyond the campus's own detector | Every campus must detect the same attacker again | Documented: fail2ban bans addresses that cause repeated authentication errors [8]. Observed: the pilot measured this baseline (Table 3) |
| Central hub: every campus sends reports to one server, which forwards them to all members; a hub service such as CrowdSec also filters reports by consensus [7] | One detection protects every member quickly | The hub's operator must be trusted by everyone; a hub that forwards every report spreads one campus's mistake to all | Documented: CrowdSec describes central consensus and defenses against false positives [7]. Assumed: the forward-everything behavior describes the simple hub in Table 2. A hub can instead apply the same k-of-n rule; Table 6 compares both hubs |
| k-of-n with no central operator: each node counts reports from different campuses and bans once k agree | No single operator; one mistaken campus cannot ban an address everywhere when k is 2 or more | Bans fewer attackers; every node must keep its own count and member list | Observed: the pilot's k = 2 result (Table 3). Assumed: the safety benefit, until C1 is tested |

Table 5. Approaches considered.

| Criterion (requirement) | Local bans only | Hub forwarding every report | Hub requiring k = 2 | k-of-n, no central operator (k = 2) |
|---|---|---|---|---|
| Attacker caught at one campus is blocked at the others (F1, F2; judgment) | No | Yes, after the first report | Only after k campuses report it | Only after k campuses report it |
| One campus's mistaken report affects other campuses (C1; judgment) | No | Yes | No, if the hub operator follows the rule | No |
| Local bans continue when other campuses are unreachable (C2; judgment) | Yes | Yes | Yes | Yes |
| If the party that decides shared bans fails (judgment) | Not applicable: nothing is shared | The hub is that party: all sharing stops | The hub is that party: all sharing stops | Each node decides for itself: sharing continues among any k nodes that can still reach each other |
| An operator can see which campuses caused each ban (F3; judgment) | Only the campus's own bans | The hub knows who reported; members see what it forwards | The hub knows who reported; members see only its decision unless it sends the reports too | Each node keeps the reports behind its own bans |
| A shared ban ends when agreement disappears (F5; judgment) | Not applicable: nothing is shared | The hub must track and expire reports for every member | The hub must track and expire reports for every member | Each node expires its own reports and lifts its shared ban when fewer than k remain |
| Reports from non-members are ignored (F4; judgment) | Not applicable: nothing is shared | The hub checks membership once for everyone | The hub checks membership once for everyone | Every node checks the member list itself |
| Bans reach every node within seconds (Q1; judgment) | Not applicable: nothing is shared | Candidate: two network hops, through the hub | Candidate: two network hops, after the k-th report | Candidate: one hop, after the k-th report |
| Who must be trusted | Nobody outside the campus | The hub operator | The hub operator, who alone could ban an address at every campus | Any k members acting together |
| Messages for one detection, with n campuses | 0 | 1 to the hub, then n − 1 from it | 1 to the hub; once k campuses have reported, one ban message to each member, and a lift message to each when fewer than k remain | n − 1 from the reporting campus |
| Fewer attempts than local bans in the pilot (all 33 nodes / 5 outside the main pool) | Baseline | 27.7–37.7% / 7.0–12.2%, inferred from k = 1 | 9.0–19.4% / 1.3%, inferred from k = 2 | 9.0–19.4% / 1.3% |
| Prototype effort | Small: configure fail2ban | Medium: one server plus a client at each campus | Medium: one server that counts and expires reports, plus a client at each campus | Largest: each node keeps counts, expiry and a member list |
| Setup for a new campus (judgment) | Install fail2ban | Someone must host and run the hub; each campus installs a client and trusts the hub | Same as the other hub | Each campus installs a node, lists all n − 1 other members, and opens its node port to them; every existing member adds the new campus |

Table 6. Comparison against the requirements, all on the same inputs (the cases of Section 2), except the pilot row, which uses the pilot replay. The pilot row is Observed for local bans and k-of-n (Table 3); no hub was run, so the hub figures are inferred: a hub that forwards every report behaves like sharing with k = 1, and a hub requiring k = 2 applies the same rule to the same reports as k-of-n with k = 2. Rows marked judgment, and the trust, message and effort rows, come from how each approach works, not from measurements. The entries for one mistaken campus and for trust in both k = 2 columns assume members cannot fake each other's addresses; without signing (Section 2, Constraints), one member could do so and reach k alone.

The two k = 2 columns separate the agreement rule from where it is calculated. With the same rule, a hub and every node give the same protection and the same C1 result; they differ in who must be trusted, what happens when the deciding party fails, the path of each message, and effort.

**Choice and reason:** k-of-n agreement with no central operator, built as a small node beside fail2ban at each campus. It is the only approach in Table 6 that shares bans (F1, F2) and keeps one mistaken campus from banning an address everywhere (C1) without a single operator that every campus must trust, and sharing continues among any k nodes that can still reach each other. Its costs are that it blocks fewer attackers than sharing every report (pilot: 9.0–19.4% against 27.7–37.7% fewer attempts) and that every node keeps its own count and member list. Local bans only remain the baseline in the evaluation.

### Decision 1: Agreement at every node, with no central operator

**Context and requirement:** A hub could also count reports and require k campuses (Section 12). Table 6 compares that hub with k-of-n on the same inputs and the same k = 2 rule: both meet C1, and the hub needs less work, so the choice must rest on trust and failure behavior rather than on C1.  
**Options:** (1) local bans only; (2) a hub that forwards every report; (3) a hub that counts reports and bans once k campuses agree; (4) k-of-n counting at every node, with no central operator.  
**Decision and reason:** Option 4. Option 1 shares nothing (F1, F2) and option 2 spreads one campus's mistake to everyone (C1). Option 3 stops one mistaken campus, but its operator alone could still ban an address at every campus, and while the hub is down no campus shares anything. Option 4 removes that single trusted party, which is the question this project investigates, and sharing continues while any k nodes can reach each other.  
**Consequences:** Every node must count reports, keep the member list and expire reports itself, so the prototype is larger than a hub client (Table 6, effort row). It bans fewer attackers than sharing every report (Table 3). Until reports are signed, a member that fakes other members' addresses could still reach k alone (Section 2, Constraints).  
**Status and revisit condition:** Accepted for the prototype. Revisit if the prototype cannot meet C1 or Q1, if Semester II measurements show k-of-n keeps too little of the benefit, or if member campuses would accept one trusted operator; option 3 would then be the simpler choice.

### Decision 2: Connect to fail2ban with an action hook and a separate shared jail

**Context and requirement:** F1 needs each local ban to reach the node with its address. F2 and F5 need the node to add and remove shared bans that block SSH. A shared ban must not be reported again, or nodes would keep re-reporting each other's bans.  
**Options:** (1) the node reads fail2ban's log file to notice bans and adds its own firewall rules; (2) a fail2ban action runs a small hook on each local ban, and the node applies shared bans through a second fail2ban jail that has no hook; (3) replace fail2ban's banning with the node's own detector and firewall rules.  
**Decision and reason:** Option 2. The action hook is fail2ban's documented way to run a command on each ban [10], and `banip` and `unbanip` are fail2ban client commands [11]. The feasibility experiment (Section 9) showed that the hook receives the banned address, that a ban in the separate `shared` jail blocks SSH without calling the hook, and that a shared ban can be lifted by command, as the node will do. Option 1 depends on log formats and duplicates firewall handling; option 3 builds a new detector, which Section 1 excludes.  
**Consequences:** Each campus runs two jails: `sshd` for local bans and `shared` for shared bans, in separate firewall chains, so ending one kind of ban does not remove the other (F5; plausible from the separate chains, not yet tested for the same address). Both jails will use an SSH-only firewall rule (port 22), so a ban never blocks reports between nodes on the node port; the experiment used fail2ban's all-ports rule, which would have. Shared bans never end on their own (ban time −1, which fail2ban treats as permanent [12]); the node lifts them when reports expire (F5). The hook also runs when a local ban ends, so the node must ignore those calls. The hook will wait at most 2 seconds for the node and always exit successfully, so a stopped node never delays fail2ban's own bans (C2); the experiment's stand-in hook only recorded its calls, so this is not yet tested. The node depends on fail2ban's client commands; these commands were tested with fail2ban 1.0.2.  
**Status and revisit condition:** Accepted; checked in one container experiment. Revisit if the same steps fail on the campus virtual machines or if a later fail2ban version changes how actions or jails behave.

## 4 Architectural design

**Boundary and outside participants:**

![System context. An attacker sends failed SSH logins, a researcher sends ordinary SSH logins that must not be wrongly refused, a campus operator sets the member list, k and the report lifetime and lists shared bans, and a non-member sender's reports are ignored and logged. All of them interact with the distributed SSH blocklist: member campuses A, B and C, each running an SSH server, fail2ban and a blocklist node, with nodes exchanging reports directly.](assets/context.png)

Figure 2. System context. The project builds the blocklist node and configures fail2ban at each member campus; the SSH server, fail2ban and the firewall are reused. In the prototype, one test machine plays both the attacker and the non-member sender. Editable source: [assets/context.dot](assets/context.dot).

**Main parts and messages:**

![Main running parts at Campus C. Inside C's virtual machine, the SSH server writes the authentication log; fail2ban reads it and adds or removes firewall rules in two chains, f2b-sshd for local bans and f2b-shared for shared bans, and those rules refuse banned addresses. On a local ban, fail2ban gives the address to the ban hook, which sends it to the node's report receiver as a local-ban request. The node's report sender sends reports as JSON over HTTP to the nodes at Campuses A and B, and its report receiver accepts their reports after checking the member list and passes valid reports and local bans to the decision logic. The decision logic saves and reads reports in the report store, counts current reports, runs the expiry timer, and tells the ban applier to ban or lift an address in fail2ban's shared jail. An operator's list command reads the report store.](assets/architecture.png)

Figure 3. Main running parts at one campus (C); A and B run the same parts. Solid arrows are calls or messages; the dashed arrow is the firewall's effect on SSH; the dotted line shows that the receiver checks senders against the member list. The expiry timer is drawn inside the decision logic but is listed as its own component in Table 7. Editable source: [assets/architecture.dot](assets/architecture.dot).

One request through the parts, in the normal case of Section 2:

1. Failed logins from 203.0.113.7 at A are written to A's authentication log; fail2ban's `sshd` jail bans the address and runs the ban hook with it.
2. The hook sends the address to A's report receiver (`POST /local-ban`), and the decision logic records a report from A's own campus; the report sender sends it to the nodes at B and C.
3. C's report receiver checks that the sender is a member; the decision logic saves the report and counts current reports for the address: 1 of 2.
4. When B's report arrives, the count reaches 2. The ban applier runs `fail2ban-client set shared banip 203.0.113.7`, fail2ban adds a rule to the `f2b-shared` chain, and C refuses SSH connections from the address.
5. The expiry timer rechecks stored reports every second. When fewer than 2 are current, the ban applier runs `unbanip` and the rule is removed.

Reports go directly from the reporting node to every other member, n − 1 messages per local ban, so no relay or broker becomes a central point. The shared ban in step 4 is enforcement, not a new detection: the `shared` jail has no hook (finding 2 in [evidence/feasibility](evidence/feasibility/README.md)), so C never reports it and it never counts toward k at any node.

**Saved state:**

- Report store (one file per node): for each address, the campuses with a report and each report's ban time. It is the node's own authority for its shared-ban decisions; nodes never share a store.
- fail2ban's state: local and shared bans and their firewall rules.
- Member list and settings (one file per node, written by the operator): member campus names and network addresses, k, the report lifetime and the node's port.

Keeping the report store and fail2ban's shared bans consistent after a restart is left to Assignment 4.

**Where parts run:**

| Machine | Runs | Note |
|---|---|---|
| Campus A, B and C virtual machines | SSH server, fail2ban with two jails, ban hook, blocklist node, report store, member list | One per simulated campus; n = 3 |
| Test machine (fourth virtual machine) | SSH client for failed and legitimate logins; a script that sends test reports | Not a member; plays the attacker and the non-member sender |
| One laptop | All four virtual machines on one local virtual network | Shared dependency: if the laptop or the virtual network fails, every campus fails together, which separate real campuses would not |

**What I build reuse or simulate:**

| Part | Build, reuse or simulate | Note |
|---|---|---|
| Blocklist node: receiver, decision logic, expiry timer, sender, ban applier, list command | Build | Python 3, standard library only |
| Ban hook and fail2ban configuration (two jails, one action file) | Build (configuration) | Configuration tested in the feasibility experiment (Section 9) with the all-ports rule (the SSH-only rule is untested); the hook only as a stand-in that records its calls |
| fail2ban, SSH server, firewall | Reuse | fail2ban 1.0.2 and OpenSSH on Debian 12 in the experiment |
| Campuses and their network | Simulate | Virtual machines on one laptop |
| Attackers and legitimate users | Simulate | Test machine with documentation-range addresses |
| Signed reports, withdrawal, recovery after network splits | Deferred | Semester II |

Python was chosen for correctness and simplicity over speed: a node handles one small message per ban, fail2ban itself is written in Python, and the standard library already includes an HTTP server and client and JSON parsing, so the prototype needs no extra packages.

## 5 Component design and interfaces

| Component | Responsibility | Input | Output or state change |
|---|---|---|---|
| Ban hook | Tell the local node about each local fail2ban ban | Run by fail2ban's `sshd` jail only, as `ban <address> sshd`; `unban` calls are ignored; the `shared` jail never runs it | One request to the node on the same machine with the address (F1) |
| Report receiver | Accept reports from other nodes and local-ban requests from the ban hook; turn away non-members and malformed reports | `POST /report` with a report and the sender's network address; `POST /local-ban` from 127.0.0.1 only | A valid report passed to the decision logic, or a defined error outcome (F4) |
| Decision logic | Keep at most one report per campus per address, count current reports, decide when to ban or lift | Reports from its own campus and from others; the clock | Updated report store; ban or lift requests (F2, C1, F5) |
| Expiry timer | Every second, drop reports past their lifetime and recheck every address | The report store | Lift requests when fewer than k current reports remain; retries of bans that failed (F5) |
| Report sender | Send its own campus's reports to every other member | Its own campus's report, from the decision logic | One `POST /report` per member, repeated a bounded number of times if unanswered (F1) |
| Ban applier | Add or remove shared bans through fail2ban | An address and "ban" or "lift" | `fail2ban-client set shared banip` or `unbanip` (F2, F5) |
| Report store | Keep reports so a restart does not forget them | Saves from the decision logic | A file on disk (format in Assignment 4) |
| List command | Show shared bans with the campuses whose reports caused them | The report store | A table for the operator (F3) |

Table 7. Components of one node. A, B and C run identical nodes.

**Critical operation:** `receive_report`. A node accepts a report from another member and, if that report brings the number of campuses with current reports to k, applies a shared ban. It carries F2, F4, C1, the `expired` part of F5 (the expiry timer carries the rest) and the k-th report timed in Q1.

**Input:**

- Caller: another member's node, sending `POST /report` (an HTTP request that carries data to the given path) to the node's port (8470 in the prototype).
- Caller identity: the sender's network address, which must be listed in the member list for the campus named in the report. This is not authenticated until reports are signed (Semester II; see below).
- Fields, as JSON:
  - `campus`: text, the name of a member campus, for example `"A"`.
  - `address`: text, an Internet Protocol version 4 (IPv4) address in dotted form, for example `"203.0.113.7"`.
  - `banned_at`: text, the time of the local ban in Coordinated Universal Time (UTC), in the international standard date-and-time format (ISO 8601), for example `"2026-11-20T09:00:00Z"`.
- Example, sent from A's address: `{"campus": "A", "address": "203.0.113.7", "banned_at": "2026-11-20T09:00:00Z"}`
- Origin: every report describes a local ban by the named campus. Nodes never forward reports they receive and never report their own shared bans, and the receiver checks that the named campus matches the sender's address, so a node cannot pass on another campus's report. The prototype therefore needs no origin field: only one kind of report exists.

**Output:** an HTTP status and a JSON body such as `{"outcome": "counted", "current_reports": 1, "k": 2}`.

| Outcome | HTTP status | Meaning | State change | Sender's action |
|---|---|---|---|---|
| `counted` | 200 | New current report from this campus; still fewer than k | Report saved | None |
| `banned` | 200 | Counted, and campuses with current reports reached k | Report saved; shared ban applied | None |
| `already_banned` | 200 | Counted, but the address already has a shared ban here (for example a third campus reports it) | Report saved; ban unchanged | None |
| `duplicate` | 200 | This campus already has a current report for the address | Ban time updated if the new one is later; count unchanged (C1) | None; repeating a report is safe |
| `expired` | 200 | The ban time is older than the report lifetime | None; logged | None; do not repeat |
| `not_member` | 403 | The sender's address is not in the member list or does not match the named campus | None; logged (F4) | Operator checks the member list |
| `invalid` | 400 | Missing field, malformed address or time, a ban time more than 60 seconds in the future, or an address that belongs to a member node | None; logged | Fix the sender; do not repeat unchanged |
| `unavailable` | 503 | Report saved, but fail2ban did not apply the ban | Report saved; the next expiry-timer pass retries the ban | None |
| No response | none | The sender cannot tell whether the report was saved | Unknown to the sender | Repeat the same report up to 3 times, 2 seconds apart (provisional); duplicates count once. If the receiver stays unreachable longer, the report is lost; recovery after network splits is Semester II work |

Table 8. Outcomes of `receive_report`.

**Errors:** described in Table 8. A node never bans an address that belongs to a member node, so a mistaken report cannot cut members off from each other.

**Examples:** k = 2 and a 24-hour lifetime, using the cases in Section 2.

1. Ordinary, at C: A's report for 203.0.113.7 with `banned_at` 09:00 returns `counted` (1 of 2). B's report with `banned_at` 09:20 returns `banned` (2 of 2), and C runs `fail2ban-client set shared banip 203.0.113.7`.
2. Repeated, at A (the adverse case): C's report for 198.51.100.20 returns `counted` (1 of 2). The same report twice more returns `duplicate`, still 1 of 2, so A does not ban the address (C1).
3. Non-member: a report from the test machine naming campus `"A"` returns `not_member`; nothing is saved (F4).
4. Expiry: at 09:00 the next day, C's expiry timer finds A's report no longer current; only B's is (1 of 2), so C runs `unbanip` for 203.0.113.7 (F5). A report arriving with a `banned_at` more than 24 hours old returns `expired`.

**Repeated or overlapping calls:**

- Repeats are safe: a node keeps one report per campus per address, so a sender can repeat a report after no response without changing the count (C1).
- Overlapping calls are handled one at a time. The receiver, the ban hook's local requests and the expiry timer all change the report store under one lock, so two reports arriving together cannot both see "1 of 2" and miss the ban, and a ban and a lift for the same address cannot interleave.
- A local ban is counted by the same step as a received report. The ban hook sends `POST /local-ban` with `{"address": "203.0.113.7"}` to the node at 127.0.0.1; the node accepts it only from its own machine, uses its own campus name, and sets `banned_at` to the time it receives the request.
- Withdrawal is not part of the prototype: if an operator lifts a mistaken local ban, the campus's report keeps counting until it expires (24 hours). Withdrawing a report is built in Semester II.

**Still being worked out (Assignment 4):** the order of checks when several outcomes could apply (for example a malformed report from a non-member); the reply to `POST /local-ban` and whether a second local ban within the lifetime is sent again; Internet Protocol version 6 (IPv6) addresses; the report store's format and when it is saved; what a node does after a restart if fail2ban's shared bans and its store disagree; how much clock difference to allow between real campuses, since expiry uses the sender's `banned_at` (the prototype assumes 100 milliseconds, Section 2); whether the provisional retry values hold; and the log format.

**Signed reports (outline; built in Semester II):** each campus would sign all three report fields (`campus`, `address` and `banned_at`) with its own private key, so no one without that key can forge a report or extend its expiry interval, and every node would check the signature against that campus's public key in the member list. A report whose signature fails would be treated like `not_member`. Until then, membership rests on network addresses only (Section 2, Constraints).

## 6 Data structure design

*Work to come in Assignment 4 (due November 27).*

## 7 Algorithm design and execution

*Work to come in Assignment 4 (due November 27).*

## 8 Failures and security

*Work to come in Assignment 4 (due November 27).*

## 9 Implementation and feasibility

**Minimal path:** the normal case of Section 2: failed logins at A and B lead to a shared ban at C, and expiry later lifts it. Build order, keeping a working command at each step:

1. One campus virtual machine: fail2ban's hook gives the node each local ban, and the node logs it.
2. Two campus virtual machines: the node sends its report, and the other node's receiver saves it.
3. Three campus virtual machines: counting and the shared ban at k = 2 (F2), with repeated reports counted once (C1).
4. Report lifetime and expiry (F5), tested with a short lifetime.
5. Member check from the test machine (F4), the list command (F3), and local bans with the other nodes stopped (C2).
6. One automated check of the normal case and the Q1 timing measurement (Assignment 5).

**Feasibility experiment:**

- Question: Can a node learn of each local fail2ban ban with its address, and apply a shared ban through fail2ban that blocks SSH without being reported again? Can the node end a shared ban itself, as expiry requires? Every requirement in Section 2 depends on this.
- Procedure: two Docker containers on one laptop, standing in for virtual machines (Debian 12, fail2ban 1.0.2). The `campus` container ran SSH and fail2ban with the two jails of Decision 2 and a stand-in hook that only records its calls; the `attacker` container made failed SSH logins. A script made 7 login attempts in its first two steps (fail2ban banned the attacker during the third), shared-banned a documentation address, removed the local ban, shared-banned the attacker, then lifted that shared ban, checking the hook's record or SSH access at each step. Details: [evidence/feasibility](evidence/feasibility/README.md).
- Evidence: [output.txt](evidence/feasibility/output.txt), from the second run on November 17, 2026, which also printed the SSH and fail2ban logs; the first run's transcript was overwritten.
- Finding: Yes to all three questions. The hook received `ban ip=172.18.0.3 jail=sshd`; shared bans never called the hook; the attacker got `Connection refused` while only the shared ban applied and reached the password check again after it was lifted. Among the unexpected results, two shaped the design. fail2ban counts matching log lines, not login attempts: each failed login wrote 3 or 4 lines to the SSH log, about 2 of which matched fail2ban's filter, so its threshold of 5 was reached within 3 failed logins. The hook also runs when a local ban ends.
- Design consequence: Decision 2 is accepted. The node ignores `unban` calls, because reports end by expiring (F5). The F1 and C2 checks now say "until fail2ban bans it" (Section 2).
- Limits: one run of each step, in containers rather than virtual machines, with fail2ban's all-ports firewall rule rather than the SSH-only rule planned in Decision 2, with one attacker and a user name that does not exist; timing was not measured.

**Current implementation:**

| Status | What |
|---|---|
| Implemented and tested | fail2ban configuration (two jails and the hook action), in containers only and with the all-ports rule (the planned SSH-only rule is untested); the hook is a stand-in that records its calls |
| Reused | fail2ban 1.0.2, OpenSSH server and iptables on Debian 12 |
| Simulated | Campuses and the attacker as containers in the experiment |
| Planned | The blocklist node (Sections 4 and 5), built on the minimal path above for Assignment 5 |
| Blocked | Nothing at present |
| Deferred | Signed reports, withdrawal, recovery after network splits, and the replay with synthetic legitimate logins (Semester II) |

**Run instructions and CI:** The experiment runs with [evidence/feasibility/run.sh](evidence/feasibility/run.sh); its README lists what it needs. Run instructions for the node and a recorded continuous integration (CI) check come with the working path in Assignment 5.

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
| November 17, 2026 | Chose k-of-n with no central operator and wrote two decision records (Section 3); added the F5 row to Table 6. Added F5 (report lifetime and expiry, 24 hours, provisional), the definition of a current report and the expiry case to Section 2; reworded the F1 and C2 checks; updated the fail2ban and clock assumptions; set the language and messaging method in the constraints. First Section 4 architecture (Figures 2 and 3) and Section 5 components and `receive_report` contract. Began Section 9 with the minimal path and the feasibility experiment ([evidence/feasibility](evidence/feasibility/README.md)). In Section 1: added expiry to the six-week contribution, removed it from Semester II, and added synthetic legitimate logins to the Semester II replay. In Section 12: updated the open questions, the assistance statement, the supporting media and the access dates; added references [11] and [12] | Assignment 3; the Assignment 1 feedback (November 16) asked what counts as a current report and what happens when agreement disappears; the feasibility experiment of November 17 |
| November 20, 2026 | Section 3: added a "Hub requiring k = 2" column and rows for failure of the deciding party and for setup of a new campus to Table 6, with a note that the two k = 2 columns separate the rule from where it is calculated; pointed the hub row of Table 5 to it; reworded the choice and revised Decision 1's context; marked the hook's 2-second limit in Decision 2 as not yet tested. Section 2: defined local and shared bans and stated that only local bans are reported (also in C1, the F2 check, the Section 4 trace, the ban hook in Table 7 and the `receive_report` input); set a provisional clock tolerance (each machine within 100 milliseconds of a common source, recorded with `chronyc tracking`); made Q1 treat results near the 5-second limit as uncertain, measured again or counted as misses; added local bans to the F5 check; stated the six-week targets for wrong and missed bans; pointed the Table 4 references to the design. Section 1: added F3 to the supporting checks. Sections 4 and 5: the report receiver serves the hook's `POST /local-ban` (Figure 3 redrawn); stated that a report is lost if its receiver stays unreachable after the retries; noted the 100-millisecond assumption among open items; named the report lifetime as the expiry interval and gave the signing outline its own paragraph, stating which fields are signed | Assignment 2 feedback (November 19) asked how a shared ban differs from an independent detection, for a clock tolerance in Q1, and for a hub with the same k = 2 rule; the Assignment 1 feedback asked for a false-ban or convergence target |
| November 21, 2026 | Section 12: added the response to feedback table and the list of unresolved items; updated the commit deadline in the header | The Assignment 3 rubric on Brightspace asks for a response record for earlier feedback and an explanation of unresolved items; the deadline moved to November 22 |

**Response to feedback:**

| Feedback | Response | Where | Status |
|---|---|---|---|
| Assignment 1: give a specific false-ban or convergence target | Six-week targets: no shared ban caused by one campus's reports (C1), and no more than 5 of 100 addresses reported by k campuses left unbanned or late (Q1) | Section 2, after Table 4 | Done; false bans of legitimate users still unmeasured (below) |
| Assignment 1: define a distinct, current report | A report counts for one expiry interval after its ban time; each campus counts once per address | Section 2 definitions, F5 and C1; Section 5 (`duplicate`, `expired`) | Done |
| Assignment 1: what happens when agreement disappears | Expiry added back to the six-week build: when fewer than k current reports remain, every node lifts the shared ban | Section 1, F5 in Section 2, expiry timer in Section 5 | Done for expiry; withdrawal is Semester II |
| Assignment 1: how stale or malicious reports affect the decision | Old reports return `expired`; reports from non-members return `not_member`; reports with a ban time more than 60 seconds in the future return `invalid`; a node never bans a member's address | Section 5, Table 8 | Partly: a member faking another member's address is open until signing |
| Assignment 1: how reports are signed, how long they stay valid, how many sites must agree | k = 2 of n = 3; a provisional 24-hour expiry interval; a signing outline (all three fields signed with each campus's key) | Section 2, Section 5 | Signing outlined, built in Semester II |
| Assignment 1: add synthetic legitimate logins from 198.51.100.20 and measure false bans | Added to the Semester II replay, kept separate from the attack-only results | Section 1, Semester II scope; open questions below | Planned for Semester II |
| Assignment 2: say how a local detection differs from a shared ban | Defined local ban (detection) and shared ban (enforcement); only local bans are reported or count toward k, so no origin field is needed; the `shared` jail has no hook | Section 2 definitions and C1; Section 4 trace; Section 5 (Origin) | Done |
| Assignment 2: define the clock error allowed in the Q1 timing check | Each machine within 100 milliseconds of a common source (chrony), offsets recorded with `chronyc tracking`; results within the sum of the two largest offsets of 5 seconds are measured again or counted as misses | Section 2, Q1 and Assumptions | Done for the prototype; the tolerance between real campuses is open |
| Assignment 2: compare a hub that also requires k = 2 | Added a "Hub requiring k = 2" column and rows for failure of the deciding party and setup of a new campus | Section 3, Table 6 and Decision 1 | Done |
| Assignment 2: call reconnection future work | Recovery after network splits is listed as Semester II; a report whose receiver stays unreachable after the retries is lost | Section 1, Semester II scope; Section 5, Table 8 | Done |

**Unresolved items:**

- How many legitimate users a mistaken shared ban locks out, and for how long, is not measured; the pilot has only attackers. It needs the synthetic legitimate logins in the Semester II replay.
- Reports are not signed in the six-week prototype, so a member that fakes other members' network addresses could reach k alone (Section 2, Constraints). Signing is built in Semester II.
- Withdrawal of a mistaken report and recovery after network splits are Semester II work; until then a mistaken report counts until it expires.
- The allowed clock difference between real campuses, the full treatment of stale and malicious reports (Section 8) and the report store's format are Assignment 4 work.
- The 24-hour expiry interval and the hook's 2-second limit are provisional and not yet tested.

| Open question | Why it matters | Next action |
|---|---|---|
| Does k-of-n agreement keep enough of the benefit of sharing? | In the pilot, k = 2 kept roughly a third to a half of the k = 1 benefit on all nodes, and about a tenth to a fifth on the 5 nodes outside the main pool | Compared in Section 3 (Table 6); repeat the replay with expiry and withdrawal in Semester II |
| Would a hub that also requires k campuses give the same safety with less effort? | If so, the difference from my approach is only who does the counting and who must be trusted | Answered for the prototype in Section 3, Decision 1: k-of-n removes the single trusted operator; revisit if campuses would accept one |
| Is 24 hours a sensible report lifetime? | Too short and attackers that move slowly are forgotten; too long and a mistaken report keeps counting | Provisional (Section 2); compare lifetimes in the Semester II replay |
| Should the prototype run in containers instead of virtual machines? | The feasibility experiment used containers, which are lighter and easier to run in an automated check | Decide in Assignment 4 |
| Is honeypot data a fair stand-in for campus SSH traffic? | The pilot has only attackers, so it cannot show how many legitimate users a wrong ban affects | Not resolved yet; add synthetic legitimate logins from the shared address in Table 2 to the Semester II replay and report them separately from the attack-only results |

**Assistance and reuse:**

I used an AI assistant (Claude) to help find and check sources, to write the pilot analysis scripts in [evidence/pilot](evidence/pilot/README.md), to draft the tables, Figures 1–3, Sections 2–5 and 9 and the text of this section, and to write the feasibility experiment files in [evidence/feasibility](evidence/feasibility/README.md), which I ran myself; I reviewed and edited all of it. Choosing Python, running the experiment for real and adding expiry to the six-week build were my decisions. The project choice, scope and open questions are my own and were approved by the instructor. The pilot reuses the CyberLab honeynet dataset under the Creative Commons Attribution 4.0 (CC BY 4.0) license [4]. The prototype will reuse fail2ban [8] as the local detector.

### References

All sources accessed November 4–17, 2026. Pilot data: CyberLab dataset version 1.0, daily files February 10–15, 2020.

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
11. fail2ban 1.0.2, `fail2ban/protocol.py` (list of client commands), accessed November 17, 2026. Supports: `fail2ban-client set <JAIL> banip <IP>` and `unbanip` ban and unban an address in a jail by hand, which is how a node applies and lifts shared bans. <https://github.com/fail2ban/fail2ban/blob/1.0.2/fail2ban/protocol.py>
12. fail2ban 1.0.2, `fail2ban/server/ticket.py`, accessed November 17, 2026. Supports: a ban time of −1 is treated as permanent, so bans in the shared jail end only when the node lifts them. <https://github.com/fail2ban/fail2ban/blob/1.0.2/fail2ban/server/ticket.py>

### Supporting media and evidence

- [assets/blocklist_workflow.png](assets/blocklist_workflow.png): Figure 1, the proposed workflow; source in [assets/blocklist_workflow.dot](assets/blocklist_workflow.dot).
- [evidence/pilot/README.md](evidence/pilot/README.md): pilot replay method, results, limits and run instructions; scripts and raw output in the same folder.
- [assets/context.png](assets/context.png) and [assets/architecture.png](assets/architecture.png): Figures 2 and 3; sources in [assets/context.dot](assets/context.dot) and [assets/architecture.dot](assets/architecture.dot).
- [evidence/feasibility/README.md](evidence/feasibility/README.md): feasibility experiment question, setup, findings and limits; configuration, scripts and [output.txt](evidence/feasibility/output.txt) in the same folder.

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
