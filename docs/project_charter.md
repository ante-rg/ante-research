# ANTE project charter

**Status:** team working draft, 15 October 2026. This charter records the intended project and decision rules. It does not certify that the course has accepted the team, that data have been provided, or that the prototype has been validated.

## Purpose and research question

ANTE will research whether changes in permitted player event data can help a responsible-gambling analyst prioritise cases for human review. The research question is: **Can transparent, time-aware features prioritise cases more usefully than a simple rules baseline at the same review capacity?** A score is an aid to review, not a diagnosis, account decision, or proof that an intervention reduces harm. The project does not claim that any regulator requires this particular system for licensing.

## Scope and outputs

| In scope | Evidence expected |
| --- | --- |
| Data source and governance decision | Permission, purpose, field inventory, provenance, access, retention and public/private boundary |
| Reproducible data pipeline | Versioned canonical schema, ingestion and quality checks, synthetic tests |
| Behavioural indicators | Documented 7- and 30-day features computed only from information available at prediction time |
| Comparator and conditional model | Transparent rules baseline; simple model and capacity-matched holdout comparison only if defensible labels are permitted |
| Analyst prototype | Local `POST /assess` API and a small read-only demonstration using synthetic or approved de-identified records |
| Academic evidence | Proposal, research protocol, evaluation and limitations, public portfolio, team process record, presentation, and each member's own reflection |

Clinical diagnosis, automatic player sanctions, live production use and claims of measured harm reduction are outside this project. Public artifacts will contain no identifiable player records, private event rows, individual scores or credentials.

## Success and acceptance

1. The team can reproduce the software pipeline and demonstrate its input validation, feature boundaries, baseline and API behavior on synthetic examples; tests and review evidence are linked.
2. Every empirical claim identifies its dataset, eligible population, outcome proxy, observation window and limitations. With suitable labels, the model and rules are compared on the same player-disjoint, chronological holdout and analyst review capacity. Without those labels, the result is a feasibility study, not predictive accuracy.
3. The public portfolio links the problem, sources, decisions, meetings, contributions, iterations, code, tests, analyses, limitations and final recommendation. A Kanban card is Done only after its question, creation, observation, analysis and conclusion have evidence links.
4. All five members can explain the work and participate in the viva. Each reflection is individually authored.

No accuracy target is set before the proxy, denominator and review capacity are defined. A passing test suite establishes software behavior, not clinical or operational validity.

## Team and decision rights

| Member | Planned role reported by Jurijs | Primary responsibility |
| --- | --- | --- |
| Jurijs Kaminskis | Product owner | Scope, priorities, stakeholder and course decisions, acceptance of documented outputs |
| Arturs Greķe | Data engineer | Source inventory, event contract, ingestion, quality and controlled data flow |
| Volodymyr Stishkovskyi | Software developer and ML engineer | Model/API implementation, reproducibility, software tests and deployment boundary |
| Andrejs Fjodorovs | Data scientist | Literature, indicators, exploratory analysis and evaluation design |
| Daniils Buts | Data scientist | Proxy/label critique, baseline comparison, analysis and reporting |

Assignments above are a working division, not evidence of completed individual work. The team will agree task owners and record actual contributions in the portfolio. Jurijs reports that the course approved five members, although the specification ordinarily states three or four; the course approval record and team number are still to be attached.

## Milestones and gates

| Planned point | Decision or deliverable | Evidence status |
| --- | --- | --- |
| 16 Oct 2026 | Proposal submission after team review | Draft prepared; Moodle deadline and receipt pending |
| 23 Oct 2026 | Data and label decision; freeze feasible research route | Owner reports permission under customer terms; agreement clause, dataset, schema and labels pending |
| 6 Nov 2026 | Ingestion, data quality and exploratory evidence | Prototype code exists; real-data quality evidence pending |
| 20 Nov 2026 | Indicators, rules baseline and evaluation protocol | Prototype features exist; empirical baseline pending |
| 4 Dec 2026 | Conditional model comparison and analyst demonstration | Local model/API prototype exists; labels and UI pending |
| 15 Dec 2026 | Public portfolio and critical evaluation | Starter portfolio and draft PR exist; final evidence pending |
| 27 Dec 2026 in specification table | Each member's own reflection | Date and submission route require Moodle confirmation |
| Presentation date to verify | Group presentation and viva | Specification table appears to contain a year error; Moodle confirmation pending |

The assessment specification also lists a conflicting overall cover-page date and an apparent presentation-year error. Moodle is the deadline authority to verify. Individual reflections and viva have separate requirements in the course specification; the team must add public-safe evidence without copying private course files into this repository.

## Data and ethics gate

Jurijs reports that, as the casino owner, he permits educational use of a dataset that he will anonymise, and that the casino's customer agreement allows him to use and transfer gameplay information at his discretion. The relevant clause and jurisdiction have not been supplied or independently reviewed. Before loading operator data, record that clause, the team's right to process the specific dataset and any applicable course or ethics approval, then record the actual fields, de-identification method, permitted purpose, access list, storage location, retention and deletion rule. Keep raw data and player-level outputs outside the public repositories. Record whether any label is independently assessed, what it means, who assigned it, when it became available, and which players were eligible for review. Unreviewed players are not assumed negative. If representative labels are absent, use only descriptive indicators and software scenarios.

The team will document false-positive and false-negative costs, selection bias, temporal leakage, subgroup limitations, re-identification risk and automation bias. A human specialist must interpret any review score. Nothing in this charter authorises deployment against live players.

## Ways of working and change control

- Use the [ANTE board](https://github.com/orgs/ante-rg/projects/1/views/1) for research questions, owners, status and evidence links. Weekly review records what was created, observed, analysed and changed.
- Keep meeting notes and decisions in [versioned GitHub repository files](meetings/README.md), with date, participants, evidence, decision, action owner and follow-up card. Do not invent attendance or outcomes for meetings that have not happened.
- Use pull requests for code and public documentation. A contributor and an independent reviewer should be different people. Tests, privacy review and documentation readback precede merge.
- The product owner may reprioritise scope; any change to data use, target label, prediction time or public claims requires a recorded team decision and an updated protocol before analysis continues.
- If the data gate fails, the team will deliver the reproducible pipeline, rule-based scenario demo and explicit feasibility report described in the proposal.

## Open decisions

1. Confirm the course team number, five-member approval record and Moodle deadlines.
2. Receive the customer-agreement clause and jurisdiction, then the proposed de-identified event schema; document the specific data-use right, handling and deletion.
3. Decide whether independently assessed labels exist and freeze the outcome definition and holdout plan.
4. Confirm task owners and actual contribution recording with the team. Meeting notes are kept in this GitHub repository by Jurijs's choice.
