import streamlit as st
from rag_engine import load_and_query, get_coverage_confidence
import os
from dotenv import load_dotenv
from security_frameworks import get_all_frameworks, get_framework_questions, get_framework_info
from datetime import datetime

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Security Intake Assistant",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 1.5rem !important;
            background: #f7f8fa !important;
            box-shadow: none !important;
            border: none !important;
        }
        .main-header {
            font-size: 2.2rem;
            font-weight: bold;
            background: linear-gradient(135deg, #1f77b4 0%, #17a2b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0.5rem;
            margin-top: 0.5rem;
        }
        .accuracy-highlight {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 0.7rem 1.2rem;
            border-radius: 12px;
            text-align: center;
            margin: 0.5rem 0 1rem 0;
            font-weight: bold;
            font-size: 1.1rem;
            box-shadow: none !important;
        }
        .stExpander, .answer-box, .source-box, .confidence-box, .upload-section, .sample-data, .search-explanation, .value-prop {
            background: #fff;
            border: 1px solid #e0e0e0 !important;
            border-radius: 14px !important;
            box-shadow: none !important;
            padding: 1.2rem 1.5rem;
            margin-bottom: 1.1rem;
        }
        .stExpander {
            margin-bottom: 0.7rem !important;
            border: none !important;
            border-radius: 14px !important;
        }
        .sidebar-header {
            color: #1f77b4;
            font-weight: bold;
            margin-bottom: 0.7rem;
            font-size: 1.1rem;
        }
        .sample-data {
            background: #e8f4fd;
            border: 1px solid #b3d9ff !important;
            font-size: 0.97rem;
            margin-bottom: 0.7rem;
        }
        .stButton > button, .stFileUploader > div, .stTextInput > div > input {
            border-radius: 8px !important;
            border: 1.5px solid #1f77b4 !important;
            font-size: 0.95rem !important;
        }
        .stButton > button {
            background: #1f77b4 !important;
            color: #fff !important;
            font-weight: 600 !important;
            margin-bottom: 0.5rem !important;
            border-radius: 12px !important;
            width: 100%;
            text-align: left;
        }
        .stButton > button:hover {
            background: #17a2b8 !important;
            color: #fff !important;
        }
        .stTextInput > div > input {
            padding: 0.5rem 1rem !important;
        }
        .stFileUploader > div {
            background: #f8f9fa !important;
            border: 2px dashed #1f77b4 !important;
            padding: 1.2rem !important;
        }
        .stFileUploader > div > label {
            color: #1f77b4 !important;
        }
        .stAlert {
            border-radius: 10px !important;
        }
        .stColumn > div {
            margin-bottom: 0 !important;
        }
        .stMarkdown, .stHeader, .stSubheader {
            margin-bottom: 0.5rem !important;
        }
        .st-bb, .st-cq, .st-cv, .st-cw, .st-cx, .st-cy, .st-cz, .st-da, .st-db, .st-dc, .st-dd, .st-de, .st-df, .st-dg, .st-dh, .st-di, .st-dj, .st-dk, .st-dl, .st-dm, .st-dn, .st-do, .st-dp, .st-dq, .st-dr, .st-ds, .st-dt, .st-du, .st-dv, .st-dw, .st-dx, .st-dy, .st-dz, .st-ea, .st-eb, .st-ec, .st-ed, .st-ee, .st-ef, .st-eg, .st-eh, .st-ei, .st-ej, .st-ek, .st-el, .st-em, .st-en, .st-eo, .st-ep, .st-eq, .st-er, .st-es, .st-et, .st-eu, .st-ev, .st-ew, .st-ex, .st-ey, .st-ez, .st-fa, .st-fb, .st-fc, .st-fd, .st-fe, .st-ff, .st-fg, .st-fh, .st-fi, .st-fj, .st-fk, .st-fl, .st-fm, .st-fn, .st-fo, .st-fp, .st-fq, .st-fr, .st-fs, .st-ft, .st-fu, .st-fv, .st-fw, .st-fx, .st-fy, .st-fz, .st-ga, .st-gb, .st-gc, .st-gd, .st-ge, .st-gf, .st-gg, .st-gh, .st-gi, .st-gj, .st-gk, .st-gl, .st-gm, .st-gn, .st-go, .st-gp, .st-gq, .st-gr, .st-gs, .st-gt, .st-gu, .st-gv, .st-gw, .st-gx, .st-gy, .st-gz, .st-ha, .st-hb, .st-hc, .st-hd, .st-he, .st-hf, .st-hg, .st-hh, .st-hi, .st-hj, .st-hk, .st-hl, .st-hm, .st-hn, .st-ho, .st-hp, .st-hq, .st-hr, .st-hs, .st-ht, .st-hu, .st-hv, .st-hw, .st-hx, .st-hy, .st-hz, .st-ia, .st-ib, .st-ic, .st-id, .st-ie, .st-if, .st-ig, .st-ih, .st-ii, .st-ij, .st-ik, .st-il, .st-im, .st-in, .st-io, .st-ip, .st-iq, .st-ir, .st-is, .st-it, .st-iu, .st-iv, .st-iw, .st-ix, .st-iy, .st-iz, .st-ja, .st-jb, .st-jc, .st-jd, .st-je, .st-jf, .st-jg, .st-jh, .st-ji, .st-jj, .st-jk, .st-jl, .st-jm, .st-jn, .st-jo, .st-jp, .st-jq, .st-jr, .st-js, .st-jt, .st-ju, .st-jv, .st-jw, .st-jx, .st-jy, .st-jz, .st-ka, .st-kb, .st-kc, .st-kd, .st-ke, .st-kf, .st-kg, .st-kh, .st-ki, .st-kj, .st-kk, .st-kl, .st-km, .st-kn, .st-ko, .st-kp, .st-kq, .st-kr, .st-ks, .st-kt, .st-ku, .st-kv, .st-kw, .st-kx, .st-ky, .st-kz, .st-la, .st-lb, .st-lc, .st-ld, .st-le, .st-lf, .st-lg, .st-lh, .st-li, .st-lj, .st-lk, .st-ll, .st-lm, .st-ln, .st-lo, .st-lp, .st-lq, .st-lr, .st-ls, .st-lt, .st-lu, .st-lv, .st-lw, .st-lx, .st-ly, .st-lz, .st-ma, .st-mb, .st-mc, .st-md, .st-me, .st-mf, .st-mg, .st-mh, .st-mi, .st-mj, .st-mk, .st-ml, .st-mm, .st-mn, .st-mo, .st-mp, .st-mq, .st-mr, .st-ms, .st-mt, .st-mu, .st-mv, .st-mw, .st-mx, .st-my, .st-mz, .st-na, .st-nb, .st-nc, .st-nd, .st-ne, .st-nf, .st-ng, .st-nh, .st-ni, .st-nj, .st-nk, .st-nl, .st-nm, .st-nn, .st-no, .st-np, .st-nq, .st-nr, .st-ns, .st-nt, .st-nu, .st-nv, .st-nw, .st-nx, .st-ny, .st-nz, .st-oa, .st-ob, .st-oc, .st-od, .st-oe, .st-of, .st-og, .st-oh, .st-oi, .st-oj, .st-ok, .st-ol, .st-om, .st-on, .st-oo, .st-op, .st-oq, .st-or, .st-os, .st-ot, .st-ou, .st-ov, .st-ow, .st-ox, .st-oy, .st-oz, .st-pa, .st-pb, .st-pc, .st-pd, .st-pe, .st-pf, .st-pg, .st-ph, .st-pi, .st-pj, .st-pk, .st-pl, .st-pm, .st-pn, .st-po, .st-pp, .st-pq, .st-pr, .st-ps, .st-pt, .st-pu, .st-pv, .st-pw, .st-px, .st-py, .st-pz, .st-qa, .st-qb, .st-qc, .st-qd, .st-qe, .st-qf, .st-qg, .st-qh, .st-qi, .st-qj, .st-qk, .st-ql, .st-qm, .st-qn, .st-qo, .st-qp, .st-qq, .st-qr, .st-qs, .st-qt, .st-qu, .st-qv, .st-qw, .st-qx, .st-qy, .st-qz, .st-ra, .st-rb, .st-rc, .st-rd, .st-re, .st-rf, .st-rg, .st-rh, .st-ri, .st-rj, .st-rk, .st-rl, .st-rm, .st-rn, .st-ro, .st-rp, .st-rq, .st-rr, .st-rs, .st-rt, .st-ru, .st-rv, .st-rw, .st-rx, .st-ry, .st-rz, .st-sa, .st-sb, .st-sc, .st-sd, .st-se, .st-sf, .st-sg, .st-sh, .st-si, .st-sj, .st-sk, .st-sl, .st-sm, .st-sn, .st-so, .st-sp, .st-sq, .st-sr, .st-ss, .st-st, .st-su, .st-sv, .st-sw, .st-sx, .st-sy, .st-sz, .st-ta, .st-tb, .st-tc, .st-td, .st-te, .st-tf, .st-tg, .st-th, .st-ti, .st-tj, .st-tk, .st-tl, .st-tm, .st-tn, .st-to, .st-tp, .st-tq, .st-tr, .st-ts, .st-tt, .st-tu, .st-tv, .st-tw, .st-tx, .st-ty, .st-tz, .st-ua, .st-ub, .st-uc, .st-ud, .st-ue, .st-uf, .st-ug, .st-uh, .st-ui, .st-uj, .st-uk, .st-ul, .st-um, .st-un, .st-uo, .st-up, .st-uq, .st-ur, .st-us, .st-ut, .st-uu, .st-uv, .st-uw, .st-ux, .st-uy, .st-uz, .st-va, .st-vb, .st-vc, .st-vd, .st-ve, .st-vf, .st-vg, .st-vh, .st-vi, .st-vj, .st-vk, .st-vl, .st-vm, .st-vn, .st-vo, .st-vp, .st-vq, .st-vr, .st-vs, .st-vt, .st-vu, .st-vv, .st-vw, .st-vx, .st-vy, .st-vz, .st-wa, .st-wb, .st-wc, .st-wd, .st-we, .st-wf, .st-wg, .st-wh, .st-wi, .st-wj, .st-wk, .st-wl, .st-wm, .st-wn, .st-wo, .st-wp, .st-wq, .st-wr, .st-ws, .st-wt, .st-wu, .st-wv, .st-wx, .st-wy, .st-wz, .st-xa, .st-xb, .st-xc, .st-xd, .st-xe, .st-xf, .st-xg, .st-xh, .st-xi, .st-xj, .st-xk, .st-xl, .st-xm, .st-xn, .st-xo, .st-xp, .st-xq, .st-xr, .st-xs, .st-xt, .st-xu, .st-xv, .st-xw, .st-xx, .st-xy, .st-xz, .st-ya, .st-yb, .st-yc, .st-yd, .st-ye, .st-yf, .st-yg, .st-yh, .st-yi, .st-yj, .st-yk, .st-yl, .st-ym, .st-yn, .st-yo, .st-yp, .st-yq, .st-yr, .st-ys, .st-yt, .st-yu, .st-yv, .st-yw, .st-yx, .st-yy, .st-yz, .st-za, .st-zb, .st-zc, .st-zd, .st-ze, .st-zf, .st-zg, .st-zh, .st-zi, .st-zj, .st-zk, .st-zl, .st-zm, .st-zn, .st-zo, .st-zp, .st-zq, .st-zr, .st-zs, .st-zt, .st-zu, .st-zv, .st-zw, .st-zx, .st-zy, .st-zz {
            margin-bottom: 0 !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

def load_sample_pdf():
    """Load the sample PDF file"""
    if os.path.exists("sample_security_policy.pdf"):
        with open("sample_security_policy.pdf", "rb") as f:
            return f.read()
    return None

def get_active_pdf(uploaded_file):
    if uploaded_file:
        return uploaded_file, False
    sample_pdf_data = load_sample_pdf()
    if sample_pdf_data:
        import io
        sample_file = io.BytesIO(sample_pdf_data)
        sample_file.name = "sample_security_policy.pdf"
        return sample_file, True
    return None, False

def initialize_session_state():
    """Initialize session state for tracking answers"""
    if 'answers' not in st.session_state:
        st.session_state.answers = []
    if 'selected_framework' not in st.session_state:
        st.session_state.selected_framework = None

def main():
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🔐 Security Intake Assistant</h1>', unsafe_allow_html=True)
    # Move the green accuracy highlight directly under the main header
    st.markdown("""
    <div class="accuracy-highlight">
        🎯 Built with confidence scoring and source citations to help maintain high answer quality
    </div>
    """, unsafe_allow_html=True)
    
    # Restore the sidebar with framework selector and example questions
    with st.sidebar:
        st.markdown('<div class="sidebar-header">💡 Example Questions</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="sample-data">
        <strong>📄 Sample Data:</strong> 
        <a href="https://github.com/nuggetswise/conveyer/blob/main/sample_security_policy.pdf" target="_blank">Download sample security policy</a>
        <br><small>Contains SOC 2, ISO27001, and security compliance sections for testing</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Security Framework Selection
        st.markdown('<div class="sidebar-header">🏛️ Security Frameworks</div>', unsafe_allow_html=True)
        frameworks = get_all_frameworks()
        framework_names = [f"{info['name']} ({key})" for key, info in frameworks.items()]
        
        selected_framework_display = st.selectbox(
            "Choose a compliance framework:",
            ["Custom Questions"] + framework_names,
            key="framework_selector"
        )
        
        if selected_framework_display != "Custom Questions":
            # Extract framework key from display name
            framework_key = selected_framework_display.split("(")[-1].rstrip(")")
            st.session_state.selected_framework = framework_key
            
            # Show framework info
            framework_info = get_framework_info(framework_key)
            if framework_info:
                st.info(f"**{framework_info['name']}**: {framework_info['description']}")
                
                # Show framework questions
                framework_questions = get_framework_questions(framework_key)
                st.markdown("**Common Questions:**")
                for i, question in enumerate(framework_questions[:5], 1):  # Show first 5
                    if st.button(f"{i}. {question}", key=f"fw_{framework_key}_{i}"):
                        st.session_state.question_input = question
                        st.session_state.example_question = question
                        st.session_state.use_sample_pdf = True
                        st.rerun()
                
                if len(framework_questions) > 5:
                    st.caption(f"... and {len(framework_questions) - 5} more questions")
        else:
            st.session_state.selected_framework = None
        
        # General example questions
        st.markdown('<div class="sidebar-header">🔍 General Questions</div>', unsafe_allow_html=True)
        example_questions = [
            "Do you encrypt data at rest?",
            "How do you handle access controls?",
            "What are your backup procedures?",
            "Do you have a disaster recovery plan?"
        ]
        for question in example_questions:
            if st.button(question, key=f"example_{question}"):
                st.session_state.question_input = question
                st.session_state.example_question = question
                st.session_state.use_sample_pdf = True
                st.rerun()
    
    # Primary workflow section (upload, ask, get answer)
    col1, col2 = st.columns([1, 1])
    with col1:
        st.header("📄 Upload Security Policy")
        with st.container():
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "Choose a PDF file",
                type="pdf",
                help="Upload your security policy, SOC2 report, ISO27001 document, etc."
            )
            st.markdown('</div>', unsafe_allow_html=True)
        if uploaded_file:
            st.success(f"✅ Uploaded: {uploaded_file.name}")
            file_size = len(uploaded_file.getvalue()) / 1024  # KB
            st.info(f"📊 File size: {file_size:.1f} KB")
    with col2:
        st.header("❓ Ask Questions")
        question = st.text_input(
            "Enter your question:",
            placeholder="e.g., Do you encrypt data at rest?",
            key="question_input"
        )
        if hasattr(st.session_state, 'example_question'):
            question = st.session_state.example_question
            del st.session_state.example_question
        active_pdf, is_sample = get_active_pdf(uploaded_file)
        if question and active_pdf:
            with st.spinner("🔍 Searching your policy..."):
                try:
                    answer, source = load_and_query(active_pdf, question)
                    confidence, reasoning = get_coverage_confidence(question)
                    answer_data = {
                        'question': question,
                        'answer': answer,
                        'source': source,
                        'confidence': confidence,
                        'reasoning': reasoning,
                        'framework': st.session_state.selected_framework,
                        'timestamp': datetime.now().isoformat()
                    }
                    st.session_state.answers.append(answer_data)
                    if answer and answer.strip():
                        st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                        st.markdown("**Answer:**")
                        st.write(answer)
                        st.markdown('</div>', unsafe_allow_html=True)
                    if source and source.strip() and ("http" in source or (source.lower().startswith("page") is False and source.lower() != "no source found")):
                        st.markdown('<div class="source-box">', unsafe_allow_html=True)
                        st.markdown("**📖 Source:**")
                        st.write(source)
                        st.markdown('</div>', unsafe_allow_html=True)
                    if confidence and confidence > 0:
                        st.markdown('<div class="confidence-box">', unsafe_allow_html=True)
                        st.markdown(f'<div class="confidence-score">🎯 Confidence: {confidence}%</div>', unsafe_allow_html=True)
                        st.markdown("**Evaluation:**")
                        st.write(reasoning)
                        st.markdown("""
                        <small>
                        <strong>What this means:</strong><br>
                        • <strong>90%+:</strong> Excellent match with detailed, relevant information<br>
                        • <strong>70-89%:</strong> Good match with sufficient context<br>
                        • <strong>50-69%:</strong> Moderate match - answer may be limited<br>
                        • <strong>Below 50%:</strong> Weak match - consider rephrasing question
                        </small>
                        """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Error processing question: {str(e)}")
                    st.info("💡 Try re-uploading the PDF or check if the file is corrupted.")
        elif question and not active_pdf:
            st.warning("⚠️ No PDF available. Please upload a PDF or ensure the sample PDF is present.")

    # Move the expandable info panels to the bottom
    st.divider()
    with st.expander("💡 What makes this unique?", expanded=False):
        st.markdown("""
        <div class="value-prop">
        <h4>🔐 Purpose-built for security workflows</h4>
        <ul>
        <li><strong>Compliance-focused:</strong> Prioritizes SOC 2, ISO27001 terminology and coverage confidence</li>
        <li><strong>Signal-oriented:</strong> Surfaces only what's needed for trust evaluation — no hallucinations</li>
        <li><strong>Minimal & embeddable:</strong> Easy to imagine inside Conveyor's UI or as a Chrome extension</li>
        <li><strong>Framework-aware:</strong> Built-in templates for SOC 2, ISO 27001, GDPR, HIPAA</li>
        </ul>
        <p><em>Designed for teams who want to <strong>answer faster, trust sooner</strong>, and automate the repetitive parts of security review.</em></p>
        </div>
        """, unsafe_allow_html=True)
    with st.expander("🔍 How does the search work?", expanded=False):
        st.markdown("""
        <div class="search-explanation">
        <h4>🧠 AI-Powered Semantic Search</h4>
        <p><strong>Step 1:</strong> Document is split into 500-word chunks with page tracking</p>
        <p><strong>Step 2:</strong> AI analyzes your question and finds the most relevant chunk using:</p>
        <ul>
        <li><strong>Semantic understanding:</strong> "encrypt data at rest" matches "AES-256 secures stored information"</li>
        <li><strong>Compliance terminology:</strong> Understands security and compliance language</li>
        <li><strong>Context relevance:</strong> Prioritizes chunks with detailed, relevant information</li>
        </ul>
        <p><strong>Step 3:</strong> AI generates precise answer from the selected chunk</p>
        <p><strong>Step 4:</strong> Confidence score evaluates answer quality and completeness</p>
        <p><strong>🎯 Goal:</strong> Maintain high accuracy through source validation and iterative improvement</p>
        </div>
        """, unsafe_allow_html=True)
    with st.expander("📊 How is accuracy measured and improved?", expanded=False):
        st.markdown("""
        <div class="search-explanation">
        <h4>🎯 Accuracy Measurement Methodology</h4>
        <h5>📈 How We Measure Accuracy:</h5>
        <ul>
        <li><strong>Human Evaluation:</strong> Security experts review answers against source documents</li>
        <li><strong>Factual Correctness:</strong> Verify answers match the actual policy content</li>
        <li><strong>Completeness:</strong> Check if answers cover the full scope of the question</li>
        <li><strong>Source Attribution:</strong> Ensure citations are accurate and relevant</li>
        </ul>
        <h5>🔧 How We Improve Accuracy:</h5>
        <ul>
        <li><strong>Confidence Scoring:</strong> Low confidence triggers human review</li>
        <li><strong>User Feedback:</strong> Collect corrections and improve training data</li>
        <li><strong>Model Fine-tuning:</strong> Retrain on security-specific documents</li>
        <li><strong>Prompt Engineering:</strong> Optimize instructions for accuracy over creativity</li>
        <li><strong>Source Validation:</strong> Cross-reference multiple chunks when needed</li>
        </ul>
        <h5>⚠️ Important Notes:</h5>
        <ul>
        <li><strong>No Guaranteed Accuracy:</strong> AI systems can make mistakes - always verify critical information</li>
        <li><strong>Domain Specific:</strong> Performance varies by document type and question complexity</li>
        <li><strong>Continuous Improvement:</strong> Accuracy improves with more training data and user feedback</li>
        <li><strong>Human Oversight:</strong> Critical decisions should always involve human review</li>
        </ul>
        <p><em>This MVP demonstrates the approach - production systems would require extensive testing, validation, and ongoing monitoring.</em></p>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>Upload security policies and get instant answers with source citations</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 