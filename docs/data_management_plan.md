# ANTE data management plan (draft)

## Data inventory and access gate

No operator data or representative harm labels have been received or inspected. Jurijs identifies Curaçao as the operator's jurisdiction and reports that clauses 3.2, 3.7 and 11.1 of the customer agreement permit use and transfer of gameplay information for Data Science purposes, including model training. Their wording and applicability to the intended data, team and transfer have not been independently reviewed; locations of players, processing and recipients are unknown. The candidate [public payments dataset](https://doi.org/10.17632/9j5gcygnwg.1) is licensed CC BY 4.0, but its obfuscated customer keys and transaction histories remain potentially linkable. Record its exact downloaded version, checksum, dictionary and attribution before analysis. The project must not ingest private operator data until the current agreement wording has been obtained and reviewed for applicability to the specific dataset, purpose, team and transfer, and any applicable course/ethics requirements, fields, access list, storage location and retention/deletion decision are documented.

## Storage and publication

- Keep raw source files immutable under `data/raw` or `data/external` in the research workspace. Both are ignored by Git. Store restricted data only in an approved access-controlled location.
- Store derived individual-level files under ignored `data/interim` or `data/processed`. Do not commit data rows, player IDs, individual predictions or trained models.
- Publish schemas, code, tests with wholly synthetic fixtures, aggregate quality summaries and charts only after a disclosure check. Suppress small cells and unusual trajectories that could identify a player.
- Keep credentials in a managed secret store, never `.env`, logs, notebooks, screenshots or repository history. `.env.example` contains placeholders only.
- Document any external transfer and prohibit unapproved upload to AI tools or third-party services.

## Quality and provenance

For each source, capture owner, URL/DOI, license, version/date, file checksum, data dictionary, period, population, limitations and any transformations. Quality reports should use counts and rates for missing IDs/times/amounts, duplicates, invalid currencies, timezone ambiguity and coverage gaps. Preserve raw input and make cleaning decisions reversible and reproducible.

## FAIR and retention

Make public-safe metadata and code findable through the portfolio README, cite datasets by DOI, and describe reusable schemas and execution steps. Keep restricted player-level records closed as necessary. Before project completion, record who owns each dataset, whether copies must be deleted, the deadline for deletion and evidence of completion. An unconfirmed retention rule is a blocker to importing private data, not permission to keep it indefinitely.

## Human oversight and reporting

The demonstration uses synthetic or explicitly approved de-identified records. Scores or indicators are for human review only. Reports separate descriptive findings, proxy-label evaluation and unmeasured real-world benefit. The team will disclose AI assistance according to course policy and verify every generated statement and citation.
