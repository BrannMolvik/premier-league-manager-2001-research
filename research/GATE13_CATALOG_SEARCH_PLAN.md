# Gate 13 PStartMenu / TeamSelect Catalog Search Plan

_Date: 30 September 2026_

## Purpose

This note defines the first search sequence to run against the complete
Gate-13 disc catalog once the authorized Library ZIP can be read by a working
execution container.

It deliberately separates **confirmed source/executable evidence** from
**secondary visual labels**. Visible labels are search hints only. They are not
asset filenames, layout coordinates, or resource bindings until the source
inventory proves that relationship.

## Confirmed anchors

### Source paths already proven elsewhere in the repository

- `FM2001_Art/Generic/bground.444`
  - **222,616 bytes** according to verified original-disc research;
  - 800x600;
  - SHA-256
    `9db0d71daf70d77b4f5f2307304bb8c5eac4ee3a07a85f2828b570fbbf3b7fb9`.
- Startup presentation resources:
  - `FMV/easp.tgq`;
  - `FMV/premintro.tgq`;
  - `FMV/bground.444`;
  - `FMV/Credits2.txt`.

Only `FM2001_Art/Generic/bground.444` is a confirmed first-slice front-end
graphic anchor. The FMV entries belong to the startup presentation path and are
not substitutes for the Gate-13 management screens.

### Executable identities

- PStartMenu screen: `0x323`.
- PStartMenu New Game event/control: `2`.
- PStartMenu vtable: `0x7C64E0`.
- TeamSelect constructor: `0x4D9290`.
- TeamSelect vtable: `0x7C7650`.
- TeamSelect Back event/control: `0x29`.
- TeamSelect Start/Continue event/control: `0x2A`.
- TeamSelect embedded `Button@ease_2001` at object `+0x3690`.

These identifiers are useful when later correlating binary/layout records with
the executable. They do not prove filenames.

## Secondary visual labels

The following strings are visible in bounded secondary screenshots and may be
used as **content/name search hints only**:

### PStartMenu

- `START NEW GAME`
- `CONTINUE`
- `LOAD GAME`
- `QUIT TO WINDOWS`

### TeamSelect

- `F.A. PREMIER LEAGUE`
- `ENGLAND`
- `DIVISION 1 (ENG)`
- `DIVISION 2 (ENG)`
- `DIVISION 3 (ENG)`
- `CONFERENCE`
- `SCOTLAND`
- `GERMANY`
- `ITALY`
- `SPAIN`
- `FRANCE`
- `HOLLAND`
- `BELGIUM`
- `MAIN MENU`
- `START GAME`
- `RIGHT CLICK`
- `LEFT CLICK`
- `RIGHT OR LEFT CLICK`
- `LOADING INFORMATION`

Do not promote any mapping from one of these strings to a particular file until
the source bytes or executable reference chain confirms it.

## First real-catalog sequence

Assume the deep source inventory has been saved as `gate13-source.json`.

### 1. Establish the source-disc shape

```text
python gate13_catalog_query.py gate13-source.json --summary
```

Record the top-level roots and suffix counts **for both the outer ZIP and
nested-disc layers** in the Gate-13 research note before extracting anything.
The `gate13_catalog_query.py` default searches both layers and marks each
match `zip` or `disc`. Use `--layer zip` and `--layer disc` to investigate
them separately. Do not discard outer-ZIP leads without inspecting them.

### 2. Enumerate the known front-end art family

```text
python gate13_catalog_query.py gate13-source.json --top-level FM2001_Art
python gate13_catalog_query.py gate13-source.json --contains generic
```

Confirm `FM2001_Art/Generic/bground.444` is present with the expected size and
later hash it through intentional extraction.

### 3. Search evidence-backed screen/control terms

Run broad path-name queries first:

```text
python gate13_catalog_query.py gate13-source.json --regex "(start|menu|team|select|button|continue|load|quit)"
```

Also search likely data/string families without assuming any one extension is
authoritative:

```text
python gate13_catalog_query.py gate13-source.json --suffix str
python gate13_catalog_query.py gate13-source.json --suffix idx
python gate13_catalog_query.py gate13-source.json --suffix txt
python gate13_catalog_query.py gate13-source.json --suffix dat
```

For graphics, inventory rather than immediately import:

```text
python gate13_catalog_query.py gate13-source.json --regex "\.(444|pcx|bmp|tga|png|gif|jpg|jpeg)$"
```

### 4. Save a reproducible exact-path shortlist

Once catalog evidence identifies plausible first-slice files:

```text
python gate13_catalog_query.py gate13-source.json \
  --regex "(start|menu|team|select|button)" \
  --paths-only > gate13-selected-paths.txt
```

Edit that path list only to remove unrelated files. Do not add paths not present
in the catalog. If a normalized path is duplicated within or between
archive layers, `--paths-only` refuses an ambiguous list. Layer filters
narrow the **search** but are not per-layer extraction selectors: isolate
the intended original resource before staging an ambiguous path.

### 5. Stage only the selected source files

```text
python gate13_source_inventory.py <source.zip> --deep \
  --extract-path-file gate13-selected-paths.txt \
  --only-explicit \
  --require-all-explicit \
  --extract-candidates-to <staging-directory> \
  --output gate13-source-selected.json
```

The report must warn if any selected path no longer exists;
`--require-all-explicit` also makes the staging command fail after writing
its audit report if any exact resource is missing. Source extraction
refuses to overwrite existing files, case-insensitive duplicate names, and
cross-layer staging collisions. Raw BIN disc images are signature-detected
so unrelated opaque interface `.bin` resources remain searchable. Use `--only-explicit`
to exclude any other heuristic candidates from staging. The size of the
known background is checked even from the catalog, prior to hashing its bytes.

### 6. Correlate before import

For each staged resource record:

1. compute/record SHA-256;
2. inspect header/format metadata;
3. correlate it with the PStartMenu or TeamSelect evidence boundary;
4. reject unrelated resources from the first slice;
5. only then use `gate13_asset_import.py` to copy the minimal confirmed set
   under `original_assets/source/` with provenance.

## Raw-disc efficiency and integrity

The documented raw MODE1/2352 BIN track is validated sector-by-sector before
listing, then read through the repository-native virtual ISO9660/Joliet view.
It does **not** generate a full-size temporary ISO copy. The separate
`convert_mode1_2352_to_iso` helper is retained for independent/manual
checks. The source ZIP, extracted raw track and selected asset staging remain
temporary, never uncontrolled original-file Git commits.

## Acceptance boundary for the first import

The first imported slice should be no larger than needed to make the
PStartMenu -> TeamSelect presentation recognizably original.

At minimum, source evidence should account for:

- the main front-end background/identity composition;
- the PStartMenu controls required for the New Game path;
- the TeamSelect background/layout/hierarchy presentation;
- the Back and Start Game presentation controls corresponding to proven IDs
  `0x29` and `0x2A`;
- any string/layout file directly required to render those pieces.

If a resource cannot yet be tied to that slice, leave it in the source catalog
rather than importing it speculatively.
