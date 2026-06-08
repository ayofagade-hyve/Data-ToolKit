import streamlit as st
import pandas as pd
import io


def render_value_classifier():
    """
    Value Classifier Tool
    ---------------------
    Lets users upload a spreadsheet, pick a column, see all unique values,
    and manually map them to new categories/groups.
    """

    st.header("🏷️ Value Classifier")

    with st.expander("ℹ️ How it works", expanded=False):
        st.markdown(
            """
            **This tool lets you reclassify values in any column of your data.**

            1. **Upload** your CSV or Excel file.
            2. **Select** the column you want to reclassify.
            3. **Review** all the unique values found in that column (with counts).
            4. **Map** each value to a new category — either one-by-one or by
               grouping multiple values together.
            5. **Download** the result with a new column containing your classifications.

            ---
            **Example:**

            | Original Value | Count | Map To |
            |---|---|---|
            | Fintech | 12 | Financial Services |
            | InsurTech | 5 | Financial Services |
            | SaaS | 20 | Software |
            | PaaS | 3 | Software |
            | Logistics | 8 | Supply Chain |

            Any value you leave unmapped keeps its original value.
            """
        )

    st.divider()

    # ------------------------------------------------------------------ #
    # STEP 1 — File upload
    # ------------------------------------------------------------------ #
    uploaded_file = st.file_uploader(
        "📂 Upload your file (CSV or Excel)",
        type=["csv", "xlsx", "xls"],
        key="vc_file_upload",
    )

    if uploaded_file is None:
        st.info("Upload a file to get started.")
        return

    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        elif uploaded_file.name.endswith(".xls"):
            df = pd.read_excel(uploaded_file, engine="xlrd")
        else:
            st.error("Unsupported file type.")
            return
    except Exception as e:
        st.error(f"Could not read file: {e}")
        return

    st.success(f"Loaded **{len(df):,}** rows × **{len(df.columns)}** columns")

    # ------------------------------------------------------------------ #
    # STEP 2 — Column selection
    # ------------------------------------------------------------------ #
    column = st.selectbox(
        "🔎 Select the column to classify",
        options=df.columns.tolist(),
        key="vc_column_select",
    )
    if column is None:
        return

    # ------------------------------------------------------------------ #
    # STEP 3 — Extract unique values & counts
    # ------------------------------------------------------------------ #
    series = df[column].copy()
    series_str = series.fillna("(blank)").astype(str)

    value_counts = series_str.value_counts().reset_index()
    value_counts.columns = ["Original Value", "Count"]
    value_counts = value_counts.sort_values("Original Value").reset_index(drop=True)

    st.markdown(f"**{len(value_counts)}** unique values found in column `{column}`")

    # ------------------------------------------------------------------ #
    # STEP 4 — Mapping mode
    # ------------------------------------------------------------------ #
    mode = st.radio(
        "Choose a mapping mode:",
        options=["Map Individually", "Group Multiple Values"],
        horizontal=True,
        key="vc_mode",
    )

    mapping = {}

    if mode == "Map Individually":
        st.markdown(
            "Edit the **Map To** column below. Leave blank to keep the original value."
        )
        edit_df = value_counts.copy()
        edit_df["Map To"] = ""
        edited = st.data_editor(
            edit_df,
            column_config={
                "Original Value": st.column_config.TextColumn("Original Value", disabled=True),
                "Count": st.column_config.NumberColumn("Count", disabled=True),
                "Map To": st.column_config.TextColumn(
                    "Map To", help="Type the new category name. Leave blank to keep original."
                ),
            },
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            key="vc_data_editor",
        )
        for _, row in edited.iterrows():
            map_to = str(row["Map To"]).strip()
            if map_to and map_to != "nan":
                mapping[row["Original Value"]] = map_to

    else:  # Group Multiple Values
        st.markdown(
            "Create groups below, then assign values to each group via multi-select."
        )
        if "vc_groups" not in st.session_state:
            st.session_state["vc_groups"] = []

        col_add1, col_add2 = st.columns([3, 1])
        with col_add1:
            new_group = st.text_input("New group name", key="vc_new_group", placeholder="e.g. Software")
        with col_add2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Add Group", key="vc_add_group"):
                if new_group and new_group not in st.session_state["vc_groups"]:
                    st.session_state["vc_groups"].append(new_group)
                    st.rerun()

        if st.session_state["vc_groups"]:
            unique_vals = value_counts["Original Value"].tolist()
            already_assigned = set()
            for group in st.session_state["vc_groups"]:
                selected = st.multiselect(
                    f"📁 **{group}** — select values to include:",
                    options=unique_vals,
                    key=f"vc_group_{group}",
                )
                for val in selected:
                    mapping[val] = group
                    already_assigned.add(val)
            unassigned = [v for v in unique_vals if v not in already_assigned]
            if unassigned:
                st.caption(
                    f"ℹ️ {len(unassigned)} value(s) not assigned to any group "
                    f"— they will keep their original value."
                )
                with st.expander("Show unassigned values"):
                    st.write(unassigned)
        else:
            st.info('Add at least one group using the field above, then click "➕ Add Group".')

    # ------------------------------------------------------------------ #
    # STEP 5 — Apply mapping
    # ------------------------------------------------------------------ #
    st.divider()
    if not mapping:
        st.warning("No mappings defined yet. Fill in your mapping above, then apply.")
    else:
        st.markdown(f"**{len(mapping)}** value(s) will be remapped.")
        with st.expander("Preview mapping"):
            st.json(mapping)

    new_col_name = st.text_input(
        "Name for the new classified column:",
        value=f"{column}_classified",
        key="vc_new_col_name",
    )

    if st.button("🚀 Apply Classification", type="primary", key="vc_apply"):
        df[new_col_name] = series_str.map(lambda v: mapping.get(v, v))
        df[new_col_name] = df[new_col_name].replace("(blank)", pd.NA)
        st.session_state["vc_result_df"] = df
        st.session_state["vc_applied"] = True

    # ------------------------------------------------------------------ #
    # STEP 6 — Preview & Download
    # ------------------------------------------------------------------ #
    if st.session_state.get("vc_applied"):
        result_df = st.session_state["vc_result_df"]
        st.subheader("✅ Result Preview")
        st.dataframe(result_df.head(50), use_container_width=True)

        st.markdown(f"**Distribution of `{new_col_name}`:**")
        dist = result_df[new_col_name].fillna("(blank)").value_counts().reset_index()
        dist.columns = [new_col_name, "Count"]
        st.dataframe(dist, use_container_width=True, hide_index=True)

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            csv_data = result_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download CSV",
                data=csv_data,
                file_name="classified_output.csv",
                mime="text/csv",
                key="vc_download_csv",
            )
        with col_dl2:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                result_df.to_excel(writer, index=False, sheet_name="Classified")
            st.download_button(
                "⬇️ Download Excel",
                data=buffer.getvalue(),
                file_name="classified_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="vc_download_xlsx",
            )
