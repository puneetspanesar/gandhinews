# People library run (weekly, once the owner approves its scheduled task; until then, run by hand)

Keeps newsroom/library/people.json (checked portraits of the people in the news) complete, so hourly runs place a person's picture in a minute instead of searching. Read newsroom/RUNBOOK.md rules A first. Nobody is watching: never ask a question.

1. `source /home/claude/gandhinews/newsroom/scripts/setup.sh library`.
2. Add people: every person named in a `hero.subjects`, a `--person` miss or a held story's reason in the last 7 days who is not in newsroom/library/people.tsv goes in it (`English name|Hindi name|Commons search`). Names only, never roles.
3. Search: for the people with fewer than 2 portraits in people.json, write queries in parts of about 30 (`{"slug": "Name||8"}`) to /home/claude/gn-work/q-libN.json and run `python3 newsroom/scripts/photos_gh.py find libN /home/claude/gn-work/q-libN.json` for each part, at most 4 at a time, 30 seconds apart.
4. Pick: `/tmp/claude-0/cvenv/bin/python newsroom/scripts/build_library.py pick /home/claude/gn-work/pcvlib0 ...` (portraits with one clear face; official event photos cropped around the face).
5. LOOK at every review sheet it writes (/home/claude/gn-work/library-sheet-*.jpg) with the Read tool. Reject every photo that is the wrong person, a namesake, a statue, mural, signature or painting, a group, a back view, a tiny figure or a duplicate: `build_library.py reject slug:n ...`. When unsure who it is, reject.
6. `build_library.py write`, then `bash newsroom/scripts/gate.sh` and `bash newsroom/scripts/publish.sh library "people library: N people, M portraits"` (commit.txt first line "Library: ...").
