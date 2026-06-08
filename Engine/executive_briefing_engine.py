def generate_executive_briefing(

    prioritised_output

):

    ranked = (
        prioritised_output[
            "ranked_insights"
        ]
    )

    top_risks = ranked[:5]

    if not top_risks:

        headline = (
            "No major operational "
            "risks detected."
        )

    else:

        headline = (
            "Enterprise workforce "
            "and operational risks "
            "require attention."
        )

    return {

        "headline":
            headline,

        "top_risks":
            top_risks
    }