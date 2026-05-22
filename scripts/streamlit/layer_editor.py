#!/usr/bin/env python3
"""
GPR Ballast Layer Editor - Interactive Streamlit GUI

Allows real-time editing of layer thicknesses, frequency, rock properties,
and fouling, with instant domain/antenna validation and on-demand geometry preview.

Run:
    streamlit run scripts/streamlit/layer_editor.py
"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import matplotlib.pyplot as plt
from src.domain.coordinates import Anchor
from scripts.streamlit.utils import (
    build_config_from_inputs,
    compute_layer_layout,
    validate_antenna_placement,
    generate_scene_checkpoint,
    preview_geometry,
    export_in_file,
    get_fdtd_info,
)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="GPR Ballast Layer Editor",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if 'checkpoint' not in st.session_state:
    st.session_state.checkpoint = None
if 'last_config' not in st.session_state:
    st.session_state.last_config = None


def main():
    st.title("⚙️ GPR Ballast Layer Editor")
    st.markdown(
        "Interactive configuration of railway ballast geometry for GPR simulation. "
        "Adjust layers below, then click **Generate Preview** to render."
    )

    # ========================================================================
    # SIDEBAR: INPUT CONTROLS
    # ========================================================================
    with st.sidebar:
        st.header("Configuration")

        # Frequency
        st.subheader("📡 Simulation Parameters")
        freq_mhz = st.slider(
            "Center Frequency (MHz)",
            min_value=100,
            max_value=2000,
            value=400,
            step=50,
            help="Radar center frequency. Higher = finer resolution, more computation.",
        )
        freq_hz = freq_mhz * 1e6

        # Layer thicknesses
        st.subheader("📏 Layer Thicknesses (m)")
        subgrade = st.slider(
            "Subgrade",
            min_value=0.10,
            max_value=0.30,
            value=0.20,
            step=0.01,
            help="Base soil layer thickness",
        )

        formation = st.slider(
            "Formation (Subballast)",
            min_value=0.05,
            max_value=0.15,
            value=0.10,
            step=0.01,
            help="Transition layer thickness",
        )

        ballast = st.slider(
            "Ballast",
            min_value=0.25,
            max_value=0.55,
            value=0.45,
            step=0.02,
            help="Main crushed rock layer thickness",
        )

        # Rock properties
        st.subheader("🪨 Rock Properties")
        angular = st.checkbox(
            "Angular Rocks",
            value=False,
            help="Polygonal rocks (triangles) vs circular cylinders",
        )

        if angular:
            sides = st.slider(
                "Rock Sides",
                min_value=4,
                max_value=12,
                value=6,
                step=1,
                help="Polygon sides (only for angular rocks)",
            )
        else:
            sides = 0  # Not used for circular rocks

        # Fouling control
        st.subheader("🌫️ Fouling (PVC)")
        pvc = st.slider(
            "Percentage Void Contamination (%)",
            min_value=0,
            max_value=100,
            value=15,
            step=5,
            help="Fine material filling voids. 0% = clean, 100% = fully fouled",
        )

        # Generate button
        st.divider()
        generate_btn = st.button(
            "🔄 Generate Preview",
            use_container_width=True,
            help="Click to generate geometry (1–5 seconds)",
        )

    # ========================================================================
    # MAIN PANEL: DISPLAY & OUTPUT
    # ========================================================================

    # Create two columns: left (metrics), right (visualization)
    col_metrics, col_geometry = st.columns([1, 2], gap="large")

    # ---- LEFT COLUMN: Domain & Antenna Metrics ----
    with col_metrics:
        st.subheader("📊 Domain & Antenna")

        # Compute layout (instant)
        coords = compute_layer_layout(subgrade, formation, ballast)
        antenna_y = coords.get_y(Anchor.ANTENNA_LEVEL)
        domain_y = coords.get_y(Anchor.DOMAIN_TOP)

        # Display domain info
        st.metric("Domain Height (Y)", f"{domain_y:.4f} m")
        st.metric("Antenna Position (Y)", f"{antenna_y:.4f} m")

        # Antenna validation
        validation = validate_antenna_placement(coords, pml_margin_m=0.15)
        if validation["is_safe"]:
            st.success(validation["status"])
        else:
            st.error(validation["status"])

        # FDTD recommendations
        st.divider()
        st.subheader("📐 FDTD Recommendations")
        fdtd = get_fdtd_info(freq_hz)
        col1, col2 = st.columns(2)
        col1.metric("Domain X", f"{fdtd['domain_x_m']:.3f} m")
        col1.metric("Resolution (dX)", f"{fdtd['dx_mm']:.2f} mm")
        col2.metric("Antenna Height", f"{fdtd['antenna_height_m']:.3f} m")
        col2.metric("λ_max", f"{fdtd['lambda_max_m']:.3f} m")

        # Layer breakdown
        st.divider()
        st.subheader("📋 Layer Breakdown")
        breakdown = {
            "Subgrade": subgrade,
            "Formation": formation,
            "Ballast": ballast,
            "Antenna Clearance": coords.stack.antenna_clearance,
            "Air Buffer": coords.stack.air_buffer,
            "**Total (Domain Y)**": domain_y,
        }
        for name, value in breakdown.items():
            if name.startswith("**"):
                st.metric(name.strip("**"), f"{value:.4f} m")
            else:
                st.write(f"  {name}: **{value:.4f} m**")

    # ---- RIGHT COLUMN: Geometry Preview & Download ----
    with col_geometry:
        st.subheader("🖼️ Geometry Preview")

        # Generate scene on button click
        if generate_btn:
            with st.spinner("Generating scene... (1–5 seconds for rock packing)"):
                try:
                    cfg = build_config_from_inputs(freq_hz, angular, sides, pvc)
                    checkpoint = generate_scene_checkpoint(cfg, pvc)
                    st.session_state.checkpoint = checkpoint
                    st.session_state.last_config = {
                        "freq_mhz": freq_mhz,
                        "subgrade": subgrade,
                        "formation": formation,
                        "ballast": ballast,
                        "angular": angular,
                        "sides": sides,
                        "pvc": pvc,
                    }
                    st.success("✓ Scene generated successfully!")
                except Exception as e:
                    st.error(f"Generation failed: {str(e)}")
                    logger.exception("Scene generation error")

        # Display preview if available
        if st.session_state.checkpoint:
            try:
                fig = preview_geometry(st.session_state.checkpoint)
                st.pyplot(fig, use_container_width=True)
                plt.close("all")

                # Download button
                in_content = export_in_file(st.session_state.checkpoint)
                filename = f"ballast_{freq_mhz}MHz_pvc{int(pvc)}.in"
                st.download_button(
                    label="📥 Download .in File",
                    data=in_content,
                    file_name=filename,
                    mime="text/plain",
                    use_container_width=True,
                )

                # Lab analysis results
                st.divider()
                st.subheader("📊 Material Properties")

                meta = st.session_state.checkpoint.metadata or {}

                col1, col2, col3, col4 = st.columns(4)

                fi_computed = meta.get("Lab_FI", None)
                fi_class = meta.get("Lab_Class", "?")
                if fi_computed:
                    col1.metric("FI (Fouling Index)", f"{fi_computed:.1f} {fi_class}")

                pvc_measured = meta.get("mc_pvc_measured", None)
                if pvc_measured:
                    col2.metric("PVC (Measured)", f"{pvc_measured:.1f}%")

                bulk_eps = meta.get("Lab_bulk_eps", None)
                if bulk_eps:
                    col3.metric("ε_bulk", f"{bulk_eps:.2f}")

                col4.metric("Rocks", st.session_state.checkpoint.rock_count)

            except Exception as e:
                st.error(f"Preview rendering failed: {str(e)}")
                logger.exception("Geometry preview error")
        else:
            st.info(
                "👆 Click **Generate Preview** to render geometry and enable download."
            )

    # ========================================================================
    # FOOTER
    # ========================================================================
    st.divider()
    st.caption(
        "**GPR Ballast Layer Editor** — Streamlit POC | "
        "[Docs](https://github.com/anthropics/claude-code) | "
        "[Code](https://github.com/alvarojeria/Synth-GPR)"
    )


if __name__ == "__main__":
    main()
