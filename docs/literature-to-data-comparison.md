# Literature-to-Data Comparison for TSI-100-v1

**Status:** targeted narrative synthesis, 28 October 2026; updated 29 October 2026 with issues #5 and #6
**Scope:** papers linked from research issues #2, #3, #4, #5, #6, and #11 in the group repository. This is not a systematic review. The summaries separate each paper's measured outcome from the project's proposed harm-risk target.

The proposed feature checks and next research actions are summarized in the [Feature Readiness and Exploratory Analysis Plan](feature-readiness-and-exploratory-analysis-plan.md).

## 1. What the attached papers actually predict

The issue references do not all study the same outcome:

| Outcome in a paper | What it means | What it does not establish |
|---|---|---|
| Future voluntary self-exclusion (VSE) | A player later chooses or activates an exclusion tool. | A clinical diagnosis, severe harm, or a regulator-confirmed need to suspend play. A person may self-exclude for reasons other than gambling harm, and some people experiencing harm may not self-exclude. |
| Self-reported PGSI / problem-gambling screen | The player reports symptoms or consequences on a questionnaire. | A clinical diagnosis by itself; responses may also be selective or incomplete. |
| Operator/manual responsible-gambling risk assessment or alert | Staff classify a flagged account, or an operator's alert system flags it, under one operator's procedures. | An independent ground truth if the same behaviors also feed the model or influenced who was reviewed or flagged. |
| Account closure attributed to gambling problems | The player closes the account and gives gambling problems as the reason. | A clinical diagnosis or a complete record of harm; players who close for other reasons, or do not close at all, may also be experiencing harm. |

This distinction matters for the proposed green/yellow/orange/red scale. None of the attached papers validates those four colors as universal levels. Most train or report a binary outcome, and their outcomes cannot be pooled as though they were interchangeable labels for addiction.

## 2. Paper-by-paper summaries

### Auer & Griffiths (2023): self-reported problem gambling in an online casino

**Question and design.** The authors linked online-casino account activity to players' self-reported Problem Gambling Severity Index (PGSI) answers. They used a 30-day feature window before the questionnaire and evaluated random-forest and gradient-boosting models. Of 1,287 respondents, 945 remained after a response-quality exclusion; 248 of those retained players had PGSI scores of at least 8. The sample consists of people who chose to complete a questionnaire that was available on the site, not a random sample of all account holders.

**Findings.** Higher-risk self-report was associated with more money lost per gambling day or session, more deposits per session, and more frequent depletion of the gambling-account balance. The reported test ROC-AUC was about 0.73 for random forest and 0.67 for gradient boosting. The paper treats these as predictive associations, not causal effects.

**Transfer to TSI-100-v1.** We can construct 30-day and session-level bet frequency, stake, observed return/loss, and deposit-count summaries. The paper gives a useful feature-definition precedent and, importantly, links behavior to a questionnaire outcome rather than to self-exclusion alone.

**Limits here.** TSI has no PGSI responses. `balance_after_eur` is not verified as own funds, and deposit timestamps are marked as technical timestamps whose alignment with actual payment behavior is unconfirmed. Therefore the paper's account-depletion and deposit-timing features cannot be reproduced faithfully. Its AUC is not a performance expectation for our data.

Source: [Auer & Griffiths (2023), Journal of Gambling Studies](https://doi.org/10.1007/s10899-022-10139-1).

### Andersson et al. (2025): temporal prediction of operator risk assessments

**Question and design.** The study uses 4.5 years of data from 35,048 authenticated customers at one Swedish operator. It combines bets, transactions, sessions, payment data, responsible-gambling activity, and manual risk assessments. The authors carefully align features to assessment dates and use temporal validation. Assessments focused on accounts already flagged for review, so the data are enriched for at-risk customers rather than sampled from the full player population.

**Labels and findings.** Staff assigned risk levels using information that included deposit patterns, session length, denied transactions, responsible-gambling tool use, and in some cases self-reported loss of control. An initial six-level classification performed poorly; the authors grouped the labels into low versus elevated risk. Their holdout metrics were modest: ROC-AUC around 0.61–0.62 for 30-, 60-, 90-day, and full-data variants, despite high recall at the selected operating point and low specificity. The paper reports that the manual labels were inconsistent over time and that many “unknown risk” records required special handling.

**Transfer to TSI-100-v1.** The strongest transferable lesson is methodological: define an as-of time, compute features only from information available by then, preserve temporal order, and inspect the consequences of the label process. Rolling 30/60/90-day features and changes over time are appropriate candidates.

**Limits here.** TSI contains no manual assessments, denied transactions, responsible-gambling tools, or verified outcomes. If our future labels are generated from rules based on deposits and session length, training on those same inputs risks teaching the model to reproduce the labeling rule. The paper also cautions against assuming four finely graded levels will be learnable; it had to collapse its original classes to two.

Source: [Andersson et al. (2025), Journal of Behavioral Addictions](https://doi.org/10.1556/2006.2025.00013); [open article PDF](https://real.mtak.hu/221839/1/2006-article-p490.pdf).

### Haeusler (2016): payment behavior and future self-exclusion

**Question and design.** This case-control study used transaction histories for 2,696 bwin.com accounts, including 1,348 players who later self-excluded and 1,348 active controls. It asks whether payment behavior can help identify future self-exclusion.

**Findings reported in later peer-reviewed summaries.** Deposit frequency and amount, withdrawal variability, reversed-withdrawal funds, and mobile-phone billing were associated with later self-exclusion. The original article's full text was not available in the source check for this synthesis, so detailed model-performance claims are intentionally omitted.

**Transfer to TSI-100-v1.** Deposit count and amount can be profiled in fixed windows; payment-category diversity may be explored where categories are populated. These should be tested as candidate signals, not treated as standalone signs of harm.

**Limits here.** Our payment event times have unresolved behavioral-time alignment. The archive does not provide a confirmed reversed-withdrawal event or dependable payment-rail semantics. VSE is also not equivalent to a harm diagnosis. This paper supports investigating payment features only after those fields are validated.

Sources: [Haeusler (2016), International Gambling Studies](https://doi.org/10.1080/14459795.2016.1158306); the accessible summary of its reported associations is also given in [Hopfgartner et al. (2023)](https://doi.org/10.1007/s10899-022-10149-z).

### Hopfgartner et al. (2023): future self-exclusion across operators and countries

**Question and design.** The authors analyzed 25,720 players from three operators in six European countries; 414 (1.61%) self-excluded in the following month. Behavior in November and December 2020 was used to predict January 2021 self-exclusion. The study required at least three active days in December and aggregated behavior relative to each player's last gambling day.

**Findings.** Across countries, future self-exclusion was associated with previous limit changes or self-exclusions, more deposit payment methods, more deposits per session, and playing more game types. Monetary-intensity features such as stakes, losses, and deposits did not add significant predictive information in five of six countries after behavioral features were included. Cross-country/operator prediction ROC-AUC ranged about 0.67–0.79. The authors explicitly note that self-exclusion is an imperfect proxy for gambling problems.

**Transfer to TSI-100-v1.** Deposit counts per session, activity frequency, and product/game variety are testable candidates. Their design also supports evaluating transfer across the five project groups instead of assuming one group's patterns apply to all.

**Limits here.** TSI does not include prior limit-setting or self-exclusion actions. The five project groups have markedly different history coverage and activity levels, so raw group comparisons are confounded by exposure and selection. A random event-row split would leak player-specific behavior; all splits must be grouped by person, and validation should also probe project-level drift.

Source: [Hopfgartner et al. (2023), Journal of Gambling Studies](https://doi.org/10.1007/s10899-022-10149-z).

### Braverman & Shaffer (2012): early behavioral trajectories in online betting

**Question and design.** The authors used the first month of online betting activity and longitudinal clustering to identify behavioral subgroups, then examined later account closure attributed to gambling problems. The reported high-risk subgroup represented only a small part of the sample.

**Findings.** The subgroup later associated with problem-related closure showed more frequent and intensive betting, greater variability in wager size, and increasing wager amounts during the first month. The authors describe these as candidate markers and call for more work to identify risk markers that cover more of the population.

**Transfer to TSI-100-v1.** We can calculate bets per active day/session, stake dispersion (median, interquartile range, and coefficient of variation where meaningful), and within-player stake trends. Comparing each account with its own prior baseline may be more informative than applying one absolute euro threshold to all players.

**Limits here.** This is a trajectory/clustering result, not a validated four-class supervised model. Its outcome is account closure attributed to gambling problems; the population is betting rather than predominantly casino slots. Treat the reported behavior as hypotheses to test, not as known casino-risk rules.

Source: [Braverman & Shaffer (2012), European Journal of Public Health](https://doi.org/10.1093/eurpub/ckp232).

### Finkenwirth et al. (2021): self-exclusion status and betting variability

**Question and design.** A one-year PlayNow.com dataset compared 2,157 players with a voluntary self-exclusion record against 17,526 controls using 20 behavioral variables. A random forest achieved AUROC 0.75 (SD 0.01); reported performance across model variants was about 0.65–0.76.

**Findings.** Variance in money bet per session had the greatest feature-importance signal. The paper tests model choices such as balanced training data and inclusion thresholds. Its target is a VSE record, not a directly measured clinical diagnosis or a standardized prospective harm event.

**Transfer to TSI-100-v1.** The completed-round file supports session-level stake dispersion. This is a strong candidate for comparison with mean stake and betting frequency, with skew-resistant statistics and personal-baseline changes included.

**Limits here.** We have no VSE label. The TSI sample has only 100 people, even though it has millions of rounds; it cannot support a credible player-level generalization test. The result does not establish that stake variability is harmful by itself.

Source: [Finkenwirth et al. (2021), International Gambling Studies](https://doi.org/10.1080/14459795.2020.1832132).

### Percy et al. (2016): supervised prediction under a rare self-exclusion outcome

**Question and design.** The study compared four supervised learning approaches on 845 online gamblers, with fewer than 1% self-excluding. Random forest performed best in their analysis, improving accuracy by 35 percentage points over baseline estimates. The authors stress the need to address the rare outcome through balanced training data.

**Transfer to TSI-100-v1.** The paper is relevant to evaluation design: report what happens to the rare positive class and do not use accuracy as the main success measure. It supports comparing a transparent baseline with a learned model when a suitable label exists.

**Limits here.** It predicts self-exclusion, not future harm, and its reported accuracy improvement cannot be compared directly with the project's proposed “recall within a 5% weekly review capacity.” That queue metric must be measured on our own temporally valid, independently labelled test population.

Source: [Percy et al. (2016), International Gambling Studies](https://doi.org/10.1080/14459795.2016.1151913).

### LaBrie & Shaffer (2011): betting patterns of players who closed accounts over gambling problems

**Question and design.** A secondary analysis of the first two years of a longitudinal bwin cohort of 47,134 Internet sports-betting subscribers. Of these, 679 closed their accounts and gave a reason. The authors compared closers who cited gambling problems with closers who gave other reasons.

**Findings reported in the abstract and later summaries.** About half of the closers who cited gambling problems formed a distinct, homogeneous group. Compared with other closers, they placed more and larger bets, bet more frequently, and were more likely to bet intensively soon after enrollment. The pattern was confirmed on an independent sample of closers. The original article's full text was not available in the source check for this synthesis, so group sizes and effect sizes are intentionally omitted.

**Transfer to TSI-100-v1.** Bets per active day can be computed from completed rounds by bet placement time. The early-intensity finding also supports comparing players at the same time since their first event.

**Limits here.** The outcome is a self-reported closure reason, and the comparison group is other closers rather than active players. The population is sports betting, while our dataset is casino play, so absolute bet counts per day are not comparable. The study describes early tenure, not a look-back window before a dated event.

Source: [LaBrie & Shaffer (2011), Addiction Research & Theory](https://doi.org/10.3109/16066359.2010.512106).

### Gray, LaPlante & Shaffer (2012): players who triggered operator responsible-gambling alerts

**Question and design.** The study compared 2,066 bwin subscribers who triggered the operator's responsible-gambling alert system with 2,066 controls who had the same amount of exposure to the service. It used discriminant function analysis on actual gambling records.

**Findings reported in the abstract.** Indices of gambling intensity, such as total number of bets and number of bets per betting day, best distinguished cases from controls, particularly for live-action sports betting. Control players behaved similarly to the operator's wider player population. The full text was not available in the source check for this synthesis.

**Transfer to TSI-100-v1.** This is the closest precedent for H5: bets per active day compared against controls matched on exposure, which our design approximates by matching on brand and time since first event.

**Limits here.** The outcome is an operator alert, not an independent harm measure. The abstract does not say what triggered the alerts; if activity volume contributed, the intensity result is partly circular. The same risk applies to our own labels if they come from an operator process.

Source: [Gray, LaPlante & Shaffer (2012), Psychology of Addictive Behaviors](https://doi.org/10.1037/a0028545).

### UK Gambling Commission (2023): customer interaction guidance for remote operators

**What it is.** Formal guidance under Social Responsibility Code 3.4.3, in force from 31 October 2023 and last updated in October 2024. Requirement 5 sets the minimum categories of indicators of harm that remote operators must monitor. Time spent gambling is one category, and time of day, "for example late night", is listed within it. The guidance states that "a higher percentage of overnight gamblers were found to be problem gamblers, than during other times of day".

**Transfer to TSI-100-v1.** This is the operational source of the night-time marker in H4. A result on our data is useful either way, because operators are already expected to monitor this indicator.

**Limits here.** This is regulation, not an evaluation of the marker. It does not define night hours, give a threshold, or cite the study behind the overnight claim. It does not show that a night-time share predicts a dated harm event.

Source: [UK Gambling Commission, Customer interaction guidance for remote gambling licensees, Requirement 5](https://www.gamblingcommission.gov.uk/guidance/customer-interaction-guidance-for-remote-gambling-licensees-formal-guidance/requirement-5-customer-interaction-guidance-for-remote-gambling-licensees-sr).

### McAuliffe et al. (2022): industry "Markers of Harm" in two cohorts of sports bettors

**Question and design.** The study evaluated nine "Markers of Harm" that a consortium of gambling companies had committed to using to estimate the risk of gambling-related harm. Late-night play is one of the nine. Each marker is scored from 0 (no risk) to 3 (high risk). The markers were tested in two independent cohorts of online sports bettors collected ten years apart.

**Findings reported in the abstract and later summaries.** Over two years, most users never reached an overall score high enough to indicate an intervention. The most active users were more likely to exceed the thresholds. The authors suggest this may reflect lower-risk samples, but also overly high thresholds or flaws in the design of some markers. Delfabbro et al. (2024) summarize that most markers predicted the study's proxies for higher-risk gambling and cite the paper as support for late-night play. The full text was not available in the source check for this synthesis, so the late-night marker's own result has not been verified here.

**Transfer to TSI-100-v1.** The closest published test of late-night play as a stand-alone marker in account data.

**Limits here.** Sports betting, where late-night activity partly reflects which events are on offer; casino play is available at any hour. The markers come from an industry scoring scheme with arbitrary thresholds, and the outcomes are proxies.

Source: [McAuliffe et al. (2022), Journal of Gambling Studies](https://doi.org/10.1007/s10899-021-10097-0).

### Delfabbro, Parke & Catania (2024): review of behavioral tracking studies

**Question and design.** A narrative review of studies that use objective account data from online operators. It groups behavioral indicators into categories: gambling intensity, variability, trajectories over time, anomalies in timing (play at night or on weekdays rather than weekends), self-recognized risk such as exclusions and account closures, and product risk.

**Findings.** The review concludes that late-night gambling "appears to be generally supported" as an indicator of higher-risk gambling, citing Forrest & McHale (2022) and McAuliffe et al. (2022). Its rationale is that people with less control over their gambling may play at night to hide it, or because they cannot stop.

**Transfer to TSI-100-v1.** Supports H4 as a recognized indicator category and places it next to the intensity markers in H5.

**Limits here.** The evidence for the timing category is thin: one of the two cited studies (Forrest & McHale, 2022) reports that bet levels are higher late at night, which describes play rather than linking it to harm. The review does not identify a study showing that the share of night-time play predicts a dated harm event on its own.

Source: [Delfabbro, Parke & Catania (2024), Journal of Gambling Studies](https://doi.org/10.1007/s10899-023-10247-6).

## 2A. Additional literature found for the observable TSI signals

These papers were found in a targeted follow-up search. They were not linked from the issues covered above. They add evidence on self-reported outcomes, loss-chasing definitions, and the limits of event-based interpretations.

### Hopfgartner et al. (published online 2024): self-reported PGSI across three countries

This study used 1,743 online casino players from Great Britain, Canada, and Spain who completed PGSI; 478 players (27.4%) scored 8 or higher. It tested 30-day behavior, including session length, deposits per session, account depletion, prior self-exclusion, and monetary intensity. Frequent in-session deposits, account depletion, prior self-exclusion, and shorter mean session length were associated with self-reported problem gambling in at least one country. Adding monetary totals did not improve the country-specific regression models after behavior was included. Models generalized weakly when a country was left out; including data from each country improved scores. The sample consists of voluntary PGSI respondents, so its prevalence and model results should not be treated as population estimates.

**TSI relevance:** strengthens the case for testing behavior-normalized features (deposit count per session, session/activity patterns) alongside monetary totals. It does not validate TSI's deposit timestamps or account balance. The article appeared online in 2024 and is assigned to a 2026 journal volume.

Source: [Hopfgartner et al., International Journal of Mental Health and Addiction](https://doi.org/10.1007/s11469-024-01312-1).

### Murch et al. (2023): PGSI prediction from one year of platform data

This study linked PGSI responses from 9,145 adults on a Canadian platform to the preceding 12 months of account data. Its best random-forest models reported ROC-AUC 0.843 for PGSI 5+ and 0.825 for PGSI 8+. Important features included betting frequency and variability and repeat engagement. The outcome is retrospective self-reported risk, and participants needed only one real-money bet in the preceding year. A later discussion of the study notes that the large number of inactive players could have helped distinguish higher from lower PGSI scores. The AUC therefore should not be read as evidence that the same model can forecast an approaching harm event.

**TSI relevance:** supports measuring both level and variability of activity, while underscoring the need to compare active players with similarly active players and test a forward prediction window rather than merely separating activity from inactivity.

Source: [Murch et al. (2023), Addiction](https://doi.org/10.1111/add.16179).

### Auer & Griffiths (published online 2022): operationalizing loss chasing

Using 16,771 players from three countries, the authors compared five account-based definitions: within-session, across-session, and across-day chasing; repeated low account balance at session end; and frequent in-session depositing. Frequent session depositing showed the clearest relationship with the study's risk categories. Those categories came from the operator's `mentor` tool, whose score already used spending, time, failed deposits, cancelled withdrawals, and limit-setting. The paper is therefore useful for comparing candidate chasing definitions, but the agreement with its operator score is not an independent validation against PGSI or clinical diagnosis. It also does not establish that every repeated deposit sequence is loss chasing.

**TSI relevance:** of the five candidates, deposit count per session is the one most directly testable in principle. In this release, payment event time is explicitly unconfirmed as behavioral time, and `balance_after_eur` is not verified as the player's own available funds. The feature should remain blocked pending source clarification. Across-session or across-day metrics based on wager and return sequences may be explored separately, with the result-availability time respected.

Source: [Auer & Griffiths, Journal of Gambling Studies](https://doi.org/10.1007/s10899-022-10144-4).

### Zhang et al. (2024): return time after a winning or losing casino visit

This study analyzed about 1.91 million online-casino sessions from 15,544 people. It defined between-session chasing as the time until the player returned after a winning or losing visit. On average, players tended to return more slowly after losses and more quickly after wins. The authors therefore found limited evidence for average loss chasing in this measure, while finding clearer win-chasing patterns; results also differed by game type.

**TSI relevance:** this is a useful counter-hypothesis for any rule that interprets a loss followed by later activity as loss chasing. A better test would compare a player's return interval after losing, winning, and break-even sessions, controlling for their ordinary return pattern. TSI could support a provisional timing analysis, but it has no harm label, and round results must be known by the prediction time.

Source: [Zhang et al. (2024), Journal of Behavioral Addictions](https://doi.org/10.1556/2006.2024.00022).

## 2B. PGSI in plain terms

Yes: **PGSI is a questionnaire that the player fills in about their own gambling.** The full Problem Gambling Severity Index has nine questions about the previous 12 months. They ask about issues such as betting more than one can afford, needing larger bets for the same excitement, returning to win back losses, borrowing or selling things to gamble, feeling that gambling is a problem, stress or anxiety, criticism from others, financial problems, and guilt.

Each answer is scored by frequency: **never = 0, sometimes = 1, most of the time = 2, almost always = 3**. The nine scores add to 0–27. A common grouping is 0 (no reported symptoms or consequences), 1–2 (low risk), 3–7 (moderate risk), and 8+ (problem gambling / high-risk range). Survey and research conventions can differ slightly in how they name the intermediate bands.

PGSI is a **screening and research measure**, not a clinical diagnosis and not a direct sensor of current play. It captures the respondent's recollection and self-report about the prior year, including consequences and perceived loss of control that transaction logs cannot directly observe. The UK Gambling Commission describes it as developed for general-population surveys rather than clinical diagnosis; Swedish National Board of Health and Welfare guidance says individual assessment should include other information. In our project, a PGSI response could be one useful label source if collected with consent and a clear time window, but a single response would not automatically supply an objective, dated onset for a forward prediction task.

Sources: [UK Gambling Commission: PGSI questions and scoring](https://www.gamblingcommission.gov.uk/statistics-and-research/publication/problem-gambling-screens); [Swedish National Board of Health and Welfare: PGSI purpose and individual-use caveat](https://www.socialstyrelsen.se/kunskapsstod-och-regler/omraden/evidensbaserad-praktik/metodguiden/pgsi-problem-gambling-severity-index/).

## 3. Candidate signals that can be built from TSI

The literature points to several feature families. Their presence in the archive does not mean they are validated risk indicators.

| Candidate family | TSI-available ingredients | Initial feature candidates | Main caveat |
|---|---|---|---|
| Play frequency and pace | Completed rounds, player-action timestamps, session numbers | Bets per active day/session; active days; median and lower-quantile inter-bet gap; session duration and round count | Event rows include state/result rows; count completed rounds or player actions, not all event rows. Sessions start after a gap of more than one hour, so breaks between sessions are always longer than one hour and depend on that rule. |
| Stakes and variability | `rounds.stake_eur`, account and session identifiers | Mean/median stake; IQR; standard deviation/CV; high-quantile stake; recent-to-personal-baseline ratio | Stakes are strongly skewed; absolute thresholds may reflect affordability, product, or project rather than harm. |
| Bet trajectory | Bet timestamps and amounts over time | 7/30-day changes in rate and stake; robust slope; abrupt increase relative to an account's own baseline | 100 players are insufficient to establish stable population thresholds. |
| Outcomes and apparent losses | `stake_eur`, `returned_eur`, result time and bet time | Net return/loss over a session or rolling window, using only results available by the prediction time | `bet_result_x` does not reconcile exactly with return/stake for all rounds; result time can occur after bet time. |
| Depositing | Payment amount and category; observed event order/time | Deposit count and total in 7/30 days; deposits per session; amount distribution | Deposit timestamps are technical and not confirmed as actual behavior time; payment category semantics need review. |
| Possible loss chasing | Betting losses/results and deposit events | Deposit after a confirmed low balance or loss; within-session top-up sequences | Cannot be validated now: balance is not verified own funds and deposit event time is uncertain. Do not implement H1 as if timestamps were authoritative. |
| Time and product context | Local hour, weekday code, product and game codes | Night-time share, session timing, game/product variety | Time zone and weekday mapping are undocumented; project and exposure differences may dominate. `local_hour` is on `events.parquet` but not on `rounds.parquet`. A share of bets is dominated by a few long night sessions; the share of active days with night play is less sensitive. Night play also rises with overall intensity, so report it alongside bets per active day. If all players in a brand share one clock, within-brand comparisons stay valid and only the meaning of "night" shifts. |

Prefer features in both fixed windows (for example, 7 and 30 days) and personal change measures. A player betting €5 per round is not necessarily escalating; a sharp change from their own stable baseline may be more informative. This is a testable design choice, not a conclusion from the 100-player profile.

## 4. What the current dataset can and cannot establish

### It can support now

1. Verify field semantics and time ordering with the data engineer.
2. Build account-time feature snapshots without labels, inspect distributions, missingness, extreme values, and differences by project/exposure.
3. Test whether the issue hypotheses are computable and stable: deposit windows, deposit-after-low-balance, average stake, stake variability, and trajectory features.
4. Create a reproducible feature table at a declared observation time, with every feature restricted to information available by that time.

### It cannot support now

- A supervised model of harm, addiction, or the proposed green/yellow/orange/red classes: there is no PGSI, manual review, harm event, intervention, or self-exclusion outcome in this release.
- Credible estimates of player-level generalization from a 100-person sample, regardless of the number of event rows.
- A validated causal claim that a feature means a player is losing control.
- A proper prospective loss-chasing feature until deposit time and own-funds balance semantics are confirmed.

Unsupervised clustering can describe behavioral patterns in this archive, but clusters are not harm labels. A rule-based score can define a provisional review policy, but it must not be used as its own “ground truth” when comparing the model with the rule.

## 5. Recommended first training-data design

The next data product should be a **person-by-index-time snapshot table**, not an event-row classification table. Each row should specify one person and one prediction time; feature windows should end at that time. Keep an explicit `label`, `label_source`, `label_date`, `label_confidence`, and `label_window_end` beside the features.

Before model training, the team needs to decide which outcome can actually be collected and audited:

1. **Preferred harm-related target:** independently defined assessment or harm event with a date, severity, and documented source. Record how assessors formed the label, and avoid using the label date or post-label information as predictors.
2. **Secondary proxy target:** future voluntary self-exclusion, if that is the only available operational event. Name it as self-exclusion prediction, not addiction detection, and state its known limitations.
3. **Research-only short-term target:** expert review of a sample of anonymized time windows using a written rubric, ideally blinded to the model features where feasible. Measure inter-rater agreement and preserve uncertain/unknown cases instead of silently forcing them into a class.

For a first baseline, compare (a) a simple, frozen transparent rule and (b) a regularized logistic model or small gradient-boosted tree using the same feature windows. Do not choose the model family from this 100-person release. If labels become available, evaluate on a future-time holdout and group every split by person. Report recall at the fixed 5% review capacity, precision/positive predictive value, PR-AUC, calibration, lead time, and false-positive burden. Also report uncertainty intervals; with rare outcomes, a high recall can still produce many false alerts.

The existing issue #11 metric—recall among a 5% weekly review queue 7–30 days before an event—is a reasonable operational question only after the event label and event time are defined. It is not directly validated by the self-exclusion papers summarized here.

## 6. Decisions and unresolved questions for the team

- What precisely is the positive event: PGSI threshold, staff review category, harm incident, self-exclusion, or an intervention trigger? Are we predicting its onset or current state?
- Can the project obtain an independent harm-related label and the date when it became knowable? Who defines label severity and uncertainty?
- Can the data owner confirm the behavior timestamp for deposits/withdrawals, the meaning of `balance_after_eur`, withdrawal cancellations, and the formula for `bet_result_x`?
- Do we want one binary “needs review” prediction first, with severity as a later task? The literature does not justify four ordinal risk labels before labels and class counts are known.
- Which time zone does `local_hour` use, how is daylight saving handled, and is it the same clock for all players within a brand?
- Are the five project groups different operators/products or only sample strata? Which group-level fields can safely be used at prediction time, and what deployment transfer do we expect?

## References

- Auer, M., & Griffiths, M. D. (2023). [Using artificial intelligence algorithms to predict self-reported problem gambling with account-based player data in an online casino setting](https://doi.org/10.1007/s10899-022-10139-1). *Journal of Gambling Studies*.
- Andersson, S., et al. (2025). [Insights into the temporal dynamics of identifying problem gambling on an online casino: A machine learning study on routinely collected individual account data](https://doi.org/10.1556/2006.2025.00013). *Journal of Behavioral Addictions*.
- Haeusler, J. (2016). [Follow the money: Using payment behaviour as predictor for future self-exclusion](https://doi.org/10.1080/14459795.2016.1158306). *International Gambling Studies*.
- Hopfgartner, N., et al. (2023). [Predicting self-exclusion among online gamblers: An empirical real-world study](https://doi.org/10.1007/s10899-022-10149-z). *Journal of Gambling Studies*.
- Braverman, J., & Shaffer, H. J. (2012). [How do gamblers start gambling: identifying behavioural markers for high-risk internet gambling](https://doi.org/10.1093/eurpub/ckp232). *European Journal of Public Health*.
- Finkenwirth, S., et al. (2021). [Using machine learning to predict self-exclusion status in online gamblers on the PlayNow.com platform in British Columbia](https://doi.org/10.1080/14459795.2020.1832132). *International Gambling Studies*.
- Percy, C., et al. (2016). [Predicting online gambling self-exclusion: an analysis of the performance of supervised machine learning models](https://doi.org/10.1080/14459795.2016.1151913). *International Gambling Studies*.
- LaBrie, R., & Shaffer, H. J. (2011). [Identifying behavioral markers of disordered Internet sports gambling](https://doi.org/10.3109/16066359.2010.512106). *Addiction Research & Theory*.
- Gray, H. M., LaPlante, D. A., & Shaffer, H. J. (2012). [Behavioral characteristics of Internet gamblers who trigger corporate responsible gambling interventions](https://doi.org/10.1037/a0028545). *Psychology of Addictive Behaviors*.
- Gambling Commission. (2023). [Customer interaction guidance for remote gambling licensees (formal guidance under SR Code 3.4.3), Requirement 5](https://www.gamblingcommission.gov.uk/guidance/customer-interaction-guidance-for-remote-gambling-licensees-formal-guidance/requirement-5-customer-interaction-guidance-for-remote-gambling-licensees-sr).
- McAuliffe, W. H. B., et al. (2022). [Using "markers of harm" to track risky gambling in two cohorts of online sports bettors](https://doi.org/10.1007/s10899-021-10097-0). *Journal of Gambling Studies*.
- Delfabbro, P., Parke, J., & Catania, M. (2024). [Behavioural tracking and profiling studies involving objective data derived from online operators: A review of the evidence](https://doi.org/10.1007/s10899-023-10247-6). *Journal of Gambling Studies*.
- Murch, W. S., et al. (2023). [Using machine learning to retrospectively predict self-reported gambling problems in Quebec](https://doi.org/10.1111/add.16179). *Addiction*.
- Auer, M., & Griffiths, M. D. (online 2022). [An empirical attempt to operationalize chasing losses in gambling utilizing account-based player tracking data](https://doi.org/10.1007/s10899-022-10144-4). *Journal of Gambling Studies*.
- Hopfgartner, N., et al. (online 2024). [Using artificial intelligence algorithms to predict self-reported problem gambling among online casino gamblers from different countries using account-based player data](https://doi.org/10.1007/s11469-024-01312-1). *International Journal of Mental Health and Addiction*.
- Zhang, K., et al. (2024). [Between-session chasing of losses and wins in an online eCasino](https://doi.org/10.1556/2006.2024.00022). *Journal of Behavioral Addictions*.

## Project issue links

- [Issue #2 — loss-chasing deposits](https://github.com/ante-rg/ante-research/issues/2)
- [Issue #3 — seven-day deposit activity](https://github.com/ante-rg/ante-research/issues/3)
- [Issue #4 — mean stake and variability](https://github.com/ante-rg/ante-research/issues/4)
- [Issue #5 - night-time betting](https://github.com/ante-rg/ante-research/issues/5)
- [Issue #6 - betting intensity](https://github.com/ante-rg/ante-research/issues/6)
- [Issue #11 — gradient boosting vs rule-based baseline](https://github.com/ante-rg/ante-research/issues/11)
