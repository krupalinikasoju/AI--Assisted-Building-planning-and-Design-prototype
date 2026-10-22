import math
from io import BytesIO

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="BuildWise AI", page_icon="🏗️", layout="wide")

# BuildWise AI is an educational concept-design prototype. Outputs are not construction documents.
st.markdown("""
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
.small-note {font-size: .88rem; color: #64748b;}
</style>
""", unsafe_allow_html=True)

st.title("🏗️ BuildWise AI")
st.caption("Building planning • coordinated concept layouts • member analysis • quantity and cost estimates")
st.warning(
    "Concept-design prototype only. It does not establish legal floor permission, soil capacity, or construction safety. "
    "Have the site data, structural model, calculations and drawings checked by qualified local professionals before construction."
)

# Only three project inputs. Geometry/engineering assumptions are shown in the results, not asked as required inputs.
with st.sidebar:
    st.header("Project inputs")
    location = st.text_input("Location", "Hyderabad, Telangana, India")
    plot_area = st.number_input("Plot area (m²)", min_value=30.0, max_value=5000.0, value=150.0, step=10.0)
    building_type = st.selectbox("Building type", ["Residential", "Commercial", "Mixed use", "Institutional"])
    st.divider()
    st.caption("These are the only project inputs. The prototype uses clearly stated geometry and loading assumptions.")

# ---------- geometry and option screening ----------
# Assumed near-rectangular plot geometry from area; not survey data.
plot_width = math.sqrt(plot_area / 1.5)
plot_length = plot_area / plot_width
# Placeholder coverage and setbacks: not locally verified.
coverage_assumption = 0.60
setback_assumption = 1.0
footprint = plot_area * coverage_assumption
approx_w = plot_width * math.sqrt(coverage_assumption)
approx_l = plot_length * math.sqrt(coverage_assumption)
floor_plate = min(footprint, max(20.0, (plot_width - 2*setback_assumption)*(plot_length - 2*setback_assumption)))
floor_plate = min(floor_plate, footprint)

# These are candidate options only; actual permissibility must be verified.
candidate_floors = [1, 2, 3, 4]
max_candidate = 4 if plot_area >= 120 else 3
options = [f for f in candidate_floors if f <= max_candidate]
option_labels = {1: "Ground floor", 2: "G+1 (2 floors)", 3: "G+2 (3 floors)", 4: "G+3 (4 floors)"}

st.subheader("1. Site assessment and floor options")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Plot area", f"{plot_area:,.1f} m²")
c2.metric("Assumed plot shape", f"{plot_width:.1f} × {plot_length:.1f} m")
c3.metric("Concept footprint", f"{floor_plate:.1f} m²")
c4.metric("Location", location[:28] + ("…" if len(location) > 28 else ""))

st.info(
    "The plot dimensions are an estimated near-rectangular geometry derived from area, not a surveyed boundary. "
    "Coverage and setback values below are demo assumptions, not verified rules for the entered location."
)
rules_df = pd.DataFrame([
    ["Plot geometry", f"{plot_width:.2f} m × {plot_length:.2f} m", "Assumed from area; survey required"],
    ["Coverage used in concept", f"{coverage_assumption*100:.0f}%", "Placeholder only; verify local rules"],
    ["Setback used in concept", f"{setback_assumption:.1f} m each side", "Placeholder only; verify local rules"],
    ["Soil bearing capacity", "Not provided", "Geotechnical report required"],
    ["FAR/FSI / height / fire limits", "Not verified", "Check applicable local authority rules"],
], columns=["Assessment item", "Prototype value", "Status"])
st.dataframe(rules_df, use_container_width=True, hide_index=True)

st.markdown("**Candidate floor options**")
option_df = pd.DataFrame([
    {"Option": option_labels[f], "Floors": f, "Indicative total floor area (m²)": round(floor_plate*f, 1),
     "Status": "Candidate only — feasibility checks required"}
    for f in options
])
st.dataframe(option_df, use_container_width=True, hide_index=True)
chosen_floors = st.radio(
    "Choose an option to develop",
    options=options,
    format_func=lambda f: option_labels[f],
    horizontal=True,
    key="floor_option"
)
total_area = floor_plate * chosen_floors

# ---------- architectural floor plan ----------
def room_plan(floor_idx, width, length, btype):
    """Make a dimensioned schematic floor plan. Room zoning is illustrative, not code-compliant design."""
    fig, ax = plt.subplots(figsize=(7.2, 8.0))
    ax.set_aspect("equal")
    ax.set_xlim(-1.7, width+1.7)
