# TSI-100-v1 Feature Readiness and Exploratory Analysis Plan

**Status:** working research plan, 28 October 2026
**Related documents:** [Data Description](data-description.md) · [Literature-to-Data Comparison](literature-to-data-comparison.md)
**Purpose:** turn the current data profile and literature review into a short, reviewable work plan. This plan does not define a clinical label or claim that the current extract can validate a risk model.

## 1. Current position

TSI-100-v1 contains a large event history for 100 people, but it has no PGSI responses, self-exclusion records, staff-review outcomes, intervention records, or approved harm-event labels. It can support data-quality checks and feature construction. It cannot currently support supervised training or a credible estimate of player-level generalization.

The first useful data object is a **person-by-index-time snapshot**: one row per person and chosen prediction time, with each feature computed only from information available by that time. Raw event rows are not independent training examples; a player with a longer history must not contribute hundreds of thousands of nominally independent observations.

## 2. Candidate feature families

The literature review suggests testing these families as candidate signals, not assuming that they identify harm:

| Family | Candidate measures | Initial data check |
|---|---|---|
| Activity frequency and pace | Bets per active day/session, active days, inter-bet gaps, session length and round count | Use player-action and completed-round rows; do not count state/result rows as separate bets. Confirm the session rule and available timestamps. |
| Stakes and variability | Mean/median stake, IQR, standard deviation or CV, upper quantiles, recent change from personal baseline | Inspect skew and extreme values; compute robust measures and avoid universal euro cutoffs. |
| Trajectory | 7-/30-day rate changes, robust slope, recent-to-baseline ratios | Account for different observation lengths and avoid windows without adequate exposure. |
| Returns and apparent losses | Net return/loss by session and window; subsequent behavior after loss, win, and break-even | Use results only once available; verify the `bet_result_x` definition and reconciliation. |
| Deposits | Count and amount per window/session; repeated deposits; category diversity | Validate that payment timestamps represent behavior time and confirm category semantics. |
| Balance transitions | Source-reported `balance_after_eur` state and transitions into zero | Confirm source semantics before interpreting as wallet depletion, own funds, loss chasing, or harm. |
| Time/product context | Activity by local hour/weekday, product breadth | Confirm timezone and weekday mapping; control for project and exposure differences. |

Compare both fixed-window summaries and changes from a player's own prior behavior. A high absolute stake is not by itself evidence of escalating harm; a change relative to personal history is a separate, testable hypothesis.

## 3. Exploratory check: balance values equal to zero

An aggregate scan in account `event_order` found 3,146,202 exact-zero values among 7,593,367 non-null `balance_after_eur` values and no negative values. Almost all zero rows were `GAME_STATE` records with `player_action=false` (3,142,500 rows). Only 3,672 zero-valued rows were `BET_PLACED`, and 29 were `BET_RESULT`.

The same ordered scan found 2,644,323 adjacent transitions from a positive `BET_PLACED` balance to a zero `GAME_STATE` balance. This is a transition in the released source field, **not yet a verified account-depletion event**. Its concentration in non-player-action state rows means the field may represent an intermediate or technical game state. `own_funds_position_eur` is null and its observation mask is false throughout the archive.

Therefore, zero balance should not be used as a harm label or as evidence of loss of control. It can be investigated as a distinct, source-reported event only after the data owner confirms what `balance_after_eur` means, which balance ledger it represents, and why `GAME_STATE` rows commonly contain zero. If confirmed, define a transition explicitly (for example, positive to zero) and separate it from merely observing a zero value.

## 4. Can unsupervised learning help?

Yes, as an **exploratory description of behavior**, not as a way to discover addiction labels automatically. Clustering can show whether this small extract contains recurring activity profiles or trajectories. It cannot tell us that one cluster is “addicted” unless an independent harm-related outcome later validates that interpretation.

Do not cluster all 7.6 million event rows as though they were independent people. First construct a compact feature vector per account or a controlled set of person-time snapshots. For the first pass:

1. Start with a small, interpretable feature set: activity frequency, session pace, stake level and variability, personal-baseline changes, and validated payment measures. Exclude unverified balance and payment-timing signals from any risk interpretation.
2. Transform heavily skewed counts and amounts, scale features, and inspect missingness and outliers before clustering. Compare results with and without monetary amounts because these may reflect affordability and project differences.
3. Compare a small number of simple methods (for example, hierarchical clustering and k-means) and inspect dimensionality-reduction plots only as visual aids. Do not select a method because a plot looks neatly separated.
4. Check whether profiles survive reasonable changes in windows, feature sets, scaling, and resampling by person. Examine whether clusters mostly encode history length, activity volume, or project membership.
5. Describe each resulting group using its original features and call it a behavioral profile. Do not convert cluster IDs into green/yellow/orange/red risk levels without an independent outcome.

With only 100 people, any cluster structure will be tentative. The millions of events help estimate each account's behavior, but do not provide millions of independent people.

## 5. Five-step work plan

1. **Confirm field semantics.** Ask the data owner about payment time, `balance_after_eur` and the balance components, `bet_result_x`, timezone, weekday numbering, and session boundaries. Record which fields are confirmed, provisional, or unusable. Existing issues: [#15](https://github.com/ante-rg/ante-research/issues/15), [#16](https://github.com/ante-rg/ante-research/issues/16). The zero-balance check has a dedicated follow-up: [#28](https://github.com/ante-rg/ante-research/issues/28).
2. **Check feature feasibility.** For hypotheses #2–#6, establish which candidate can be computed from the current files, its usable coverage and exposure denominator, and what semantics block interpretation. Preserve the difference between computable and validated. Existing issues: [#2](https://github.com/ante-rg/ante-research/issues/2), [#3](https://github.com/ante-rg/ante-research/issues/3), [#4](https://github.com/ante-rg/ante-research/issues/4), [#5](https://github.com/ante-rg/ante-research/issues/5), [#6](https://github.com/ante-rg/ante-research/issues/6), [#16](https://github.com/ante-rg/ante-research/issues/16).
3. **Build point-in-time snapshots.** Specify the index-time schedule, 7-/30-day lookback windows, person/account keys, feature-availability rules, and missingness representation. Keep the output local while using TSI-100-v1; never write player-level rows into Git. Backlog issue: [#29](https://github.com/ante-rg/ante-research/issues/29).
4. **Run two descriptive explorations.** First, profile the candidate signals at account and snapshot level. Second, investigate source-reported balance transitions as a separate event and perform tentative unsupervised behavioral segmentation only after snapshots and field checks are ready. These outputs are descriptive and do not label harm. Backlog issues: [#28](https://github.com/ante-rg/ante-research/issues/28) and [#30](https://github.com/ante-rg/ante-research/issues/30).
5. **Obtain independent outcome labels, then evaluate.** Continue the requests for self-exclusion and staff-review data; define which event is a harm-related outcome, its severity, and when it becomes knowable. Only then compare the frozen rule baseline with a learned model using the existing 5% review-capacity decision protocol. Existing issues: [#17](https://github.com/ante-rg/ante-research/issues/17), [#22](https://github.com/ante-rg/ante-research/issues/22), [#25](https://github.com/ante-rg/ante-research/issues/25), [#11](https://github.com/ante-rg/ante-research/issues/11).

## 6. Guardrails for interpreting results

- A zero in `balance_after_eur` is not a gambling-harm label. It is not even confirmed to mean that the player's own available funds reached zero.
- Unsupervised clusters describe similarity under the chosen features and scaling. They do not establish severity, diagnosis, causality, or intervention need.
- A rule derived from the same fields as an operator label is not independently validated against that label.
- Use player-level grouping for any train/test split. Keep the raw archive, account-level feature snapshots, and evaluation artifacts derived from real player histories out of Git.
- Keep feature definitions, label definitions, and evaluation rules in English in the repository. Keep raw player-level outputs local and excluded from source control.
