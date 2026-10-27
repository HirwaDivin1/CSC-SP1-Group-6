# Proposal: A Ransomware Tripwire for a Group of Linux Machines

## Problem
Ransomware encrypts a victim's files and demands payment for the key. Groups such as LockBit and Akira now ship versions built for Linux, but the free Linux security tools I looked at (Wazuh, Falco, auditd) mostly collect events or follow rules the administrator writes. None of them comes with a simple way to notice ransomware while it is encrypting and stop it. Once ransomware is inside an organization, it is also usually launched on many machines, often as the same program copied to each one.

The idea for this project came from NSF Award 2348719, a research project on defending research computing against ransomware, which points to a "shortage of host-based techniques that would proactively mitigate the threat." I would like to work on a small version of this problem for a group of Linux machines.

## Proposed idea
I propose a small distributed system with two parts.

The first part is an agent that runs on each machine. It would place decoy ("canary") files in folders worth protecting. No normal program has a reason to open them, so a process that modifies one is very likely ransomware. The agent would also count how quickly each process rewrites, renames or deletes files, since ransomware changes a lot of files in a short time. The agent would watch file activity through fanotify, which reports which process made each change. When a process trips a canary or crosses the rate limit, the agent pauses it (SIGSTOP) instead of killing it, so a person can decide whether to stop it or let it continue.

The second part is a coordinator that connects the agents. When one agent pauses a suspicious program, it reports the program's hash to the coordinator, and the coordinator shares it with the other agents. If the same program starts on another machine, that agent can pause it right away instead of waiting for it to damage files. Each agent has to keep protecting its own machine when the coordinator is unreachable. It would save its alerts while offline and send them when it reconnects, and receiving the same warning twice should not cause problems. Handling these failures correctly is the main distributed systems part of the project.

Since the coordinator can tell every machine to pause a program, a fake warning could cause harm. At minimum, agents would only accept warnings from the coordinator using a shared secret, and a remote warning could only pause a program, never delete or kill anything.

## How it could be evaluated
I plan to test on three or four virtual machines on one laptop, using a small encryption program I write myself that only touches a test folder. I would measure:

- how many files are lost before the agent pauses the program
- how often normal work (zipping files, compiling code, updates) is wrongly paused
- how long a warning takes to reach the other machines
- whether a machine that was offline catches up correctly when it reconnects

The coordinator will not help in every case. If an attacker starts the program on every machine at the same moment, the warning arrives too late, and each agent has to rely on its own canaries. I would include that case in the results.

## Open questions
- Can the agent be fast enough that only a few files are lost before the pause?
- Where should canary files be placed so ransomware is likely to hit them early?
- How should the agent tell real backup or encryption tools apart from ransomware?

## Possible extensions
If time allows: checking whether file contents suddenly look encrypted, identifying which client is encrypting a shared Samba folder, and restoring damaged files from snapshots.

## Existing work
Commercial products such as Microsoft Defender and CrowdStrike Falcon already share detections across many machines, but they are closed source and mainly built around Windows. CryptoDrop (Scaife et al., 2016) showed that watching file behavior can stop ransomware after a median of 10 lost files. RansomFree, a discontinued Windows tool, used decoy files the same way this project plans to. I have not found an open-source Linux tool that combines canary files, process pausing and shared warnings.

## Sources
- NSF Award 2348719 (source of the project idea): https://www.nsf.gov/awardsearch/show-award?AWD_ID=2348719
- Scaife et al., "CryptoLock (and Drop It): Stopping Ransomware Attacks on User Data," IEEE ICDCS 2016: https://www.cise.ufl.edu/~butler/pubs/icdcs16.pdf
- fanotify(7) Linux manual page: https://man7.org/linux/man-pages/man7/fanotify.7.html
- CrowdStrike, offline host protection: https://www.crowdstrike.com/blog/tech-center/falcon-protects-off-line-hosts-from-new-threats/
