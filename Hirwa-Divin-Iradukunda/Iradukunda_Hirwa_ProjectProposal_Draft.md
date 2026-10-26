# LockSentry: A Distributed Ransomware Early-Warning System for Linux

*Mock project proposal, Senior Project II (draft; name is a placeholder)*

## What I am building
A small distributed system that stops ransomware on a group of Linux machines. Each machine runs an **agent** that detects ransomware behavior and **freezes** the process on its own. A **coordinator** connects the agents. It identifies which client is encrypting a shared folder on the file server and sends signed warnings to the other machines. Agents keep protecting their machines when the coordinator is unreachable, and they catch up when they reconnect.

## The problem
In about 60% of human-operated ransomware attacks, files are encrypted over the network from a different machine (Microsoft, 2023). The file server sees only its file-sharing service (Samba) writing, so it cannot tell which client is attacking. Freezing that service would cut off every user. In over 90% of attacks that reached the ransom stage, the attackers used unmanaged devices (Microsoft, 2024), so the server must be able to defend itself. NSF Award 2348719 also points to *"the shortage of host-based techniques that would proactively mitigate the threat."*

## How it works
1. **Agent (every machine):** watches file activity (fanotify) and scores each process on cheap warning signs: canary files, bursts of rewrites, renames and deletes, and new extensions. It checks contents (entropy, file type) only for processes already under suspicion, and freezes the process tree with Linux control groups.
2. **File server:** each Samba client gets its own server process, so the agent can tell which client and user is encrypting. It freezes only that client's session and blocks its IP; other users keep working.
3. **Coordinator:** keeps a numbered log of signed warnings, such as an encryptor's file hash. Agents pull any warnings they missed with `Sync(after_seq)`, and applying the same warning twice has no effect.
4. **Safety rules:** a warning from another machine can only *freeze* a program whose hash matches exactly. It never kills, deletes or runs anything. A hash goes fleet-wide only after two machines report it, and system packages can never be targeted.
5. **Recovery:** btrfs snapshots restore exactly the files on the affected list.

## Demo (4 VMs on one laptop)
A client encrypts a shared folder on the file server. The server identifies that client, freezes its session and blocks it, while a second client keeps working. The same encryptor then starts later on another client and is frozen immediately by the warning. Finally, I cut a client off the network: it still protects itself, and it syncs when reconnected.

## How I will know it works
| Measure | Target |
|---|---|
| Files lost on the first machine | Median ≤ 10 (CryptoDrop, 2016) |
| Files lost on later machines (staggered launch) | ≈ 0 |
| Correct client identified | 100%, checked against Samba's audit log |
| Protection while disconnected | Same as a standalone agent; no alerts lost |
| Fake warning from a compromised agent | Freezes nothing |

I will also show where the coordinator does **not** help: when every machine starts encrypting at the same moment.

## Scope
**In:** agents, coordinator (gRPC with mutual TLS), Samba file server, a status page, and 4 virtual machines. **Out:** NFS client identification, peer-to-peer designs, Windows, VMware ESXi, and real ransomware samples. Weeks 1–7: the single-machine agent. **Week 8 checkpoint:** if the agent is reliable, weeks 8–11 build the coordinator, week 12 runs the evaluation, week 13 is buffer, and week 14 is the demo.

## Sources
- NSF Award 2348719: https://www.nsf.gov/awardsearch/show-award?AWD_ID=2348719
- Microsoft Digital Defense Report 2023: https://www.microsoft.com/en-gb/security/security-insider/microsoft-digital-defense-report-2023-state-of-cybercrime
- Scaife et al., "CryptoLock (and Drop It)," ICDCS 2016: https://www.cise.ufl.edu/~butler/pubs/icdcs16.pdf
- Vasilomanolakis et al., "Taxonomy and Survey of Collaborative Intrusion Detection," ACM Computing Surveys, 2015
