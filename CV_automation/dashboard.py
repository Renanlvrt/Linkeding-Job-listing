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

def load_css():
    with open(os.path.join(os.path.dirname(__file__), "dashboard_style.css"), "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_match_evidence(job):
    """Section for 3-step reasoning insights (Flexible for user modification)"""
    st.markdown("### ✨ Match Strategy")
    with st.expander("🔍 View Skill Mapping Evidence", expanded=True):
        found = job.get('keywords_found', {})
        missing = job.get('missing_keywords', [])
        
        if found:
            st.markdown("#### ✅ Alignment Found")
            for skill, snippet in found.items():
                if snippet:
                    st.markdown(f"<div class='evidence-found'><b>{skill}:</b><br><i>{snippet}</i></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='evidence-found'><b>{skill}:</b> Identified (Implicit)</div>", unsafe_allow_html=True)
        
        if missing:
            st.markdown("#### ⚠️ Potential Gaps")
            for skill in missing:
                st.markdown(f"<div class='evidence-missing'>{skill}</div>", unsafe_allow_html=True)

def render_cv_editor(supabase, job):
    """Modular CV Editor - User can change CV logic here later"""
    st.subheader("📝 Tailored CV Draft")
    tailored_text = st.text_area("Markdown Preview", job.get('tailored_cv', ''), height=500)
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🚀 Update & Approve", use_container_width=True):
            supabase.table("job_descriptions").update({
                "tailored_cv": tailored_text,
                "status": "completed"
            }).eq("id", job['id']).execute()
            st.toast("Success! CV finalized.")
            st.rerun()
    with col_b:
        if st.button("♻️ Re-Generate", use_container_width=True):
            supabase.table("job_descriptions").update({"status": "pending"}).eq("id", job['id']).execute()
            st.toast("Triggering AI Tailoring...")
            st.rerun()

def main():
    load_css()
    st.title("🌱 Sprout Review Center")
    st.markdown("---")

    supabase = init_supabase()

    # Authentication Session State (Simplified logic as requested)
    if 'user' not in st.session_state:
        st.sidebar.subheader("🔒 Authentication")
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            try:
                auth_res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = auth_res.user
                st.rerun()
            except: st.sidebar.error("Auth failed.")
        
        if not st.session_state.get('user'):
            st.sidebar.info("Dev Mode: Service Role")
            st.session_state.user = None
    else:
        if st.sidebar.button("Logout"):
            del st.session_state.user
            st.rerun()

    # Sidebar: Status and High-Level Actions
    st.sidebar.header("Pipeline Status")
    status_filter = st.sidebar.selectbox("Filter", ["pending", "retry", "completed", "failed"], index=2)
    
    # Real-time Metrics
    try:
        all_res = supabase.table("job_descriptions").select("id, status, ats_score").execute()
        total = len(all_res.data)
        completed = sum(1 for d in all_res.data if d['status'] == 'completed')
        avg_score = sum(d['ats_score'] for d in all_res.data if d['status'] == 'completed') / (completed or 1)
        
        st.sidebar.metric("Active Jobs", total)
        st.sidebar.metric("Match Velocity", f"{avg_score:.1f}%")
        
        df = pd.DataFrame([{'score': j['ats_score']} for j in all_res.data if j.get('ats_score')])
        if not df.empty:
            fig = px.histogram(df, x='score', title='Global ATS Distribution', color_discrete_sequence=['#10b981'])
            fig.update_layout(height=200, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.sidebar.plotly_chart(fig, use_container_width=True)
    except: pass

    # Fetch Jobs
    query = supabase.table("job_descriptions").select("*").eq("status", status_filter)
    if st.session_state.get('user'):
        query = query.eq("created_by", st.session_state.user.id)
    
    jobs = query.order("updated_at", desc=True).execute().data

    if not jobs:
        st.info(f"No jobs currently in '{status_filter}' state.")
        return

    # Modern Selector
    job_ids = [f"{j['company']} ({j['id'][:8]})" for j in jobs]
    selected_idx = st.selectbox("Select Application to Review", range(len(job_ids)), format_func=lambda i: job_ids[i])
    selected_job = jobs[selected_idx]

    # Status Display
    status_class = f"badge-{selected_job['status']}"
    st.markdown(f"Status: <span class='badge {status_class}'>{selected_job['status'].upper()}</span>", unsafe_allow_html=True)

    # main Layout (Flexible/Modular)
    row1 = st.container()
    row2 = st.container()

    with row1:
        c1, c2 = st.columns([2, 3])
        with c1:
            st.markdown("### 📋 Job Context")
            st.text_area("Description", selected_job['description'], height=500, disabled=True)
        with c2:
            render_cv_editor(supabase, selected_job)

    with row2:
        st.divider()
        m1, m2 = st.columns([3, 2])
        with m1:
            render_match_evidence(selected_job)
        with m2:
            st.markdown("### 📊 Scoring Metrics")
            raw_metrics = selected_job.get('keyword_match_json', {})
            if isinstance(raw_metrics, str):
                raw_metrics = json.loads(raw_metrics or '{}')
            
            if raw_metrics:
                for k, v in raw_metrics.items():
                    st.progress(v/100, text=f"{k.replace('_', ' ').title()}: {v:.1f}%")
            
            if selected_job.get('error_log'):
                with st.expander("🛠 AI Optimization Logs"):
                    st.info(selected_job['error_log'])

if __name__ == "__main__":
    main()
