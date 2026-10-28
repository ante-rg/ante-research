# TSI-100-v1 Data Description

**Status:** local exploratory profile, 28 October 2026
**Purpose:** describe the released files, their row grains, observable signals, and limits for the first feature and baseline design. This is a schema and aggregate profile, not a model result or a clinical interpretation.

## 1. Dataset at a glance

TSI-100-v1 contains **100 anonymised people**, selected as the 20 newest available registrations from each of five projects. The manifest says the assignment avoids selecting the same protected person more than once. The archive contains each selected account's complete *observed cached* game, payment, bonus, and free-spin history up to an exclusive source cutoff of **2026-09-28**. The selection is deliberately balanced by project count, not by account activity or history length.

The event table has **7,611,732 rows and 48 columns**. The completed-round table has **3,606,452 rows and 16 columns**. The files contain no absolute account dates, personal identifiers, source IDs, transaction IDs, round IDs, notes, or raw JSON. Event times are relative to each account's first observed event; local hour and weekday are retained. Project codes (`P1`–`P5`) and account aliases (`S001`–`S100`) are archive-local pseudonyms.

The sample is large at the **event-row** level and small at the **person** level. A row split would leak information about the same people across train and test. The effective independent sample for player-level claims is at most 100 people, and fewer once harm-event labels are applied. This release is suitable for schema discovery and exploratory feature construction; it cannot establish that a risk model generalises or that a four-level risk scale is calibrated.

## 2. Files and grains

| File | Grain and contents | Main use and caveat |
|---|---|---|
| `events.parquet` | One source-faithful game action, canonical payment/bonus action, or free-spin package result per row. | Main event stream. Includes both player actions and technical/state/result rows. Sort by account and `event_order` for the released account timeline. |
| `rounds.parquet` | One proven completed ordinary round per row, with stake, return, and `bet_result_x`. | Round-level stakes, results, bet gaps, and result delays. Sorted by result availability; bet time and result time are separate. |
| `accounts.csv` | One row per account, with total events, sessions, observed span, bet/result/payment counts, and free-spin package count. | Account-history coverage and aggregate denominators. `bet_events` and `result_events` are raw event counts, not completed-round counts. |
| `account_coverage.parquet` | One row per account with the same coverage dimensions. | Compact coverage table. Do not use it as an independent outcome table. |
| `events_preview.csv` | First 10 events for each of the 100 aliases (1,000 rows). | Format preview only; not a random sample and not suitable for distribution estimates. |
| `data_dictionary.csv` | Declared field names, physical types, and short descriptions. | Several descriptions point back to the README or say only “canonical”; detailed source semantics still need owner confirmation. |
| `quality_report.csv` | Counts by explicit quality flag and account coverage. | Provenance and known extraction limitations. |
| `manifest.json`, `checksums.sha256` | Release metadata, selection, cutoff, file sizes, and hashes. | Reproducibility and file-integrity check. |
| `inspect_history.ipynb` | Two cells: reads the tables and displays coverage plus one account's event rows. | Inspection example only. It is not a profiling or modelling notebook; this profile uses aggregates and does not display player rows. |

The local aggregate profile and figures were generated from the Parquet files, `accounts.csv`, manifest, and quality report. They contain no event-level records or account-level output table.

## 3. Population and observed coverage

There are exactly 20 accounts in each project. Account histories vary sharply:

| Measure | Minimum | Median | 90th percentile | Maximum |
|---|---:|---:|---:|---:|
| Event rows per account | 13 | 26,846 | 239,850 | 640,616 |
| Sessions per account | 1 | 26 | 234 | 579 |
| Observed span in days | 1 | 122 | 615 | 772 |
| Bet events per account | 5 | 12,774 | 111,903 | 280,904 |
| Deposit events per account | 1 | 43 | 345 | 1,352 |
| Withdrawal-request events per account | 1 | 6 | 27 | 348 |

The account-level median observed span differs substantially by project: P1 97 days, P2 620, P3 56, P4 69, and P5 106. Median event counts also differ, from 11,593 in P4 to 53,009 in P2. These are not comparable population rates by themselves. Project, time covered, and account activity are entangled, so cross-project comparisons need exposure-aware, account-level summaries.

A data check confirms that event order starts at 1 and is continuous within every account in this extract. The full event table's order runs to 640,616. There are 7,228 sessions in the account summary. The README defines a new session after a gap of more than 3,600 seconds between player actions.

## 4. Event composition

| `event_type` | Rows |
|---|---:|
| `BET_PLACED` | 3,629,649 |
| `GAME_STATE` | 3,142,500 |
| `BET_RESULT` | 821,216 |
| `DEPOSIT` | 12,150 |
| `BONUS_ACTIVATION` | 2,895 |
| `WITHDRAWAL_REQUEST` | 1,634 |
| `FREE_SPIN_PACKAGE` | 881 |
| `BONUS_CANCEL` | 805 |
| `BONUS_RESULT` | 1 |
| `BONUS_BET` | 1 |

Only **3,647,134 rows** are marked `player_action=true`; **3,964,598** are marked false. Therefore, “event count” is not a count of deliberate player actions. Game-state and result records are part of the chronology and can be useful for reconstructing rounds, but they should not be treated as separate bets.

The most common recorded product is `SLOTS` (7,582,585 rows), followed by `LIVE` (7,089) and `SPORTSBOOK` (3,693). Product and game/provider codes are missing on 18,365 non-game/payment/bonus rows. The archive contains 63 distinct provider codes and 261,575 event-level game codes; codes are local to this archive and are not human-readable product names.

Exploratory aggregate figures were generated during the local profile. The figures and profiling artifacts remain alongside the local data archive and are not included in this repository document. Log axes were used where counts or amounts are highly skewed. Stake and `bet_result_x` histograms use a reproducible random sample of up to 5,000 rows per Parquet batch; reported exact row counts and sums come from full-table passes.

## 5. Round, payment, and amount profile

`rounds.parquet` contains 3,606,452 ordinary completed rounds across all 100 accounts. Stakes are strictly positive in this table. The mean stake is €1.35; a reproducible random sample of 60,000 rounds gives a median of €0.50, a 90th percentile of €2, a 95th percentile of €4, and a 99th percentile of €10. The full-table maximum is €3,005.48. Returns are zero for 79.4% of rounds; the distribution of `bet_result_x` is strongly right-skewed, with median 0, 90th percentile 1, 99th percentile 16, and maximum 7,065.5.

There are 12,150 deposit events. Their `payment_amount_eur` is present on every deposit row: median €23, 90th percentile €99, 95th percentile €100, 99th percentile €200, and maximum €1,000. These are descriptive values for this selected 100-account extract; they are not thresholds or evidence of harm.

A consistency check found that **45,302 of 3,606,452 rows (1.26%)** have `bet_result_x` differing from `returned_eur / stake_eur` by more than 1e-8. The difference exceeds 0.01 on 28,437 rows and exceeds 1 on 386 rows. The data dictionary does not define the formula or rounding policy for `bet_result_x`; this is an unresolved semantics check, not yet evidence of a defect. Confirm the source definition before recomputing or using the ratio as a feature or outcome.

The release README records six potential rounds excluded from `rounds.parquet` because the source showed a positive original stake but a zero EUR equivalent. They came from one account. The event table also has 37 negative `stake_eur` values on `BET_PLACED` rows, and seven negative `returned_eur` values (five on `BET_PLACED`, two on `BET_RESULT`). None appear in the completed-round table. Treat these as source-edge cases to resolve, not as valid negative betting amounts without confirmation.

## 6. Time and availability semantics

- `events.seconds_from_first_event` and `days_from_first_event` are relative to the account's first observed event. They do not reveal calendar dates.
- `local_hour` ranges from 0 to 23. `weekday` ranges from 1 to 7; the exact weekday numbering convention is not declared in the included documentation.
- Session numbering is based on player-action gaps over one hour. `seconds_from_previous_action` is null on every non-player-action row and on 100 player-action rows, likely the first action per account; confirm this assumption before imputing it.
- The 13,784 `DEPOSIT` and `WITHDRAWAL_REQUEST` rows use `TECHNICAL_ADD_DATE_NOT_CONFIRMED_BEHAVIOR_TIME`. Their order/time is not guaranteed to be within 10 minutes of the actual behaviour time. This directly affects the proposed loss-chasing marker and seven-day deposit windows.
- The 3,700 `BONUS_ACTIVATION` and `BONUS_CANCEL` rows use `SOURCE_TIME` and carry `PAYMENT_RAIL_UNRESOLVED` quality flags. They are not deposit events.
- `FREE_SPIN_PACKAGE` rows use `SOURCE_PACKAGE_TIME`; package count and total win are present, but nominal stake is not proven.
- In `rounds.parquet`, `round_order_by_result` follows when the result became available. `bet_seconds_from_first_event` and `bet_session_no` refer to bet placement. Late results can therefore make bet time or bet-session number decrease when rows are read in result order. A feature must use the time when that information became available; otherwise it can leak future outcomes.

## 7. Field reference

Descriptions below translate the supplied dictionary and add cautious working interpretations from field names and the README. Where the source contract is not explicit, treat the description as provisional and confirm it with the data engineer before fixing a production feature definition. `NULL` means the field is absent in the row, not zero.

### `events.parquet` (48 columns)

| Field | Type | Working description |
|---|---|---|
| `share_account_id` | string | Archive-local pseudonym for one of the 100 accounts. |
| `project_code` | string | Anonymised project/brand group (`P1`–`P5`). |
| `event_order` | int64 | 1-based order in the account's full observed history; checked as continuous in this release. |
| `session_no` | int64 | Session number; new session follows a >3,600-second gap between player actions. |
| `event_order_in_session` | int64 | Event's order within its session. |
| `days_from_first_event` | int64 | Whole elapsed days from the account's first observed event. |
| `seconds_from_first_event` | int64 | Elapsed seconds from the first observed event. |
| `seconds_from_session_start` | int64 | Elapsed seconds from the start of the current session. |
| `seconds_from_previous_action` | int64, nullable | Seconds since the previous player action; absent on non-action rows and 100 player-action rows. |
| `local_hour` | int32 | Recorded local hour (0–23). Exact timezone and daylight-saving treatment are not stated. |
| `weekday` | int32 | Recorded weekday code (1–7); mapping is not stated. |
| `event_type` | string | Canonical row type, such as `BET_PLACED`, `GAME_STATE`, `BET_RESULT`, `DEPOSIT`, or `WITHDRAWAL_REQUEST`. |
| `player_action` | bool | Flag distinguishing player-action rows from technical/state/result rows. |
| `product` | string, nullable | Product family, e.g. slots, live casino, or sportsbook. |
| `provider_code` | string, nullable | Salted archive-local provider code; identity is not disclosed. |
| `game_code` | string, nullable | Salted archive-local provider/game code; identity is not disclosed. |
| `bet_count` | int64, nullable | Source-derived bet count/value for the game row; exact scope is undocumented. |
| `win_count` | int64, nullable | Source-derived win count/value for the game row; exact scope is undocumented. |
| `stake_eur` | double, nullable | Source-derived stake amount in EUR. Sparse on non-game rows; 37 negative event values need source clarification. |
| `returned_eur` | double, nullable | Source-derived amount returned in EUR. Its exact relation to `bet_result_x` needs clarification. |
| `bet_open_eur` | double, nullable | Source field for open bet amount in EUR; exact lifecycle semantics are undocumented. |
| `win_open_eur` | double, nullable | Source field for open win amount in EUR; exact lifecycle semantics are undocumented. |
| `bet_refund_eur` | double, nullable | Source field for bet refund amount in EUR. |
| `win_refund_eur` | double, nullable | Source field for win refund amount in EUR. |
| `debit_eur` | double, nullable | Source-derived debit amount in EUR. |
| `credit_eur` | double, nullable | Source-derived credit amount in EUR. |
| `main_bet_eur` | double, nullable | Source-derived main-balance bet amount in EUR. Confirm whether this is mutually exclusive with bonus/free-spin stake. |
| `bonus_bet_eur` | double, nullable | Source-derived bonus-balance bet amount in EUR. |
| `free_spin_bet_eur` | double, nullable | Source-derived free-spin bet amount in EUR; package nominal stake is not proven. |
| `free_spin_win_eur` | double, nullable | Source-derived free-spin win amount in EUR. |
| `bonus_wagered_eur` | double, nullable | Source-derived amount wagered toward a bonus in EUR. |
| `total_balance_eur` | double, nullable | Source-reported total balance in EUR. Not a verified own-funds balance. |
| `internal_balance_eur` | double, nullable | Source-reported internal balance in EUR; exact inclusion rules need confirmation. |
| `bonus_balance_eur` | double, nullable | Source-reported bonus balance in EUR. |
| `balance_after_eur` | double, nullable | Source-reported balance after the game row in EUR. It is not a verified own-funds position. |
| `payment_category` | string, nullable | Payment method/category code; observed values include card, bank, wallet, voucher, and crypto. |
| `payment_amount_eur` | double, nullable | Payment event amount in EUR. The payment event timestamp is technical, not confirmed behavioural time. |
| `payment_delta` | int32, nullable | Source payment/bonus delta code. Its unit and sign convention are undocumented; do not assume EUR. |
| `free_spin_count` | int64, nullable | Number of free spins in a package-level record. |
| `free_spin_total_win_eur` | double, nullable | Package-level free-spin win total in EUR. |
| `funding_source` | string, nullable | Intended funding-source classification; null for all rows in this archive. |
| `funding_source_observed` | bool | Observation mask; false for all rows because the source does not prove real/bonus/mixed funding. |
| `own_funds_position_eur` | double, nullable | Own-funds position; null for all rows because no confirmed ledger is available. |
| `own_funds_position_observed` | bool | Observation mask; false for all rows. |
| `time_semantics` | string | Source timing class, including game time, technical payment add date, bonus source time, and package time. |
| `quality_flag` | string | Explicit provenance/quality boundary for a row, e.g. observed game/payment, unresolved payment rail, or unproven package nominal. |
| `is_session_start` | bool | Marks session boundary/start according to the release's session logic. |
| `is_session_end` | bool | Marks session boundary/end according to the release's session logic. |

### `rounds.parquet` (16 columns)

| Field | Type | Working description |
|---|---|---|
| `share_account_id` | string | Archive-local account pseudonym. |
| `project_code` | string | Anonymised project/brand group. |
| `round_order_by_result` | int64 | Round sequence by result availability, not bet placement. |
| `bet_session_no` | int64 | Session in which the bet was placed. |
| `days_from_first_event` | int64 | Elapsed whole days on the round's result-availability timeline; confirm exact anchor before reuse. |
| `seconds_from_first_event` | int64 | Elapsed seconds on the result-availability timeline. |
| `bet_seconds_from_first_event` | int64 | Elapsed seconds at bet placement. Use to time the bet itself. |
| `seconds_since_previous_bet` | int64, nullable | Gap between bet placements; null on 100 first-bet rows. |
| `result_delay_seconds` | int64 | Delay from bet placement to result availability. |
| `product` | string | Product family for the round. |
| `provider_code` | string | Salted archive-local provider code. |
| `game_code` | string | Salted archive-local game code. |
| `stake_eur` | double | Completed-round stake in EUR; positive in this table. |
| `returned_eur` | double | Completed-round return in EUR, including zero returns. |
| `bet_result_x` | double | Source/canonical round result multiple; formula/rounding needs confirmation. |
| `quality_flag` | string | Constant `CAUSAL_COMPLETED_ORDINARY_ROUND` in this release. |

### `accounts.csv` and `account_coverage.parquet` (10 fields)

| Field | Type in CSV | Working description |
|---|---|---|
| `share_account_id` | string | Archive-local account pseudonym. |
| `project_code` | string | Anonymised project/brand group. |
| `event_count` | integer | Total observed event rows for the account. |
| `session_count` | integer | Number of sessions under the >1-hour player-action gap rule. |
| `observed_days` | integer | Observed history span in days; not a calendar registration age. |
| `bet_events` | integer | Number of `BET_PLACED` event rows. |
| `result_events` | integer | Number of `BET_RESULT` event rows, not necessarily completed ordinary rounds. |
| `deposit_events` | integer | Number of `DEPOSIT` event rows. |
| `withdrawal_request_events` | integer | Number of withdrawal-request event rows. A request is not evidence of a completed withdrawal. |
| `free_spin_packages` | integer | Number of free-spin package rows. |

## 8. Missingness and quality boundaries

Missingness is mainly **structural** and depends on event type:

- The game/product and balance/stake fields listed above are null on 18,365 rows (0.24%), corresponding to non-game or auxiliary event rows. Do not fill these nulls with zero before grouping by event type.
- Payment category and amount are null on 7,597,948 rows (99.82%) and populated on the 13,784 deposit/withdrawal-request rows. `payment_delta` is populated on 17,484 rows, including bonus activation/cancellation events; its definition is not supplied.
- Free-spin count and win total are null on 7,610,851 rows (99.99%), and populated on 881 package rows.
- `funding_source` and `own_funds_position_eur` are null on every row. Their observation masks are false on every row.
- `seconds_since_previous_bet` is missing for 100 rounds; this matches one first bet per account, but confirm before imputation.

The quality report records 7,593,367 `OBSERVED_GAME_ROW` rows, 13,784 `OBSERVED_PAYMENT_EVENT` rows, 3,700 `PAYMENT_RAIL_UNRESOLVED` rows, and 881 `PACKAGE_LEVEL_NOMINAL_UNPROVEN` rows. These flags sum to the 7,611,732 event rows. It also records six excluded zero-EUR-equivalent rounds in one account.

## 9. First feature-readiness view

| Candidate signal | Data availability | Constraint before using it |
|---|---|---|
| Deposit count/amount in a 7-day window (H2, issue #3) | Deposit rows, EUR amounts, and relative event times are present. | Deposit timestamps are technical and may not equal behavioural time. Harm-event labels and a sufficiently large labelled cohort are absent from TSI-100-v1. |
| Deposit soon after balance falls below €1 (H1, issue #2) | Deposit events and game `balance_after_eur` exist. | `balance_after_eur` is not a confirmed own-funds balance; payment timing is not confirmed within the proposed 10 minutes. A causal event join cannot be validated yet. |
| Source-reported balance changes to zero | 3,146,202 of 7,593,367 non-null `balance_after_eur` values are zero; almost all zero rows are non-player-action `GAME_STATE` rows. | This may be an intermediate or technical state, not the player's usable wallet reaching zero. Treat it as a separate exploratory event until the source semantics are confirmed. See the [feature-readiness plan](feature-readiness-and-exploratory-analysis-plan.md). |
| Mean stake and stake variability (H3, issue #4) | Completed rounds include stake and account history time; distributions are strongly skewed. | Define windows at player level and handle repeated rounds within the same person. Confirm result/stake semantics and avoid player-row leakage. |
| Activity intensity, inter-bet gaps, and sessions | Bet rows, relative times, session numbers, and bet gaps are available. | This is observed gaming/payment traffic, not a complete login/clickstream record. Account history length and project differ sharply. |
| Night-time activity | Local hour is present on events. | Timezone and weekday coding are undocumented; use only after confirming these semantics. |
| Harm-risk outcome / green-yellow-orange-red label | No harm event, self-exclusion, staff-review outcome, or severity label appears in these files. | Cannot train or evaluate a supervised risk model or compare against the rule baseline from this release alone. Obtain the agreed person-level labels and their event times. |

For a first feature baseline, aggregate windows at the **person/account** level: for example, rolling 7- and 30-day deposit counts and sums, stake mean/median/variability, bet rate, inter-bet gaps, session duration, and carefully timed post-loss deposits. Keep `player_action` and event type distinctions. Define each feature's *as-of* timestamp and include only information available then. The next modelling stage needs person-level harm labels and their dates, plus enough people to hold out by person. Millions of event rows do not compensate for only 100 sampled people.

The rule-based score in issue #25 is a useful transparent benchmark, but it is not a substitute for measuring incremental early-warning performance. Issue #11 already defines a decision comparison at 5% weekly review capacity and a 7–30 day lead window. TSI-100-v1 cannot run that evaluation because it has no labels and only 100 people. This is a feasibility and feature-definition release, not evidence for either side of the rule-based-versus-model debate.

## 10. Current blockers and next research step

The current sample can define schemas, data-quality checks, provisional features, and a leakage-safe aggregation design. The following are not resolved by these files:

1. Approved harm-event definition, severity mapping, and event timestamps (blocker in issues #2, #3, #4, and #11).
2. Actual-deposit timing error for the technical payment timestamps (direct blocker for issue #2 and a limitation for issue #3).
3. Source definitions for `bet_result_x`, `payment_delta`, balance fields, weekday coding, timezone, and session boundary flags.
4. A larger labelled extract, with multiple accounts for each person linked safely, before grouped model evaluation.

The issue-linked paper comparison is recorded in the [Literature-to-Data Comparison](literature-to-data-comparison.md). The recommended next actions—including field-semantic checks, point-in-time snapshots, unsupervised descriptive analysis, and label requirements—are in the [Feature Readiness and Exploratory Analysis Plan](feature-readiness-and-exploratory-analysis-plan.md).

## 11. Reproduction and provenance

- Source repository: [ante-research](https://github.com/ante-rg/ante-research)
- Source release: [TSI-100-v1](https://github.com/ante-rg/ante-research/releases/tag/tsi-100-v1)
- The original README, data dictionary, manifest, and quality report are included in the [TSI-100-v1 release archive](https://github.com/ante-rg/ante-research/releases/tag/tsi-100-v1). The archive is kept locally under `data/raw/TSI-100-v1/`, which is ignored by Git.
- Profiling was performed locally from the released Parquet files. The script, aggregate profile JSON, and exploratory figures remain local to the workspace and are not included here.
- This document contains aggregate descriptions only. Do not stage the raw archive, player-level records, or derived player-level tables.
