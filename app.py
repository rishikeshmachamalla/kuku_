import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="Kuku | Promo Extractor (Tension-Arc)", layout="wide")
st.title("🎬 Kuku Promo Finder: Tension-Arc Pipeline")
st.markdown("Extracts continuous 20-60s ad creatives using Arousal Anchors (Hooks) and Suspense Nodes (Cliffhangers).")

api_key = st.text_input("Enter Gemini API Key (Required):", type="password")
script_text = st.text_area("Paste Screenplay Episode Here:", height=350)

PROMPT_TEMPLATE = """
You are a performance marketing video editor for a microdrama app. Your task is to apply the "Tension-Arc" methodology to the following script and extract the top 3 best standalone promos.

RULES:
1. Duration: Must be between 20s and 60s continuous (use the provided timestamps).
2. Arousal Anchor (Hook): The first 3 seconds must contain extreme emotional dialogue, a physical confrontation, or a dramatic reveal.
3. Suspense Node (Cliffhanger): The clip must cut on an unresolved moment of physical jeopardy or high emotional tension.
4. Context Independence: The clip must require ZERO backstory to understand the stakes.

Return strictly as a JSON array. Format exactly as follows without markdown backticks:
[
  {
    "rank": 1,
    "episode": "Episode Number",
    "start_timestamp": "00:00.00",
    "end_timestamp": "00:00.00",
    "duration": "45s",
    "hook": "Describe the 3-second hook event.",
    "cliffhanger": "Describe the unresolved tension at the cut.",
    "why_it_works": "Why this converts cold audiences.",
    "quality_check": "Identify any potential weakness (e.g., quiet tension, complex lore)."
  }
]

SCRIPT:
{script}
"""

if st.button("Extract Promos"):
    if not api_key or not script_text:
        st.error("Please provide both an API key and script text.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')

            with st.spinner("Executing Tension-Arc Pipeline... isolating hooks and cliffhangers..."):
                response = model.generate_content(PROMPT_TEMPLATE.format(script=script_text))
                
                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text.replace("```json", "").replace("```", "").strip()
                elif raw_text.startswith("```"):
                    raw_text = raw_text.replace("```", "").strip()
                    
                promos = json.loads(raw_text)

                st.success("Analysis Complete! Top candidate arcs extracted:")
                
                for promo in promos:
                    with st.expander(f"Rank {promo['rank']}: {promo['start_timestamp']} to {promo['end_timestamp']} ({promo['duration']})"):
                        st.markdown(f"**🪝 Hook (0-3s):** {promo['hook']}")
                        st.markdown(f"**✂️ Cliffhanger:** {promo['cliffhanger']}")
                        st.markdown(f"**🎯 Why it works:** {promo['why_it_works']}")
                        st.markdown(f"**⚠️ Quality Check:** {promo['quality_check']}")

        except Exception as e:
            st.error(f"Pipeline Execution Error: {e}")
