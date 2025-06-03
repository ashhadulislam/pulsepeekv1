import streamlit as st
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


st.set_page_config(page_title="YouTube Insight Viewer", layout="wide")

INSIGHT_FOLDER = "insights"

def get_video_id(filename):
    return filename.split("_")[0]

def render_tag_list(title, items, bg_color="var(--secondary-background-color)"):
    st.markdown(f"### {title}")
    st.markdown(
        " ".join([
            f"<span style='background-color:{bg_color}; padding:4px 10px; border-radius:10px; margin:2px; display:inline-block; color:var(--text-color)'>{item}</span>"
            for item in items
        ]),
        unsafe_allow_html=True
    )

# Helper to extract video_id, title, and uploader from each file
def get_insight_metadata():
    metadata = []
    for f in os.listdir(INSIGHT_FOLDER):
        if f.endswith(".json"):
            with open(os.path.join(INSIGHT_FOLDER, f), "r") as file:
                data = json.load(file)
                video_id = f.split("_")[0]
                title = data.get("title", "[No Title]")
                uploader = data.get("uploader_id", "[Unknown Uploader]")
                label = f"{title} ({uploader})"
                metadata.append({"video_id": video_id, "label": label, "filename": f})
    return metadata

# Load metadata
insight_meta = get_insight_metadata()
options = [item["label"] for item in insight_meta]
selected_label = st.selectbox("Select Video", options)

# Match selected label back to video_id
selected_meta = next(item for item in insight_meta if item["label"] == selected_label)
selected_id = selected_meta["video_id"]
selected_file = selected_meta["filename"]

def load_insight_file_by_name(filename):
    with open(os.path.join(INSIGHT_FOLDER, filename), "r") as f:
        return json.load(f)

#def load_insight_file(video_id):
#    files = [f for f in os.listdir(INSIGHT_FOLDER) if f.startswith(video_id)]
#    if not files:
#        return None
#    latest_file = sorted(files)[-1]  # Pick latest timestamp
#    with open(os.path.join(INSIGHT_FOLDER, latest_file), "r") as f:
#        return json.load(f)

# UI

st.title("🎥 YouTube Comment Insight Dashboard")

# Find all video IDs
all_files = [f for f in os.listdir(INSIGHT_FOLDER) if f.endswith(".json")]
video_ids = sorted({get_video_id(f) for f in all_files})

#selected_id = st.selectbox("Select Video ID", video_ids)

if selected_id:
    #data = load_insight_file(selected_id)
    data = load_insight_file_by_name(selected_file)
    st.markdown(f"### ▶️ Video Preview")
    st.video(f"https://www.youtube.com/watch?v={selected_id}")

    if data:
        st.markdown("### 📝 Summary")
        st.info(data["summary"])

        # KPIs
        col1, col2, col3 = st.columns(3)
        col1.metric("🧪 Toxic Comments", data["toxic_comment_count"])
        col2.metric("🧹 Spam Comments", data["spam_comment_count"])
        col3.metric("⚖️ Controversy Score", round(data["controversy_score"], 2))

        # Pie Chart
        st.markdown("### 💬 Sentiment Distribution")
        sentiments = data["overall_sentiment_distribution"]
        fig, ax = plt.subplots()
        ax.pie(sentiments.values(), labels=sentiments.keys(), autopct="%1.1f%%")
        ax.axis("equal")
        st.pyplot(fig)

        # Emotions
        #st.markdown("### 😶‍🌫️ Dominant Emotions")
        #st.markdown(" ".join([f"<span style='background-color:#f0f0f0;padding:4px 10px;border-radius:10px;margin:2px'>{e}</span>" for e in data["dominant_emotions"]]), unsafe_allow_html=True)
        render_tag_list("😶‍🌫️ Dominant Emotions", data["dominant_emotions"])

        if data.get("sarcasm_detected"):
            st.warning("😏 Sarcasm or irony detected in the comment section.")

        # Usage:
        render_tag_list("🧠 Key Discussion Topics", data["key_topics"])
        render_tag_list("🏷️ Frequent Bias / Group Mentions", data["frequent_bias_or_group_mentions"])
        render_tag_list("🌐 Languages Detected", data["languages_detected"])

       # # Topics
       # st.markdown("### 🧠 Key Discussion Topics")
       # st.markdown(" ".join([f"<span style='background-color:#e0f7fa;padding:4px 10px;border-radius:10px;margin:2px'>{t}</span>" for t in data["key_topics"]]), unsafe_allow_html=True)

       # # Bias Mentions
       # st.markdown("### 🏷️ Frequent Bias / Group Mentions")
       # st.markdown(" ".join([f"<span style='background-color:#ffe0b2;padding:4px 10px;border-radius:10px;margin:2px'>{b}</span>" for b in data["frequent_bias_or_group_mentions"]]), unsafe_allow_html=True)

       # # Languages
       # st.markdown("### 🌐 Languages Detected")
       # st.markdown(" ".join([f"<span style='background-color:#dcedc8;padding:4px 10px;border-radius:10px;margin:2px'>{l}</span>" for l in data["languages_detected"]]), unsafe_allow_html=True)

        # Raw JSON
        with st.expander("🔍 View Raw JSON"):
            st.json(data)

        # Download
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_filename = f"{selected_id}_insight_export_{timestamp}.json"
        st.download_button("📥 Download JSON", json.dumps(data, indent=2), file_name=export_filename)