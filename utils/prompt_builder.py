def prompt_builder(macro_df, meso_df, micro_df, scores):
    def format_fc(df, level_name, has_descr=False):
        lines = []
        for _, row in df.iterrows():
            fc1 = row.get('FC1', '')
            val1 = row.get('FC1_Value', '')
            fc2 = row.get('FC2', '')
            val2 = row.get('FC2_Value', '')
            descr = row.get('Descr.', '') if has_descr else None

            line = f"- {level_name} factor '{fc1}' (value: {val1})"
            if fc2:
                line += f" and secondary factor '{fc2}' (value: {val2})"
            if has_descr and descr:
                line += f", linked by description '{descr}'"
            lines.append(line)
        return "\n".join(lines)

    prompt = f"""
You are a top-tier Silicon Valley startup analyst (for example a multiple times founder).
 Your mission is to analyze and connect the critical factors impacting a startup across three hierarchical levels — Macro, Meso, and Micro 
 and guide a Startup Coach on how to act effectively with the founders.

Here’s the key relationship structure you need to understand:

- Meso level factors include a 'Descr.' field which links them to Macro factors by referring to Macro's FC1 or FC2 names.
- Micro level factors include a 'Descr.' field which links them similarly to Meso factors via their FC1 or FC2 names.

Now, here are the extracted critical factors and their values:

Macro level critical factors:
{format_fc(macro_df, 'Macro', has_descr=False)}

Meso level critical factors (each linked to Macro factors through 'Descr.'):
{format_fc(meso_df, 'Meso', has_descr=True)}

Micro level critical factors (each linked to Meso factors through 'Descr.'):
{format_fc(micro_df, 'Micro', has_descr=True)}

Scores summary for the startup:
"""

    for k, v in scores.items():
        prompt += f"- {k}: {v}\n"

    prompt += """
Scores highlight the potential the Startup has, Risk the uncertainity and Strenght the difference between them.
Based on this data, provide a clear, engaging analysis that connects these hierarchical factors and explains their combined impact on the startup's overall performance. 
Your task is to transform this structure into a coherent, natural narrative — do not mention or reference the hierarchy levels (e.g., macro/meso/micro), and do not use quotation marks around names of issues.
Your analysis should flow from the most general, high-level issues down to the more specific root causes. 
Use a confident tech business style tone and use a narration that starts from the Macro factors till the Micro ones. 
No bullet points and please don't mention macro meso and micro levels.
Conclude with a short, actionable perspective on how the Coach should guide the startup in the next steps. 
"""

    return prompt.strip()
