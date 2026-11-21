# -*- coding: utf-8 -*-
"""Ask Jev (TypeSafe System One) how serious each remaining W6b finding is. One request, parallel questions.

Needs TYPESAFE_API_KEY in the environment (never printed, never stored). Sends only the generic finding text below:
no names, emails or personal data. Per the TypeSafe skill, Jev's output is a recommendation; hard tests stay with code.
"""
import json, os, sys, urllib.request

KEY = os.environ.get("TYPESAFE_API_KEY")
if not KEY:
    sys.exit("TYPESAFE_API_KEY is not set in this environment")

STATE = {
    "system": "A study-support retrieval system for accounting courses. Answers come from indexed course sources with source labels. "
              "It is about to be published to a git remote. All automated gates pass: core regression is identical, 13 course evals pass "
              "(one has a documented waiver), refresh plan shows no change, concept validators pass.",
    "findings": {
        "G16": "A few concept names (for example 'Tờ khai hải quan', 'rút dự toán', two spreadsheet sheet names) come from sentences in the course "
               "text, not from headings. Retrieval results and sources are unaffected; only the concept label's provenance is weaker.",
        "G19": "One legal instrument (Circular 80/2021) has two records written with two citation styles, so asking about it shows two summaries "
               "that say the same thing.",
        "G20": "A brand-new empty course folder does not trigger the 'new course' stop until its first file appears. Nothing is ingested wrongly.",
        "G21": "A reference textbook is noted with the 2013 edition on its cover while the study guide cites the 2016 edition. Only a note.",
        "G22": "A course cue written with underscores around it (for example _hcsn_) still routes to a course; students do not type this.",
        "parallel_regression_incident": "Three workers ran the regression suite at the same time once, which rewrote ten historical raw report files "
                                         "and one eval report. All were restored from git HEAD and everything was re-verified sequentially afterwards.",
        "unreviewed_round": "The fixes of the latest round (regression gate, eval exit codes, router for tax questions, evidence-label validation) "
                            "were checked by the lead engineer with full re-runs, but have not had a second independent review.",
    },
}

questions = {}
for k in STATE["findings"]:
    questions[f"{k}_block"] = {
        "type": "noul",
        "instructions": f"Looking only at finding `findings.{k}` in the state: should it block publishing this system now? "
                        "Yes only if it can give a learner a wrong or misleading answer, lose data, or break the update process.",
    }
    questions[f"{k}_severity"] = {
        "type": "score",
        "instructions": f"How severe is finding `findings.{k}` for learners and maintainers of this system?",
        "criteria": [  # ordered array: position = level number (0..4)
            "Cosmetic: a note or wording issue; no behavior difference.",
            "Minor: slight redundancy or weaker provenance; answers and sources are still correct.",
            "Moderate: can occasionally mislead or degrade results for some questions.",
            "Major: regularly gives wrong answers, loses data, or breaks updates.",
            "Critical: unsafe or corrupting; must be fixed before any use.",
        ],
    }
questions["overall_publish"] = {
    "type": "choice",
    "instructions": "Given all findings and checks in the state, what is the most sensible next step for the system?",
    "criteria": {
        "publish_now": "Remaining issues are all minor; all automated gates pass; publish now.",
        "review_then_publish": "Gates pass but a recent set of unreviewed fixes carries meaningful risk; get one more independent review first.",
        "fix_first": "There is a known issue that can give wrong answers or corrupt data; fix it before publishing.",
    },
}

body = json.dumps({"model": "jev-latest", "state": STATE, "questions": questions}, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request("https://api.typesafe.ai/v1/systemone", data=body, method="POST",
                             headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        out = json.loads(r.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    sys.exit(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}")
print(json.dumps(out, ensure_ascii=False, indent=1))
