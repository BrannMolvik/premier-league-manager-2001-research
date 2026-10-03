# Gate 14 original FastViewTeam art boundary

_Status: independent Gate-14 work-ahead while Gate 13 remains the earliest incomplete validation gate and Codex owns its closure._

Recovery 226 promotes the already source-closed seven-resource
`FastViewTeam::TeamTable` family into a fail-closed original-art loading
boundary without inventing PlayerRow raster behavior.

The canonical executable/disc evidence already proves exact full paths, byte
sizes, SHA-256 values, EA444 dimensions and executable string addresses for:

- four 259x16 TeamTable name-grid resources;
- `team_bar_1.444`, `blank_bar.444`, and `team_bar_2.444`, each 82x16.

`gate14_fastview_resource_catalog.py` now includes all seven TeamTable
resources, so exact-path source inventories cannot silently validate only the
bar subset.

`original_fastview_team_resources.py` validates every supplied original file
by exact path, byte count, SHA-256 and EA444 header geometry. The source root is
explicit and may be an outside-Git private extraction or a later
provenance-controlled `original_assets/source` staging tree.

`original_fastview_team_art.py` then decodes only those verified bytes with
the canonical executable's already recovered EA444 tables and quantization
matrix. The returned object exposes the seven exact RGBA resources in source
contract order.

This checkpoint deliberately does **not** claim:

- generic PlayerRow text rasterization;
- localization-to-pixel resolution;
- the own-goal native color interpretation;
- source-pixel mapping for the dynamically resized energy PictureControl;
- cross-component z-order;
- a complete TeamTable or complete FastView raster frame.

The authorized original archive was re-resolved and materialized during this
recovery, but both container and alternate Python execution currently return
the same sandbox `ClientError` even for trivial filesystem access. Therefore
no new private source-byte extraction result is claimed here. The loader is
designed so the exact original pixels can be verified and consumed immediately
when byte execution resumes; hosted CI covers the fail-closed contract using
synthetic decoded images only.
