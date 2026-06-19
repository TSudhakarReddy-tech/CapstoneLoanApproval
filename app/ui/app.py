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
                location = st.text_input(
                    "Location",
                    placeholder="New York, NY",
                )
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
                                st.info(f"**Status:** {result.get('status')}")

                            with col_right:
                                st.info(f"**Submitted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

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
                        st.success(f"**Status:** {app_data.get('status')}")

                        if app_data.get("decision"):
                            decision = app_data["decision"]
                            st.subheader("Decision Details")
                            st.write(f"**Decision:** {decision.get('decision')}")
                            st.write(f"**Case Reference:** {decision.get('case_reference')}")

                    else:
                        st.error("Application not found")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter an Application ID")

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
