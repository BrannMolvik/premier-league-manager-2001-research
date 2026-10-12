# Recovery552: original PSupportStart six-source raster inputs

PR #648 was source-review and exact-head CI verified, then merged at
`436ed015dc36cc3f3488c47e2cf3fc1b6de3ca95`. This new branch
stages the remaining verified authentic original SupportStart art.
These are **native sources**, not a rendering-complete or click-capable screen.

The previous source sweep already established original 760×500 modal,
seven 326×37 staff rows, fourth stars child, fifth text label, and
original Exit/Tick event dispatch. The missing five referenced original
EA444 art files were retrieved *individually* from the owner's private
extracted FM2001 folder rather than reprocessing disc ZIP/BIN.
Exact byte identities independently SHA-256 verified in the worker's
local container; source Git blobs independently matched calculated Git
blob SHA-1. They are intentionally placed under the existing project
authorized `original_assets/source` tree with separate manifest entries:

| Source relative path | Bytes | Native dimensions | SHA-256 |
|---|---:|---|---|
| `FM2001_Art/Generic/user_entry/background.444` | 176016 | 760 × 500 | `a7536fe303e6a340bf6f30a345ce77b7f396b91c8330957e6fd7a30915a3f6c4` |
| `FM2001_Art/Generic/user_entry/text_bars.444` | 11124 | 306 × 68 | `8c569018962a7084c33e5f4fda5d67e63f384d2e18d778281a7ad5aba2cba723` |
| `FM2001_Art/Generic/GenericButtonsAndBars/user_entry_anim.444` | 19720 | 17 × 851 | `7eb9df5610dade0d32cde3051e457216be1fb5062dcc66209012ca969203d1bc` |
| `FM2001_Art/Generic/GenericButtonsAndBars/exit_button.444` | 4864 | 30 × 90 | `3c317bbb4449a03efbeb867d1de4fd2e5b7d936f29d31f1c11af2092556fa0f9` |
| `FM2001_Art/Generic/GenericButtonsAndBars/tick_button.444` | 4372 | 30 × 90 | `119178ce89378df72f917f7fee4e17fb7edb5d43a5a5dee6229a89fbcf6be5c4` |
| `FM2001_Art/Support/stars.444` (already merged in #648) | 2776 | 75 × 10 | `16c619e305ebad013e7404ea9e5d4414a9f9a8bd0d6ad26f269ee82a49849633` |

New `reconstruction/original_supportstart_art.py` is a small strict
source-identity gate: reads only these six canonical originals,
validates byte length, SHA-256, native header descriptor and source
dimensions. It preserves the *known* native first source crops
`text_bars.444 (0,0,306,17)` and Exit/Tick
`(0,0,30,30)`; it does **not** invent hover, selected sprite
frame indexes, user_entry animation cropping, parent transforms,
hitboxes, rendered composition or native staff first/surnames.

The regression `test_original_supportstart_art.py` validates all
six authentic source assets, deliberately rejects missing originals
and independently rejects tampered source bytes.
The original star crop map/test from PR648 remains canonical.
The source loader is a reusable minimum for real later
`PSupportStart` graphical integration but is not itself
a completed GUI or an excuse to close Gate13.

Next source/implementation task: use recovered original UI
renderer/resource conventions, ascertain parent and child
drawing positions/opaque/hover native states (do not substitute
fake art), connect legitimate upstream input callbacks and
true selected-user personal name/staff pointer state to the
seven-row Tk modal. Apply/Cancel must preserve original
staff/name side effects and TeamSelect return. Verify exact-head
full/impacted tests/asset policy before a cohesive player-visible PR.

Gate13–17 remain open; original executable has not run in
a genuine Windows11 GUI verification.
