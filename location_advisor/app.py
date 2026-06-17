import streamlit as st
from dotenv import load_dotenv
import sys
import os

# Ensure the project root is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from src.agents.intake_agent import extract_brief
from src.agents.research_agent import research_areas
from src.agents.recommendation_agent import generate_recommendation

# Page configuration
st.set_page_config(
    page_title="Business Location Advisor",
    page_icon="📍",
    layout="centered"
)

# Custom Premium Styling (Sleek Dark/Modern Theme, Gradients, Glassmorphism)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
        
        * {
            font-family: 'Outfit', sans-serif;
        }
        
        .main {
            background: linear-gradient(135deg, #0d0f12 0%, #171c24 100%);
        }
        
        /* Premium Header Styling */
        .title-container {
            text-align: center;
            padding: 2.5rem 1rem 1rem 1rem;
        }
        .main-title {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(90deg, #ff7e5f, #feb47b, #86e3ce);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            font-size: 1.1rem;
            color: #a0aec0;
            font-weight: 300;
        }
        
        /* Glassmorphic Container */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 16px;
            padding: 2rem;
            border: 1px rgba(255, 255, 255, 0.08) solid;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            margin-bottom: 2rem;
        }
        
        /* Results Section Styling */
        .rec-box {
            background: rgba(134, 227, 206, 0.05);
            border-left: 5px solid #86e3ce;
            border-radius: 8px;
            padding: 1.5rem;
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        /* Data Metric Styling */
        .metric-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        .area-title {
            color: #feb47b;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        .badge {
            background-color: rgba(255, 255, 255, 0.1);
            color: #e2e8f0;
            padding: 0.2rem 0.6rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-right: 0.5rem;
            display: inline-block;
        }
        .badge-high {
            background-color: rgba(239, 68, 68, 0.2);
            color: #f87171;
        }
        .badge-medium {
            background-color: rgba(245, 158, 11, 0.2);
            color: #fbbf24;
        }
        .badge-low {
            background-color: rgba(16, 185, 129, 0.2);
            color: #34d399;
        }
    </style>
""", unsafe_allow_html=True)

# Layout: Header
st.markdown("""
    <div class="title-container">
        <h1 class="main-title">Business Location Advisor</h1>
        <p class="subtitle">Find the perfect commercial area for your business in Pakistan using AI market intelligence</p>
    </div>
""", unsafe_allow_html=True)

# Layout: Body Glass Card
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

user_idea = st.text_area(
    "Describe your business idea:",
    placeholder="Example: I have 800000 rupees and want to open a bakery in Lahore",
    height=100
)

submit_button = st.button("Find Best Location", type="primary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

if submit_button:
    if not user_idea.strip():
        st.warning("Please enter your business idea description.")
    else:
        try:
            # Stage 1: Extract Brief
            with st.spinner("Understanding your idea..."):
                brief = extract_brief(user_idea)
                
            city = brief.get("city")
            business_type = brief.get("business_type")
            
            if not city or not business_type:
                st.error(
                    "Could not extract the City or Business Type from your request. "
                    "Please specify both the city (e.g. Lahore, Karachi) and your business type (e.g. bakery, cafe) and try again."
                )
                # Show parsed details to let user know what was missing
                st.json(brief)
            else:
                # Stage 2: Research Areas
                with st.spinner("Researching areas..."):
                    areas = research_areas(brief)
                
                # Stage 3: Prepare Recommendation
                with st.spinner("Preparing recommendation..."):
                    recommendation = generate_recommendation(brief, areas)
                
                # Display success and recommendation
                st.success("Analysis Complete!")
                st.markdown("### 📋 Advisor Recommendation")
                st.markdown(f'<div class="rec-box">{recommendation}</div>', unsafe_allow_html=True)
                
                # Display data breakdown in expander
                with st.expander("See the data"):
                    st.markdown("### Researched Commercial Areas")
                    for area in areas:
                        comp_val = area.get("competition_level", "low").lower()
                        traffic_val = area.get("foot_traffic", "low").lower()
                        
                        comp_class = f"badge-{comp_val}" if comp_val in ["low", "medium", "high"] else ""
                        traffic_class = f"badge-{traffic_val}" if traffic_val in ["low", "medium", "high"] else ""

                        st.markdown(f"""
                            <div class="metric-card">
                                <div class="area-title">📍 {area.get('area_name')}</div>
                                <div>
                                    <span class="badge {comp_class}">Competition: {comp_val.upper()}</span>
                                    <span class="badge {traffic_class}">Foot Traffic: {traffic_val.upper()}</span>
                                </div>
                                <p style="margin-top: 0.5rem; margin-bottom: 0.2rem;"><strong>Rent Expectation:</strong> {area.get('rent_notes')}</p>
                                <p style="color: #cbd5e0; font-size: 0.95rem;">{area.get('summary')}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
        except Exception as e:
            st.error(f"An error occurred while processing your request: {e}")
            st.info("Please verify your API keys and connection settings in the configuration.")
