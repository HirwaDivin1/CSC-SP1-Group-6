# Pilot replay: does sharing bans help, and what does agreement cost?

A small replay of public honeypot data, run before the design work started. It is early evidence for the problem in Section 1 of [DESIGN.md](../../DESIGN.md), not a result of the proposed system.

## Data

CyberLab honeynet dataset, Zenodo record 3687527 (CC BY 4.0): <https://zenodo.org/records/3687527>. Files used: `cyberlab_2020-02-10.json.gz` through `cyberlab_2020-02-15.json.gz` (six days). The data are not committed here because they are about 460 MB. Download them from Zenodo with names such as `https://zenodo.org/api/records/3687527/files/cyberlab_2020-02-10.json.gz/content`.

SHA-256 of the files used:

```text
8603b42a45886fa4be5ecd457f06ff2844238d72480d9c38d3a9a575b33603fd  cyberlab_2020-02-10.json.gz
80fdffca9f5c7d27e7242272065ddda6ddd32ba5e7703f3174d7dc18f5b5feef  cyberlab_2020-02-11.json.gz
a4c3c2d5db6c56a86c8bff99d6131f53f0bcfb68cbeacc2e318da4a462f68ff6  cyberlab_2020-02-12.json.gz
050d0fc75b2a1947a00b45e4cdec8c5d947579d20a219e76f95fdc6123c54fd3  cyberlab_2020-02-13.json.gz
e2246be772cc41d5ad14e7cdd3c387ec34c65ed1a2173c565d3a4f5bd93e56b8  cyberlab_2020-02-14.json.gz
364a661fe8573b37bf6be7123fa86c4f559dc62f738d1eafd52ecde877c4b277  cyberlab_2020-02-15.json.gz
```

## Run

```sh
python3 extract.py <folder with the .json.gz files> logins.tsv   # one row per login attempt
python3 marginal.py logins.tsv > marginal_output.txt
python3 quorum.py logins.tsv > quorum_output.txt
```

Python 3 standard library only.

## Method

Each honeypot node is treated as a separate site. A site bans a source after `T` login attempts within `W` seconds (fail2ban-style). The honeypots accept some passwords, so both failed and accepted logins count as attempts; on a real server fail2ban would count failures only. Attempts are counted as reaching SSH if they arrive before the ban that applies at that node.

- **Local only:** each node bans only on its own detection.
- **Shared, k of n:** a source is also banned at every node once `k` different nodes have detected it locally (optionally after a propagation delay).
- **Reported number:** the percentage reduction in attempts reaching SSH, compared with local only.

## Results

Raw output: [marginal_output.txt](marginal_output.txt) and [quorum_output.txt](quorum_output.txt).

| Setting | All 33 nodes | 5 nodes outside the main sensor pool |
|---|---|---|
| k = 1 | 27.7–37.7% fewer attempts | 7.0–12.2% fewer |
| k = 2 | 9.0–19.4% | 1.3% |
| k = 3 | 4.3–13.5% | 0.1–0.3% |

Ranges cover thresholds 5 per hour, 10 per 24 hours and 30 per 24 hours. Delaying shared bans by one hour changed the k = 1 result by at most one percentage point (for example 37.7% to 36.7% at 5 per hour).

## Limits

- Six days, attackers only, one honeypot operator. 88% of events come from one sensor pool (`ubuntu_basic_pool`), so the nodes are not independent organizations.
- There are no legitimate users, so false bans cannot be measured.
- Source addresses are pseudonymized; the analysis assumes a pseudonym is consistent across nodes.
- Bans last for the whole window; expiry and revocation are not modelled.
