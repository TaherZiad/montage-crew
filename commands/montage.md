---
description: Edit an Arabic short video (or make one from an idea with no footage) with montage-crew
argument-hint: "[video file | folder | idea text] [options, e.g. 16:9, pro, بستايل neon-blue]"
---
Load the montage-crew skill (Skill tool: `montage-crew:montage-crew`, or `montage-crew` in a ZIP install) and follow its SKILL.md from §0: setup check, profile (first use runs onboarding, then continues), routing (§0 step 1b), then the edit (§3).

Request: $ARGUMENTS

- A file or folder → edit it. Text with no file («فكرة فيديو عن…») → idea-only video (`footage = none` for this video).
- Options in the request (format, mode, «بستايل <slug>», «هذا تسجيل شاشة») apply to this video only.
- Empty request → ask in one short line which video or idea to work on.
