import streamlit as st
import pandas as pd
import json
import io

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="ClarityIQ | Smart Data Cleaning Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# PROFESSIONAL CSS DESIGN
# ==========================================

st.markdown("""
<style>

.main {
    background-color: #F5F8FC;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1, h2, h3 {
    color: #17365D;
}

[data-testid="stMetric"] {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #DCE6F1;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.04);
}

.stButton button {
    background-color: #1769AA;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 8px 20px;
}

.stButton button:hover {
    background-color: #104E80;
    color: white;
}

[data-testid="stFileUploader"] {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    border: 1px dashed #1769AA;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("ClarityIQ")

st.sidebar.write(
    "Your Smart Data Cleaning Assistant"
)

st.sidebar.markdown("---")

st.sidebar.info(
    "Upload your data file, analyze data quality "
    "and clean your dataset easily."
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "Supported Formats: CSV, Excel, JSON, TSV"
)


# ==========================================
# MAIN HEADER
# ==========================================

st.title("ClarityIQ")

st.subheader(
    "Smart Online Data Cleaning Tool"
)

st.write(
    "Analyze, clean and improve your datasets "
    "with an easy-to-use dashboard."
)

st.markdown("---")


# ==========================================
# FILE UPLOAD
# ==========================================

st.subheader("📁 Upload Your Dataset")

st.caption(
    "Supported formats: CSV, XLSX, XLS, JSON and TSV"
)

uploaded_file = st.file_uploader(
    "Choose your data file",
    type=["csv", "xlsx", "xls", "json", "tsv"]
)


# ==========================================
# SAFE DUPLICATE DETECTION
# ==========================================

def get_duplicate_mask(data):

    compare_df = data.copy()

    for column in compare_df.columns:

        compare_df[column] = compare_df[column].map(
            lambda x: json.dumps(
                x,
                sort_keys=True,
                default=str
            )
            if isinstance(x, (dict, list))
            else x
        )

    return compare_df.duplicated()


# ==========================================
# READ FILE FUNCTION
# ==========================================

def read_uploaded_file(uploaded_file):

    file_name = uploaded_file.name.lower()

    file_bytes = uploaded_file.getvalue()

    if file_name.endswith(".csv"):

        return pd.read_csv(
            io.BytesIO(file_bytes)
        )

    elif file_name.endswith((".xlsx", ".xls")):

        return pd.read_excel(
            io.BytesIO(file_bytes)
        )

    elif file_name.endswith(".json"):

        return pd.read_json(
            io.StringIO(
                file_bytes.decode("utf-8-sig")
            )
        )

    elif file_name.endswith(".tsv"):

        return pd.read_csv(
            io.BytesIO(file_bytes),
            sep="\t"
        )

    else:

        raise ValueError(
            "Unsupported file format."
        )


# ==========================================
# MAIN APPLICATION
# ==========================================

if uploaded_file is not None:

    try:

        # Read Uploaded File

        df = read_uploaded_file(uploaded_file)

        st.success(
            f"✅ {uploaded_file.name} uploaded successfully!"
        )

        if df.empty:

            st.warning(
                "The uploaded file is empty. Please upload a dataset containing data."
            )

        else:

            # ==========================================
            # DATA PREVIEW
            # ==========================================

            st.markdown("---")

            st.subheader("📊 Your Uploaded Data")

            st.dataframe(
                df,
                use_container_width=True
            )


            # ==========================================
            # DASHBOARD OVERVIEW
            # ==========================================

            st.markdown("---")

            st.subheader("📈 Dashboard Overview")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Total Rows",
                df.shape[0]
            )

            col2.metric(
                "Total Columns",
                df.shape[1]
            )

            col3.metric(
                "Missing Values",
                int(df.isnull().sum().sum())
            )

            col4.metric(
                "Duplicate Rows",
                int(get_duplicate_mask(df).sum())
            )


            # ==========================================
            # CATEGORY WISE COUNT
            # ==========================================

            category_columns = {
                "city": "🏙️ City Wise Student Count",
                "country": "🌍 Country Wise Record Count",
                "category": "📊 Category Wise Record Count"
            }

            matched_column = next(
                (
                    col for col in df.columns
                    if str(col).strip().lower() in category_columns
                ),
                None
            )

            if matched_column:

                st.markdown("---")

                st.subheader(
                    category_columns[matched_column.strip().lower()]
                )

                category_count = df[matched_column].value_counts()

                st.bar_chart(category_count)


            # ==========================================
            # DYNAMIC CHARTS
            # ==========================================

            st.markdown("---")

            st.subheader("📊 Dynamic Charts")

            chart_columns = df.select_dtypes(
                include=["object", "category"]
            ).columns.tolist()

            if chart_columns:

                chart_column = st.selectbox(
                    "Select a column for chart:",
                    chart_columns
                )

                chart_values = df[chart_column].map(
                    lambda x: json.dumps(
                        x,
                        sort_keys=True,
                        default=str
                    )
                    if isinstance(x, (dict, list))
                    else str(x)
                )

                st.bar_chart(
                    chart_values.value_counts().head(20)
                )

            else:

                st.info(
                    "No text columns available for dynamic charts."
                )


            # ==========================================
            # STATISTICAL SUMMARY
            # ==========================================

            st.markdown("---")

            st.subheader("📐 Statistical Summary")

            numeric_df = df.select_dtypes(
                include="number"
            )

            if not numeric_df.empty:

                summary_col1, summary_col2 = st.columns(2)

                with summary_col1:

                    st.write("**Mean (Average)**")

                    st.dataframe(
                        numeric_df.mean().to_frame(name="Mean"),
                        use_container_width=True
                    )

                    st.write("**Minimum Values**")

                    st.dataframe(
                        numeric_df.min().to_frame(name="Minimum"),
                        use_container_width=True
                    )

                with summary_col2:

                    st.write("**Median**")

                    st.dataframe(
                        numeric_df.median().to_frame(name="Median"),
                        use_container_width=True
                    )

                    st.write("**Maximum Values**")

                    st.dataframe(
                        numeric_df.max().to_frame(name="Maximum"),
                        use_container_width=True
                    )

            else:

                st.info(
                    "No numeric columns available for statistical analysis."
                )


            # ==========================================
            # DATA QUALITY REPORT
            # ==========================================

            st.markdown("---")

            st.subheader("🔍 Data Quality Report")

            quality_report = pd.DataFrame({

                "Column": df.columns,

                "Missing Values": df.isnull().sum().values,

                "Data Type": df.dtypes.astype(str).values

            })

            st.dataframe(
                quality_report,
                use_container_width=True
            )

            st.download_button(
                label="📥 Download Data Quality Report",

                data=quality_report.to_csv(
                    index=False
                ).encode("utf-8"),

                file_name="data_quality_report.csv",

                mime="text/csv"
            )

            st.write("**Missing Values in Each Column:**")

            st.write(df.isnull().sum())

            st.write("**Total Duplicate Rows:**")

            st.write(
                int(get_duplicate_mask(df).sum())
            )


            # ==========================================
            # COLUMN DATA TYPES
            # ==========================================

            st.markdown("---")

            st.subheader("📋 Column Data Types")

            st.write(
                df.dtypes.astype(str)
            )


            # ==========================================
            # DATA CLEANING
            # ==========================================

            st.markdown("---")

            st.subheader("🧹 Clean Your Data")

            st.write(
                "Choose how you want to handle missing values."
            )

            missing_method = st.selectbox(

                "Missing Value Handling",

                [
                    "Not Available",
                    "Mean",
                    "Median",
                    "Drop Rows"
                ]

            )

            if st.button(
                "🧹 Clean Data",
                use_container_width=True
            ):

                # Remove Duplicate Rows

                cleaned_df = df.loc[
                    ~get_duplicate_mask(df)
                ].copy()


                # Remove Completely Empty Columns

                cleaned_df = cleaned_df.dropna(
                    axis=1,
                    how="all"
                )


                # Handle Missing Values

                if missing_method == "Not Available":

                    cleaned_df = cleaned_df.fillna(
                        "Not Available"
                    )


                elif missing_method == "Mean":

                    for column in cleaned_df.select_dtypes(
                        include="number"
                    ).columns:

                        column_mean = cleaned_df[column].mean()

                        if pd.notna(column_mean):

                            cleaned_df[column] = cleaned_df[column].fillna(
                                column_mean
                            )

                    cleaned_df = cleaned_df.fillna(
                        "Not Available"
                    )


                elif missing_method == "Median":

                    for column in cleaned_df.select_dtypes(
                        include="number"
                    ).columns:

                        column_median = cleaned_df[column].median()

                        if pd.notna(column_median):

                            cleaned_df[column] = cleaned_df[column].fillna(
                                column_median
                            )

                    cleaned_df = cleaned_df.fillna(
                        "Not Available"
                    )


                elif missing_method == "Drop Rows":

                    cleaned_df = cleaned_df.dropna()


                # ==========================================
                # CLEANING SUCCESS
                # ==========================================

                st.success(
                    "✅ Your data has been cleaned successfully!"
                )


                # ==========================================
                # CLEANED DATA
                # ==========================================

                st.markdown("---")

                st.subheader("✨ Cleaned Data")

                st.dataframe(
                    cleaned_df,
                    use_container_width=True
                )


                # ==========================================
                # BEFORE VS AFTER CLEANING
                # ==========================================

                st.markdown("---")

                st.subheader(
                    "📊 Before vs After Cleaning"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.write("### Before Cleaning")

                    st.metric(
                        "Total Rows",
                        df.shape[0]
                    )

                    st.metric(
                        "Duplicate Rows",
                        int(get_duplicate_mask(df).sum())
                    )

                    st.metric(
                        "Missing Values",
                        int(df.isnull().sum().sum())
                    )


                with col2:

                    st.write("### After Cleaning")

                    st.metric(
                        "Total Rows",
                        cleaned_df.shape[0]
                    )

                    st.metric(
                        "Duplicate Rows",
                        int(get_duplicate_mask(cleaned_df).sum())
                    )

                    st.metric(
                        "Missing Values",
                        int(cleaned_df.isnull().sum().sum())
                    )


                # ==========================================
                # CLEANING SUMMARY
                # ==========================================

                st.markdown("---")

                st.subheader("📄 Cleaning Summary")

                summary = pd.DataFrame({

                    "Metric": [

                        "Rows Before Cleaning",

                        "Rows After Cleaning",

                        "Rows Removed",

                        "Duplicates Before Cleaning",

                        "Duplicates After Cleaning",

                        "Missing Values Before Cleaning",

                        "Missing Values After Cleaning"

                    ],

                    "Value": [

                        df.shape[0],

                        cleaned_df.shape[0],

                        df.shape[0] - cleaned_df.shape[0],

                        int(get_duplicate_mask(df).sum()),

                        int(get_duplicate_mask(cleaned_df).sum()),

                        int(df.isnull().sum().sum()),

                        int(cleaned_df.isnull().sum().sum())

                    ]

                })


                st.dataframe(
                    summary,
                    use_container_width=True
                )


                st.download_button(

                    label="📥 Download Cleaning Summary",

                    data=summary.to_csv(
                        index=False
                    ).encode("utf-8"),

                    file_name="cleaning_summary.csv",

                    mime="text/csv"

                )


                # ==========================================
                # DOWNLOAD CLEANED CSV
                # ==========================================

                st.download_button(

                    label="📥 Download Cleaned CSV",

                    data=cleaned_df.to_csv(
                        index=False
                    ).encode("utf-8"),

                    file_name="cleaned_data.csv",

                    mime="text/csv"

                )


    except Exception as e:

        st.error(
            f"Unable to process this file: {e}"
        )

        st.info(
            "Please check your file format and try again."
        )


else:

    st.info(
        "👆 Please upload a CSV, Excel, JSON or TSV file to get started."
    )

    st.markdown("---")

    st.subheader("🚀 What ClarityIQ Can Do")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write("📊 **Data Analysis**")

        st.caption(
            "View rows, columns, missing values and duplicates."
        )

    with col2:

        st.write("🧹 **Data Cleaning**")

        st.caption(
            "Remove duplicates and handle missing values."
        )

    with col3:

        st.write("📥 **Download Results**")

        st.caption(
            "Download cleaned datasets and quality reports."
        )


# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.caption(
    "ClarityIQ | Smart Data Cleaning & Analysis Tool"
)
