PROMPTS = {
    "german_level": """Classify the German level required in the job text below, using the CEFR scale.

The list below is a reference baseline covering common phrasings, not an exhaustive or
absolute lookup table. If the posting uses different wording not listed here, do not default
to "none" just because the exact phrase isn't covered - reason by analogy using the same
pattern these examples follow (how explicitly the requirement is stated, how strong/formal the
language is) and assign the CEFR level that fits best.

- Grundkenntnisse / basic German -> A2
- gute Deutschkenntnisse / good German -> B2 (this phrase alone does not reliably distinguish B1
  from B2 in German job postings; when ambiguous, resolve to B2 rather than B1)
- sehr gute Deutschkenntnisse / very good German -> C1
- verhandlungssicheres Deutsch / fliessend / muttersprachlich / native -> C2
- "von Vorteil" or "Bereitschaft Deutsch zu lernen" (nice-to-have / willingness to learn, not required) -> none

Reserve "none" specifically for when German is not mentioned as a requirement or expectation
anywhere in the text. If German is mentioned at all - even just listed with no descriptor - it
is not "none"; judge the level from context using the reasoning above.

Answer with ONLY one of these values, no extra text:
A1, A2, B1, B2, C1, C2, none
Job text:
""",

    "keywords": """Extract up to 12 keywords from the job posting below. 12 is a ceiling, not a target -
prefer fewer, highly specific keywords over padding the list to reach 12.

Prioritize technical/hard skills (tools, technologies, methods, qualifications).
Do not include language proficiency requirements (e.g. German, English) as keywords.
Include at most 1-2 soft skills, and only if specific to this posting - skip generic
traits that appear in almost every job posting (e.g. "team player", "self-motivated",
"structured working style").

The job posting may be in German. Always answer in English, regardless of the language of the job posting.

Answer with ONLY a comma-separated list, no extra text, no labels.

Job posting:
""",

    "cover_letter": """Write the body of a cover letter adapted to the job posting below, based on the candidate's CV as reference material.

Only use facts, dates, and employment status explicitly present in the candidate's CV below.
Do not infer, combine, or invent any fact not explicitly stated (e.g. do not claim
concurrent/dual enrollment in two degree programs unless the CV explicitly states they overlap).

When connecting the candidate's experience to the job posting's terminology, describe the
actual activity the candidate performed - do not relabel it using the job posting's vocabulary
(e.g. do not describe commissioning work as formal "testing", "test planning", or "test
execution" unless the CV explicitly uses that language). Draw the connection explicitly
instead of renaming the activity.

Do not use semicolons (;) or colons (:) to connect clauses within a sentence. Do not use a
dash surrounded by spaces to connect clauses either (hyphens inside compound words like
"real-time" are fine). Break information into separate, short sentences using periods instead.

Never open with generic phrasing such as "I am writing to express my interest/enthusiasm",
"I am excited about the opportunity", or similar. Instead, open with a concrete, specific fact
from the candidate's background, stated directly.

Throughout the letter, avoid narrating or labeling why a fact is relevant (e.g. "this taught
me...", "this showed me...", "a skill directly transferable to...", "which demonstrates my
ability to..."). State the concrete fact and the concrete parallel to what the role needs, and
let the connection be self-evident rather than explained.

Write 5 paragraphs, covering in order:
1. Motivation/introduction - open with a concrete fact whose relevance to the role's main
   objective is clear on its own, without stating the comparison explicitly (do not say "which
   is the same as...", "this maps directly onto...", "this matches..." or similar).
2. Relevant experience - prioritize quantifiable achievements (percentages, metrics, completed
   projects) over restating the CV. Focus on the hard skills most central to the job posting.
3. Working methodology and soft skills - describe how the candidate works (structured delivery,
   cross-team communication, problem-solving, etc.), always grounding each trait in a specific
   action or hard skill from the reference material rather than stating it as an abstract trait
   on its own. If it strengthens the paragraph, bring in a hard skill not already covered in
   paragraph 2 and use it as the evidence for a soft skill.
4. Availability - the candidate is not currently employed and has no notice period, so is
   available to start immediately. If the job posting is for an on-site/in-person position in
   a specific city or region, also state the candidate's readiness to relocate there, based on
   the relocation availability stated in the candidate's CV below; omit this if the position is
   remote, hybrid, or does not specify an on-site location. Explicitly state availability for
   an interview to further discuss qualifications.
5. Closing/thanks - thank the recipient for the opportunity. Do not repeat the interview
   availability or forward-looking interest already stated in paragraph 4.

Keep the total length between 1500 and 2400 characters.

The job posting may be in German. Always answer in English, regardless of the language of the job posting.

Use only plain ASCII characters. Do not use subscripts or superscripts (write CO2, not CO with a subscript 2), smart/curly quotes (use straight quotes), em-dashes or en-dashes (use a regular hyphen), or any other special Unicode symbols.

Output ONLY the 5 paragraphs, separated by a blank line between each. No greeting, no closing/signature, no preamble, no explanation.
""",

    "affinity_score": """Compare the candidate's skills below with the job posting below, and rate how well they match.

Weigh skills central to the job's core function more heavily than generic or incidental
terms that happen to overlap (e.g. "programming" or "manufacturing" alone should not count
as a strong match if the job's core specialization is unrelated to the candidate's background).

Answer with ONLY a single whole number from 1 to 10, no extra text, no explanation.
"""
}
