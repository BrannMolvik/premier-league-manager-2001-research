# Inbox producer ownership — 10 October 2026

Gate13 OPEN. This closes a required data dependency, not the missing Inbox UI.
Canonical EXE SHA256:
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Raw source, scripts and output remain private outside Git; no original process.

## Source contract before implementation

Native4022D0 reads packed Master club+48 into DBTClub+40.403660 copies it
into DBRClub+40. The imported Southport key is195, not club index349.
Actual reader/import prefixes passed against original Master.dat SHA256
`183dd457d09ce616f99a664636727668ec15eab3f65b9057ef0953e76548b6b8`.
Only fread/string resolution were substituted; this does not prove human binding.

TeamSelect4D8EF8 ->413BB0 appends the new DBRUser, then4258D0 binds the club
and clears user+6B4.413C5B calls426090. Its4151C0 scan excludes manager keys
already owned by registered humans, then accepts the first manager whose
first-name first byte is '!'.4261BE writes its table index to club+40;
4261D2/E1 write the manager's club/date.415870 releases the previous manager.
If no candidate exists, no key replacement occurs. Actual426090 through4261E5,
4151C0/413B10/403E10/415870 passed seven adversarial synthetic-owner cases,
including an occupied '!', '!!', leading-space nonmatch and exhausted table.
No native leaves were substituted. This is not full original startup acceptance.
The authorized database contains1612 managers; every packed manager ID equals
its table index, independently checked from the43-byte original records.
The first reserve is0 '!Spare'.
Thus a fresh single-human Southport binding routes to key0, not195 or349.

41B61E/41B63F captures the player's active club and that club's runtime+40
at transfer-request production;56FAD0 owns recipient[1,key,-1] and
sender[2,player,activeclub]. The caller schedules current+1 and flags|6.
Delivery5CFA20 stamps the envelope date and transfers ownership, then413020
compares the captured key against each user's live club+40 and tail-appends
to user+6B4. Do not resolve the recipient from current selection on Inbox open.
Existing independent owner/constructor/delivery fixtures qualify this bounded
family; renewals' sender20 additionally needs the actual type1 staff owner.

## Minimum compatibility change / unknowns

Retain the single supported human's source-qualified runtime recipient key at
fresh select_club, separately from immutable imported AI-manager metadata.
Capture recipient and active-club context at the existing transfer-request
producer sink, with no RNG changes. Persist both; older/synthetic unknown inputs
remain unknown. Do not treat pending requests as delivered Inbox messages.

Ordered delivered-owner/global MPM scheduling, live renewal staff/contract
payloads, transfer-body lazy RNG/text and complete original PEAMail rendering/
ordinary input remain to integrate. No fake welcome message, queue merge,
synthetic sender, blank destination or new UI convention is authorized.
SOURCE-VERIFIED: bounded loader/binding/recipient producer described above.
INTEGRATION-VERIFIED:245 final focused tests/34.005s passed, including actual select_club,
producer-sink capture with one unchanged RNG30 draw, loan-active-club context,
schema48 roundtrip/older unknown preservation and malformed-context rejection.
Withdrawn real Windows/Tk at1x/1.5x confirmed actual fresh Southport key0,
all30 players, menu updates and Return/Continue without item/photo growth.
Those adapter calls are not physical-mouse or Inbox acceptance. Asset policy
and diff checks passed. No new full-suite/package or visible acceptance claim.
VISIBLE-ACCEPTED: no; actual delivered Inbox/render/input remains missing.
