# Ante Research Protocol (Draft)

## Purpose and Claim Boundary

Ante studies whether time-aware behavioural summaries can prioritise potential gambling-related harm for **human review**. It does not diagnose gambling disorder or automate player contact, account restrictions, or production decisions. This protocol is a plan; it records no empirical result.

## Data Route Decision

1. Record each candidate source's owner, license, fields, population, period, allowed uses, retention and access controls.
2. Use a player-level source only after the team records permission and the approved storage/publication boundary.
3. The public [Ghaharian payment dataset](https://doi.org/10.17632/9j5gcygnwg.1) can support exploratory payment analysis. It does not provide a verified harm label, bets, sessions or gambling loss. Its obfuscated identifier still needs controlled handling.
4. If representative outcome labels and permissions are unavailable by 23 October 2026, switch to the declared descriptive/feasibility route. Do not train a purported harm classifier on invented labels.

## Canonical Prototype Event Contract

The initial pipeline accepts a deliberately narrow payment-event CSV, separate from any source-specific adapter:

| Column | Meaning | Validation |
| --- | --- | --- |
| `event_id` | Stable event identifier | Non-empty and unique |
| `player_id` | Pseudonymous player key | Non-empty; never export raw rows to public reports |
| `event_time` | Event occurrence instant | Explicit timezone; normalized to UTC |
| `event_type` | `deposit` or `withdrawal` | Exactly one of these two values |
| `amount` | Positive transaction amount | Finite, greater than zero |
| `currency` | Transaction currency | Three uppercase ASCII letters; registry membership is not yet validated |

This contract is not a claim that the public dataset has these columns. A source adapter and dictionary must be approved before importing external rows. Separate currencies are never summed together. `deposit amount - withdrawal amount` is called **net deposits**, not gambling loss.

## Prediction Time and Features

At an `as_of` instant, use events in `[as_of - 7 days, as_of)` and `[as_of - 30 days, as_of)`. A timestamp equal to `as_of` belongs to the future for that prediction. Features are deposit/withdrawal counts and amounts and net deposits per player and currency. Bet, session, failed-payment and responsible-gambling-tool signals are out of scope until a permitted source supplies them. Tests cover UTC offsets, lookback boundaries, currencies, invalid events and future-event leakage.

## Evaluation, Only If Labels Become Available

Freeze the cohort, prediction instant, outcome proxy, horizon, observation window and review budget before model fitting. Record who is assessed and why: analyst-reviewed players are selected, and unreviewed players are not verified negatives. Split by time, keep every player out of both train and test where feasible, and ensure no post-outcome features. Compare a transparent rule baseline with logistic regression at the same review capacity. Report observed proxy precision and uncertainty; population recall, false-negative rate, calibration and lead time require a defensible representative adjudication design. Examine available permitted subgroups with adequate samples and state which groups cannot be assessed. Do not infer harm reduction from a ranking metric.

The current model prototype accepts **separately supplied**, single-currency training and holdout CSVs. Each row has one player, an aware `as_of_utc`, the ten 7/30-day payment features, a binary `label`, and an aware `label_available_at_utc`. A documented source must establish the label meaning and why it was available at that time; code checks format and timing, not truth. Training and holdout players must be disjoint, and every training label must be available before the first holdout prediction instant. The JSON artifact rejects prediction instants at or before that availability boundary. The fixed baseline ranks by 30-day net deposits; the model ranks by logistic-regression score. The aggregate report compares proxy precision for the same review capacity. The local API accepts canonical events and returns relative scores for human review; its separate UI is pending.

## Iteration and Evidence

Every Kanban card states: **Question → Create → Observe → Analyze → Decision**. Define Observe before building. Link code, tests, aggregate outputs, written analysis and a backlog decision. A card is Done only after those links are present. Weekly reviews record attendance, decisions, feedback, contributions and unresolved risks. Public portfolio evidence must not contain player rows, individual predictions, credentials or unapproved private data.

## Sources for the Initial Framing

- [UK Gambling Commission remote customer-interaction guidance, Requirement 5](https://www.gamblingcommission.gov.uk/guidance/customer-interaction-guidance-for-remote-gambling-licensees-formal-guidance/requirement-5-customer-interaction-guidance-for-remote-gambling-licensees-sr): indicator taxonomy for licensed UK remote operators; regulatory applicability to Ante has not been established.
- [Andersson et al. (2025)](https://doi.org/10.1556/2006.2025.00013): time-aware analysis of operator account data, with study-specific labels and access.
- Mindway AI [GameScanner](https://mindway.ai/gamescanner/) and Kindred's [PS-EDS](https://www.kindredgroup.com/contentassets/9f72062caa9b41e69f1b7443620cd8be/kindred-groups-ars--och-hallbarhetsrapport-2023-engelska.pdf): existing approaches, described by their vendors/operators. Their claims are not Ante results or independent benchmarks.
