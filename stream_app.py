import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="YouTube Insight Viewer", layout="wide")

CSV_FILE = "analyzed_comments/analyzed_comments.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_FILE)
    df['analysis'] = df['analysis'].apply(json.loads)
    return df

def render_tag_list(title, items, bg_color="var(--secondary-background-color)"):
    st.markdown(f"### {title}")
    st.markdown(
        " ".join([
            f"<span style='background-color:{bg_color}; padding:4px 10px; border-radius:10px; margin:2px; display:inline-block; color:var(--text-color)'>{item}</span>"
            for item in items
        ]),
        unsafe_allow_html=True
    )

df = load_data()

# Creator filter
creators = sorted(df["creator_id"].unique())
selected_creator = st.selectbox("Select YouTube Creator", creators)

# Audience Summary per Creator
st.markdown("## 🧭 Audience Interaction Summary")

# Load summarized analysis CSV
summary_file = "summarized_analyzed_comments/summarized_analyzed.csv"
if "summary_df" not in st.session_state:
    summary_df = pd.read_csv(summary_file)    
    summary_df["summary_analysis"] = summary_df["summary_analysis"].apply(json.loads)
    st.session_state.summary_df = summary_df
else:
    summary_df = st.session_state.summary_df

# Fetch the latest summary for the selected creator
creator_summary = summary_df[summary_df["creator_id"] == selected_creator]
if not creator_summary.empty:
    latest_entry = creator_summary.sort_values("timestamp", ascending=False).iloc[0]
    summary = latest_entry["summary_analysis"]

    st.subheader(f"📊 Audience Summary for {selected_creator}")
    st.markdown(f"**Summarized from {len(latest_entry['summarized_video_ids'])} recent videos**")

    col1, col2, col3 = st.columns(3)
    sentiment = summary["audience_sentiment_overview"]
    col1.metric("👍 Positive", sentiment.get("positive", 0))
    col2.metric("😐 Neutral", sentiment.get("neutral", 0))
    col3.metric("👎 Negative", sentiment.get("negative", 0))

    render_tag_list("💥 Common Emotions", summary["common_emotions_expressed"])
    render_tag_list("🧵 Recurrent Themes", summary["recurrent_themes"])
    render_tag_list("🏷️ Group/Bias Mentions", summary["bias_or_group_mentions"])
    render_tag_list("🌍 Languages", summary["languages_used"])

    if summary.get("is_sarcasm_common"):
        st.warning("😏 Sarcasm appears frequently in audience comments.")

    st.markdown(f"**Toxicity Level**: `{summary['spam_or_toxicity_prevalence'].capitalize()}`")
    st.markdown(f"**Behavior Summary**: _{summary['overall_audience_behavior_summary']}_")
    st.success(summary["concluding_summary"])


## End of creator summary    


# Filter videos for selected creator
creator_videos = df[df["creator_id"] == selected_creator]
video_options = creator_videos["title"] + " (" + creator_videos["id"] + ")"
selected_video = st.selectbox("Select Video", video_options)

# Extract row for selected video
video_id = selected_video.split("(")[-1].strip(")")
video_data = creator_videos[creator_videos["id"] == video_id].iloc[0]
analysis = video_data["analysis"]

st.title("🎥 YouTube Comment Insight Dashboard")
st.markdown(f"### ▶️ Video Preview")
st.video(f"https://www.youtube.com/watch?v={video_id}")

# Summary
st.markdown("### 📝 Summary")
st.info(analysis["summary"])

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("🧪 Toxic Comments", analysis["toxic_comment_count"])
col2.metric("🧹 Spam Comments", analysis["spam_comment_count"])
col3.metric("⚖️ Controversy Score", round(analysis["controversy_score"], 2))

# Pie Chart
st.markdown("### 💬 Sentiment Distribution")
sentiments = analysis["overall_sentiment_distribution"]
fig, ax = plt.subplots()
ax.pie(sentiments.values(), labels=sentiments.keys(), autopct="%1.1f%%")
ax.axis("equal")
st.pyplot(fig)

# Render tags
render_tag_list("😶‍🌫️ Dominant Emotions", analysis["dominant_emotions"])
render_tag_list("🧠 Key Discussion Topics", analysis["key_topics"])
render_tag_list("🏷️ Frequent Bias / Group Mentions", analysis["frequent_bias_or_group_mentions"])
render_tag_list("🌐 Languages Detected", analysis["languages_detected"])

# Sarcasm flag
if analysis.get("sarcasm_detected"):
    st.warning("😏 Sarcasm or irony detected in the comment section.")

# Raw JSON
with st.expander("🔍 View Raw JSON"):
    st.json(analysis)

# Download
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
export_filename = f"{video_id}_insight_export_{timestamp}.json"
st.download_button("📥 Download JSON", json.dumps(analysis, indent=2), file_name=export_filename)



