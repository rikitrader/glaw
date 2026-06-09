<!-- GLAW COURT MOTION STYLE SHEET — the firm's house style for any motion filed in state or federal
     court. Enforced by /glaw-motion-drafting (architecture) + /glaw-legal-writing (polish) and the
     deterministic gate `glaw-writing-check --motion`. NOT legal advice. -->

# Court Motion Writing Style Sheet

## Primary objective
Draft motions that are **concise, authoritative, persuasive, fact-driven, and immediately filable**
in state or federal court.

## Tone
**Use:** professional · objective · precise · respectful · authoritative · confident.
**Avoid:** emotional argument · hyperbole · personal attacks · speculation · unsupported conclusions
· excessive adjectives.

## Writing philosophy
Every paragraph answers one question: **"Why should the Court grant this relief?"** Every sentence
advances the argument. Delete anything that does not support the requested relief.

## Structure (in order)
1. Introduction → 2. Statement of Relevant Facts → 3. Legal Standard → 4. Argument →
5. Requested Relief → 6. Conclusion.

## Opening-paragraph formula
> COMES NOW the [Plaintiff/Defendant], and respectfully moves this Court for [requested relief]. As
> set forth below, the undisputed facts and controlling law establish that the requested relief is
> warranted.

## Fact-section rules
Chronological order. State facts objectively. **Cite the record after every material fact.**
> On [DATE], Defendant received Plaintiff's invoice for completed work. (Ex. A.)
> Defendant never disputed the invoice. (Ex. B.) Payment remains outstanding. (Ex. C.)

## Argument structure (every argument)
**A.** State the rule → **B.** Cite authority → **C.** Apply the facts → **D.** Explain why relief
must be granted.  *(Rule → Authority → Application → Conclusion.)*

## Topic-sentence rule
Every paragraph begins with the **legal point**; the rest of the paragraph proves it.
> "The judgment should be vacated because it was procured through fraud upon the court."

## Citation rules — order of authority
1. Constitution → 2. Statutes → 3. Regulations → 4. Binding precedent → 5. Persuasive precedent →
6. Secondary sources. Always pin-cite when available.
> Smith v. Jones, 123 F.3d 456, 460 (11th Cir. 2024).

## Sentence rules
Preferred length **15–25 words**; **maximum 40**. Active voice.
- Good: "Defendant breached the contract by refusing payment."
- Bad: "It appears that payment may not have been made."

## Prohibited phrases (replace with evidence + authority)
*Clearly · Obviously · It is undeniable · Everyone knows · It appears · Perhaps · Maybe · Arguably.*

## Transitions
Furthermore, · Moreover, · Additionally, · By contrast, · Consequently, · Therefore, · Accordingly,
· For these reasons,.

## Request for relief (end with specific relief)
> WHEREFORE, Plaintiff respectfully requests that the Court:
> A. Vacate the Judgment; B. Dissolve the Writ of Garnishment; C. Award costs and fees as permitted
> by law; and D. Grant such further relief as the Court deems just and proper.

## Quality-control checklist (run `glaw-writing-check --motion`, then confirm)
- [ ] Every factual statement cited to the record
- [ ] Every legal proposition supported by authority
- [ ] No unsupported conclusions · no emotional language · no unnecessary repetition
- [ ] Relief clearly stated and **matches the argument**
- [ ] Grammar and punctuation reviewed
- [ ] Headings correspond to legal issues
- [ ] Record citations verified (→ `/glaw-legal-research`)

## Final output standard
Draft as though the motion will be reviewed by (1) a federal district judge, (2) an appellate court,
and (3) opposing counsel hunting for weakness. **Every sentence must withstand scrutiny.**

<!-- UPL / attorney work-product — not legal advice; verify every cite + the record before filing. -->
