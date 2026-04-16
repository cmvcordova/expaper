---

## Writing directives

<!-- TUNE THIS FILE. Delete the format block you're not writing. Adjust page budget and venue. -->

### Format

Choose one and delete the other:

**Conference paper** (NeurIPS / ICML / ICLR tier):
- Structure: abstract → intro → related work → method → experiments → conclusion
- Length: 8–9 pages main body + unlimited references (check venue)
- Citations: `\citep{}` / `\citet{}` per venue style
- Quotation marks: LaTeX style — ` ``...'' ` or `\enquote{}` (csquotes package)
- Heading case: follow the venue template — many enforce Title Case

**Technical blog post**:
- Structure: summary paragraph → problem → method → results → open questions
- Length: 800–2000 words; figures carry weight
- Citations: hyperlink the relevant subject noun phrase (~5 words); never link punctuation; the text must make the argument without requiring the reader to click
- Quotation marks: double curly (""). Punctuation inside.
- Headings: sentence case, not Title Case

---

### Voice

Write for two readers simultaneously: a domain expert who will stress-test the claims, and a researcher from an adjacent field who needs the stakes explained.

- **Active voice.** "We show that X" not "It was shown that X."
- **Concrete over abstract.** Cite numbers. "Accuracy improved 4.2%" not "performance improved."
- **Short sentences win.** If a sentence needs two em dashes and a subordinate clause, split it.
- **Define jargon on first use**, briefly, inline. After that, use the term freely.

---

### Structure

**Abstract / summary paragraph**: State the problem, what you did, and the headline result. One paragraph—not bullets. The reader should know whether to keep reading after the first four sentences.

**Introduction / opening**: Lead with the stakes. Why does this problem matter, and why now? Establish the gap your work closes before describing your approach.

**Method**: Explain the intuition before the formalism. A reader who understands *why* a design choice was made will forgive notation they have to look up.

**Results**: State what the numbers show in prose—don't make the reader interpret tables alone. Lead with the headline result, then address ablations and failure modes.

**Limitations**: Visible, not buried. One honest paragraph beats three paragraphs of hedged optimism.

**Figures**: Each figure must stand alone. Caption = one sentence on what it shows + one sentence on the takeaway. A reader skimming figures should reconstruct the paper's argument.

---

### Numbers and punctuation (both formats)

Numbers: spell out one through nine; numerals for 10 and above. Use %, not "percent."

Em dashes (—) no spaces, for sharp asides only—use sparingly. En dashes (–) for ranges only.

---

### Patterns to avoid

**Zombie nouns.** Convert nominalizations back to verbs: "An investigation of X was conducted" → "We investigated X."

**Throat-clearing.** Delete: "It is important to note that…" / "In today's rapidly evolving landscape…" / "Here's what this means for…"

**Intensifiers that insist.** "This genuinely works," "This is truly novel" — the evidence makes the claim, not the adverb.

**The "not X—it's Y" construction.** Never.

**Academese.** "The prevention of neurogenesis was observed to result in the diminishment of fear extinction" → "Blocking neurogenesis made mice worse at unlearning fear."

**Puffed-up synonyms.** utilize → use. leverage → use. facilitate → help. demonstrate → show.

---

### Honesty

Acknowledge limitations clearly and early—not in a footnote, not in the last line of the conclusion. A reader who discovers an unacknowledged limitation will distrust the rest; one who sees you flag it first will trust your results more.

<!-- Tuning: set venue in the Format block above, delete the unused format, add co-author preferences here -->
