from __future__ import annotations

import json
import os
from pathlib import Path

import requests
import streamlit as st


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "runs"
API_URL = os.getenv("SPECFORGE_PLATFORM_API_URL", "http://localhost:8000")


def load_latest(kind: str) -> dict | None:
    try:
        response = requests.get(f"{API_URL}/artifacts/{kind}", timeout=2)
        if response.ok:
            return response.json()
    except requests.RequestException:
        pass

    kind_dir = ARTIFACTS_DIR / kind
    files = sorted(kind_dir.glob("*.json"))
    if not files:
        return None
    return json.loads(files[-1].read_text(encoding="utf-8"))["payload"]


st.set_page_config(page_title="SpecForge AI", layout="wide")
st.title("SpecForge AI Dashboard")
st.caption("Evidence-driven quality engineering for the bundled demo system")

quality_plan = load_latest("quality-plan")
generated_tests = load_latest("generated-tests")
run_result = load_latest("run-result")
eval_result = load_latest("eval-result")
report = load_latest("release-report")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Requirements", len((quality_plan or {}).get("requirements", [])))
col2.metric("Generated Tests", len((generated_tests or {}).get("test_cases", [])))
col3.metric(
    "Findings",
    sum(len(item.get("findings", [])) for item in (run_result or {}).get("adapter_runs", [])),
)
col4.metric("Eval Score", (eval_result or {}).get("score", "n/a"))

left, right = st.columns([1.3, 1])

with left:
    st.subheader("Release Recommendation")
    if report:
        st.markdown(f"**Recommendation:** `{report.get('recommendation', 'unknown')}`")
        st.write(report.get("summary", "No summary available yet."))
        st.markdown("**Highlights**")
        for item in report.get("highlights", []):
            st.write(f"- {item}")
    else:
        st.info("No release report has been generated yet.")

    st.subheader("Generated Test Cases")
    for case in (generated_tests or {}).get("test_cases", []):
        with st.expander(f"{case['id']} - {case['title']}"):
            st.write(case["objective"])
            st.write("Adapter:", case["adapter"])
            st.write("Assertions:")
            for assertion in case["assertions"]:
                st.write(f"- {assertion}")

with right:
    st.subheader("Findings")
    adapter_runs = (run_result or {}).get("adapter_runs", [])
    if not adapter_runs:
        st.info("No execution results available yet.")
    for adapter in adapter_runs:
        st.markdown(f"**{adapter['adapter']}** - `{adapter['status']}`")
        for finding in adapter.get("findings", []):
            st.write(f"- [{finding['severity']}] {finding['title']}")

    st.subheader("Eval Metrics")
    for metric in (eval_result or {}).get("metrics", []):
        st.write(
            f"- {metric['name']}: {metric['score']} "
            f"(threshold {metric['threshold']}, passed={metric['passed']})"
        )

st.subheader("Grounded Context")
for item in (quality_plan or {}).get("retrieved_context", []):
    st.code(item["content"], language="markdown")

