CATEGORY_RULES = {
    "Account Information": {
        "linddun": ["Identifiability", "Linkability"],
        "panoptic_activity": "PA05 Identification / PA03 Collection",
        "risk_level": "Medium/High",
        "reason": "Account information can directly or indirectly identify a user.",
        "mitigation": "Collect only required account fields and clearly explain account-data use."
    },

    "Payment Information": {
        "linddun": ["Disclosure of Information", "Identifiability", "Non-compliance"],
        "panoptic_activity": "PA03 Collection / PA04 Insecurity",
        "risk_level": "High",
        "reason": "Payment and billing data can be sensitive and may create financial or identity risk.",
        "mitigation": "Use strong protection, limit retention, and clearly disclose payment-data handling."
    },

    "User Content": {
        "linddun": ["Disclosure of Information", "Unawareness", "Non-compliance"],
        "panoptic_activity": "PA03 Collection / PA09 Processing / PA11 Use",
        "risk_level": "High",
        "reason": "Prompts, outputs, files, messages, and feedback may contain sensitive user-provided content.",
        "mitigation": "Warn users before collecting sensitive content and provide clear deletion/control options."
    },

    "Device and Technical Data": {
        "linddun": ["Linkability", "Identifiability", "Detectability"],
        "panoptic_activity": "PA03 Collection / PA05 Identification",
        "risk_level": "Medium",
        "reason": "Device, browser, IP, and log data can support tracking or user/device identification.",
        "mitigation": "Minimize technical metadata collection and disclose automatic collection clearly."
    },

    "Location Data": {
        "linddun": ["Linkability", "Identifiability", "Detectability"],
        "panoptic_activity": "PA03 Collection / PA05 Identification",
        "risk_level": "High",
        "reason": "Location-related data can reveal user movement, region, or physical context.",
        "mitigation": "Avoid precise location collection unless necessary and provide clear user control."
    },

    "Cookies and Tracking": {
        "linddun": ["Linkability", "Detectability", "Unawareness"],
        "panoptic_activity": "PA03 Collection / PA05 Identification",
        "risk_level": "Medium/High",
        "reason": "Cookies and tracking technologies can link user behavior across sessions or services.",
        "mitigation": "Provide cookie controls, explain cookie purposes, and separate necessary from optional tracking."
    },

    "Security and Safety Data": {
        "linddun": ["Nonrepudiation", "Disclosure of Information", "Non-compliance"],
        "panoptic_activity": "PA06 Quality Assurance / PA09 Processing",
        "risk_level": "Medium",
        "reason": "Safety, abuse, moderation, and security review data may preserve sensitive interactions.",
        "mitigation": "Limit access to safety-review data and clearly explain when human or automated review occurs."
    },

    "Retention and Storage": {
        "linddun": ["Unawareness", "Non-compliance"],
        "panoptic_activity": "PA12 Retention & Destruction",
        "risk_level": "Medium/High",
        "reason": "Longer retention increases privacy exposure and may conflict with user expectations.",
        "mitigation": "State retention periods clearly and provide deletion or retention-control options when possible."
    },

    "Model Improvement and Training": {
        "linddun": ["Unawareness", "Non-compliance", "Disclosure of Information"],
        "panoptic_activity": "PA09 Processing / PA11 Use",
        "risk_level": "High",
        "reason": "Using user data for model improvement can be a secondary use beyond the immediate interaction.",
        "mitigation": "Clearly separate service operation from training use and provide opt-out controls."
    },

    "Third Party Sharing": {
        "linddun": ["Disclosure of Information", "Linkability", "Non-compliance"],
        "panoptic_activity": "PA10 Sharing",
        "risk_level": "High",
        "reason": "Sharing data with outside entities increases downstream disclosure and control risks.",
        "mitigation": "Identify third-party recipients, explain sharing purposes, and limit unnecessary sharing."
    },
}


DEFAULT_RULE = {
    "linddun": ["Needs Manual Review"],
    "panoptic_activity": "Needs Manual Review",
    "risk_level": "Needs Manual Review",
    "reason": "No specific threat rule matched this category.",
    "mitigation": "Review the evidence quote manually."
}


RISK_SCORES = {
    "Low": {
        "likelihood": 1,
        "consequence": 1,
    },
    "Medium": {
        "likelihood": 2,
        "consequence": 2,
    },
    "Medium/High": {
        "likelihood": 2,
        "consequence": 3,
    },
    "High": {
        "likelihood": 3,
        "consequence": 3,
    },
    "Needs Manual Review": {
        "likelihood": None,
        "consequence": None,
    },
}


def get_category_rule(category):
    return CATEGORY_RULES.get(category, DEFAULT_RULE)


def get_risk_score(risk_level):
    score_data = RISK_SCORES.get(risk_level, RISK_SCORES["Needs Manual Review"])

    likelihood = score_data["likelihood"]
    consequence = score_data["consequence"]

    if likelihood is None or consequence is None:
        return None, None, None

    return likelihood, consequence, likelihood * consequence


def add_contextual_threats(row, base_linddun, base_panoptic):

    linddun = set(base_linddun)
    panoptic = set([base_panoptic])

    text = " ".join([
        str(row.get("Evidence_Quote", "")),
        str(row.get("Data_Type", "")),
        str(row.get("Purpose_Stated", "")),
        str(row.get("Retention_Stated", "")),
        str(row.get("Training_Use_Stated", "")),
        str(row.get("Third_Party_Sharing_Stated", "")),
    ]).lower()

    if any(term in text for term in ["retain", "retention", "store", "stored", "delete", "deleted"]):
        linddun.add("Unawareness")
        panoptic.add("PA12 Retention & Destruction")

    if any(term in text for term in ["third party", "third-party", "service provider", "vendor", "share", "sharing", "disclose"]):
        linddun.add("Disclosure of Information")
        panoptic.add("PA10 Sharing")

    if any(term in text for term in ["training", "train", "model improvement", "improve our services", "evaluation"]):
        linddun.add("Unawareness")
        panoptic.add("PA09 Processing / PA11 Use")

    if any(term in text for term in ["cookie", "tracking", "advertising identifier", "analytics"]):
        linddun.add("Linkability")
        linddun.add("Detectability")
        panoptic.add("PA03 Collection / PA05 Identification")

    if any(term in text for term in ["ip address", "device", "browser", "location", "geolocation"]):
        linddun.add("Identifiability")
        linddun.add("Linkability")
        panoptic.add("PA05 Identification")

    if any(term in text for term in ["opt out", "consent", "control", "delete your", "access your"]):
        panoptic.add("PA07 Manageability")
    
    return sorted(linddun), " | ".join(sorted(panoptic))


def needs_manual_review(row, risk_level):
    text = " ".join([
        str(row.get("Evidence_Quote", "")),
        str(row.get("Disclosure_Quality", "")),
        str(row.get("Retention_Stated", "")),
        str(row.get("Training_Use_Stated", "")),
        str(row.get("Third_Party_Sharing_Stated", "")),
    ]).lower()

    if risk_level in {"High", "Medium/High"}:
        return "Yes"

    if "needs manual review" in text:
        return "Yes"

    if "not stated" in text:
        return "Yes"

    return "No"