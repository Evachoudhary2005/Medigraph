"""General Medicine questionnaire with three modes: full, brief, returning."""

def _q(id_, type_, text_en, text_hi, **extra):
    d = {"id": id_, "type": type_, "text_en": text_en, "text_hi": text_hi}
    d.update(extra)
    return d


def _opt(v, en, hi):
    return {"value": v, "label_en": en, "label_hi": hi}


# ---------------- Core questions used in all modes ----------------

CHIEF_COMPLAINT = {
    "id": "chief_complaint",
    "title_en": "Why you are here",
    "title_hi": "\u0906\u092a \u092f\u0939\u093e\u0901 \u0915\u094d\u092f\u094b\u0902 \u0906\u092f\u0947 \u0939\u0948\u0902",
    "questions": [
        _q("q_cc_main", "text",
           "What is your main problem today?",
           "\u0906\u091c \u0906\u092a\u0915\u0940 \u092e\u0941\u0916\u094d\u092f \u0938\u092e\u0938\u094d\u092f\u093e \u0915\u094d\u092f\u093e \u0939\u0948?",
           required=True),
        _q("q_cc_duration", "duration",
           "How long has this been going on?",
           "\u092f\u0939 \u0915\u093f\u0924\u0928\u0947 \u0938\u092e\u092f \u0938\u0947 \u0939\u0948?"),
        _q("q_cc_severity", "single_choice",
           "How severe is it?",
           "\u092f\u0939 \u0915\u093f\u0924\u0928\u093e \u0917\u0902\u092d\u0940\u0930 \u0939\u0948?",
           options=[
               _opt("1", "Mild", "\u0939\u0932\u094d\u0915\u093e"),
               _opt("2", "Moderate", "\u092e\u0927\u094d\u092f\u092e"),
               _opt("3", "Severe", "\u0917\u0902\u092d\u0940\u0930"),
               _opt("4", "Very severe", "\u092c\u0939\u0941\u0924 \u0917\u0902\u092d\u0940\u0930"),
           ]),
    ],
}

ABOUT_THE_PROBLEM = {
    "id": "about_problem",
    "title_en": "About the problem",
    "title_hi": "\u0938\u092e\u0938\u094d\u092f\u093e \u0915\u0947 \u092c\u093e\u0930\u0947 \u092e\u0947\u0902",
    "questions": [
        _q("q_hpi_onset", "single_choice",
           "Did it start suddenly or gradually?",
           "\u092f\u0939 \u0905\u091a\u093e\u0928\u0915 \u0936\u0941\u0930\u0942 \u0939\u0941\u0906 \u092f\u093e \u0927\u0940\u0930\u0947-\u0927\u0940\u0930\u0947?",
           options=[
               _opt("sudden", "Suddenly", "\u0905\u091a\u093e\u0928\u0915"),
               _opt("gradual", "Gradually", "\u0927\u0940\u0930\u0947-\u0927\u0940\u0930\u0947"),
           ]),
        _q("q_hpi_associated", "multi_choice",
           "Any of these symptoms along with it?",
           "\u0907\u0938\u0915\u0947 \u0938\u093e\u0925 \u0907\u0928\u092e\u0947\u0902 \u0938\u0947 \u0915\u094b\u0908 \u0932\u0915\u094d\u0937\u0923?",
           options=[
               _opt("fever", "Fever", "\u092c\u0941\u0916\u093e\u0930"),
               _opt("nausea", "Nausea", "\u091c\u0940 \u092e\u093f\u091a\u0932\u093e\u0928\u093e"),
               _opt("vomiting", "Vomiting", "\u0909\u0932\u094d\u091f\u0940"),
               _opt("headache", "Headache", "\u0938\u093f\u0930\u0926\u0930\u094d\u0926"),
               _opt("dizziness", "Dizziness", "\u091a\u0915\u094d\u0915\u0930"),
               _opt("cough", "Cough", "\u0916\u093e\u0902\u0938\u0940"),
               _opt("breath", "Breathing trouble", "\u0938\u093e\u0902\u0938 \u092e\u0947\u0902 \u0924\u0915\u0932\u0940\u092b"),
           ]),
    ],
}

MEDICAL_BACKGROUND = {
    "id": "medical_background",
    "title_en": "Medical background",
    "title_hi": "\u091a\u093f\u0915\u093f\u0924\u094d\u0938\u0940\u092f \u092a\u0943\u0937\u094d\u0920\u092d\u0942\u092e\u093f",
    "questions": [
        _q("q_pmh_conditions", "multi_choice",
           "Do you have any of these long-term conditions?",
           "\u0915\u094d\u092f\u093e \u0906\u092a\u0915\u094b \u0907\u0928\u092e\u0947\u0902 \u0938\u0947 \u0915\u094b\u0908 \u0926\u0940\u0930\u094d\u0918\u0915\u093e\u0932\u093f\u0915 \u0938\u094d\u0925\u093f\u0924\u093f \u0939\u0948?",
           options=[
               _opt("diabetes", "Diabetes", "\u092e\u0927\u0941\u092e\u0947\u0939"),
               _opt("hypertension", "High blood pressure", "\u0909\u091a\u094d\u091a \u0930\u0915\u094d\u0924\u091a\u093e\u092a"),
               _opt("heart", "Heart disease", "\u0939\u0943\u0926\u092f \u0930\u094b\u0917"),
               _opt("asthma", "Asthma", "\u0926\u092e\u093e"),
               _opt("thyroid", "Thyroid disease", "\u0925\u093e\u092f\u0930\u0949\u0907\u0921"),
               _opt("kidney", "Kidney disease", "\u0917\u0941\u0930\u094d\u0926\u093e \u0930\u094b\u0917"),
               _opt("none", "None of the above", "\u0907\u0928\u092e\u0947\u0902 \u0938\u0947 \u0915\u094b\u0908 \u0928\u0939\u0940\u0902"),
           ]),
        _q("q_med_allergies", "yes_no",
           "Do you have any known allergies?",
           "\u0915\u094d\u092f\u093e \u0906\u092a\u0915\u094b \u0915\u094b\u0908 \u091c\u094d\u091e\u093e\u0924 \u090f\u0932\u0930\u094d\u091c\u0940 \u0939\u0948?"),
        _q("q_med_allergies_detail", "text",
           "Please list your allergies.",
           "\u0915\u0943\u092a\u092f\u093e \u0905\u092a\u0928\u0940 \u090f\u0932\u0930\u094d\u091c\u0940 \u0938\u0942\u091a\u0940\u092c\u0926\u094d\u0927 \u0915\u0930\u0947\u0902\u0964",
           visible_if={"question_id": "q_med_allergies", "equals": "yes"}),
    ],
}

LIFESTYLE = {
    "id": "lifestyle",
    "title_en": "Lifestyle",
    "title_hi": "\u091c\u0940\u0935\u0928\u0936\u0948\u0932\u0940",
    "questions": [
        _q("q_pers_smoking", "single_choice",
           "Do you smoke?",
           "\u0915\u094d\u092f\u093e \u0906\u092a \u0927\u0942\u092e\u094d\u0930\u092a\u093e\u0928 \u0915\u0930\u0924\u0947 \u0939\u0948\u0902?",
           options=[
               _opt("never", "Never", "\u0915\u092d\u0940 \u0928\u0939\u0940\u0902"),
               _opt("past", "Used to", "\u092a\u0939\u0932\u0947"),
               _opt("current", "Currently", "\u0935\u0930\u094d\u0924\u092e\u093e\u0928 \u092e\u0947\u0902"),
           ]),
        _q("q_pers_alcohol", "single_choice",
           "Do you drink alcohol?",
           "\u0915\u094d\u092f\u093e \u0906\u092a \u0936\u0930\u093e\u092c \u092a\u0940\u0924\u0947 \u0939\u0948\u0902?",
           options=[
               _opt("never", "Never", "\u0915\u092d\u0940 \u0928\u0939\u0940\u0902"),
               _opt("occasional", "Occasionally", "\u0915\u092d\u0940-\u0915\u092d\u0940"),
               _opt("regular", "Regularly", "\u0928\u093f\u092f\u092e\u093f\u0924"),
           ]),
    ],
}


# ---------------- Modes ----------------

def _wrap(mode, name_en, name_hi, sections):
    return {
        "id": f"gm_v1_{mode}",
        "name_en": name_en,
        "name_hi": name_hi,
        "sections": sections,
    }


BRIEF = _wrap(
    "brief",
    "Quick intake",
    "\u0938\u0902\u0915\u094d\u0937\u093f\u092a\u094d\u0924 \u092a\u094d\u0930\u0935\u0947\u0936",
    [CHIEF_COMPLAINT, ABOUT_THE_PROBLEM, MEDICAL_BACKGROUND, LIFESTYLE],
)

RETURNING = _wrap(
    "returning",
    "Follow-up visit",
    "\u092a\u0941\u0928\u0903 \u092a\u0930\u093e\u092e\u0930\u094d\u0936",
    [CHIEF_COMPLAINT, ABOUT_THE_PROBLEM],
)

# Full questionnaire (kept for research / clinician-initiated full intake)
FULL = _wrap(
    "full",
    "General Medicine Intake",
    "\u0938\u093e\u092e\u093e\u0928\u094d\u092f \u091a\u093f\u0915\u093f\u0924\u094d\u0938\u093e \u092a\u094d\u0930\u0935\u0947\u0936",
    [CHIEF_COMPLAINT, ABOUT_THE_PROBLEM, MEDICAL_BACKGROUND, LIFESTYLE],
)

REGISTRY = {
    "gm_v1":          FULL,
    "gm_v1_brief":    BRIEF,
    "gm_v1_returning": RETURNING,
}

# Back-compat: the file previously exposed GM_QUESTIONNAIRE
GM_QUESTIONNAIRE = FULL
