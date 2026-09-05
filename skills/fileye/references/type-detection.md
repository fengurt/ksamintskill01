# Type detection

Order of evidence: magic bytes → container contents → text sniffing → extension (hint only). The extension is recorded as `claimed_extension` and compared to the detected type; disagreement raises a warning and the detected type wins.

## Magic bytes checked at offset 0

| Signature (hex / ascii) | Type |
|---|---|
| `50 4B 03 04` / `50 4B 05 06` (PK) | zip container → refined below |
| `D0 CF 11 E0 A1 B1 1A E1` | OLE2 compound document (xls, doc, ppt, msg) |
| `25 50 44 46` (%PDF) | pdf |
| `89 50 4E 47 0D 0A 1A 0A` | png |
| `FF D8 FF` | jpeg |
| `47 49 46 38 37/39 61` (GIF87a/GIF89a) | gif |
| `53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00` (SQLite format 3\0) | sqlite |
| `50 41 52 31` (PAR1) | parquet |
| `41 52 52 4F 57 31` (ARROW1) | arrow IPC |
| `93 4E 55 4D 50 59` | numpy .npy |
| `1F 8B` | gzip |
| `42 5A 68` (BZh) | bzip2 |
| `FD 37 7A 58 5A 00` | xz |
| `28 B5 2F FD` | zstd |
| `37 7A BC AF 27 1C` | 7z |
| `52 61 72 21 1A 07` | rar |
| `75 73 74 61 72` at offset 257 (ustar) | tar |
| `7B 5C 72 74 66` ({\rtf) | rtf |
| `52 49 46 46` (RIFF) + bytes 8–11 | wav / avi / webp |
| bytes 4–7 `66 74 79 70` (ftyp) | mp4 family; brand hei*/mif → heic |
| `4F 67 67 53` | ogg |
| `66 4C 61 43` | flac |
| `49 44 33` | mp3 with ID3 tag |
| `1A 45 DF A3` | matroska / webm |
| `7F 45 4C 46` | ELF executable |
| `4D 5A` | PE executable |
| `CA FE BA BE` / `CF FA ED FE` | Mach-O |
| `25 21 50 53` | PostScript |
| `38 42 50 53` | psd |
| `49 49 2A 00` / `4D 4D 00 2A` | tiff |
| `42 4D` | bmp |
| `77 4F 46 46` / `77 4F 46 32` | woff / woff2 |
| `00 01 00 00 00` / `4F 54 54 4F` | ttf / otf |
| `89 48 44 46 0D 0A 1A 0A` | hdf5 |
| `43 44 46 01/02` | netcdf classic |
| `80 04 95` / `80 05 95` | python pickle (protocol 4/5) |

## Zip container refinement

1. `[Content_Types].xml` present → OOXML. `xl/` → xlsx (xlsm if `xl/vbaProject.bin`); `word/` → docx/docm; `ppt/` → pptx/pptm; `visio/` → vsdx.
2. `mimetype` entry present → read it: `opendocument.spreadsheet` → ods, `.text` → odt, `.presentation` → odp, `epub` → epub.
3. `META-INF/MANIFEST.MF` → jar. `AndroidManifest.xml` → apk. `Index/Document.iwa` → Apple Numbers/Pages.
4. Otherwise plain zip.
5. Unreadable central directory → `zip-corrupt`.

## OLE2

Distinguishing xls/doc/ppt properly requires reading the compound-file directory stream (`Workbook`, `WordDocument`, `PowerPoint Document` stream names). Current script reports `ole2:<extension-hint>`; add a directory parser here if OLE2 files are common in your corpus.

## Text sniffing (no signature matched)

- Any NUL byte in the first 8 KiB → `binary-unknown`.
- Decode attempts in order: utf-8-sig (BOM), utf-16 (BOM), utf-8, gb18030, shift_jis, latin-1. The first success is recorded as `encoding`. latin-1 always succeeds, so a latin-1 result for non-Western text means the real encoding was not recognised.
- `<?xml` → xml; `<!doctype html` / `<html` → html; `<svg` → svg.
- First non-space char `{` or `[` and `json.loads` succeeds → json; else if every non-empty line (first 50) parses on its own → ndjson.
- `.yml/.yaml` with `key:` at line start → yaml.
- `.md` or ATX headings → markdown.
- Known source extensions → `source:<ext>`.
- `csv.Sniffer` succeeds over the first 20 lines and delimiter counts are consistent → csv.
- Otherwise `text`.

## Extending

Add a `(signature, name)` pair to `MAGIC`, a MIME entry to `MIME`, an expected-extension set to `EXT_FOR`, and, if the type has internal structure worth inventorying, a `structure_<type>()` function wired into `structure_for()`. Bump `FILEYE_VERSION` so old manifests can be identified for re-run.
