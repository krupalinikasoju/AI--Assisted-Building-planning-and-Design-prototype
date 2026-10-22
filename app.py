import math
from datetime import date
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc

st.set_page_config(page_title="BuildWise AI", page_icon="🏗️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.block-container {max-width: 1500px; padding-top: 1rem; padding-bottom: 3rem;}
[data-testid="stAppViewContainer"] {overflow-y: auto !important;}
[data-testid="stMain"] {overflow: visible !important;}
.bw-note {font-size: .9rem; color: #536273;}
</style>
""", unsafe_allow_html=True)

st.title("🏗️ BuildWise AI")
st.subheader("AI-Assisted Building Planning & Structural Design")
st.write("Concept workflow: site assessment → floor options → architectural concept → RCC layout → preliminary analysis → quantities and estimate.")
st.warning("Educational prototype only. Drawings are schematic and calculations are preliminary demonstrations, not construction-ready or certified designs. Local rules, site survey, geotechnical data, and professional structural verification are required.")

with st.sidebar:
    st.header("1. Project inputs")
    location = st.text_input("Location", "Hyderabad, Telangana, India")
    plot_area = st.number_input("Plot area (m²)", min_value=30.0, max_value=10000.0, value=150.0, step=10.0)
    building_type = st.selectbox("Building type", ["Residential", "Commercial", "Mixed use", "Institutional"])
    st.caption("These are the three main project inputs. The other values are explicitly stated concept assumptions.")

# transparent demo assumptions
coverage = 0.60
setback = 1.0
plot_w = math.sqrt(plot_area / 1.5)
plot_l = plot_area / plot_w
footprint = min(plot_area * coverage, max(20.0, (plot_w - 2*setback) * (plot_l - 2*setback)))
foot_w = math.sqrt(footprint / 1.5)
foot_l = footprint / foot_w
floor_height = 3.0
candidate_floors = [1, 2, 3, 4] if plot_area >= 120 else [1, 2, 3]
labels = {1: "Ground floor (G+0)", 2: "G+1 (2 floors)", 3: "G+2 (3 floors)", 4: "G+3 (4 floors)"}

st.header("2. Site assessment and floor options")
a, b, c, d = st.columns(4)
a.metric("Plot area", f"{plot_area:.1f} m²")
b.metric("Concept footprint", f"{footprint:.1f} m²")
c.metric("Estimated plot geometry", f"{plot_w:.1f} × {plot_l:.1f} m")
d.metric("Location", location if len(location) < 24 else location[:21] + "…")
st.caption("Plot geometry is inferred from area, not a site survey. 60% coverage and 1 m setbacks are demo assumptions, not verified local regulations.")
option_rows = []
for floors in candidate_floors:
    option_rows.append({"Option": labels[floors], "Floors": floors, "Indicative floor area (m²)": round(footprint*floors, 1), "Status": "Candidate only; planning and structural checks required"})
option_df = pd.DataFrame(option_rows)
st.dataframe(option_df, use_container_width=True, hide_index=True)
selected_label = st.selectbox("Choose a floor option to develop", [labels[x] for x in candidate_floors], index=min(1, len(candidate_floors)-1))
selected_floors = next(k for k, v in labels.items() if v == selected_label)
built_area = footprint * selected_floors
st.success(f"Selected concept: {selected_label} • Indicative total floor area: {built_area:.1f} m²")

# helper for drawings
def style_plan(ax, title, w, l):
    ax.set_title(title, fontsize=12, pad=12)
    ax.set_xlim(-1.5, w+1.5); ax.set_ylim(-1.8, l+1.8)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(f"Width ≈ {w:.2f} m"); ax.set_ylabel(f"Length ≈ {l:.2f} m")
    ax.grid(False)
    ax.annotate("N", xy=(w+0.8, l+0.8), ha="center", va="center", fontweight="bold")
    ax.annotate("", xy=(w+0.8, l+0.35), xytext=(w+0.8, l-0.1), arrowprops={"arrowstyle":"->", "lw":1.5})

def architectural_plan(w, l, floor_no):
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.add_patch(Rectangle((0,0), w, l, fill=False, linewidth=3, edgecolor="black"))
    # Conceptual room zoning. These are not detailed architectural/CAD drawings.
    splitx, splity = w*0.52, l*0.52
    ax.plot([splitx, splitx], [0, l], color="black", lw=1.7)
    ax.plot([0, w], [splity, splity], color="black", lw=1.7)
    ax.plot([splitx, w], [splity*0.55, splity*0.55], color="black", lw=1.4)
    ax.text(splitx/2, (splity+l)/2, "Living / common\narea", ha="center", va="center", fontsize=9)
    ax.text((splitx+w)/2, (splity+l)/2, "Bedroom / room", ha="center", va="center", fontsize=9)
    ax.text(splitx/2, splity/2, "Kitchen / dining", ha="center", va="center", fontsize=9)
    ax.text((splitx+w)/2, l*0.23, "Bedroom / utility", ha="center", va="center", fontsize=9)
    # entry gap and simple door swing marker
    ax.plot([w*0.25, w*0.42], [0,0], color="white", lw=5)
    ax.plot([w*0.25, w*0.25], [0, min(0.8,l*.12)], color="black", lw=1.2)
    ax.add_patch(Arc((w*.25,0), min(1.5,w*.25), min(1.5,w*.25), theta1=0, theta2=90, color="black", lw=1))
    # dimension lines
    ax.annotate("", xy=(0,-.65), xytext=(w,-.65), arrowprops={"arrowstyle":"<->", "lw":1})
    ax.text(w/2,-.95,f"{w:.2f} m",ha="center",va="top",fontsize=9)
    ax.annotate("", xy=(-.65,0), xytext=(-.65,l), arrowprops={"arrowstyle":"<->", "lw":1})
    ax.text(-.95,l/2,f"{l:.2f} m",ha="center",va="center",rotation=90,fontsize=9)
    style_plan(ax, f"Floor {floor_no+1} — schematic room-zone plan", w, l)
    fig.tight_layout()
    return fig

def structural_plan(kind, w, l):
    fig, ax = plt.subplots(figsize=(9, 6))
    nx, ny = 3, 3
    xs = np.linspace(0,w,nx); ys = np.linspace(0,l,ny)
    ax.add_patch(Rectangle((0,0),w,l,fill=False,edgecolor="black",lw=1.5))
    for i,x in enumerate(xs):
        ax.plot([x,x],[0,l], color="black", lw=1.0 if kind=="Column plan" else .7, linestyle="--" if kind=="Column plan" else "-")
    for j,y in enumerate(ys):
        ax.plot([0,w],[y,y], color="black", lw=1.0 if kind=="Column plan" else .7, linestyle="--" if kind=="Column plan" else "-")
    for i,x in enumerate(xs):
        for j,y in enumerate(ys):
            if kind == "Column plan":
                ax.add_patch(Rectangle((x-.12,y-.12),.24,.24,fill=False,edgecolor="black",lw=1.6))
                ax.text(x+.15,y+.15,f"C{i*ny+j+1}",fontsize=8)
            elif kind == "Beam plan":
                ax.text(x+.08,y+.12,f"J{i*ny+j+1}",fontsize=7)
            elif kind == "Slab plan":
                if i<nx-1 and j<ny-1:
                    ax.text((xs[i]+xs[i+1])/2,(ys[j]+ys[j+1])/2,f"S{j*(nx-1)+i+1}",ha="center",va="center",fontsize=9)
            elif kind == "Foundation plan":
                ax.add_patch(Rectangle((x-.28,y-.28),.56,.56,fill=False,edgecolor="black",lw=1.3))
                ax.text(x+.3,y+.3,f"F{i*ny+j+1}",fontsize=8)
    style_plan(ax, kind + " — concept grid", w, l)
    fig.tight_layout()
    return fig

st.header("3. Architectural planning")
st.write("Choose a floor below to view its schematic room zoning. This is not a permit-ready plan; detailed room dimensions, wall thicknesses, all openings and stair design need architectural development.")
arch_tabs = st.tabs(["Ground floor"] + [f"Floor {i+1}" for i in range(1, selected_floors)])
for i, tab in enumerate(arch_tabs):
    with tab:
        st.pyplot(architectural_plan(foot_w, foot_l, i), use_container_width=True)
        st.caption("Outer dimensions are approximate footprint dimensions. Internal room divisions are schematic, not measured room sizes.")

st.header("4. RCC structural layout sheets")
st.write("The same conceptual grid is used for all sheets. Member IDs are placeholders and are not a designed structural frame.")
struct_tabs = st.tabs(["Column plan", "Beam plan", "Slab plan", "Foundation plan"])
for tab, kind in zip(struct_tabs, ["Column plan", "Beam plan", "Slab plan", "Foundation plan"]):
    with tab:
        st.pyplot(structural_plan(kind, foot_w, foot_l), use_container_width=True)
        st.caption("Concept coordination drawing only. Final member locations and sizes require engineering design and site-specific information.")

st.header("5. Preliminary load analysis")
slab_t = 0.15
concrete_unit_weight = 25.0
finish_load = 1.0
wall_allowance = 1.0
live_load = 2.0 if building_type == "Residential" else 3.0
slab_dead = slab_t * concrete_unit_weight
service_area_load = slab_dead + finish_load + wall_allowance + live_load
load_df = pd.DataFrame([
    ["Slab self-weight", f"{slab_t:.2f} m × {concrete_unit_weight:.1f} kN/m³", slab_dead, "Assumed"],
    ["Floor finish allowance", "Allowance", finish_load, "Assumed"],
    ["Wall/partition allowance", "Allowance", wall_allowance, "Assumed"],
    ["Imposed load", building_type, live_load, "Illustrative; verify applicable standard"],
    ["Total service area load", "Sum of above", service_area_load, "Preliminary only"],
], columns=["Load item", "Basis", "Load (kN/m²)", "Status"])
st.dataframe(load_df, use_container_width=True, hide_index=True)
st.caption("This simple ledger excludes detailed wall line loads, member self-weight, load combinations, and complete wind/seismic modelling.")

st.header("6. Simplified beam analysis demo")
col1, col2, col3 = st.columns(3)
span = col1.number_input("Illustrative beam span (m)", min_value=2.0, max_value=8.0, value=4.0, step=.5)
trib_width = col2.number_input("Illustrative tributary width (m)", min_value=1.0, max_value=6.0, value=3.0, step=.5)
beam_self_weight = col3.number_input("Beam self-weight allowance (kN/m)", min_value=1.0, max_value=10.0, value=2.5, step=.5)
line_load = service_area_load * trib_width + beam_self_weight
reaction = line_load * span / 2
max_moment = line_load * span**2 / 8
max_shear = line_load * span / 2
# elastic deflection for a simply supported beam under UDL; illustrative section/material values
E = 25e6 # kN/m², illustrative concrete modulus
bw, depth = .25, .40
I = bw * depth**3 / 12
delta_mm = (5 * line_load * span**4 / (384 * E * I)) * 1000
m1,m2,m3,m4 = st.columns(4)
m1.metric("Line load", f"{line_load:.2f} kN/m")
m2.metric("Reaction (each support)", f"{reaction:.2f} kN")
m3.metric("Max. moment", f"{max_moment:.2f} kN·m")
m4.metric("Estimated deflection", f"{delta_mm:.2f} mm")
x = np.linspace(0, span, 100)
V = reaction - line_load*x
M = reaction*x - line_load*x**2/2
p1,p2 = st.columns(2)
with p1:
    fig, ax = plt.subplots(figsize=(6,3.4)); ax.plot(x,V); ax.axhline(0,color="black",lw=.8); ax.fill_between(x,V,0,alpha=.15); ax.set_title("Shear force diagram (SFD)"); ax.set_xlabel("Span (m)"); ax.set_ylabel("Shear (kN)"); ax.grid(True,alpha=.25); st.pyplot(fig,use_container_width=True)
with p2:
    fig, ax = plt.subplots(figsize=(6,3.4)); ax.plot(x,M); ax.axhline(0,color="black",lw=.8); ax.fill_between(x,M,0,alpha=.15); ax.set_title("Bending moment diagram (BMD)"); ax.set_xlabel("Span (m)"); ax.set_ylabel("Moment (kN·m)"); ax.grid(True,alpha=.25); st.pyplot(fig,use_container_width=True)
st.caption("This is a separate simply supported beam example under a uniform load. It is not analysis of the full building, and it is not a code design check.")

st.header("7. Preliminary quantity and cost estimate")
# rough concept allowances, not a measured BOQ
concrete_m3 = footprint * selected_floors * 0.22 + footprint * 0.12
steel_kg = concrete_m3 * 95
masonry_m2 = footprint * selected_floors * 0.75
rates = {"Concrete materials (INR/m³)": 7000.0, "Reinforcement steel (INR/kg)": 75.0, "Masonry (INR/m²)": 900.0, "Labour and miscellaneous (%)": 25.0, "Contingency (%)": 5.0}
with st.expander("Edit indicative unit rates"):
    r1,r2,r3 = st.columns(3)
    rates["Concrete materials (INR/m³)"] = r1.number_input("Concrete materials (₹/m³)", min_value=0.0, value=rates["Concrete materials (INR/m³)"], step=500.0)
    rates["Reinforcement steel (INR/kg)"] = r2.number_input("Steel (₹/kg)", min_value=0.0, value=rates["Reinforcement steel (INR/kg)"], step=5.0)
    rates["Masonry (INR/m²)"] = r3.number_input("Masonry (₹/m²)", min_value=0.0, value=rates["Masonry (INR/m²)"], step=100.0)
concrete_cost = concrete_m3 * rates["Concrete materials (INR/m³)"]
steel_cost = steel_kg * rates["Reinforcement steel (INR/kg)"]
masonry_cost = masonry_m2 * rates["Masonry (INR/m²)"]
subtotal = concrete_cost + steel_cost + masonry_cost
labour = subtotal * rates["Labour and miscellaneous (%)"] / 100
contingency = (subtotal + labour) * rates["Contingency (%)"] / 100
total_cost = subtotal + labour + contingency
estimate_df = pd.DataFrame([
    ["Concrete material allowance", f"{concrete_m3:.2f} m³", rates["Concrete materials (INR/m³)"], concrete_cost],
    ["Reinforcement steel allowance", f"{steel_kg:.0f} kg", rates["Reinforcement steel (INR/kg)"], steel_cost],
    ["Masonry allowance", f"{masonry_m2:.1f} m²", rates["Masonry (INR/m²)"], masonry_cost],
    ["Labour and miscellaneous allowance", "25% of subtotal", None, labour],
    ["Contingency allowance", "5% after labour", None, contingency],
], columns=["Item", "Rough quantity", "Indicative unit rate (₹)", "Indicative amount (₹)"])
st.dataframe(estimate_df, use_container_width=True, hide_index=True)
st.metric("Indicative total", f"₹{total_cost:,.0f}")
st.caption("Rough planning allowances only—not a measured bill of quantities. It excludes detailed reinforcement schedules, openings, finishes, MEP, excavation and local rate verification.")

st.header("8. Design checks and limitations")
checks_df = pd.DataFrame([
    ["Local planning / FAR / setbacks", "Not verified", "Confirm with current local authority rules"],
    ["Soil bearing capacity / settlement", "Not checked", "Geotechnical investigation required"],
    ["Full building frame analysis", "Not implemented", "Requires a coordinated structural model"],
    ["Wind / seismic design", "Not implemented", "Determine applicable parameters and code combinations"],
    ["RCC strength and reinforcement design", "Not implemented", "Design and verify using applicable Indian Standards"],
    ["Foundation sizing and design", "Not implemented", "Requires column reactions and geotechnical data"],
], columns=["Check", "Status", "Next requirement"])
st.dataframe(checks_df, use_container_width=True, hide_index=True)

st.header("9. Download preliminary report")
report = f"""BUILDWISE AI — PRELIMINARY CONCEPT REPORT\nDate: {date.today().isoformat()}\nLocation: {location}\nBuilding type: {building_type}\nPlot area: {plot_area:.2f} m²\nSelected option: {selected_label}\nConcept footprint: {footprint:.2f} m²\nIndicative total floor area: {built_area:.2f} m²\nAssumptions: coverage {coverage*100:.0f}%, setback {setback:.1f} m (not verified locally), slab thickness {slab_t:.2f} m.\n\nSIMPLIFIED BEAM EXAMPLE\nSpan: {span:.2f} m\nLine load: {line_load:.2f} kN/m\nSupport reaction: {reaction:.2f} kN each\nMaximum moment: {max_moment:.2f} kN m\nMaximum shear: {max_shear:.2f} kN\nEstimated elastic deflection: {delta_mm:.2f} mm\n\nROUGH ESTIMATE\nConcrete allowance: {concrete_m3:.2f} m³\nSteel allowance: {steel_kg:.0f} kg\nMasonry allowance: {masonry_m2:.1f} m²\nIndicative total: INR {total_cost:,.0f}\n\nLIMITATIONS\nConcept-only schematic drawings and rough quantity allowances. No certified local planning compliance, full building structural analysis, code-compliant RCC design, or foundation design. Do not use for construction without qualified professional review and site-specific data.\n"""
st.download_button("Download preliminary report (.txt)", data=report, file_name="buildwise_preliminary_report.txt", mime="text/plain")
st.download_button("Download floor options (.csv)", data=option_df.to_csv(index=False), file_name="buildwise_floor_options.csv", mime="text/csv")
st.download_button("Download rough estimate (.csv)", data=estimate_df.to_csv(index=False), file_name="buildwise_rough_estimate.csv", mime="text/csv")
st.success("The page has reached the final section. Scroll through each section above to review the concept outputs.")
