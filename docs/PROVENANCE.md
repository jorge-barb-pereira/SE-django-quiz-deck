# Provenance and original development dates

Source collection: `Original Codes/Django`. Every original file remains unchanged outside the publication checkout.

| Evidence | Date supported |
| --- | --- |
| Polls initial migration, Django 5.1.3 header | 23 January 2025, 19:37 |
| Movies and polls follow-up migration headers | 28 January 2025 |
| Quiz player migration header | 13 February 2025, 11:43 |
| Quiz questions, games and cards migration headers | 14 February 2025 |
| Answer-history migration header | 17 February 2025, 02:09 |
| Game-duration migration header | 18 February 2025, 17:05 |
| Final ZIP's Python entry timestamps | Through 18 February 2025, 19:05 |
| Maintained package, English interface and tests | October 2026 |

Migration headers provide stronger evidence than the October 2026 import-directory timestamps. ZIP metadata corroborates the sequence but does not prove a development start date. New commits use their actual dates and are not backdated.

The supplied final game project is the main application. Its historical source is in `archive/quiz/`; earlier polls, movies and DRF exercises are in `archive/tutorials/`. The archive contains source only, not a second runnable deployment. No source from the ZIP duplicates is imported a second time.

`archive/manifest.json` maps all 58 published historical source files to their originals and records SHA-256 hashes before and after transformations. Publication normalizes UTF-8/LF and file-ending whitespace, removes embedded secret/mail identity settings, and replaces the original institution-specific address domain with `example.invalid`. These are sanitized copies, not byte-identical originals. No credential values or secret-derived identifiers are written into the documentation or manifest.

Excluded: both original SQLite databases, ZIPs, instructor slides, the resources document, caches and local environment files. Only database table-name inventories were examined; no original database rows were exported. All maintained questions are newly invented, and participant records are created only when running the demo.

The project is presented as Jorge Pereira's first Django work. The source does not establish exclusive authorship of course templates or framework tutorial examples; those are explicitly retained as reference material with attribution. Original Django admin scaffolding and the DRF quickstart patterns retain their third-party origin.
