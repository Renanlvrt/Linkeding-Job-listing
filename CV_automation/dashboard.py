import streamlit as st
import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="Sprout CV Review Dashboard", layout="wide")

load_dotenv(find_dotenv())

def init_supabase() -> Client:
    return create_client(
        os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    )

def main():
    st.title("🌱 Sprout CV Review Dashboard")
    st.markdown("---")

    supabase = init_supabase()

    # Supabase Auth Session State
    if 'user' not in st.session_state:
        # Note: This is a stub for the user's specific credentials
        # In a real app, you would use st.text_input for email/password
        email = os.getenv("AUTH_EMAIL")
        password = os.getenv("AUTH_PASSWORD")
        if email and password:
            try:
                auth_res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = auth_res.user
            except Exception as e:
                st.sidebar.error(f"Auth failed: {e}")
        else:
            st.sidebar.warning("Auth credentials missing in .env (AUTH_EMAIL/PASSWORD)")
            # Default to service role bypass for local development if allowed
            st.session_state.user = None

    # Sidebar: Stats and Filters
    st.sidebar.header("Operations")
    status_filter = st.sidebar.selectbox("Filter by Status", ["pending", "retry", "completed", "failed"], index=0)
    
    # Real-time Metrics (Aggregated)
    try:
        all_res = supabase.table("job_descriptions").select("id, status, ats_score").execute()
        total = len(all_res.data)
        completed = sum(1 for d in all_res.data if d['status'] == 'completed')
        avg_score = sum(d['ats_score'] for d in all_res.data if d['status'] == 'completed') / (completed or 1)
        
        st.sidebar.metric("Total Jobs", total)
        st.sidebar.metric("Completed", completed)
        st.sidebar.metric("Avg ATS Score", f"{avg_score:.1f}")
    except Exception as e:
        st.sidebar.error("Failed to load metrics.")

    # Main List - Filtered by created_by if auth is active
    query = supabase.table("job_descriptions").select("*").eq("status", status_filter)
    if st.session_state.get('user'):
        query = query.eq("created_by", st.session_state.user.id)
    
    res = query.order("updated_at", desc=True).execute()
    jobs = res.data

    # Metrics Distribution Chart
    if jobs:
        df = pd.DataFrame([{'status': j['status'], 'score': j['ats_score']} for j in jobs if j.get('ats_score')])
        if not df.empty:
            fig = px.histogram(df, x='score', color='status', title='ATS Score Distribution', nbins=20, 
                               color_discrete_map={"completed": "#10b981", "failed": "#ef4444", "retry": "#f59e0b"})
            st.sidebar.plotly_chart(fig, use_container_width=True)

    if not jobs:
        st.info(f"No jobs found with status: {status_filter}")
        return

    # Selection
    job_ids = [f"{j['company']} ({j['id'][:8]})" for j in jobs]
    selected_idx = st.selectbox("Select Application to Review", range(len(job_ids)), format_func=lambda i: job_ids[i])
    selected_job = jobs[selected_idx]

    # Review Section
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Job Description")
        st.text_area("Original JD", selected_job['description'], height=400, disabled=True)
        
    with col2:
        st.subheader("Tailored CV Preview")
        tailored_cv = st.text_area("Markdown Output", selected_job.get('tailored_cv', ''), height=400)
        
        # Actions
        if st.button("Update and Approve"):
            supabase.table("job_descriptions").update({
                "tailored_cv": tailored_cv,
                "status": "completed"
            }).eq("id", selected_job['id']).execute()
            st.success("CV Updated and Approved!")
            st.rerun()

    # Scorer & Metrics Breakdown
    st.markdown("### 📊 Scorer Breakdown")
    metrics_json = json.loads(selected_job.get('keyword_match_json', '{}'))
    if metrics_json:
        cols = st.columns(6)
        m_names = list(metrics_json.keys())
        for i, col in enumerate(cols):
            if i < len(m_names):
                label = m_names[i].replace("_", " ").title()
                col.metric(label, f"{metrics_json[m_names[i]]:.1f}")
    
    st.markdown("#### Quality Suggestions")
    st.warning(selected_job.get('error_log', 'No suggestions available.'))

if __name__ == "__main__":
    main()
