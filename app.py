import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="Kuku Promo Finder", layout="wide")
st.title("🎬 Kuku Microdrama Promo Finder")
st.write("Extracts 20-60 second promo segments based on 3-second hooks, unresolved cliffhangers, and cold-audience coherence.")

api_key = st.text_input("Enter Gemini API Key (Required for inference):", type="password")
script_text = st.text_area("Paste Screenplay (or Episode Text) Here:", height=300)

PROMPT_TEMPLATE = """
You are an expert microdrama video editor. Analyze the following screenplay text and extract the top 3 best promotional clips (promos).
A good promo must:
1. Be 20 to 60 seconds long (calculate duration using the script's timestamps).
2. Open on a powerful hook in the first 3 seconds (e.g., a slap, dramatic reveal, or shocking line).
3. End on a cliffhanger (an unresolved narrative or physical moment).
4. Make complete sense to a scrolling viewer who has never seen the show.

Return the results STRICTLY as a JSON array of objects. Do not include markdown formatting or backticks. Format each object exactly like this:
[
  {
    "rank": 1,
    "episode": "Episode Name/Number",
    "start_timestamp": "00:00.00",
    "end_timestamp": "00:00.00",
    "hook": "Describe the 3-second hook.",
    "cliffhanger": "Describe the unresolved moment at the cut.",
    "why_it_works": "One line on why this works for a cold audience.",
    "quality_check": "Note any potential weakness (e.g., lacks visual action, relies too heavily on prior context)."
  }
]

Screenplay:
{script}
"""

if st.button("Find Promos"):
    if not api_key or not script_text:
        st.error("Please provide both an API key and the screenplay text.")
    else:
        try:
            genai.configure(api_key=api_key)
            # 1.5 Flash is used for high-speed, long-context parsing
            model = genai.GenerativeModel('gemini-1.5-flash')

            with st.spinner("Analyzing screenplay for optimal hooks and cliffhangers..."):
                response = model.generate_content(PROMPT_TEMPLATE.format(script=script_text))
                
                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text.replace("```json", "").replace("```", "").strip()
                elif raw_text.startswith("```"):
                    raw_text = raw_text.replace("```", "").strip()
                    
                promos = json.loads(raw_text)

                st.success("Analysis Complete! Top candidate promos ranked:")
                
                for promo in promos:
                    with st.expander(f"Rank {promo['rank']}: {promo['start_timestamp']} - {promo['end_timestamp']} ({promo['episode']})"):
                        st.markdown(f"**🪝 Hook (0-3s):** {promo['hook']}")
                        st.markdown(f"**✂️ Cliffhanger:** {promo['cliffhanger']}")
                        st.markdown(f"**🎯 Why it works:** {promo['why_it_works']}")
                        st.markdown(f"**⚠️ Quality Check:** {promo['quality_check']}")

        except Exception as e:
            st.error(f"An error occurred during processing: {e}")
