"""Streamlit UI for loan application chatbot."""

import streamlit as st
import requests
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Loan Approval Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar
st.sidebar.title("🏦 Loan Approval System")
st.sidebar.markdown("""
AI-powered loan approval automation using Claude agents.

**Features:**
- Instant loan decisions
- Transparent reasoning
- Compliance tracking
""")

API_URL = "http://localhost:8000/api"


def submit_loan_application(form_data: dict):
    """Submit application to API."""
    try:
        response = requests.post(f"{API_URL}/applications", json=form_data, timeout=60)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to API. Is the server running on localhost:8000?")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def main():
    """Main Streamlit app."""
    st.title("💰 Loan Approval Assistant")
    st.markdown("Submit your loan application for instant AI-powered evaluation")

    # Create tabs
    tab1, tab2 = st.tabs(["📝 New Application", "📊 Application Status"])

    with tab1:
        st.header("Loan Application Form")

        with st.form("loan_application_form"):
            # Personal Information
            st.subheader("👤 Personal Information")
            col1, col2 = st.columns(2)

            with col1:
                applicant_name = st.text_input(
                    "Full Name",
                    placeholder="John Doe",
                )
                age = st.number_input(
                    "Age",
                    min_value=18,
                    max_value=80,
                    value=35,
                )

            with col2:
                # Location with country selection
                location_options = {
                    "India (IN)": "India",
                    "United States (US)": "United States",
                    "United Kingdom (GB)": "United Kingdom",
                    "Canada (CA)": "Canada",
                    "Australia (AU)": "Australia",
                    "Germany (DE)": "Germany",
                    "France (FR)": "France",
                    "Japan (JP)": "Japan",
                    "Singapore (SG)": "Singapore",
                    "United Arab Emirates (AE)": "United Arab Emirates",
                    "Hong Kong (HK)": "Hong Kong",
                    "Malaysia (MY)": "Malaysia",
                    "Thailand (TH)": "Thailand",
                    "Indonesia (ID)": "Indonesia",
                    "Philippines (PH)": "Philippines",
                    "South Korea (KR)": "South Korea",
                    "Brazil (BR)": "Brazil",
                    "Mexico (MX)": "Mexico",
                    "New Zealand (NZ)": "New Zealand",
                    "South Africa (ZA)": "South Africa",
                }
                location_display = st.selectbox(
                    "Country/Location",
                    list(location_options.keys()),
                    index=0  # Default to India
                )
                location = location_options[location_display]

                employment_type = st.selectbox(
                    "Employment Type",
                    ["Salaried", "Self-employed", "Business Owner"],
                )

            # Financial Information
            st.subheader("💵 Financial Information")
            col3, col4 = st.columns(2)

            with col3:
                monthly_income = st.number_input(
                    "Monthly Income ($)",
                    min_value=1000,
                    value=5000,
                    step=100,
                )
                years_employed = st.number_input(
                    "Years at Current Employment",
                    min_value=0.0,
                    value=3.0,
                    step=0.5,
                )

            with col4:
                credit_score = st.slider(
                    "Credit Score",
                    min_value=300,
                    max_value=850,
                    value=750,
                )
                total_liabilities = st.number_input(
                    "Total Outstanding Debts ($)",
                    min_value=0,
                    value=0,
                    step=1000,
                )

            # Loan Details
            st.subheader("📋 Loan Details")
            col5, col6 = st.columns(2)

            with col5:
                loan_amount = st.number_input(
                    "Requested Loan Amount ($)",
                    min_value=5000,
                    value=50000,
                    step=5000,
                )

            with col6:
                loan_tenure_months = st.number_input(
                    "Loan Tenure (Months)",
                    min_value=6,
                    max_value=360,
                    value=60,
                    step=6,
                )

            # DTI Calculation and Display
            st.divider()
            st.subheader("📊 Financial Metrics")

            # Calculate DTI
            annual_income = monthly_income * 12
            monthly_loan_payment = (loan_amount / loan_tenure_months) if loan_tenure_months > 0 else 0
            total_monthly_debt = (total_liabilities / 12) + monthly_loan_payment if total_liabilities > 0 else monthly_loan_payment
            dti_ratio = (total_monthly_debt / monthly_income * 100) if monthly_income > 0 else 0

            col_dti1, col_dti2, col_dti3 = st.columns(3)

            with col_dti1:
                st.metric("Annual Income", f"${annual_income:,.0f}")

            with col_dti2:
                st.metric("Estimated Monthly Payment", f"${monthly_loan_payment:,.0f}")

            with col_dti3:
                dti_color = "🟢" if dti_ratio < 43 else "🟡" if dti_ratio < 50 else "🔴"
                st.metric("Debt-to-Income Ratio", f"{dti_color} {dti_ratio:.1f}%")

            # Submit button
            submitted = st.form_submit_button(
                "🚀 Submit Application",
                use_container_width=True,
            )

            if submitted:
                if not applicant_name:
                    st.error("Please enter your name")
                else:
                    with st.spinner("🔄 Processing your application..."):
                        form_data = {
                            "applicant_name": applicant_name,
                            "age": age,
                            "monthly_income": monthly_income,
                            "employment_type": employment_type,
                            "years_employed": years_employed,
                            "credit_score": credit_score,
                            "total_liabilities": total_liabilities,
                            "loan_amount": loan_amount,
                            "loan_tenure_months": loan_tenure_months,
                            "location": location,
                        }

                        result = submit_loan_application(form_data)

                        if result:
                            st.success("✅ Application submitted successfully!")
                            st.session_state.application_id = result.get("application_id")
                            st.session_state.show_result = True

                            # Display result
                            st.subheader("📄 Application Summary")
                            col_left, col_right = st.columns(2)

                            with col_left:
                                st.info(f"**Application ID:** {result.get('application_id')}")
                                status = result.get('status', 'Unknown')
                                st.info(f"**Status:** {status.upper()}")

                            with col_right:
                                st.info(f"**Submitted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                            # Display decision if available
                            if result.get("decision"):
                                st.divider()
                                decision = result["decision"]
                                decision_type = decision.get("decision", "UNKNOWN")
                                risk_level = decision.get("risk_level", "UNKNOWN")
                                confidence = decision.get("confidence_score", 0)
                                case_id = decision.get("case_id", "N/A")

                                # Decision badge with color
                                col_dec1, col_dec2, col_dec3 = st.columns(3)

                                with col_dec1:
                                    if decision_type == "APPROVED":
                                        st.success(f"✅ **DECISION: {decision_type}**")
                                    elif decision_type == "REJECTED":
                                        st.error(f"❌ **DECISION: {decision_type}**")
                                    else:
                                        st.warning(f"⏳ **DECISION: {decision_type}**")

                                with col_dec2:
                                    # Risk level badge
                                    if risk_level == "LOW":
                                        st.success(f"🟢 Risk: {risk_level}")
                                    elif risk_level == "MEDIUM":
                                        st.warning(f"🟡 Risk: {risk_level}")
                                    elif risk_level == "HIGH":
                                        st.error(f"🔴 Risk: {risk_level}")
                                    else:
                                        st.error(f"⚫ Risk: {risk_level}")

                                with col_dec3:
                                    st.info(f"📊 Confidence: {confidence:.0f}%")

                                # Case ID and Summary
                                st.markdown(f"**Case ID:** `{case_id}`")

                                if decision.get("decision_summary"):
                                    st.subheader("📋 Decision Summary")
                                    st.text_area(
                                        "Summary",
                                        value=decision["decision_summary"],
                                        height=120,
                                        disabled=True
                                    )

                                # Show rejection reason if rejected
                                if decision_type == "REJECTED" and decision.get("rejection_reason"):
                                    st.error("**Rejection Reason:**")
                                    st.write(decision["rejection_reason"])

                                # Show approval conditions if approved
                                if decision_type == "APPROVED" and decision.get("approval_conditions"):
                                    st.success("**Approval Conditions:**")
                                    conditions = decision.get("approval_conditions", {})
                                    if isinstance(conditions, dict):
                                        for key, value in conditions.items():
                                            st.write(f"• **{key}:** {value}")

                                # Show review notes if under review
                                if decision_type == "UNDER_REVIEW" and decision.get("review_notes"):
                                    st.warning("**Review Notes:**")
                                    st.write(decision["review_notes"])

    with tab2:
        st.header("Check Application Status")

        application_id = st.text_input(
            "Enter your Application ID",
            value=st.session_state.get("application_id", ""),
        )

        if st.button("Check Status", use_container_width=True):
            if application_id:
                try:
                    response = requests.get(f"{API_URL}/applications/{application_id}")
                    if response.status_code == 200:
                        app_data = response.json()

                        # Status overview
                        col_status1, col_status2 = st.columns(2)
                        with col_status1:
                            status = app_data.get('status', 'Unknown')
                            status_color = "🟢" if status == "completed" else "🟡" if status == "processing" else "🔴"
                            st.metric("Application Status", f"{status_color} {status.upper()}")

                        with col_status2:
                            st.metric("Application ID", application_id[:8] + "...")

                        if app_data.get("decision"):
                            decision = app_data["decision"]
                            st.divider()

                            # Decision category with color
                            decision_cat = decision.get('decision_category', decision.get('decision', 'UNKNOWN'))
                            if decision_cat == "APPROVED":
                                st.success(f"✅ DECISION: {decision_cat}")
                            elif decision_cat == "REJECTED":
                                st.error(f"❌ DECISION: {decision_cat}")
                            else:
                                st.warning(f"⏳ DECISION: {decision_cat}")

                            # Case ID and Reference
                            col_case1, col_case2 = st.columns(2)
                            with col_case1:
                                case_id = decision.get('case_id', 'N/A')
                                st.info(f"**Case ID:** `{case_id}`")
                            with col_case2:
                                case_ref = decision.get('case_reference', 'N/A')
                                st.info(f"**Case Reference:** `{case_ref}`")

                            # Confidence and Risk Level
                            col_conf1, col_conf2 = st.columns(2)
                            with col_conf1:
                                confidence = decision.get('confidence_score', 0) * 100
                                st.metric("Confidence Score", f"{confidence:.1f}%")
                            with col_conf2:
                                risk = decision.get('risk_level', 'UNKNOWN')
                                risk_emoji = "🟢" if risk == "LOW" else "🟡" if risk == "MEDIUM" else "🔴" if risk == "HIGH" else "⚫"
                                st.metric("Risk Level", f"{risk_emoji} {risk}")

                            # Decision Summary
                            st.subheader("📋 Decision Summary")
                            summary = decision.get('decision_summary', decision.get('decision_reasoning', 'No summary available'))
                            st.text_area("Summary", value=summary, height=150, disabled=True)

                            # Rejection Reason (if rejected)
                            if decision_cat == "REJECTED" and decision.get('rejection_reason'):
                                st.subheader("❌ Rejection Details")
                                st.error(decision.get('rejection_reason'))

                            # Approval Conditions (if approved)
                            if decision_cat == "APPROVED" and decision.get('approval_conditions'):
                                st.subheader("✅ Approval Conditions")
                                conditions = decision.get('approval_conditions', {})
                                if isinstance(conditions, dict):
                                    for key, value in conditions.items():
                                        st.write(f"• **{key}**: {value}")

                            # Review Notes (if under review)
                            if decision_cat == "UNDER_REVIEW" and decision.get('review_notes'):
                                st.subheader("⏳ Review Notes")
                                st.info(decision.get('review_notes'))

                            # Financial Analysis
                            st.subheader("💰 Financial Analysis")
                            fin_analysis = decision.get('financial_analysis', {})
                            if fin_analysis:
                                col_fin1, col_fin2 = st.columns(2)
                                with col_fin1:
                                    for key, value in list(fin_analysis.items())[:3]:
                                        st.write(f"• **{key}**: {value}")
                                with col_fin2:
                                    for key, value in list(fin_analysis.items())[3:]:
                                        st.write(f"• **{key}**: {value}")

                            # Profile Analysis
                            st.subheader("👤 Profile Analysis")
                            profile = decision.get('profile_analysis', {})
                            if profile:
                                col_prof1, col_prof2 = st.columns(2)
                                with col_prof1:
                                    for key, value in list(profile.items())[:3]:
                                        st.write(f"• **{key}**: {value}")
                                with col_prof2:
                                    for key, value in list(profile.items())[3:]:
                                        st.write(f"• **{key}**: {value}")

                            # Compliance Status
                            st.subheader("📋 Compliance Status")
                            compliance = decision.get('compliance_status', 'Unknown')
                            st.info(f"**Status:** {compliance}")

                        else:
                            st.warning("⏳ Decision not yet available. Please check back later.")

                    else:
                        st.error("❌ Application not found")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please enter an Application ID")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
        <p>🤖 Powered by Claude AI Agents | LangGraph | FastAPI | Streamlit</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
