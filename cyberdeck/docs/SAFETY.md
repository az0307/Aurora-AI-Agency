# Cyberdeck — Authorization & Safety

This subsystem **provisions a device you own** (a Samsung S10 running
Termux + Kali NetHunter) into a portable security-testing workstation. It does
not attack anything. Provisioning is lawful; **use** of the resulting tools is
only lawful against systems you own or have **written authorization** to test.

## Hard rules
- **Scope first.** No active testing without a signed scope-of-work / rules of
  engagement. Mirror the RoE model in `../hexstrike-ai/proposals/`.
- **Your own device only.** These scripts assume the S10 belongs to the
  operator. Rooting/unlocking a device you do not own may breach warranty and
  law.
- **No third-party targeting** is configured or implied anywhere in this repo.
- **Key-based SSH only.** `30-ssh-cyberdeck.sh` disables password auth and
  requires your laptop's public key.
- **Authorization gate.** Every script calls `require_authorization`; in
  automation set `CYBERDECK_AUTHORIZED=yes` to record the acknowledgement.

## Legal
Unauthorized access to computer systems is a criminal offence (in AU: the
*Criminal Code Act 1995* Cth, Part 10.7). You are solely responsible for how
the provisioned device is used. When in doubt, don't.
