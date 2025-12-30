import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import os
import streamlit as st
import uuid



def show_downloaded_posts():
    st.subheader("📥 Downloaded Instagram Posts")

    files = [f for f in os.listdir(".") if f.endswith(".mp4")]

    if not files:
        st.warning("No downloaded posts found")
        return

    for file in sorted(files, reverse=True):
        st.markdown(f"**{file}**")

        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.video(file)

        st.divider()


# ==========================
# CONFIG
# ==========================

BASE_DIR = Path(__file__).parent
JOBS_FILE = BASE_DIR / "scheduled_jobs.json"

SCRIPTS = {
    "instaloader": BASE_DIR / "instaloader.py",
    "fetch_medias" : BASE_DIR / "fetch_medias.py",
    "filter": BASE_DIR / "filter.py",
    "watermark": BASE_DIR / "watermark.py",
    "feature_engine": BASE_DIR / "feature4_engine.py",
    "ready_to_post": BASE_DIR / "ready_to_post.py",
    "auto_bulk": BASE_DIR / "auto_bulk_scheduler.py",
}

STATUS_COLORS = {
    "pending": "badge-pending",
    "running": "badge-running",
    "failed": "badge-failed",
    "done": "badge-done",
}

# ==========================
# HELPERS
# ==========================

def run_script(label: str, script_path: Path, args=None):
    """
    Run one of your existing Python scripts (instaloader, filter, watermark, etc.)
    and show stdout/stderr nicely in the UI.
    """
    if args is None:
        args = []
    cmd = [sys.executable, str(script_path)] + list(args)
    st.write(f"🔄 Running: `{' '.join(cmd)}`")

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(BASE_DIR),
        )
        out = proc.stdout.strip()
        err = proc.stderr.strip()

        if out:
            st.markdown("**stdout:**")
            st.code(out, language="bash")
        if err:
            st.markdown("**stderr:**")
            st.code(err, language="bash")

        if proc.returncode == 0:
            st.success(f"✅ {label} completed successfully.")
        else:
            st.error(f"❌ {label} failed with code {proc.returncode}.")
    except Exception as e:
        st.error(f"❌ Error running {label}: {e}")


def load_jobs():
    if not JOBS_FILE.exists():
        return []
    try:
        return json.loads(JOBS_FILE.read_text(encoding="utf8"))
    except Exception:
        return []


def save_jobs(jobs):
    JOBS_FILE.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf8")


def status_badge(status: str) -> str:
    css_class = STATUS_COLORS.get(status, "badge-pending")
    label = status.upper()
    return f"<span class='badge {css_class}'>{label}</span>"


def parse_time(j):
    try:
        return datetime.fromisoformat(j["scheduled_time"].replace(" ", "T"))
    except Exception:
        return datetime.max


# ==========================
# PAGE CONFIG & GLOBAL STYLE
# ==========================

st.set_page_config(
    page_title="Insta Automation Control Center",
    page_icon="🚀",
    layout="wide",
)

# Premium CSS
st.markdown(
    """
    <style>
    body {
        background: radial-gradient(circle at top left, #020617, #020617 40%, #020617 100%);
        color: #e5e7eb;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    /* Sidebar glass */
    [data-testid="stSidebar"] > div {
        background: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(22px);
        border-right: 1px solid rgba(148, 163, 184, 0.35);
    }

    /* Glass cards */
    .glass-card {
        background: radial-gradient(circle at top left, rgba(30,64,175,0.18), rgba(15,23,42,0.96));
        padding: 18px 20px;
        border-radius: 20px;
        border: 1px solid rgba(148, 163, 184, 0.4);
        box-shadow: 0 18px 45px rgba(15,23,42,0.85);
        backdrop-filter: blur(26px);
        margin-bottom: 14px;
        transition: 0.22s ease;
    }
    .glass-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 26px 60px rgba(15,23,42,0.95);
    }

    .section-title {
        font-size: 18px;
        font-weight: 600;
        color: #f9fafb;
        margin-bottom: 4px;
    }
    .section-sub {
        font-size: 12px;
        color: #9ca3af;
    }

    /* KPI cards */
    .metric-box {
        background: linear-gradient(145deg, rgba(15,23,42,0.96), rgba(30,64,175,0.35));
        border-radius: 18px;
        border: 1px solid rgba(129, 140, 248, 0.75);
        padding: 16px 18px;
        text-align: left;
        backdrop-filter: blur(18px);
        box-shadow: 0 18px 45px rgba(15,23,42,0.95);
        transition: .22s;
    }
    .metric-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 26px 65px rgba(59,130,246,0.75);
    }
    .metric-label {
        font-size: 11px;
        color: #cbd5f5;
        text-transform: uppercase;
        letter-spacing: .12em;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #e5e7ff;
    }
    .metric-sub {
        font-size: 11px;
        color: #9ca3af;
        margin-top: 3px;
    }

    /* Neon badges */
    .badge {
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: .06em;
        color: #f9fafb;
    }
    .badge-pending {
        background: rgba(250, 204, 21, 0.22);
        box-shadow: 0 0 16px rgba(250, 204, 21, 0.55);
    }
    .badge-running {
        background: rgba(59, 130, 246, 0.32);
        box-shadow: 0 0 16px rgba(59, 130, 246, 0.75);
    }
    .badge-done {
        background: rgba(34, 197, 94, 0.28);
        box-shadow: 0 0 16px rgba(34, 197, 94, 0.75);
    }
    .badge-failed {
        background: rgba(239, 68, 68, 0.3);
        box-shadow: 0 0 16px rgba(239, 68, 68, 0.85);
    }

    /* Jobs cards */
    .job-card {
        padding: 10px 12px;
        border-radius: 16px;
        background: radial-gradient(circle at top left, rgba(15,23,42,0.95), rgba(15,23,42,0.98));
        border: 1px solid rgba(55, 65, 81, 0.85);
        margin-bottom: 8px;
    }
    .job-path {
        color: #e5e7eb;
        font-size: 13px;
        font-weight: 500;
    }
    .job-meta {
        color: #9ca3af;
        font-size: 11px;
        margin-top: 2px;
    }

    /* Top title */
    .top-title {
        font-size: 24px;
        font-weight: 700;
        letter-spacing: .08em;
        text-transform: uppercase;
        color: #e5e7eb;
    }
    .top-sub {
        font-size: 12px;
        color: #9ca3af;
        margin-top: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================
# SIDEBAR NAV
# ==========================

st.sidebar.title("🚀 Insta Automation")
st.sidebar.caption("Full pipeline control · Aman edition")

page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "📥 Downloaded Posts",
        "1) Download & Filter",
        "2) Watermark",
        "3) AI Generation",
        "4) Ready-to-Post",
        "5) Bulk Scheduler",
        "6) Jobs Monitor",
        "Settings / Info",
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption("Pipeline: Download → Filter → Watermark → AI → Ready → Schedule → Post")
": Download → Filter → Watermark → AI → Ready → Schedule → Post"

# ==========================
# COMMON DATA
# ==========================

jobs = load_jobs()
total_jobs = len(jobs)
pending_jobs = sum(1 for j in jobs if j.get("status") == "pending")
running_jobs = sum(1 for j in jobs if j.get("status") == "running")
failed_jobs = sum(1 for j in jobs if j.get("status") == "failed")
done_jobs = sum(1 for j in jobs if j.get("status") == "done")


# ==========================
# PAGE: DASHBOARD
# ==========================


# ---------------- CONFIG ----------------
ACCOUNTS_FILE = "accounts.json"
JOBS_FILE = "scheduled_jobs.json"
UPLOAD_DIR = Path("posts/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Instagram Automation", layout="centered")

st.title("📸 Instagram Automation Panel")

# ---------------- LOAD ACCOUNTS ----------------
if Path(ACCOUNTS_FILE).exists():
    accounts = json.loads(Path(ACCOUNTS_FILE).read_text())
else:
    accounts = []

# ---------------- ADD ACCOUNT ----------------
st.subheader("🔐 Add Instagram Account")

username = st.text_input("Instagram Username")
session_file = st.text_input("Session File (example: session_account1.json)")

if st.button("➕ Add Account"):
    if username and session_file:
        accounts.append({
            "username": username,
            "session_file": session_file
        })
        Path(ACCOUNTS_FILE).write_text(json.dumps(accounts, indent=2))
        st.success("✅ Account added")
    else:
        st.error("❌ Fill both fields")

# ---------------- SELECT ACCOUNT ----------------
st.divider()
st.subheader("👤 Select Account")

if not accounts:
    st.warning("⚠️ Add at least one account")
    st.stop()

st.subheader("👥 Select Accounts (Multiple)")

selected_accounts = st.multiselect(
    "Choose accounts to post",
    options=accounts,
    format_func=lambda x: x["username"]
)

if not selected_accounts:
    st.warning("⚠️ At least one account select cheyyali")
    st.stop()


# ---------------- CREATE POST ----------------
st.divider()
st.subheader("📝 Create Post")

post_type = st.radio("Post Type", ["Image", "Reel", "Story"])

uploaded_file = st.file_uploader(
    "Upload media",
    type=["jpg", "png", "mp4"]
)

caption = st.text_area(
    "Caption (leave empty for AI auto-generate)"
)

if uploaded_file:
    file_path = UPLOAD_DIR / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("📂 Media uploaded")

# ---------------- ACTION BUTTONS ----------------
col1, col2 = st.columns(2)
post_now = col1.button("🚀 Post Now")
schedule_later = col2.button("📅 Schedule Later")

# ---------------- POST NOW ----------------
import time
import shutil
from auto_scheduler import post_image, post_reel, post_story

if post_now and uploaded_file:

    for i, acc in enumerate(selected_accounts):
        session = acc["session_file"]
        username = acc["username"]

        try:
            # 🔥 IMPORTANT: create UNIQUE reel per account
            unique_path = file_path.with_name(
                f"{file_path.stem}_{username}{file_path.suffix}"
            )
            shutil.copy(file_path, unique_path)

            if post_type == "Image":
                post_image(session, str(unique_path), username)

            elif post_type == "Reel":
                post_reel(session, str(unique_path), username)

                # ⏳ VERY IMPORTANT delay
                time.sleep(60)

            else:
                post_story(session, str(unique_path), username)

            st.success(f"✅ Posted to @{username}")

        except Exception as e:
            st.error(f"❌ Failed for @{username}: {e}")



# ---------------- SCHEDULE LATER ----------------
if schedule_later and uploaded_file:
    date = st.date_input("Select date")
    time = st.time_input("Select time")

    run_at = datetime.combine(date, time).isoformat()

    jobs = []
    if Path(JOBS_FILE).exists():
        jobs = json.loads(Path(JOBS_FILE).read_text())

    for acc in selected_accounts:
        job = {
            "id": uuid.uuid4().hex,
            "username": acc["username"],
            "session_file": acc["session_file"],
            "post_type": post_type.lower(),
            "media_path": str(file_path),
            "caption": caption,
            "run_at": run_at,
            "status": "pending"
        }
        jobs.append(job)

    Path(JOBS_FILE).write_text(json.dumps(jobs, indent=2))
    st.success("📅 Scheduled for ALL selected accounts")


# st.markdown("### 🔍 Fetch Instagram Posts")



# target_username = st.text_input(
#     "Instagram username (posts fetch",
#     placeholder="example: natgeo"
# )


# if st.button("📥 Fetch My Instagram Posts"):
#     if not target_username.strip():
#         st.error("❌ Username enter")
#     else:
#         run_script(
#             "Fetch Instagram Posts",
#             SCRIPTS["fetch_medias"],
#             args=[target_username]
#         )



# if page == "Dashboard":
#     st.markdown(
#         """
#         <div style="margin-bottom: 12px;">
#           <div class="top-title">INSTA AUTOMATION CONTROL CENTER</div>
#           <div class="top-sub">One place to orchestrate your full pipeline from download → upload</div>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )

#     col1, col2, col3, col4 = st.columns(4)
#     with col1:
#         st.markdown(
#             f"""
#             <div class="metric-box">
#               <div class="metric-label">TOTAL JOBS</div>
#               <div class="metric-value">{total_jobs}</div>
#               <div class="metric-sub">All time</div>
#             </div>
#             """,
#             unsafe_allow_html=True,
#         )
#     with col2:
#         st.markdown(
#             f"""
#             <div class="metric-box">
#               <div class="metric-label">PENDING</div>
#               <div class="metric-value">{pending_jobs}</div>
#               <div class="metric-sub">Queued for posting</div>
#             </div>
#             """,
#             unsafe_allow_html=True,
#         )
#     with col3:
#         st.markdown(
#             f"""
#             <div class="metric-box">
#               <div class="metric-label">DONE</div>
#               <div class="metric-value">{done_jobs}</div>
#               <div class="metric-sub">Uploaded successfully</div>
#             </div>
#             """,
#             unsafe_allow_html=True,
#         )
#     with col4:
#         st.markdown(
#             f"""
#             <div class="metric-box">
#               <div class="metric-label">FAILED / STUCK</div>
#               <div class="metric-value">{failed_jobs}</div>
#               <div class="metric-sub">Needs attention</div>
#             </div>
#             """,
#             unsafe_allow_html=True,
#         )

#     st.markdown("<br>", unsafe_allow_html=True)

elif page == "📥 Downloaded Posts":
    st.markdown("## 📥 Downloaded Instagram Posts")
    show_downloaded_posts()
    


    # Pipeline visualization
    st.markdown(
        """
        <div class="glass-card">
          <div class="section-title">Automation Pipeline</div>
          <div class="section-sub">Full flow your backend already does — now visualized.</div>
          <div style="display:flex; gap:12px; margin-top:14px;">
            <div class="metric-box" style="flex:1; text-align:center;">
              <div class="metric-label">STEP 1</div>
              <div class="metric-value" style="font-size:16px;">Download</div>
              <div class="metric-sub">instaloader.py</div>
            </div>
            <div class="metric-box" style="flex:1; text-align:center;">
              <div class="metric-label">STEP 2</div>
              <div class="metric-value" style="font-size:16px;">Filter</div>
              <div class="metric-sub">filter.py</div>
            </div>
            <div class="metric-box" style="flex:1; text-align:center;">
              <div class="metric-label">STEP 3</div>
              <div class="metric-value" style="font-size:16px;">Watermark</div>
              <div class="metric-sub">watermark.py</div>
            </div>
            <div class="metric-box" style="flex:1; text-align:center;">
              <div class="metric-label">STEP 4</div>
              <div class="metric-value" style="font-size:16px;">AI Generate</div>
              <div class="metric-sub">feature4_engine.py</div>
            </div>
            <div class="metric-box" style="flex:1; text-align:center;">
              <div class="metric-label">STEP 5</div>
              <div class="metric-value" style="font-size:16px;">Ready</div>
              <div class="metric-sub">ready_to_post.py</div>
            </div>
            <div class="metric-box" style="flex:1; text-align:center;">
              <div class="metric-label">STEP 6</div>
              <div class="metric-value" style="font-size:16px;">Schedule</div>
              <div class="metric-sub">auto_bulk_scheduler.py + scheduler_runner.py</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### ⏱ Upcoming Jobs")
    upcoming = [j for j in jobs if j.get("status") in ("pending", "failed")]
    upcoming = sorted(upcoming, key=parse_time)

    if not upcoming:
        st.info("No pending or failed jobs. All clear ✅")
    else:
        for j in upcoming[:10]:
            status = j.get("status", "pending")
            st.markdown(
                """
                <div class="job-card">
                  <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                      <div class="job-path">
                        {j['media_path'].split('final_ready_to_post')[-1].lstrip('\\\\/')}
                      </div>
                      <div class="job-meta">
                        ID: {j['id'][:10]} · User: @{j['username']} · Created: {j.get('created_at','-')}
                      </div>
                    </div>
                    <div style="text-align:right;">
                      <div style="font-size:12px; color:#e5e7eb; font-weight:500;">
                        {j['scheduled_time']}
                      </div>
                      <div style="margin-top:4px;">
                        {status_badge(status)}
                      </div>
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )



# ==========================
# 1) DOWNLOAD & FILTER
# ==========================

elif page == "1) Download & Filter":
    st.markdown("## 1️⃣ Download & Filter")

    st.markdown(
        """
        <div class="glass-card">
          <div class="section-title">Instaloader — Download posts</div>
          <div class="section-sub">Run your <code>instaloader.py</code> script to pull fresh posts.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("⬇ Run instaloader.py", use_container_width=True):
        run_script("Instaloader", SCRIPTS["instaloader"])

    st.markdown(
        """
        <div class="glass-card">
          <div class="section-title">Filter media</div>
          <div class="section-sub">Clean invalid / broken downloads using <code>filter.py</code>.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("🧹 Run filter.py", use_container_width=True):
        run_script("Filter", SCRIPTS["filter"])

# ==========================
# 2) WATERMARK
# ==========================

elif page == "2) Watermark":
    st.markdown("## 2️⃣ Watermark")

    st.markdown(
        """
        <div class="glass-card">
          <div class="section-title">Apply watermark on media</div>
          <div class="section-sub">
            Uses <code>watermark.py</code> to read from filtered downloads and write to
            <code>filtered_downloads_watermarked/</code>.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("💧 Run watermark.py", use_container_width=True):
        run_script("Watermark", SCRIPTS["watermark"])

# ==========================
# 3) AI GENERATION
# ==========================

elif page == "3) AI Generation":
    st.markdown("## 3️⃣ AI Caption / Hook / CTA / Hashtags")

    st.markdown(
        """
        <div class="glass-card">
          <div class="section-title">Run feature4_engine.py</div>
          <div class="section-sub">
            Generates caption, hook, CTA, comments, hashtags, keywords, analysis for each post under
            <code>filtered_downloads_watermarked/</code>.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("🤖 Run feature4_engine.py", use_container_width=True):
        run_script("Feature4 Engine", SCRIPTS["feature_engine"])

# ==========================
# 4) READY-TO-POST
# ==========================

elif page == "4) Ready-to-Post":
    st.markdown("## 4️⃣ Build final ready_to_post folders")

    st.markdown(
        """
        <div class="glass-card">
          <div class="section-title">Create final_ready_to_post</div>
          <div class="section-sub">
            Uses <code>ready_to_post.py</code> to assemble each post folder with media + final_caption.txt.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("📦 Run ready_to_post.py", use_container_width=True):
        run_script("Ready to Post", SCRIPTS["ready_to_post"])

# ==========================
# 5) BULK SCHEDULER
# ==========================

elif page == "5) Bulk Scheduler":
    st.markdown("## 5️⃣ Auto Bulk Scheduler")

    st.markdown(
        """
        <div class="glass-card">
          <div class="section-title">Create jobs from final_ready_to_post</div>
          <div class="section-sub">
            Runs <code>auto_bulk_scheduler.py</code> and appends jobs into <code>scheduled_jobs.json</code>.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("🗂 Run auto_bulk_scheduler.py", use_container_width=True):
        run_script("Auto Bulk Scheduler", SCRIPTS["auto_bulk"])

    st.markdown("### Jobs summary")
    st.write(f"Jobs file: `{JOBS_FILE}`")
    st.write(f"Total jobs: {total_jobs}, Pending: {pending_jobs}, Done: {done_jobs}, Failed: {failed_jobs}")

# ==========================
# 6) JOBS MONITOR
# ==========================

elif page == "6) Jobs Monitor":
    st.markdown("## 6️⃣ Jobs Monitor (JSON view)")

    st.info(
        "Posting actually runs from `scheduler_runner.py` via Windows Task Scheduler. "
        "This page is a live view / manual editor for `scheduled_jobs.json`."
    )

    filter_status = st.selectbox(
        "Filter by status",
        options=["all", "pending", "running", "failed", "done"],
        index=0,
    )

    filtered = jobs
    if filter_status != "all":
        filtered = [j for j in jobs if j.get("status") == filter_status]

    if not filtered:
        st.info("No jobs for this filter.")
    else:
        for j in filtered:
            status = j.get("status", "pending")
            st.markdown(
                """
                <div class="job-card">
                  <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                      <div class="job-path">
                        {j['media_path'].split('final_ready_to_post')[-1].lstrip('\\\\/')}
                      </div>
                      <div class="job-meta">
                        ID: {j['id']}<br>
                        User: @{j['username']}<br>
                        Scheduled: {j['scheduled_time']}<br>
                        Created: {j.get('created_at','-')}<br>
                        Retries: {j.get('retries',0)}
                      </div>
                    </div>
                    <div style="text-align:right;">
                      <div>{status_badge(status)}</div>
                      <div class="job-meta" style="margin-top:6px; max-width:260px;">
                        Last error: {j.get('last_error','-')[:110]}
                      </div>
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("### Manual status update")
    colA, colB, colC = st.columns(3)
    with colA:
        target_id = st.text_input("Job ID")
    with colB:
        new_status = st.selectbox(
            "New status",
            options=["pending", "failed", "done", "running"],
        )
    with colC:
        if st.button("Update job"):
            if not target_id.strip():
                st.error("Enter job ID.")
            else:
                jobs2 = load_jobs()
                ok = False
                for job in jobs2:
                    if job["id"] == target_id.strip():
                        job["status"] = new_status
                        ok = True
                        break
                if ok:
                    save_jobs(jobs2)
                    st.success("Job updated.")
                    st.experimental_rerun()
                else:
                    st.error("Job ID not found.")

# ==========================
# SETTINGS / INFO
# ==========================

else:
    st.markdown("## ⚙️ Settings & Info")

    st.markdown(
        f"""
        <div class="glass-card">
          <div class="section-title">Paths</div>
          <div class="section-sub">
            <code>Base dir:</code> {BASE_DIR}<br>
            <code>Jobs file:</code> {JOBS_FILE}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="glass-card">
          <div class="section-title">How this UI works</div>
          <div class="section-sub">
            <ul>
              <li>Ye dashboard tumhare existing Python scripts ko <code>subprocess</code> se run karta hai.</li>
              <li>Real posting: <code>scheduler_runner.py</code> + Windows Task Scheduler se hoti hai (jaise abhi setup hai).</li>
              <li>Agar isse Streamlit Cloud par host karoge, wahan local scripts / JSON direct access nahi milega –
              uske liye alag API bridge banana padega (future upgrade).</li>
            </ul>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🔁 Reload jobs from disk"):
        st.experimental_rerun()
