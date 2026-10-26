# Proposal: Distributed Ransomware Early Warning for Linux

## Problem
Ransomware does not always run on the machine whose files it encrypts. Microsoft's 2023 Digital Defense Report found that about 60% of human-operated ransomware attacks used remote encryption, where a compromised machine encrypts files on a network share. In that case the file server only sees its own file-sharing service (Samba) writing to disk. It cannot tell which client is responsible, and stopping the service would cut off every user. Microsoft also reported that over 90% of attacks that reached the ransom stage involved unmanaged devices, so the attacking machine usually has no security software of its own.

I would like to work on this problem for Linux machines that share files with each other.

## Proposed idea
I propose a small distributed system with two parts.

The first part is an agent that runs on each Linux machine. It would watch file activity through fanotify and look for behavior typical of ransomware, such as touching decoy ("canary") files, rewriting or renaming many files in a short time, or file contents suddenly looking random. When enough of these signs line up, the agent would pause the process with Linux control groups instead of killing it, so a person can decide what to do. This follows the approach of CryptoDrop (Scaife et al., 2016), which stopped ransomware after a median of 10 lost files.

The second part is a coordinator that connects the agents. On a file server, Samba starts a separate process for each client session, so the agent could map suspicious writes back to a client and user and pause only that session. The coordinator would then share what was learned, such as the hash of the encrypting program, with the other machines. Each agent has to keep working on its own if the coordinator is unreachable and catch up when it reconnects. This is where most of the distributed systems work is: making sure warnings are not lost or applied twice, and that the system behaves well during network failures.

A coordinator that can tell every machine what to do is also a target. The 2021 Kaseya attack showed attackers using a management channel to push ransomware to every connected machine. Because of that, I expect remote warnings to be signed and limited to pausing a program with an exact matching hash, never deleting or killing anything.

## How it could be evaluated
I plan to test the system on a few virtual machines on one laptop, using a simple encryption program I write myself that only touches a test folder. Things I would measure:

- how many files are lost before the agent pauses the process
- whether the file server identifies the correct client
- whether a machine that is disconnected still protects itself
- how quickly a warning reaches the other machines
- whether a fake warning from a compromised agent can cause harm

I also expect there are cases where the coordinator will not help, for example when an attacker starts encryption on every machine at the same moment. Measuring that would be part of the results.

## Open questions
- Can fanotify see writes that a machine makes to a mounted network share? The client side of the design depends on this.
- Is NFS realistic to support, or should the project focus on Samba?
- How much of the coordinator can be finished in one semester, after the single-machine agent works?

## Existing work
Commercial tools already do parts of this on Windows. Microsoft Defender's automatic attack disruption contains devices and IPs across a network, and Sophos CryptoGuard blocks remote machines that encrypt shared files. Open-source Linux tools like Wazuh and Falco collect events but do not include a ransomware detector that pauses processes. Research such as REDFISH (Morato et al., 2018) detects ransomware on network shares from traffic, but it cannot stop the process. I have not found an open-source Linux system that combines these pieces.

## Sources
- Microsoft Digital Defense Report 2023: https://www.microsoft.com/en-gb/security/security-insider/microsoft-digital-defense-report-2023-state-of-cybercrime
- Scaife et al., "CryptoLock (and Drop It): Stopping Ransomware Attacks on User Data," IEEE ICDCS 2016: https://www.cise.ufl.edu/~butler/pubs/icdcs16.pdf
- Microsoft Defender automatic attack disruption: https://learn.microsoft.com/en-us/defender-xdr/automatic-attack-disruption
- Sophos remote ransomware whitepaper: https://assets.sophos.com/X24WTUEQ/at/88p2fwqbfg9sc3jfq488ng4/sophos-remote-ransomware-guide-wp.pdf
- Morato et al., "Ransomware early detection by the analysis of file sharing traffic," JNCA 2018
