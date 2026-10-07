# Gate 17 exact FFmpeg source snapshot

_Status: deterministic source-assembly checkpoint only; not a legal conclusion._

The minimal Windows helper is built from FFmpeg commit
`46d8f462eeb87ee1f704d8c44a0ee24fca471ad1`. This checkpoint creates a
deterministic source archive from that exact Git tree, preserves
`COPYING.LGPLv2.1`, and records the exact configure arguments used by the
minimal helper.

CI uses `git archive` from the pinned clean checkout and deterministic xz
settings. The resulting archive, license copy, build-recipe manifest, and
receipt are uploaded as an artifact for independent hash review.

This checkpoint deliberately keeps `source_material_complete=false` and
`legal_compliance_claimed=false`. It proves that the exact FFmpeg source used
for the helper can be reproduced and archived. It does not decide the legal
sufficiency of the final redistribution bundle, notice wording, delivery
method, or release compliance.
