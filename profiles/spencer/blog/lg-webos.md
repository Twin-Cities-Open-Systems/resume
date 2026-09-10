# Rooting a TV Into Submission
**Date:** 2026-08-30
**Author:** Spencer Butler (with the fleet)
**Tag:** HWOps For Life

---

Dad's TV is a rooted LG webOS set, and tonight it earned that rooting all over again. The short version: we built a real package pipeline for a device that actively fights you at every layer, broke its remote-control daemon trying to add SNMP, found a completely different way to talk to it instead, and along the way a family TV briefly went dark before coming back on its own.

## The read-only wall

Everything on this TV assumes you'll never write to it. The root filesystem is protected at the block-device level -- not a mount flag, a real hardware/kernel guarantee, confirmed the hard way when `mount -o remount,rw /` came back with "cannot remount /dev/root read-write, is write-protected." No amount of cleverness gets around that; it's not meant to move.

So every real fix this session had the same shape: find where the device already keeps writable state, and live there instead of fighting the wall. DNS got fixed by editing connman's own per-service settings file, not `/etc/resolv.conf`. A package manager that assumed a writable `/usr/lib/opkg` got repointed entirely into `/media/developer/temp` -- including, less obviously, its actual install destination, since `opkg` checks free space against the real filesystem root before it ever looks at where a package's files are declared to go.

We proved the whole pipeline end to end with the smallest possible package: a one-line shell script, packaged by hand as a real `.ipk` (it's just an `ar` archive of three files), installed, and run from its real location. It printed "hello from a real TCOS-built ipk on Dad TV." Small, but it meant the mechanism itself was proven before betting anything real on it.

## Then we bet something real on it

The actual goal was SNMP -- specifically the kind with `extend` support, so the TV could expose custom facts under TCOS's own real IANA-assigned identifier, not just generic system stats. No prebuilt static binary for that exists anywhere for this architecture, so the plan became: stand up a real cross-compilation environment in its own container, build `net-snmp` for real, package it the same proven way, and wire it into a genuine, documented auto-start hook the TV's own boot sequence already runs.

That last step is what went sideways. Testing the auto-start script triggered a reboot, and the TV didn't come back on SSH. Not slow -- stuck. It still answered ping, still worked as an actual television, but every path we had into it was gone.

> **Honest note:** whether that specific script caused a genuine hang was never confirmed. It's the one new thing introduced right before the failure, which makes it the real suspect -- not a diagnosed cause.

A physical power cycle brought the TV back completely normal as a television, but rooting was gone -- Homebrew Channel itself wasn't there anymore. The one piece of real good news: the firmware was still the exact version the original rooting exploit needs. Nothing forced an update in the background; the safeguard we'd set specifically for that held. Re-rooting is a known, repeatable process from here, whenever that actually happens.

## The mystery that turned out not to matter

Long before any of this, there was a smaller, stranger problem: the TV's own internal command bus -- the same mechanism its remote-control daemon uses -- would accept a request, process it, and then just... say nothing back. Every tool, every target, every invocation style, always the same silence.

Tracing the actual system calls settled it precisely: the client genuinely connects, genuinely sends its request, and then never calls the one function that would wait for a reply. It exits right after asking the question. A real bug in that specific tool, confirmed by watching the exact bytes go out and never come back -- not a permissions problem, not a networking problem, just a program that stopped listening to itself.

The fix wasn't fixing that bug at all. The TV has a second, completely separate way to be controlled -- the same protocol phone remote-control apps and home-automation integrations use, reachable straight over the network with no SSH involved. A one-time on-screen pairing prompt, accepted once, and after that: real, live answers. What's playing, what channel, the volume, whether it's muted -- all correct, all immediate, confirmed against exactly what was actually on screen at the time.

## What's still open

Re-rooting hasn't happened yet. Whether the new auto-start script was actually the cause of the hang hasn't been tested in isolation. And the tools that came out of tonight -- the package-build pattern, the writable-storage fix, the remote-control client -- are proven, working code sitting in scratch files, not yet turned into the kind of small, reusable tool the rest of the fleet can just pick up and use. That's the actual next step: not a new capability, just making tonight's real, working code available to whoever needs it next.
