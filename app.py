import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# -----------------------------------------------------------
# 📌 TITLE
# -----------------------------------------------------------
st.title("📊 Data Inspection & Cleaning Dashboard")
st.markdown("---")

# -----------------------------------------------------------
# 📌 LOAD DATA
# -----------------------------------------------------------
st.markdown("## 📥 Upload Dataset")
uploaded_file = st.file_uploader(
    "Choose your Excel file (supports .xlsx and .xls)",
    type=["xlsx", "xls"],
    help="Upload the household questionnaire Excel file to analyze the data."
)

if uploaded_file is not None:
    try:
        # --- Main sheet (default/first sheet) ---
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        uploaded_file.seek(0)  # Reset pointer for second read
        
        # --- Crop sheet ---
        try:
            crop_df = pd.read_excel(uploaded_file, sheet_name="crop", engine='openpyxl')
            st.success("✅ Crop sheet loaded successfully.")
        except ValueError:
            crop_df = None
            st.warning("⚠️ No sheet named 'crop' found. Crop-related sections will be skipped.")
        
        uploaded_file.seek(0)  # Reset again if needed later
        
        st.success(f"✅ Successfully loaded: **{uploaded_file.name}** ({uploaded_file.size:,} bytes)")
        
        st.markdown("### 🔍 First Look at Main DataFrame")
        st.dataframe(df.head(10))
        
        with st.expander("📊 DataFrame Info & Summary"):
            st.write("**Shape:**", df.shape)
            st.write("**Columns:**", list(df.columns))
            st.write("**Missing values per column:**")
            st.dataframe(df.isnull().sum().sort_values(ascending=False))
            
    except Exception as e:
        st.error(f"❌ Error reading the file: {e}")
        st.stop()
else:
    st.info("👆 Please upload an Excel file to get started.")
    st.stop()

# -----------------------------------------------------------
# 📐 Data Shape
# -----------------------------------------------------------
st.markdown("### 📐 Data Shape")
st.write(df.shape)
st.markdown("---")

# -----------------------------------------------------------
# 🧹 Find & Drop Empty Columns
# -----------------------------------------------------------
st.markdown("## 🧹 Columns with No Data")
empty_cols = df.columns[df.isna().all()].tolist()
st.write(f"**{len(empty_cols)} completely empty columns:** {empty_cols}")

df = df.dropna(axis=1, how='all')
st.write(f"**After dropping:** {len(df.columns)} columns remain")
st.markdown("---")

# -----------------------------------------------------------
# 🔎 Missing Values Overview
# -----------------------------------------------------------
st.markdown("## 🔎 Missing Values Overview")
st.dataframe(df.isnull().sum().sort_values(ascending=False))
st.markdown("---")

# -----------------------------------------------------------
# 🔄 Column Renaming (Part 1 – Main long columns)
# -----------------------------------------------------------
rename_dict = {
  # ENUMERATOR'S IDENTIFICATION
    # ----------------------------------------------------------------------
    "ENUMERATOR'S IDENTIFICATION/The fieldwork ID (number) of the enumerator": 'enum_fieldwork_id',
    "ENUMERATOR'S IDENTIFICATION/The work position of the enumerator at INES - Ruhengeri": 'enum_work_position',
    "ENUMERATOR'S IDENTIFICATION/Enumerator's phone number:": 'enum_phone_1',
    "ENUMERATOR'S IDENTIFICATION/Enumerator's phone number No. 2:": 'enum_phone_2',
    "ENUMERATOR'S IDENTIFICATION/Enumerator's personal e-mail address": 'enum_email_personal',
    "ENUMERATOR'S IDENTIFICATION/Enumerator's office/work e-mail address": 'enum_email_office',

    # ----------------------------------------------------------------------
    # GPS
    # ----------------------------------------------------------------------
    'Please take a GPS point of the location of the respondent / interview': 'gps_point',
    '_Please take a GPS point of the location of the respondent / interview_latitude': 'gps_latitude',
    '_Please take a GPS point of the location of the respondent / interview_longitude': 'gps_longitude',
    '_Please take a GPS point of the location of the respondent / interview_altitude': 'gps_altitude',
    '_Please take a GPS point of the location of the respondent / interview_precision': 'gps_precision',

    # ----------------------------------------------------------------------
    # RESPONDENT'S IDENTIFICATION
    # ----------------------------------------------------------------------
    "RESPONDENT'S IDENTIFICATION/Respondent No. (serial number in the interviews made)": 'resp_serial_no',
    "RESPONDENT'S IDENTIFICATION/Gender of the respondent": 'resp_gender',
    "RESPONDENT'S IDENTIFICATION/Respondent's education level:": 'resp_education',
    "RESPONDENT'S IDENTIFICATION/Interview No.:": 'resp_interview_no',

    # ---------|-------------------------------------------------------------
    # ECOSYSTEM IDENTITY
    # ----------------------------------------------------------------------
    'ECOSYSTEM IDENTITY/Please select the ecosystem type': 'eco_type',
    'ECOSYSTEM IDENTITY/Please indicate the name of the forest': 'eco_forest_name',
    'ECOSYSTEM IDENTITY/Please indicate the name of the wetland': 'eco_wetland_name',
    'ECOSYSTEM IDENTITY/Case Study No.': 'eco_case_study_no',
    'ECOSYSTEM IDENTITY/To which one among the types of forests in Rwanda does this forest belong?': 'eco_forest_type_rwanda',
    'ECOSYSTEM IDENTITY/Is it a State or district forest?': 'eco_forest_ownership',
    'ECOSYSTEM IDENTITY/What type of wetland is this?': 'eco_wetland_type',
    'ECOSYSTEM IDENTITY/Is the case study a protected area (ecosystem)? Indicate the legal/policy status:': 'eco_protected_area_status',

    # ----------------------------------------------------------------------
    # CONSENT
    # ----------------------------------------------------------------------
    'CONSENT/Before proceeding, please ask the respondent if he/she consents to be interviewed': 'consent_asked',
    'CONSENT/The respondent accepted, then continue!': 'consent_accepted',

    # ----------------------------------------------------------------------
    # ADDRESS
    # ----------------------------------------------------------------------
    'Address/Select the Province where the respondent is residing': 'addr_province',
    'Address/In which District are you living?': 'addr_district',
    'Address/In which Sector do you reside?': 'addr_sector',
    'Address/What is the name of the Cell you live in?': 'addr_cell',
    'Address/In which village do you reside?': 'addr_village',

    # ----------------------------------------------------------------------
    # AGE & EXPERIENCE
    # ----------------------------------------------------------------------
    "Respondent's age and experience in the area/Born in (year)": 'resp_birth_year',
    "Respondent's age and experience in the area/age:": 'resp_age',
    "Respondent's age and experience in the area/We want to calculate how many years you have been living in this area and seeing this forest. You are here since when (year)?": 'resp_start_year_forest',
    "Respondent's age and experience in the area/We want to calculate how many years you have been living in this area and seeing this wetland. You are here since when (year)?": 'resp_start_year_wetland',
    "Respondent's age and experience in the area/years_in_the_area_forest": 'resp_years_area_forest',
    "Respondent's age and experience in the area/years_in_the_area_wetland": 'resp_years_area_wetland',

    # ----------------------------------------------------------------------
    # ECOSYSTEM SERVICES BENEFITED (Overall Questions)
    # ----------------------------------------------------------------------
    'ECOSYSTEM SERVICES BENEFITED/Do you think this forest is important?': 'benefits_forest_important',
    'ECOSYSTEM SERVICES BENEFITED/Do you think this wetland is important?': 'benefits_wetland_important',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?': 'benefits_forest_list',

    # ----------------------------------------------------------------------
    # ECOSYSTEM SERVICES BENEFITED (Forest Specific)
    # ----------------------------------------------------------------------
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/wood provision': 'b_forest_wood_provision',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/timber': 'b_forest_timber',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/income generation': 'b_forest_income_gen',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/provide refuge/habitat to animal species': 'b_forest_habitat_animal',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/provide refuge/habitat to plant species': 'b_forest_habitat_plant',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/tourism': 'b_forest_tourism',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/beauty, aesthetics': 'b_forest_aesthetics',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/recreation': 'b_forest_recreation',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/air regulation': 'b_forest_air_reg',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/flood control': 'b_forest_flood_control',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/climate regulation': 'b_forest_climate_reg',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/food for livestock': 'b_forest_food_livestock',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/agricultural production': 'b_forest_agri_prod',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/fishery': 'b_forest_fishery',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/provide honey': 'b_forest_honey',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/we get mushroom': 'b_forest_mushroom',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/provide fruits': 'b_forest_fruits',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/snail': 'b_forest_snail',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/other food for humans': 'b_forest_food_other',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/charcoal provision': 'b_forest_charcoal',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/water regulation': 'b_forest_water_reg',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/soil erosion control': 'b_forest_soil_control',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/carbon sequestration': 'b_forest_carbon_seq',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/scientific research': 'b_forest_research',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/medicaments': 'b_forest_medicaments',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/hunting (!)': 'b_forest_hunting',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/cultural activities': 'b_forest_cultural',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this forest?/OTHER': 'b_forest_other',

    # ----------------------------------------------------------------------
    # ATMOSPHERIC REGULATION
    # ----------------------------------------------------------------------
    'ATMOSPHERIC REGULATION AWARENESS/Do you know something about how the forest regulates climate/water/air?': 'reg_aware_forest',
    'ATMOSPHERIC REGULATION AWARENESS/Please elaborate:': 'reg_aware_forest_elaborate',
    'ATMOSPHERIC REGULATION AWARENESS/Do you know something about how the wetland regulates the atmosphere?': 'reg_aware_wetland',

    # ----------------------------------------------------------------------
    # AESTHETICS / BEAUTY
    # ----------------------------------------------------------------------
    'AESTHETICS / BEAUTY/Is this forest beautiful in your perception?': 'aesthetics_forest_perception',
    'AESTHETICS / BEAUTY/Please elaborate how beautiful the forest is in your perception': 'aesthetics_forest_elaborate',
    'AESTHETICS / BEAUTY/Is this wetland beautiful in your perception?': 'aesthetics_wetland_perception',
    'Please rate how beautiful the forest is': 'aesthetics_forest_rating',

    # ----------------------------------------------------------------------
    # SENSE OF PLACE
    # ----------------------------------------------------------------------
    'SENSE OF PLACE & BELONGINGNESS/How do you feel to be residing in the surroundings of this forest?': 'sense_place_feel_forest',
    'SENSE OF PLACE & BELONGINGNESS/How do you feel to be residing in the surroundings of this wetland?': 'sense_place_feel_wetland',

    # ----------------------------------------------------------------------
    # CONSEQUENCES OF ABSENSE (Forest - Absent)
    # ----------------------------------------------------------------------
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this forest was significantly depleted or even absent?': 'abs_conseq_forest_absent',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this forest was significantly depleted or even absent?/I think my whole life could be affected proportionally': 'abs_conseq_forest_absent_life_affected',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this forest was significantly depleted or even absent?/My income could be reduced': 'abs_conseq_forest_absent_income_reduced',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this forest was significantly depleted or even absent?/I could shift and go to reside at another place': 'abs_conseq_forest_absent_shift_place',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this forest was significantly depleted or even absent?/No consequence this could have to my life': 'abs_conseq_forest_absent_no_conseq',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this forest was significantly depleted or even absent?/other consequence': 'abs_conseq_forest_absent_other',

    # ----------------------------------------------------------------------
    # CONSEQUENCES OF ABSENSE (Wetland - Absent)
    # ----------------------------------------------------------------------
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this wetland was significantly depleted or even absent?': 'abs_conseq_wetland_absent',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this wetland was significantly depleted or even absent?/I think my whole life could be affected proportionally': 'abs_conseq_wetland_absent_life_affected',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this wetland was significantly depleted or even absent?/My income could be reduced': 'abs_conseq_wetland_absent_income_reduced',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this wetland was significantly depleted or even absent?/I could shift and go to reside at another place': 'abs_conseq_wetland_absent_shift_place',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this wetland was significantly depleted or even absent?/No consequence this could have to my life': 'abs_conseq_wetland_absent_no_conseq',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this wetland was significantly depleted or even absent?/other consequence': 'abs_conseq_wetland_absent_other',

    # ----------------------------------------------------------------------
    # CONSEQUENCES OF REDUCTION (Forest - 50%)
    # ----------------------------------------------------------------------
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this forest was reduced by say 50% (half)?': 'abs_conseq_forest_half',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this forest was reduced by say 50% (half)?/I think my whole life could be affected proportionally': 'abs_conseq_forest_half_life_affected',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this forest was reduced by say 50% (half)?/My income could be reduced': 'abs_conseq_forest_half_income_reduced',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this forest was reduced by say 50% (half)?/I could shift and go to reside at another place': 'abs_conseq_forest_half_shift_place',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this forest was reduced by say 50% (half)?/No consequence this could have to my life': 'abs_conseq_forest_half_no_conseq',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this forest was reduced by say 50% (half)?/other consequence': 'abs_conseq_forest_half_other',

    # ----------------------------------------------------------------------
    # CONSEQUENCES OF REDUCTION (Wetland - 50%)
    # ----------------------------------------------------------------------
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this wetland was reduced by say 50% (half)?': 'abs_conseq_wetland_half',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this wetland was reduced by say 50% (half)?/I think my whole life could be affected proportionally': 'abs_conseq_wetland_half_life_affected',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this wetland was reduced by say 50% (half)?/My income could be reduced': 'abs_conseq_wetland_half_income_reduced',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this wetland was reduced by say 50% (half)?/I could shift and go to reside at another place': 'abs_conseq_wetland_half_shift_place',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this wetland was reduced by say 50% (half)?/No consequence this could have to my life': 'abs_conseq_wetland_half_no_conseq',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What if this wetland was reduced by say 50% (half)?/other consequence': 'abs_conseq_wetland_half_other',

    # ----------------------------------------------------------------------
    # HUMAN WELL-BEING (Forest)
    # ----------------------------------------------------------------------
    'HUMAN WELL-BEING/What can you say about the benefits of the forest on your own wellbeing?': 'wellbeing_forest_general',
    'HUMAN WELL-BEING/What can you say about the benefits of the forest on your own wellbeing?/It improves our physical health and wellbeing since when we need medicine urgently, we can get it quickly from the forest': 'wellbeing_forest_physical_health',
    'HUMAN WELL-BEING/What can you say about the benefits of the forest on your own wellbeing?/I feel well when I see birds and some animals in the forest': 'wellbeing_forest_mental_birds',
    'HUMAN WELL-BEING/What can you say about the benefits of the forest on your own wellbeing?/It improves my general wellbeing in many ways': 'wellbeing_forest_general_improve',
    'HUMAN WELL-BEING/What can you say about the benefits of the forest on your own wellbeing?/other': 'wellbeing_forest_other',

    # ----------------------------------------------------------------------
    # HUMAN WELL-BEING (Wetland)
    # ----------------------------------------------------------------------
    'HUMAN WELL-BEING/What can you say about the benefits of the wetland on your own wellbeing?': 'wellbeing_wetland_general',
    'HUMAN WELL-BEING/What can you say about the benefits of the wetland on your own wellbeing?/It improves our physical health and wellbeing since when we need medicine urgently, we can get it quickly from some plants found around the wetland': 'wellbeing_wetland_physical_health',
    'HUMAN WELL-BEING/What can you say about the benefits of the wetland on your own wellbeing?/I feel well when I visit the wetland, it refreshes mind by itself': 'wellbeing_wetland_mental_visit',
    'HUMAN WELL-BEING/What can you say about the benefits of the wetland on your own wellbeing?/It improves my general wellbeing in many ways': 'wellbeing_wetland_general_improve',
    'HUMAN WELL-BEING/What can you say about the benefits of the wetland on your own wellbeing?/other': 'wellbeing_wetland_other',

    # ----------------------------------------------------------------------
    # BENEFITS TO THE SOCIETY (Forest)
    # ----------------------------------------------------------------------
    'BENEFITS TO THE SOCIETY/How do your neighbours and the society as a whole in this area benefit from the forest?': 'society_benefit_forest_general',
    'BENEFITS TO THE SOCIETY/How do your neighbours and the society as a whole in this area benefit from the forest?/Since our traditional activities are conducted in the forest, the forest helps the entire society': 'society_benefit_forest_trad_activities',
    'BENEFITS TO THE SOCIETY/How do your neighbours and the society as a whole in this area benefit from the forest?/We are surrounded with clean air and we take it as a privilege as a society': 'society_benefit_forest_clean_air',
    'BENEFITS TO THE SOCIETY/How do your neighbours and the society as a whole in this area benefit from the forest?/It socially ties us (brings us together as a society)': 'society_benefit_forest_social_tie',
    'BENEFITS TO THE SOCIETY/How do your neighbours and the society as a whole in this area benefit from the forest?/It makes our society to get a lot of visitors and connections since people from far away come here for research, tourism, etc...': 'society_benefit_forest_visitors',
    'BENEFITS TO THE SOCIETY/How do your neighbours and the society as a whole in this area benefit from the forest?/other': 'society_benefit_forest_other',

    # ----------------------------------------------------------------------
    # WATER FOR DOMESTIC USES
    # ----------------------------------------------------------------------
    'WATER FOR DOMESTIC USES/Where do you get water for domestic uses (washing dishes, bath, cooking, etc.)?': 'water_domestic_source_list',
    'WATER FOR DOMESTIC USES/Where do you get water for domestic uses (washing dishes, bath, cooking, etc.)?/wetland water': 'water_domestic_source_wetland',
    'WATER FOR DOMESTIC USES/Where do you get water for domestic uses (washing dishes, bath, cooking, etc.)?/springs water': 'water_domestic_source_springs',
    'WATER FOR DOMESTIC USES/Where do you get water for domestic uses (washing dishes, bath, cooking, etc.)?/water well / borehole': 'water_domestic_source_well',
    'WATER FOR DOMESTIC USES/Where do you get water for domestic uses (washing dishes, bath, cooking, etc.)?/piped water': 'water_domestic_source_piped',
    'WATER FOR DOMESTIC USES/Where do you get water for domestic uses (washing dishes, bath, cooking, etc.)?/other': 'water_domestic_source_other',

    # ----------------------------------------------------------------------
    # MATS
    # ----------------------------------------------------------------------
    'MATS/Does your household personally make mats?': 'mats_hh_make',
    'MATS/But are you aware of (or do you benefit from) the practice of others who make mats?': 'mats_aware_others',
    'MATS/frequency_mats_year_equivalency': 'mats_frequency_year',

    # ----------------------------------------------------------------------
    # VALUE: WOOD
    # ----------------------------------------------------------------------
    'VALUE: WOOD/Does your household personally get wood from the forest?': 'v_wood_hh_get',
    'VALUE: WOOD/But are you aware of (or do you benefit from) the practice of others getting wood from the forest?': 'v_wood_aware_others',
    'VALUE: WOOD/frequency_wood_year_equivalency': 'v_wood_frequency_year',

    # ----------------------------------------------------------------------
    # VALUE: TIMBER
    # ----------------------------------------------------------------------
    'VALUE: TIMBER/Does your household personally get timber from the forest?': 'v_timber_hh_get',
    'VALUE: TIMBER/But are you aware of (or do you benefit from) the practice of others getting timber from the forest?': 'v_timber_aware_others',
    'VALUE: TIMBER/frequency_timber_year_equivalency': 'v_timber_frequency_year',

    # ----------------------------------------------------------------------
    # VALUE: CHARCOAL
    # ----------------------------------------------------------------------
    'VALUE: CHARCOAL/Does your household personally make charcoal from the forest?': 'v_charcoal_hh_make',
    'VALUE: CHARCOAL/But are you aware of (or do you benefit from) the practice of charcoal making by others - using trees from the forest?': 'v_charcoal_aware_others',
    'VALUE: CHARCOAL/frequency_charcoal_year_equivalency': 'v_charcoal_frequency_year',

    # ----------------------------------------------------------------------
    # VALUE: HONEY
    # ----------------------------------------------------------------------
    'VALUE: HONEY/Does your household personally make honey from the forest?': 'v_honey_hh_make',
    'VALUE: HONEY/But are you aware of (or do you benefit from) the practice of honey making by others - from the forest?': 'v_honey_aware_others',
    'VALUE: HONEY/frequency_honey_year_equivalency': 'v_honey_frequency_year',

    # ----------------------------------------------------------------------
    # VALUE: MUSHROOMS
    # ----------------------------------------------------------------------
    'VALUE: MUSHROOMS/Does your household personally get mushrooms from the forest?': 'v_mushroom_hh_get',
    'VALUE: MUSHROOMS/But are you aware of (or do you benefit from) the practice of others getting mushrooms from the forest?': 'v_mushroom_aware_others',
    'VALUE: MUSHROOMS/frequency_mushroom_year_equivalency': 'v_mushroom_frequency_year',

    # ----------------------------------------------------------------------
    # VALUE: FISH
    # ----------------------------------------------------------------------
    'VALUE: FISH/Does your household personally carry out fishery in the wetland?': 'v_fish_hh_do',
    'VALUE: FISH/But are you aware of (or do you benefit from) the practice of others who practice fishing in the wetland?': 'v_fish_aware_others',
    'VALUE: FISH/practice_fish_yes_count': 'v_fish_practice_yes_count',
    'VALUE: FISH/practice_fish_no_count': 'v_fish_practice_no_count',
    'VALUE: FISH/practice_fish_no_aware_yes_count': 'v_fish_practice_no_aware_yes_count',
    'VALUE: FISH/practice_fish_no_aware_no_count': 'v_fish_practice_no_aware_no_count',

    # ----------------------------------------------------------------------
    # WATER FOR CONSTRUCTION
    # ----------------------------------------------------------------------
    'WATER FOR CONSTRUCTION/In this area, where do you get water for construction of houses?': 'water_const_source_list',
    'WATER FOR CONSTRUCTION/In this area, where do you get water for construction of houses?/wetland water': 'water_const_source_wetland',
    'WATER FOR CONSTRUCTION/In this area, where do you get water for construction of houses?/springs water': 'water_const_source_springs',
    'WATER FOR CONSTRUCTION/In this area, where do you get water for construction of houses?/water well / borehole': 'water_const_source_well',
    'WATER FOR CONSTRUCTION/In this area, where do you get water for construction of houses?/piped water': 'water_const_source_piped',
    'WATER FOR CONSTRUCTION/In this area, where do you get water for construction of houses?/other': 'water_const_source_other',

    # ----------------------------------------------------------------------
    # LIVESTOCK KEEPING
    # ----------------------------------------------------------------------
    'LIVESTOCK KEEPING/Does your household practice livestock keeping?': 'livestock_hh_practice',
    'LIVESTOCK KEEPING/frequency_livestock_water_year_equivalency': 'livestock_water_frequency_year',

    # ----------------------------------------------------------------------
    # FARMING PRACTICE
    # ----------------------------------------------------------------------
    'FARMING PRACTICE/Does your household conduct crop cultivation _*around the wetland or somewhere else but using resources (water, etc…) from the wetland_?*': 'farming_hh_wetland_use',
    'FARMING PRACTICE/But are you aware of the practice of others who carry out farming near / using the wetland?': 'farming_aware_others_wetland',
    'FARMING PRACTICE/practice_farming_yes_count': 'farming_practice_yes_count',
    'FARMING PRACTICE/practice_farming_no_count': 'farming_practice_no_count',
    'FARMING PRACTICE/practice_farming_no_aware_yes_count': 'farming_practice_no_aware_yes_count',
    'FARMING PRACTICE/practice_farming_no_aware_no_count': 'farming_practice_no_aware_no_count',
    'FARMING PRACTICE/practice_farming_yes_sum': 'farming_practice_yes_sum',
    'FARMING PRACTICE/practice_farming_no_sum': 'farming_practice_no_sum',
    'FARMING PRACTICE/practice_farming_no_aware_yes_sum': 'farming_practice_no_aware_yes_sum',
    'FARMING PRACTICE/practice_farming_no_aware_no_sum': 'farming_practice_no_aware_no_sum',

    # ----------------------------------------------------------------------
    # VALUE: WATER FOR IRRIGATION
    # ----------------------------------------------------------------------
    'VALUE: WATER FOR IRRIGATION/Does your household personally carry out irrigation using water from the wetland?': 'v_irrigation_hh_do',
    'VALUE: WATER FOR IRRIGATION/But are you aware of (or do you benefit from) the practice of others who irrigate farms using water from the wetland?': 'v_irrigation_aware_others',

    # ----------------------------------------------------------------------
    # NON-ECONOMIC / INTANGIBLE BENEFITS
    # ----------------------------------------------------------------------
    'NON-ECONOMIC / INTANGIBLE BENEFITS/Apart from the economic and the tangible benefits you mentioned / we discussed, are there other non-economic / intangible benefits you get from the forest?': 'b_intangible_forest',
    'NON-ECONOMIC / INTANGIBLE BENEFITS/Apart from the economic and the tangible benefits you mentioned / we discussed, are there other non-economic / intangible benefits you get from the wetland?': 'b_intangible_wetland',

    # ----------------------------------------------------------------------
    # WILLINGNESS TO PAY
    # ----------------------------------------------------------------------
    'WILLINGNESS TO PAY/Are you willing to pay for the costs of managing the forest?': 'wtp_forest_management',
    'WILLINGNESS TO PAY/If you are asked to pay for the costs of managing the wetland, will you be willing to pay?': 'wtp_wetland_management',

    # ----------------------------------------------------------------------
    # TRADEOFFS
    # ----------------------------------------------------------------------
    'TRADEOFFS/Generally, what tradeoffs to the environment you know which are caused by the forest ecosystem services access?': 'tradeoffs_forest_access',
    'TRADEOFFS/Does the practice of crops cultivation have a negative effect on the forest?': 'tradeoffs_crop_neg_effect_forest',
    'TRADEOFFS/Does any human practice on ${wetland_name} in this area affect human health?': 'tradeoffs_human_practice_wetland_health',

    # ----------------------------------------------------------------------
    # HARM BY ANIMALS
    # ----------------------------------------------------------------------
    'HARM BY ANIMALS/Are there any incidences of wild animals harming humans in the forest?': 'harm_animal_forest_to_human',
    'HARM BY ANIMALS/Are there any incidences of wild animals harming livestock in the forest?': 'harm_animal_forest_to_livestock',

    # ----------------------------------------------------------------------
    # FINAL COMMENTS
    # ----------------------------------------------------------------------
    'FINAL COMMENTS/Do you have any other comments or remarks?': 'final_comments_resp',
    'FINAL COMMENTS/Dear Interviewer / enumerator, do you have any important observation remarks?': 'final_comments_enum'
}

df.rename(columns=rename_dict, inplace=True)
st.markdown("## 🔄 Column Renaming Applied (Part 1)")
st.write("Sample of renamed columns:", df.columns.tolist()[:20])
st.markdown("---")

# -----------------------------------------------------------
# 🔄 Column Renaming (Part 2 – Remaining columns)
# -----------------------------------------------------------
column_rename_map_part2 = {
    # --- Livestock Keeping ---
    'LIVESTOCK KEEPING/Which animals do you keep (domesticate)?/chicken / poultry': 'livestock_kept_chicken_poultry',
    'LIVESTOCK KEEPING/Which animals do you keep (domesticate)?/other': 'livestock_kept_other',
    'LIVESTOCK KEEPING/Which animals do you keep (domesticate)?/pig': 'livestock_kept_pig',
    'LIVESTOCK KEEPING/Which animals do you keep (domesticate)?/cat': 'livestock_kept_cat',
    'LIVESTOCK KEEPING/Which animals do you keep (domesticate)?/duck': 'livestock_kept_duck',
    'LIVESTOCK KEEPING/Which animals do you keep (domesticate)?/Guineafowl': 'livestock_kept_guineafowl',
    'LIVESTOCK KEEPING/Which animals do you keep (domesticate)?/dove/pigeon': 'livestock_kept_dove_pigeon',
    'LIVESTOCK KEEPING/Which animals do you keep (domesticate)?/turkey': 'livestock_kept_turkey',
    'LIVESTOCK KEEPING/What is the grazing place for your livestock?': 'livestock_grazing_place',
    'LIVESTOCK KEEPING/specify:': 'livestock_grazing_place_specify',
    'LIVESTOCK KEEPING/What is the grazing place for your livestock?.1': 'livestock_grazing_place_wetland_check', # Assuming .1 is a wetland-specific/related check
    'LIVESTOCK KEEPING/specify:.1': 'livestock_grazing_wetland_specify',
    'LIVESTOCK KEEPING/Where do you get water for your livestock?': 'livestock_water_source',
    'LIVESTOCK KEEPING/specify:.2': 'livestock_water_source_specify',
    'LIVESTOCK KEEPING/You procure fodder for your livestock (and store it or feed the livestock directly):': 'livestock_procure_fodder_store_feed',
    'LIVESTOCK KEEPING/You procure fodder for your livestock (and store it or feed the livestock directly):.1': 'livestock_procure_fodder_direct_store', # Assuming .1 is a specific question about storage
    'LIVESTOCK KEEPING/You provide or store water for your livestock:': 'livestock_water_provide_store',
    'livestock_water_frequency_year': 'livestock_water_freq_year_calc', # Already short, but keeping it in the map for completeness
    'LIVESTOCK KEEPING/Water for livestock is stored or measured in:': 'livestock_water_unit',
    'LIVESTOCK KEEPING/Your livestock consume how many ${livestock_water_unit}s - ${livestock_water_frequency}?': 'livestock_water_quantity',
    'LIVESTOCK KEEPING/How many litres are contained in one ${livestock_water_unit}?': 'livestock_water_unit_to_L',
    'LIVESTOCK KEEPING/If obtained elsewhere (not from the ${wetland_name} wetland), one jerrycan (bidon - 20 liters) of water costs RWF:': 'livestock_water_alt_cost_RWF',
    'LIVESTOCK KEEPING/How much (RWF) cost do you incur in order to get water for your livestock from the wetland?': 'livestock_water_cost_incurred_RWF',
    'LIVESTOCK KEEPING/Value of water for livestock in Rwandan Francs per year:': 'livestock_water_value_year_RWF_note',
    'LIVESTOCK KEEPING/Value of water in Rwandan Francs per year: ${value_livestock_water} RWF': 'livestock_water_value_year_RWF_calc',

    # --- Farming Practice (General) ---
    'FARMING PRACTICE/Does your household conduct crop cultivation _*around the wetland or somewhere else but using resources (water, etc\x85) from the wetland_?*': 'farm_cultivate_around_or_use_wetland_resources',
    'farming_aware_others_wetland': 'farm_aware_others_wetland', # Already short
    'FARMING PRACTICE/Ok, so, you know something about farming thanks to the wetland!': 'farm_aware_wetland',
    'FARMING PRACTICE/So, let us talk about each crop you grow around the wetland or using the wetland water, one crop after another...': 'farm_start_crop_detail_note',
    'farming_practice_yes_count': 'farm_practice_yes_count', # Already short
    'farming_practice_no_count': 'farm_practice_no_count', # Already short
    'farming_practice_no_aware_yes_count': 'farm_practice_no_aware_yes_count', # Already short
    'farming_practice_no_aware_no_count': 'farm_practice_no_aware_no_count', # Already short
    'farming_practice_yes_sum': 'farm_practice_yes_sum', # Already short
    'farming_practice_no_sum': 'farm_practice_no_sum', # Already short
    'farming_practice_no_aware_yes_sum': 'farm_practice_no_aware_yes_sum', # Already short
    'farming_practice_no_aware_no_sum': 'farm_practice_no_aware_no_sum', # Already short

    # --- Crops Cultivated (List & Checks) ---
    'CROPS CULTIVATED/Let us first know which crops you grow.': 'crop_list_intro_note',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?': 'crop_cultivated_list', # Long but generic
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/maize': 'crop_maize_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/beans': 'crop_beans_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/chick peas': 'crop_chick_peas_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/rice/paddy': 'crop_rice_paddy_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/wheat': 'crop_wheat_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/sugarcane': 'crop_sugarcane_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/sorghum': 'crop_sorghum_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/sesame': 'crop_sesame_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/tomatoes': 'crop_tomatoes_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/onions': 'crop_onions_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/garlic': 'crop_garlic_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/chilli pepper': 'crop_chilli_pepper_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/bell/capsicum/sweet pepper': 'crop_bell_sweet_pepper_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/amaranth': 'crop_amaranth_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/spinach': 'crop_spinach_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/cassava': 'crop_cassava_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/pumpkins': 'crop_pumpkins_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/tea': 'crop_tea_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/flowers': 'crop_flowers_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/bananas': 'crop_bananas_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/peanut': 'crop_peanut_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/cashew': 'crop_cashew_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/sunflower': 'crop_sunflower_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/palm': 'crop_palm_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/irish potatoes': 'crop_irish_potatoes_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/sweet potatoes': 'crop_sweet_potatoes_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/tamarillo/ tree tomato/ "blood fruit" - (*Solanum betaceum*)': 'crop_tamarillo_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Coconut': 'crop_coconut_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Olive': 'crop_olive_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Mangoes': 'crop_mangoes_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Avocado': 'crop_avocado_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Grape': 'crop_grape_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Oranges': 'crop_oranges_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/lemon': 'crop_lemon_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Mandarin': 'crop_mandarin_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Pear': 'crop_pear_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/strawberry': 'crop_strawberry_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/goldenberry (Peruvian groundcherry) - _Physalis peruviana_': 'crop_goldenberry_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/pineapple': 'crop_pineapple_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Apple': 'crop_apple_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/passion': 'crop_passion_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/watermelon': 'crop_watermelon_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/papaya': 'crop_papaya_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Carrots': 'crop_carrots_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Ginger': 'crop_ginger_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/beetroot': 'crop_beetroot_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Cucumber': 'crop_cucumber_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Okra': 'crop_okra_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Celery': 'crop_celery_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Eggplant': 'crop_eggplant_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/African eggplant': 'crop_african_eggplant_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/green bean': 'crop_green_bean_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Cabbage': 'crop_cabbage_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Soybean': 'crop_soybean_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Papyrus': 'crop_papyrus_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/red stinkwood / African cherry': 'crop_african_cherry_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Bamboo': 'crop_bamboo_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/taro': 'crop_taro_check',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/yam': 'crop_yam_check',

    # --- Crops Cultivated (Short Names/Calculations) ---
    'CROPS CULTIVATED/maize_grown': 'crop_maize_grown', # Already short
    'CROPS CULTIVATED/beans_grown': 'crop_beans_grown', # Already short
    'CROPS CULTIVATED/chick_peas_grown': 'crop_chick_peas_grown', # Already short
    'CROPS CULTIVATED/rice_grown': 'crop_rice_grown', # Already short
    'CROPS CULTIVATED/wheat_grown': 'crop_wheat_grown', # Already short
    'CROPS CULTIVATED/sugarcane_grown': 'crop_sugarcane_grown', # Already short
    'CROPS CULTIVATED/sorghum_grown': 'crop_sorghum_grown', # Already short
    'CROPS CULTIVATED/sesame_grown': 'crop_sesame_grown', # Already short
    'CROPS CULTIVATED/tomatoes_grown': 'crop_tomatoes_grown', # Already short
    'CROPS CULTIVATED/onions_grown': 'crop_onions_grown', # Already short
    'CROPS CULTIVATED/garlic_grown': 'crop_garlic_grown', # Already short
    'CROPS CULTIVATED/pepper_grown': 'crop_pepper_grown', # Already short
    'CROPS CULTIVATED/poivrons_grown': 'crop_poivrons_grown', # Already short
    'CROPS CULTIVATED/amaranth_grown': 'crop_amaranth_grown', # Already short
    'CROPS CULTIVATED/spinach_grown': 'crop_spinach_grown', # Already short
    'CROPS CULTIVATED/cassava_grown': 'crop_cassava_grown', # Already short
    'CROPS CULTIVATED/pumpkins_grown': 'crop_pumpkins_grown', # Already short
    'CROPS CULTIVATED/tea_grown': 'crop_tea_grown', # Already short
    'CROPS CULTIVATED/flowers_grown': 'crop_flowers_grown', # Already short
    'CROPS CULTIVATED/bananas_grown': 'crop_bananas_grown', # Already short
    'CROPS CULTIVATED/peanut_grown': 'crop_peanut_grown', # Already short
    'CROPS CULTIVATED/cashew_grown': 'crop_cashew_grown', # Already short
    'CROPS CULTIVATED/sunflower_grown': 'crop_sunflower_grown', # Already short
    'CROPS CULTIVATED/palm_grown': 'crop_palm_grown', # Already short
    'CROPS CULTIVATED/potatoes_irish_grown': 'crop_potatoes_irish_grown', # Already short
    'CROPS CULTIVATED/potatoes_sweet_grown': 'crop_potatoes_sweet_grown', # Already short
    'CROPS CULTIVATED/prune_grown': 'crop_prune_grown', # Already short
    'CROPS CULTIVATED/coconut_grown': 'crop_coconut_grown', # Already short
    'CROPS CULTIVATED/olive_grown': 'crop_olive_grown', # Already short
    'CROPS CULTIVATED/mangoes_grown': 'crop_mangoes_grown', # Already short
    'CROPS CULTIVATED/avocado_grown': 'crop_avocado_grown', # Already short
    'CROPS CULTIVATED/grape_grown': 'crop_grape_grown', # Already short
    'CROPS CULTIVATED/oranges_grown': 'crop_oranges_grown', # Already short
    'CROPS CULTIVATED/lemon_grown': 'crop_lemon_grown', # Already short
    'CROPS CULTIVATED/mandarin_grown': 'crop_mandarin_grown', # Already short
    'CROPS CULTIVATED/pear_grown': 'crop_pear_grown', # Already short
    'CROPS CULTIVATED/strawberry_grown': 'crop_strawberry_grown', # Already short
    'CROPS CULTIVATED/goldenberry_grown': 'crop_goldenberry_grown', # Already short
    'CROPS CULTIVATED/pineapple_grown': 'crop_pineapple_grown', # Already short
    'CROPS CULTIVATED/apple_grown': 'crop_apple_grown', # Already short
    'CROPS CULTIVATED/passion_grown': 'crop_passion_grown', # Already short
    'CROPS CULTIVATED/watermelon_grown': 'crop_watermelon_grown', # Already short
    'CROPS CULTIVATED/papaya_grown': 'crop_papaya_grown', # Already short
    'CROPS CULTIVATED/carrots_grown': 'crop_carrots_grown', # Already short
    'CROPS CULTIVATED/ginger_grown': 'crop_ginger_grown', # Already short
    'CROPS CULTIVATED/beetroot_grown': 'crop_beetroot_grown', # Already short
    'CROPS CULTIVATED/cucumber_grown': 'crop_cucumber_grown', # Already short
    'CROPS CULTIVATED/okra_grown': 'crop_okra_grown', # Already short
    'CROPS CULTIVATED/celery_grown': 'crop_celery_grown', # Already short
    'CROPS CULTIVATED/eggplant_grown': 'crop_eggplant_grown', # Already short
    'CROPS CULTIVATED/intoryi_grown': 'crop_intoryi_grown', # Assuming intoryi means African Eggplant/similar
    'CROPS CULTIVATED/green_bean_grown': 'crop_green_bean_grown', # Already short
    'CROPS CULTIVATED/cabbage_grown': 'crop_cabbage_grown', # Already short
    'CROPS CULTIVATED/soybean_grown': 'crop_soybean_grown', # Already short
    'CROPS CULTIVATED/papyrus_grown': 'crop_papyrus_grown', # Already short
    'CROPS CULTIVATED/Prunus_africana_grown': 'crop_african_cherry_grown', # Shortening the Latin name
    'CROPS CULTIVATED/bamboo_grown': 'crop_bamboo_grown', # Already short
    'CROPS CULTIVATED/taro_grown': 'crop_taro_grown', # Already short
    'CROPS CULTIVATED/yam_grown': 'crop_yam_grown', # Already short

    # --- Count: Crops Cultivated ---
    'COUNT: CROPS CULTIVATED/crops_wetland_grown_list': 'crop_wetland_grown_list', # Already short
    'COUNT: CROPS CULTIVATED/So, you grow the following crops: ${crops_wetland_grown_list}': 'crop_grown_list_note',
    'COUNT: CROPS CULTIVATED/Are you a member of an agricultural association?': 'farm_member_agri_association_check',
    'COUNT: CROPS CULTIVATED/In which farming association are you?': 'farm_association_type',
    'COUNT: CROPS CULTIVATED/In which farming association are you?.1': 'farm_association_name_check',
    'COUNT: CROPS CULTIVATED/Specify the name of the association:': 'farm_association_name_specify',
    'COUNT: CROPS CULTIVATED/crops_wetland_grown_sum': 'crop_wetland_grown_sum', # Already short
    'COUNT: CROPS CULTIVATED/We can now start detailing each of the ${crops_wetland_grown_sum} crops that you grow': 'crop_start_detailing_note',

    # --- Values Summary of Crops You Cultivate ---
    'VALUES SUMMARY OF CROPS YOU CULTIVATE/The total number of crops which you cultivate is: ${crops_wetland_grown_sum}': 'crop_total_grown_sum_note',
    'VALUES SUMMARY OF CROPS YOU CULTIVATE/value_farming_rwf_year_total': 'crop_value_total_year_RWF',
    'VALUES SUMMARY OF CROPS YOU CULTIVATE/So, the total amount which you benefit every year from all the ${crops_wetland_grown_sum} crops is ${value_farming_rwf_year_total} RWF.': 'crop_value_total_year_RWF_note',
    'VALUES SUMMARY OF CROPS YOU CULTIVATE/income_stated_calculated_deviation': 'crop_income_stated_calc_deviation_RWF',
    'VALUES SUMMARY OF CROPS YOU CULTIVATE/deviation (calculated [farming] vs stated): ${income_stated_calculated_deviation} RWF': 'crop_income_deviation_note',
    'VALUES SUMMARY OF CROPS YOU CULTIVATE/value_farming_rwf_year_minimum': 'crop_value_min_year_RWF',
    'VALUES SUMMARY OF CROPS YOU CULTIVATE/So, the minimum amount which you benefit every year among all crops is: ${value_farming_rwf_year_minimum} RWF': 'crop_value_min_year_RWF_note',
    'VALUES SUMMARY OF CROPS YOU CULTIVATE/value_farming_rwf_year_maximum': 'crop_value_max_year_RWF',
    'VALUES SUMMARY OF CROPS YOU CULTIVATE/The maximum amount which you benefit every year from crop cultivation is: ${value_farming_rwf_ha_year_maximum} RWF': 'crop_value_max_year_RWF_note',
    'VALUES SUMMARY OF CROPS YOU CULTIVATE/value_farming_rwf_ha_year_average': 'crop_value_avg_year_RWF',
    'VALUES SUMMARY OF CROPS YOU CULTIVATE/The average amount which you benefit every year from crop cultivation is: ${value_farming_rwf_year_average} RWF': 'crop_value_avg_year_RWF_note',
    'VALUES SUMMARY OF CROPS YOU CULTIVATE/value_farming_rwf_ha_year_minimum': 'crop_value_min_ha_year_RWF',
    'VALUES SUMMARY OF CROPS YOU CULTIVATE/The minimum amount which you benefit among all the ${crops_wetland_grown_sum} you grow per hectare per year is: ${value_farming_rwf_ha_year_minimum} RWF': 'crop_value_min_ha_year_RWF_note',
    'VALUES SUMMARY OF CROPS YOU CULTIVATE/value_farming_rwf_ha_year_maximum': 'crop_value_max_ha_year_RWF',
    'VALUES SUMMARY OF CROPS YOU CULTIVATE/The maximum amount which you benefit every year from crop cultivation is: ${value_farming_rwf_ha_year_maximum} RWF per hectare per year': 'crop_value_max_ha_year_RWF_note',
    'VALUES SUMMARY OF CROPS YOU CULTIVATE/value_farming_rwf_ha_year_total': 'crop_value_total_ha_year_RWF',
    'VALUES SUMMARY OF CROPS YOU CULTIVATE/value_farming_rwf_ha_year_average': 'crop_value_avg_ha_year_RWF',
    'VALUES SUMMARY OF CROPS YOU CULTIVATE/The average amount which you benefit every year per hectare from crop cultivation is: ${value_farming_rwf_ha_year_average} RWF': 'crop_value_avg_ha_year_RWF_note',

    # --- Sorghum Local Beer / Wine ---
    'SORGHUM LOCAL BEER / WINE/Does your household (any member) make local beer from sorghum? We want just to estimate the income / benefit and nothing else. Do you make local beer?': 'beer_make_from_sorghum_check',
    'SORGHUM LOCAL BEER / WINE/Which crop do you use for making beer?': 'beer_crop_used_list',
    'SORGHUM LOCAL BEER / WINE/You make beer every:': 'beer_make_frequency',
    'SORGHUM LOCAL BEER / WINE/frequency_beer_year_equivalency': 'beer_make_freq_year_equiv',
    'SORGHUM LOCAL BEER / WINE/How much money (RWF) do you get in average from beer making per ${frequency_beer}?': 'beer_income_per_freq_RWF',
    'SORGHUM LOCAL BEER / WINE/How much (RWF) expenses do you incur for making beer evey ${frequency_beer}?': 'beer_expense_per_freq_RWF',
    'SORGHUM LOCAL BEER / WINE/beer_income_year': 'beer_income_year_calc',
    'SORGHUM LOCAL BEER / WINE/So, per year, you get: ${beer_income_year} RWF': 'beer_income_year_RWF_note',

    # --- Water for Local Beer / Wine ---
    'WATER FOR LOCAL BEER / WINE/Where do you get water for making beer?': 'beer_water_source',
    'WATER FOR LOCAL BEER / WINE/specify:': 'beer_water_source_specify',
    'WATER FOR LOCAL BEER / WINE/Do you pay money or you just fetch water from the wetland?': 'beer_water_pay_or_fetch',
    'WATER FOR LOCAL BEER / WINE/How many jerrycans of water do you use for making beer per ${frequency_beer}?': 'beer_water_quantity_jerrycans',
    'WATER FOR LOCAL BEER / WINE/Please write zero (0) as an answer to the question below:': 'beer_water_cost_zero_note',
    'WATER FOR LOCAL BEER / WINE/How much money (RWF) do you pay for getting (or for someone to fetch for you) the ${beer_water_quantity} jerrycans of water?': 'beer_water_paid_RWF',
    'WATER FOR LOCAL BEER / WINE/(Opportunity cost:) But, how much could it cost you to get ONE JERRYCAN of water if were not from the wetland?': 'beer_water_opp_cost_jerrycan_RWF',
    'WATER FOR LOCAL BEER / WINE/beer_water_value_year': 'beer_water_value_year_calc',
    'WATER FOR LOCAL BEER / WINE/Value: benefit of water for beer making from the wetland per year: ${beer_water_value_year} RWF': 'beer_water_value_year_RWF',

    # --- Value: Water for Irrigation ---
    'v_irrigation_hh_do': 'v_irrigation_hh_do', # Already short
    'v_irrigation_aware_others': 'v_irrigation_aware_others', # Already short
    'VALUE: WATER FOR IRRIGATION/Ok, so, you know something about water for irrigation (from the wetland)!': 'v_irrigation_aware_wetland',
    'VALUE: WATER FOR IRRIGATION/Water for irrigation is fetched from the wetland (per concerned household):': 'v_irrigation_water_source_frequency',
    'VALUE: WATER FOR IRRIGATION/You measure water from the wetland in:': 'v_irrigation_water_unit',
    'VALUE: WATER FOR IRRIGATION/How many litres are contained in one ${unit_water_irrigation}?': 'v_irrigation_water_unit_to_L',
    'VALUE: WATER FOR IRRIGATION/How many ${unit_water_irrigation}s of water do you fetch from the wetland ${frequency_water_irrigation}?': 'v_irrigation_water_quantity',
    'VALUE: WATER FOR IRRIGATION/You do irrigate ${frequency_water_irrigation}. So, the number of times you irrigate per year is:': 'v_irrigation_freq_year_equiv',
    'VALUE: WATER FOR IRRIGATION/If obtained elsewhere (not from the ${wetland_name} wetland), one jerrycan (bidon - 20 liters) of water costs RWF:': 'v_irrigation_alt_cost_jerrycan_RWF',
    'VALUE: WATER FOR IRRIGATION/How much (RWF) cost do you incur in order to get water for irrigation from the wetland?': 'v_irrigation_cost_incurred_RWF',
    'VALUE: WATER FOR IRRIGATION/Value of water in Rwandan Francs per year:': 'v_irrigation_value_year_RWF_calc_note',
    'VALUE: WATER FOR IRRIGATION/Value of water in Rwandan Francs per year: ${value_water_irrigation} RWF': 'v_irrigation_value_year_RWF',

    # --- Non-Economic / Intangible Benefits ---
    'b_intangible_forest': 'b_intangible_forest_list',
    'NON-ECONOMIC / INTANGIBLE BENEFITS/specify:': 'b_intangible_forest_specify',
    'b_intangible_wetland': 'b_intangible_wetland_list',
    'NON-ECONOMIC / INTANGIBLE BENEFITS/specify:.1': 'b_intangible_wetland_specify',

    # --- Willingness to Pay (WTP) ---
    'wtp_forest_management': 'wtp_forest_management_check',
    'wtp_wetland_management': 'wtp_wetland_management_check',
    'WILLINGNESS TO PAY/What is the maximum amount (RWF) you are willing to pay for the costs of managing the forest?': 'wtp_forest_amount_RWF',
    'WILLINGNESS TO PAY/What is the maximum amount (RWF) you are willing to pay for the costs of managing the wetland ?': 'wtp_wetland_amount_RWF',

    # --- Biodiversity: Reptiles ---
    'BIODIVERSITY: REPTILES/Reptiles found in the wetland:': 'biodiv_reptiles_wetland_list',
    'BIODIVERSITY: REPTILES/Reptiles found in the wetland:/lizards': 'biodiv_reptile_lizards_check',
    'BIODIVERSITY: REPTILES/Reptiles found in the wetland:/lizard - gecko': 'biodiv_reptile_gecko_check',
    'BIODIVERSITY: REPTILES/Reptiles found in the wetland:/snakes': 'biodiv_reptile_snakes_check',
    'BIODIVERSITY: REPTILES/Reptiles found in the wetland:/crocodile': 'biodiv_reptile_crocodile_check',
    'BIODIVERSITY: REPTILES/Reptiles found in the wetland:/turtles': 'biodiv_reptile_turtles_check',
    'BIODIVERSITY: REPTILES/Reptiles found in the wetland:/other': 'biodiv_reptile_other_check',
    'BIODIVERSITY: REPTILES/specify:': 'biodiv_reptile_other_specify',
    'BIODIVERSITY: REPTILES/Which types of snake are found in the wetland?': 'biodiv_snake_types_list',
    'BIODIVERSITY: REPTILES/Which types of snake are found in the wetland?/double beating snake': 'biodiv_snake_double_beating_check',
    'BIODIVERSITY: REPTILES/Which types of snake are found in the wetland?/grass snake': 'biodiv_snake_grass_check',
    'BIODIVERSITY: REPTILES/Which types of snake are found in the wetland?/green non-venomous snake': 'biodiv_snake_green_non_venomous_check',
    'BIODIVERSITY: REPTILES/Which types of snake are found in the wetland?/other': 'biodiv_snake_other_check',
    'BIODIVERSITY: REPTILES/specify:.1': 'biodiv_snake_other_specify',

    # --- Tradeoffs (Forest) ---
    'TRADEOFFS/What tradeoffs to the environment you know which are caused by charcoal making / wood / timber benefits from the forest?': 'tradeoffs_forest_benefits_list',
    'TRADEOFFS/What tradeoffs to the environment you know which are caused by charcoal making / wood / timber benefits from the forest?/benefiting from timber/wood/charcoal causes deforestation': 'tradeoffs_forest_deforestation_check',
    'TRADEOFFS/What tradeoffs to the environment you know which are caused by charcoal making / wood / timber benefits from the forest?/global warming': 'tradeoffs_forest_global_warming_check',
    'TRADEOFFS/What tradeoffs to the environment you know which are caused by charcoal making / wood / timber benefits from the forest?/carbon stock reduction': 'tradeoffs_forest_carbon_stock_reduction_check',
    'TRADEOFFS/What tradeoffs to the environment you know which are caused by charcoal making / wood / timber benefits from the forest?/habitat destruction (displaced/dead species)': 'tradeoffs_forest_habitat_destruction_check',
    'TRADEOFFS/What tradeoffs to the environment you know which are caused by charcoal making / wood / timber benefits from the forest?/other': 'tradeoffs_forest_other_check',
    'TRADEOFFS/explain': 'tradeoffs_forest_other_explain',
    'tradeoffs_forest_access': 'tradeoffs_forest_access', # Already short
    'tradeoffs_crop_neg_effect_forest': 'tradeoffs_crop_neg_effect_forest', # Already short
    'TRADEOFFS/elaborate': 'tradeoffs_crop_neg_effect_forest_elaborate',

    # --- Tradeoffs (Wetland) ---
    'TRADEOFFS/Does the practice of crops cultivation have a negative effect on the wetland?': 'tradeoffs_crop_neg_effect_wetland_check',
    'TRADEOFFS/elaborate.1': 'tradeoffs_crop_neg_effect_wetland_elaborate',
    'TRADEOFFS/Does the practice of making beer from sorghum have a negative implication on the wetland?': 'tradeoffs_beer_sorghum_neg_effect_wetland_check',
    'TRADEOFFS/elaborate.2': 'tradeoffs_beer_sorghum_neg_effect_wetland_elaborate',
    'TRADEOFFS/Does the practice of making beer from ${crops_wetland_beer} have a negative implication on the wetland?': 'tradeoffs_beer_other_neg_effect_wetland_check',
    'TRADEOFFS/elaborate.3': 'tradeoffs_beer_other_neg_effect_wetland_elaborate',
    'TRADEOFFS/Generally, what [other] tradeoffs to the environment you know which are caused by the wetland?': 'tradeoffs_wetland_general_other_list',
    'tradeoffs_human_practice_wetland_health': 'tradeoffs_human_practice_wetland_health', # Already short
    'TRADEOFFS/How is health affected?': 'tradeoffs_wetland_health_affected_list',
    'TRADEOFFS/How is health affected?/The wetland has a negative effect on our wellbeing since it is a factor to some waterborne diseases here': 'tradeoffs_wetland_health_waterborne_diseases',
    'TRADEOFFS/How is health affected?/Human defecation is sometimes done in the wetland, so it is not good in that way for our well-being': 'tradeoffs_wetland_health_human_defecation',
    'TRADEOFFS/How is health affected?/other': 'tradeoffs_wetland_health_other_check',
    'TRADEOFFS/elaborate.4': 'tradeoffs_wetland_health_other_elaborate',

    # --- Harm by Animals ---
    'HARM BY ANIMALS/Are there any incidences of a crocodile harm to human life or livestock in the wetland?': 'harm_crocodile_check',
    'HARM BY ANIMALS/Please elaborate': 'harm_crocodile_elaborate',
    'harm_animal_forest_to_human': 'harm_animal_forest_to_human', # Already short
    'harm_animal_forest_to_livestock': 'harm_animal_forest_to_livestock', # Already short
    'HARM BY ANIMALS/elaborate': 'harm_animal_forest_elaborate',
    'HARM BY ANIMALS/Do the snakes beat people or have they ever beaten someone in the wetland?': 'harm_snakes_check',
    'HARM BY ANIMALS/What do you do/use as cure for snake beat?': 'harm_snake_cure_list',
    'HARM BY ANIMALS/What do you do/use as cure for snake beat?/We go hospital/dispensary directly!': 'harm_snake_cure_hospital_check',
    'HARM BY ANIMALS/What do you do/use as cure for snake beat?/We use traditional medicine from the wetland': 'harm_snake_cure_wetland_trad_med_check',
    'HARM BY ANIMALS/What do you do/use as cure for snake beat?/We use medicinal plant from forest': 'harm_snake_cure_forest_med_plant_check',
    'HARM BY ANIMALS/What do you do/use as cure for snake beat?/We use the "small black stone" ("pierre noire")': 'harm_snake_cure_pierre_noire_check',
    'HARM BY ANIMALS/What do you do/use as cure for snake beat?/We do nothing and no more consequences occur': 'harm_snake_cure_nothing_check',
    'HARM BY ANIMALS/What do you do/use as cure for snake beat?/other': 'harm_snake_cure_other_check',
    'HARM BY ANIMALS/specify:': 'harm_snake_cure_other_specify',

    # --- Final Comments ---
    'final_comments_resp': 'final_comments_respondent', # Already short
    'FINAL COMMENTS/Explain:': 'final_comments_respondent_explain',
    'final_comments_enum': 'final_comments_enumerator', # Already short
    'FINAL COMMENTS/Please enter observation remarks or any other comments': 'final_comments_enumerator_remarks',
    'FINAL COMMENTS/........................................................': 'final_comments_separator1',
    'FINAL COMMENTS/THANKS A LOT FOR ANSWERING ALL QUESTIONS!': 'final_comments_thanks_note',
    'FINAL COMMENTS/.........................................................1': 'final_comments_separator2',
    'FINAL COMMENTS/Filled Form No.: **${interview_id}**': 'final_comments_form_id',

    # --- Duplicate Crop Checks/Counts (These are the .1 and _count suffixes) ---
    'CROPS CULTIVATED/Which crop(s) do you cultivate?.1': 'crop_cultivated_list_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/maize.1': 'crop_maize_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/beans.1': 'crop_beans_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/chick peas.1': 'crop_chick_peas_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/rice/paddy.1': 'crop_rice_paddy_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/wheat.1': 'crop_wheat_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/sugarcane.1': 'crop_sugarcane_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/sorghum.1': 'crop_sorghum_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/sesame.1': 'crop_sesame_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/tomatoes.1': 'crop_tomatoes_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/onions.1': 'crop_onions_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/garlic.1': 'crop_garlic_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/chilli pepper.1': 'crop_chilli_pepper_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/bell/capsicum/sweet pepper.1': 'crop_bell_sweet_pepper_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/amaranth.1': 'crop_amaranth_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/spinach.1': 'crop_spinach_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/cassava.1': 'crop_cassava_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/pumpkins.1': 'crop_pumpkins_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/tea.1': 'crop_tea_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/flowers.1': 'crop_flowers_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/bananas.1': 'crop_bananas_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/peanut.1': 'crop_peanut_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/cashew.1': 'crop_cashew_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/sunflower.1': 'crop_sunflower_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/palm.1': 'crop_palm_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/irish potatoes.1': 'crop_irish_potatoes_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/sweet potatoes.1': 'crop_sweet_potatoes_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/tamarillo/ tree tomato/ "blood fruit" - (*Solanum betaceum*).1': 'crop_tamarillo_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Coconut.1': 'crop_coconut_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Olive.1': 'crop_olive_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Mangoes.1': 'crop_mangoes_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Avocado.1': 'crop_avocado_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Grape.1': 'crop_grape_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Oranges.1': 'crop_oranges_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/lemon.1': 'crop_lemon_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Mandarin.1': 'crop_mandarin_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Pear.1': 'crop_pear_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/strawberry.1': 'crop_strawberry_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/goldenberry (Peruvian groundcherry) - _Physalis peruviana_.1': 'crop_goldenberry_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/pineapple.1': 'crop_pineapple_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Apple.1': 'crop_apple_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/passion.1': 'crop_passion_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/watermelon.1': 'crop_watermelon_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/papaya.1': 'crop_papaya_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Carrots.1': 'crop_carrots_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Ginger.1': 'crop_ginger_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/beetroot.1': 'crop_beetroot_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Cucumber.1': 'crop_cucumber_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Okra.1': 'crop_okra_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Celery.1': 'crop_celery_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Eggplant.1': 'crop_eggplant_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/African eggplant.1': 'crop_african_eggplant_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/green bean.1': 'crop_green_bean_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Cabbage.1': 'crop_cabbage_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Soybean.1': 'crop_soybean_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Papyrus.1': 'crop_papyrus_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/red stinkwood / African cherry.1': 'crop_african_cherry_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/Bamboo.1': 'crop_bamboo_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/taro.1': 'crop_taro_check_duplicate',
    'CROPS CULTIVATED/Which crop(s) do you cultivate?/yam.1': 'crop_yam_check_duplicate',
    'COUNT: CROPS CULTIVATED/maize_grown_count': 'crop_maize_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/beans_grown_count': 'crop_beans_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/chick_peas_grown_count': 'crop_chick_peas_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/rice_grown_count': 'crop_rice_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/wheat_grown_count': 'crop_wheat_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/sugarcane_grown_count': 'crop_sugarcane_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/sorghum_grown_count': 'crop_sorghum_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/sesame_grown_count': 'crop_sesame_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/tomatoes_grown_count': 'crop_tomatoes_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/onions_grown_count': 'crop_onions_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/garlic_grown_count': 'crop_garlic_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/pepper_grown_count': 'crop_pepper_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/poivrons_grown_count': 'crop_poivrons_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/amaranth_grown_count': 'crop_amaranth_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/spinach_grown_count': 'crop_spinach_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/cassava_grown_count': 'crop_cassava_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/pumpkins_grown_count': 'crop_pumpkins_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/tea_grown_count': 'crop_tea_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/flowers_grown_count': 'crop_flowers_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/bananas_grown_count': 'crop_bananas_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/peanut_grown_count': 'crop_peanut_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/cashew_grown_count': 'crop_cashew_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/sunflower_grown_count': 'crop_sunflower_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/palm_grown_count': 'crop_palm_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/potatoes_irish_grown_count': 'crop_potatoes_irish_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/potatoes_sweet_grown_count': 'crop_potatoes_sweet_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/prune_grown_count': 'crop_prune_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/coconut_grown_count': 'crop_coconut_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/olive_grown_count': 'crop_olive_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/mangoes_grown_count': 'crop_mangoes_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/avocado_grown_count': 'crop_avocado_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/grape_grown_count': 'crop_grape_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/oranges_grown_count': 'crop_oranges_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/lemon_grown_count': 'crop_lemon_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/mandarin_grown_count': 'crop_mandarin_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/pear_grown_count': 'crop_pear_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/strawberry_grown_count': 'crop_strawberry_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/goldenberry_grown_count': 'crop_goldenberry_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/pineapple_grown_count': 'crop_pineapple_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/apple_grown_count': 'crop_apple_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/passion_grown_count': 'crop_passion_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/watermelon_grown_count': 'crop_watermelon_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/papaya_grown_count': 'crop_papaya_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/carrots_grown_count': 'crop_carrots_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/ginger_grown_count': 'crop_ginger_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/beetroot_grown_count': 'crop_beetroot_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/cucumber_grown_count': 'crop_cucumber_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/okra_grown_count': 'crop_okra_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/celery_grown_count': 'crop_celery_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/eggplant_grown_count': 'crop_eggplant_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/intoryi_grown_count': 'crop_intoryi_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/green_bean_grown_count': 'crop_green_bean_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/cabbage_grown_count': 'crop_cabbage_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/soybean_grown_count': 'crop_soybean_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/papyrus_grown_count': 'crop_papyrus_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/Prunus_africana_grown_count': 'crop_african_cherry_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/bamboo_grown_count': 'crop_bamboo_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/taro_grown_count': 'crop_taro_grown_count', # Already short
    'COUNT: CROPS CULTIVATED/yam_grown_count': 'crop_yam_grown_count', # Already short
     'VALUES SUMMARY OF CROPS YOU CULTIVATE/The maximum amount which you benefit every year from crop cultivation is: ${value_farming_rwf_year_maximum} RWF': 'v_farming_value_year_RWF',
 'VALUES SUMMARY OF CROPS YOU CULTIVATE/value_farming_rwf_year_average': 'v_farming_value_year_average_RWF'
}

# --- 2. Execute the Renaming ---
# Assuming your DataFrame is loaded into a variable named 'df'.
st.markdown("## 🔄 Execute Column Renaming — Part 2")

try:
    # Attempt the renaming
    df.rename(columns=column_rename_map_part2, inplace=True)

    st.success("✅ Column renaming (Part 2) executed successfully!")

except NameError:
    st.error("❌ Error: The DataFrame **'df'** was not found. Please ensure the DataFrame is loaded and named **df**.")

except Exception as e:
    st.error(f"⚠️ An unexpected error occurred during renaming: **{e}**")

st.markdown('''

| Original Column Name | Shortened Column Name | Section |
|---------------------|--------------------|---------|
| RESPONDENT'S IDENTIFICATION |  |  |
| RESPONDENT'S IDENTIFICATION/What is the phone number of the respondent? | resp_phone_number | ID |
| --- | --- | --- |
| BENEFITS AWARENESS / IMPORTANCE |  |  |
| ECOSYSTEM SERVICES BENEFITED/If it is not beneficial, why do you think the forest is not important? | forest_not_important_reason | Importance |
| benefits_wetland_important | wetland_important_check | Importance |
| ECOSYSTEM SERVICES BENEFITED/If it is not beneficial, why do you think the wetland is not important? | wetland_not_important_reason | Importance |
| --- | --- | --- |
| FOREST BENEFITS (Initial List) |  |  |
| ECOSYSTEM SERVICES BENEFITED/You said "Other". Please mention what "other food" you get from this forest | forest_other_food_specify | Food |
| ECOSYSTEM SERVICES BENEFITED/You said "Other". Please explain the benefits you get from this forest | forest_other_benefit_explain | General |
| --- | --- | --- |
| WETLAND BENEFITS (Initial List - Checklists) |  |  |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland? | wetland_benefit_initial_list | General |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/fish for food | wetland_benefit_fish_check | Food |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/snail | wetland_benefit_snail_check | Food |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/other food for humans | wetland_benefit_other_food_check | Food |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/provide refuge/habitat to animal species | wetland_benefit_habitat_animal_check | Habitat |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/provide refuge/habitat to plant species | wetland_benefit_habitat_plant_check | Habitat |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/income generation | wetland_benefit_income_check | Economic |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/tourism | wetland_benefit_tourism_check | Cultural |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/beauty, aesthetics | wetland_benefit_aesthetics_check | Cultural |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/recreation | wetland_benefit_recreation_check | Cultural |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/air pollution control | wetland_benefit_air_control_check | Regulating |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/water for livestock | wetland_benefit_water_livestock_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/water for industrial use | wetland_benefit_water_industrial_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/water for domestic use | wetland_benefit_water_domestic_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/water for making local beer | wetland_benefit_water_beer_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/agricultural production | wetland_benefit_agri_prod_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/sleeping mat | wetland_benefit_mats_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/water purification | wetland_benefit_water_purif_check | Regulating |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/hydroelectric benefits | wetland_benefit_hydro_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/soil erosion control | wetland_benefit_erosion_control_check | Regulating |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/carbon sequestration | wetland_benefit_carbon_seq_check | Regulating |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/scientific research | wetland_benefit_research_check | Cultural |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/cultural activities | wetland_benefit_cultural_check | Cultural |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/medicaments | wetland_benefit_medicaments_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/hunting (!) | wetland_benefit_hunting_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/transport | wetland_benefit_transport_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/OTHER | wetland_benefit_other_check | General |
| ECOSYSTEM SERVICES BENEFITED/You said "Other food". Please mention what "other food" you get from this wetland | wetland_other_food_specify | Food |
| ECOSYSTEM SERVICES BENEFITED/You said "Other". Please explain the benefits you get from this wetland | wetland_other_benefit_explain | General |
| --- | --- | --- |
| FOREST BENEFITS (Confirmation List - Checklists) |  |  |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest? | forest_benefit_confirmation_check | General |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/wood provision | forest_benefit_wood_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/timber | forest_benefit_timber_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/income generation | forest_benefit_income_check | Economic |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/provide refuge/habitat to animal species | forest_benefit_habitat_animal_check | Habitat |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/provide refuge/habitat to plant species | forest_benefit_habitat_plant_check | Habitat |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/tourism | forest_benefit_tourism_check | Cultural |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/beauty, aesthetics | forest_benefit_aesthetics_check | Cultural |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/recreation | forest_benefit_recreation_check | Cultural |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/air regulation | forest_benefit_air_reg_check | Regulating |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/flood control | forest_benefit_flood_control_check | Regulating |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/climate regulation | forest_benefit_climate_reg_check | Regulating |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/food for livestock | forest_benefit_food_livestock_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/agricultural production | forest_benefit_agri_prod_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/fishery | forest_benefit_fishery_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/provide honey | forest_benefit_honey_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/we get mushroom | forest_benefit_mushroom_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/provide fruits | forest_benefit_fruits_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/snail | forest_benefit_snail_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/other food for humans | forest_benefit_other_food_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/charcoal provision | forest_benefit_charcoal_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/water regulation | forest_benefit_water_reg_check | Regulating |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/soil erosion control | forest_benefit_erosion_control_check | Regulating |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/carbon sequestration | forest_benefit_carbon_seq_check | Regulating |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/scientific research | forest_benefit_research_check | Cultural |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/medicaments | forest_benefit_medicaments_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/hunting (!) | forest_benefit_hunting_check | Provisioning |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/cultural activities | forest_benefit_cultural_check | Cultural |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/OTHER | forest_benefit_other_check | General |

| Original Column Name | Shortened Column Name | Section |
|---------------------|--------------------|---------|
| --- | --- | --- |
| WETLAND BENEFITS (Confirmation List - Checklists) |  |  |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland? | wetland_benefit_confirmation_check | General |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/fish for food | wetland_conf_benefit_fish_check | Food |
| ... (Other specific wetland benefits confirmed) | ... | ... |
| ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/OTHER | wetland_conf_benefit_other_check | General |
| --- | --- | --- |
| ATMOSPHERIC REGULATION / AESTHETICS / SENSE OF PLACE |  |  |
| ATMOSPHERIC REGULATION AWARENESS/Please elaborate:.1 | air_reg_elaborate | Regulating |
| AESTHETICS / BEAUTY/Please elaborate how beautiful the wetland is in your perception | wetland_beauty_elaborate | Cultural |
| Please rate how beautiful the wetland is | wetland_beauty_rating | Cultural |
| SENSE OF PLACE & BELONGINGNESS/Please explain why you don't feel well to be residing in the surroundings of this forest | sense_place_forest_not_well_explain | Cultural |
| sense_place_feel_wetland | sense_place_wetland_feel_check | Cultural |
| SENSE OF PLACE & BELONGINGNESS/Please explain why you don't feel well to be residing in the surroundings of this wetland | sense_place_wetland_not_well_explain | Cultural |
| --- | --- | --- |
| CONSEQUENCES OF ABSENSE / REDUCTION |  |  |
| CONSEQUENCES OF ABSENSE / REDUCTION/Please elaborate how you could be affected by the depletion of the forest | cons_absense_forest_elaborate | General |
| CONSEQUENCES OF ABSENSE / REDUCTION/Please elaborate how you could be affected by the depletion of the wetland | cons_absense_wetland_elaborate | General |
| CONSEQUENCES OF ABSENSE / REDUCTION/Please explain | cons_explain_1 | General |
| CONSEQUENCES OF ABSENSE / REDUCTION/Please explain.1 | cons_explain_2 | General |
| CONSEQUENCES OF ABSENSE / REDUCTION/But then, Rugezi marshland has been partly degraded. How does the degradation affect you? | cons_degrad_affect_you_list | Degradation |
| CONSEQUENCES OF ABSENSE / REDUCTION/But then, Rugezi marshland has been partly degraded. How does the degradation affect you?/My whole life has been affected | cons_degrad_life_affected_check | Degradation |
| CONSEQUENCES OF ABSENSE / REDUCTION/But then, Rugezi marshland has been partly degraded. How does the degradation affect you?/It reduces my income since I depend on the wetland for livelihood | cons_degrad_income_reduced_check | Degradation |
| CONSEQUENCES OF ABSENSE / REDUCTION/But then, Rugezi marshland has been partly degraded. How does the degradation affect you?/I think I should shift to another province or district | cons_degrad_shift_district_check | Degradation |
| CONSEQUENCES OF ABSENSE / REDUCTION/But then, Rugezi marshland has been partly degraded. How does the degradation affect you?/I feel I should shift to a neighboring country | cons_degrad_shift_country_check | Degradation |
| CONSEQUENCES OF ABSENSE / REDUCTION/But then, Rugezi marshland has been partly degraded. How does the degradation affect you?/It doesn't affect my life | cons_degrad_no_effect_check | Degradation |
| CONSEQUENCES OF ABSENSE / REDUCTION/But then, Rugezi marshland has been partly degraded. How does the degradation affect you?/Other effects | cons_degrad_other_check | Degradation |
| CONSEQUENCES OF ABSENSE / REDUCTION/specify: | cons_degrad_other_specify | Degradation |
| CONSEQUENCES OF ABSENSE / REDUCTION/What do you think is / are the reason(s) for the experienced decreasing water level of Rugezi wetland? | cons_water_level_decrease_reasons_list | Water Level |
| CONSEQUENCES OF ABSENSE / REDUCTION/What do you think is / are the reason(s) for the experienced decreasing water level of Rugezi wetland?/Water drainage by Electrogaz to lake Burera & Ruhondo | cons_water_drainage_check | Water Level |
| CONSEQUENCES OF ABSENSE / REDUCTION/What do you think is / are the reason(s) for the experienced decreasing water level of Rugezi wetland?/human activities (unsustainable land use practices) | cons_water_human_activities_check | Water Level |
| CONSEQUENCES OF ABSENSE / REDUCTION/What do you think is / are the reason(s) for the experienced decreasing water level of Rugezi wetland?/climate change | cons_water_climate_change_check | Water Level |
| CONSEQUENCES OF ABSENSE / REDUCTION/What do you think is / are the reason(s) for the experienced decreasing water level of Rugezi wetland?/deforestation | cons_water_deforestation_check | Water Level |
| CONSEQUENCES OF ABSENSE / REDUCTION/What do you think is / are the reason(s) for the experienced decreasing water level of Rugezi wetland?/increase of population size (demographic factors) | cons_water_pop_increase_check | Water Level |
| CONSEQUENCES OF ABSENSE / REDUCTION/What do you think is / are the reason(s) for the experienced decreasing water level of Rugezi wetland?/soil erosion on surrounding valleys | cons_water_soil_erosion_check | Water Level |
| CONSEQUENCES OF ABSENSE / REDUCTION/What do you think is / are the reason(s) for the experienced decreasing water level of Rugezi wetland?/geological reasons | cons_water_geological_check | Water Level |
| CONSEQUENCES OF ABSENSE / REDUCTION/What do you think is / are the reason(s) for the experienced decreasing water level of Rugezi wetland?/other | cons_water_other_check | Water Level |
| CONSEQUENCES OF ABSENSE / REDUCTION/specify:.1 | cons_water_other_specify | Water Level |

| Original Column Name | Shortened Column Name | Section |
|---------------------|--------------------|---------|
| --- | --- | --- |
| BENEFITS TO THE SOCIETY |  |  |
| BENEFITS TO THE SOCIETY/explain: | society_benefit_forest_explain | Forest |
| BENEFITS TO THE SOCIETY/How do your neighbours and the society as a whole in this area benefit from the wetland? | society_benefit_wetland_list | Wetland |
| BENEFITS TO THE SOCIETY/How do your neighbours and the society as a whole in this area benefit from the wetland?/Sometimes we meet as a society in the "open spaces"... | society_wetland_meet_open_space_check | Wetland |
| BENEFITS TO THE SOCIETY/How do your neighbours and the society as a whole in this area benefit from the wetland?/We have a lot of fish, water, etc... and we take it as a privilege... | society_wetland_privilege_check | Wetland |
| BENEFITS TO THE SOCIETY/How do your neighbours and the society as a whole in this area benefit from the wetland?/It makes our society to get a lot of visitors and connections... | society_wetland_visitors_check | Wetland |
| BENEFITS TO THE SOCIETY/How do your neighbours and the society as a whole in this area benefit from the wetland?/other | society_wetland_other_check | Wetland |
| BENEFITS TO THE SOCIETY/explain:.1 | society_wetland_other_explain | Wetland |
| BENEFITS TO THE SOCIETY/Do you benefit from the Ntaruka and Mukungwa hydroelectric power plants? | society_benefit_hydro_plants_check | Hydro |
| BENEFITS TO THE SOCIETY/specify: | society_benefit_hydro_specify | Hydro |
| --- | --- | --- |
| STATED / DECLARED INCOME |  |  |
| STATED / DECLARED INCOME/Earlier, you also mentioned "income generation" among benefits you get from the forest. Generally, how much (Rwandan Francs) in total do you get from the forest monthly? | stated_income_forest_monthly_RWF | Forest Income |
| STATED / DECLARED INCOME/income_generated_forest_year | stated_income_forest_annual_RWF | Forest Income |
| STATED / DECLARED INCOME/Earlier, you also mentioned "income generation" among benefits you get from the wetland. Generally, how much (Rwandan Francs) in total do you get from the wetland monthly? | stated_income_wetland_monthly_RWF | Wetland Income |
| STATED / DECLARED INCOME/income_generated_wetland_year | stated_income_wetland_annual_RWF | Wetland Income |
| --- | --- | --- |
| WATER FOR DOMESTIC USES |  |  |
| WATER FOR DOMESTIC USES/What time do you take to access water from the wetland? Time in minutes: | water_domestic_access_time_min | Time/Distance |
| WATER FOR DOMESTIC USES/You fetch water from the wetland every: | water_domestic_frequency | Frequency |
| WATER FOR DOMESTIC USES/water_domestic_frequency_year_equivalency | water_domestic_freq_year_equiv | Calculation |
| WATER FOR DOMESTIC USES/unit for fetching/measuring water: | water_domestic_unit | Unit |
| WATER FOR DOMESTIC USES/One ${water_domestic_unit} is equivalent to how many litres ? | water_domestic_unit_to_L | Conversion |
| WATER FOR DOMESTIC USES/Please estimate how many ${water_domestic_unit}s of water you fetch / use every ${water_domestic_frequency} | water_domestic_quantity | Quantity |
| WATER FOR DOMESTIC USES/If not fetched from the wetland, how much (RWF) does one jerrycan of water cost? | water_domestic_alt_cost_jerrycan_RWF | Cost |
| WATER FOR DOMESTIC USES/How much costs (if any) do you incur to get the ${water_domestic_quantity} - ${water_domestic_unit}s of water that you get every ${water_domestic_frequency}? | water_domestic_incurred_cost_RWF | Cost |
| WATER FOR DOMESTIC USES/Value of water in Rwandan Francs per year: | water_domestic_value_year_RWF | Calculated Value |
| --- | --- | --- |
| MATS VALUE / PRACTICE |  |  |
| MATS/What is the use of the mats you make? | mats_use_list | Use |
| MATS/What is the use of the mats you make?/for our own use (e.g. at home: sleeping, etc...) and not for sale | mats_use_own_check | Use Check |
| MATS/What is the use of the mats you make?/for sale | mats_use_sale_check | Use Check |
| MATS/Ok, so, you know something about mats making practice! | mats_aware_note | Awareness |
| MATS/What materials are used to make mats called "ibirago"? | mats_materials_ibirago | Materials |
| MATS/Apart from the ${mats_materials}, is there any other materials you use for making any model/type of local local mats? | mats_materials_alt_check | Materials |
| MATS/What is the name of the other material or other grass/weed/sedge used? | mats_materials_alt_name | Materials |
| MATS/Do you use the ${mats_materials_alternative} for making mats which are different (type) from the mats model made from ${mats_materials}? | mats_alt_materials_type_diff_check | Materials |
| MATS/What other model of mats do you make from ${mats_materials_alternative}? | mats_alt_model_list | Model |
| MATS/What other model of mats do you make from ${mats_materials_alternative}?/sleeping mats (ibirago) | mats_alt_model_ibirago_check | Model Check |
| MATS/What other model of mats do you make from ${mats_materials_alternative}?/imikeka | mats_alt_model_imikeka_check | Model Check |
| MATS/What other model of mats do you make from ${mats_materials_alternative}?/rug (imisambi) | mats_alt_model_imisambi_check | Model Check |
| MATS/What other model of mats do you make from ${mats_materials_alternative}?/"ibidasesa" (woven grass mat for dying things outside) | mats_alt_model_ibidasesa_check | Model Check |
| MATS/Where do the "${mats_materials}" materials come from? | mats_materials_origin_list | Origin |
| MATS/Where do the "${mats_materials}" materials come from?/from the wetland | mats_materials_wetland_check | Origin Check |
| MATS/Where do the "${mats_materials}" materials come from?/not from the wetland | mats_materials_not_wetland_check | Origin Check |
| MATS/Where do the "${mats_materials_alternative}" materials come from? | mats_materials_alt_origin_list | Origin |
| MATS/Where do the "${mats_materials_alternative}" materials come from?/from the wetland | mats_materials_alt_wetland_check | Origin Check |
| MATS/Where do the "${mats_materials_alternative}" materials come from?/not from the wetland | mats_materials_alt_not_wetland_check | Origin Check |
| MATS/Are there any mats (_already fabricated_ or "ready-made") FOR SALE which originate from somewhere else apart from being made here using the local materials that you have just mentioned? | mats_ready_made_for_sale_check | Market |
| MATS/Where do the mats originate from? | mats_origin_list | Market |
| MATS/Where do the mats originate from?/other provinces in Rwanda | mats_origin_provinces_check | Market Check |
| MATS/Where do the mats originate from?/Uganda | mats_origin_uganda_check | Market Check |
| MATS/Where do the mats originate from?/Burundi | mats_origin_burundi_check | Market Check |
| MATS/Where do the mats originate from?/Tanzania | mats_origin_tanzania_check | Market Check |
| MATS/Where do the mats originate from?/Congo (DRC) | mats_origin_congo_check | Market Check |
| MATS/Where do the mats originate from?/other place | mats_origin_other_check | Market Check |
| MATS/Please rate what you think is the proportion of the mats locally-made and those coming from ${mats_origin} | mats_proportion_local_imported | Market |
| MATS/The "${mats_materials}" are taken for making mats every: | mats_materials_frequency | Frequency |
| MATS/unit of measuring the ${mats_materials}: | mats_materials_unit | Unit |
| MATS/One ${unit_mats_materials} is equivalent to how many kilograms by estimate? | mats_materials_unit_to_kg | Conversion |
| MATS/How many unit_mats_materials of ${mats_materials} are used to make mats every ${frequency_mats}? | mats_materials_quantity | Quantity |
| MATS/How many [sleeping] mats are made out of the ${quantity_mats_materials} unit_mats_materials of ${mats_materials} every ${frequency_mats}? | mats_quantity_made | Output |
| MATS/How much cost (RWF) do you incur until you fabricate the ${quantity_mats} mats every ${frequency_mats}? | mats_fabrication_cost_RWF | Cost |
| MATS/Where is the market for mats located? | mats_market_location | Market |
| MATS/Do you think those making mats for selling get much money from the business? | mats_business_profitable_check | Profit |
| MATS/please elaborate: | mats_business_profitable_elaborate | Profit |
| MATS/How much do you estimate they make in 3 months? | mats_income_3_months_RWF | Income |


| Original Column Name | Shortened Column Name | Section |
|---------------------|--------------------|---------|
| --- | --- | --- |
| FOREST VALUE (WOOD, TIMBER, HONEY, MUSHROOMS) |  |  |
| VALUE: WOOD/Wood is taken from the forest (per concerned household) every: | value_wood_frequency | Frequency |
| VALUE: TIMBER/Timber is taken from the forest (per concerned household) every: | value_timber_frequency | Frequency |
| VALUE: TIMBER/One ${unit_timber} is equivalent to how many kilograms? | value_timber_unit_to_kg | Conversion |
| VALUE: TIMBER/How many ${unit_timber}s of timber do you get from the forest every ${frequency_timber}? | value_timber_quantity | Quantity |
| VALUE: TIMBER/Its market price in RWF per ${unit_timber} is: | value_timber_market_price_RWF | Price |
| VALUE: TIMBER/How much cost (RWF) do you incur in order to get the ${quantity_timber} ${unit_timber}s of timber every ${frequency_timber}? | value_timber_cost_RWF | Cost |
| VALUE: HONEY/Ok, so, you know something about honey practice! | value_honey_aware_note | Awareness |
| VALUE: HONEY/Honey is made from the forest (per concerned household) every: | value_honey_frequency | Frequency |
| VALUE: HONEY/One ${unit_honey} is equivalent to how many litres? | value_honey_unit_to_L | Conversion |
| VALUE: HONEY/How many ${unit_honey}s of honey do you get from the forest every ${frequency_honey}? | value_honey_quantity | Quantity |
| VALUE: HONEY/Its market price in RWF per ${unit_honey} is: | value_honey_market_price_RWF | Price |
| VALUE: HONEY/How much cost (RWF) do you incur in order to make the ${quantity_honey} - ${unit_honey}s of honey every ${frequency_honey}? | value_honey_cost_RWF | Cost |
| VALUE: MUSHROOMS/Ok, so, you know something about mushroom provision! | value_mushroom_aware_note | Awareness |
| VALUE: MUSHROOMS/Mushroom is obtained from the forest (per concerned household) every: | value_mushroom_frequency | Frequency |
| VALUE: MUSHROOMS/One ${unit_mushroom} is equivalent to how many kilograms? | value_mushroom_unit_to_kg | Conversion |
| VALUE: MUSHROOMS/How many ${unit_mushroom}s of mushrooms do you get from the forest every ${frequency_mushroom}? | value_mushroom_quantity | Quantity |
| VALUE: MUSHROOMS/Its market price in RWF per ${unit_mushroom} is: | value_mushroom_market_price_RWF | Price |
| VALUE: MUSHROOMS/How much cost (RWF) do you incur in order to get the ${quantity_mushroom} ${unit_mushroom}s of mushroom every ${frequency_mushroom}? | value_mushroom_cost_RWF | Cost |
| VALUE: MUSHROOMS/value_mushroom | value_mushroom_annual_RWF | Calculated Value |
| --- | --- | --- |
| WETLAND VALUE (FISH) |  |  |
| VALUE: FISH/Ok, so, you know something about fishery in the wetland! | value_fish_aware_note | Awareness |
| VALUE: FISH/Fresh fish is obtained from the wetland (per concerned household) every: | value_fish_frequency | Frequency |
| VALUE: FISH/you measure the fish in: | value_fish_unit | Unit |
| VALUE: FISH/One ${unit_fish} of fish is equivalent to how many kilograms (kg)? | value_fish_unit_to_kg | Conversion |
| VALUE: FISH/How many ${unit_fish}s of fish do you get every ${frequency_fish} from the wetland? | value_fish_quantity | Quantity |
| VALUE: FISH/You get the ${quantity_fish} fish ${unit_fish} every ${frequency_fish}. As you know, the number of ${frequency_fish}s in a year is: | value_fish_freq_year_note | Note |
| VALUE: FISH/So, every year, the number of kilograms of fish you get from the wetland is: | value_fish_annual_kg_note | Note |
| VALUE: FISH/Its market price in RWF per ${unit_fish} is: | value_fish_market_price_RWF | Price |
| VALUE: FISH/Do you incur any cost (RWF) in order to get the ${quantity_fish} - ${unit_fish} of fish every ${frequency_fish}? | value_fish_cost_check | Cost Check |
| VALUE: FISH/So, the money (Rwandan Francs) so obtained from fishing per ${frequency_fish}: | value_fish_income_per_freq_RWF | Income |
| --- | --- | --- |
| FISHING PRACTICE & FISH NAMES |  |  |
| FISHING PRACTICE & FISH NAMES/Do you know some types (genera or specific names) of fish found in the wetland? | fish_know_types_check | Knowledge |
| FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery? | fish_types_list | Types |
| FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/tilapia | fish_type_tilapia_check | Type Check |
| FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/Burera haplo (Haplochromis erythromaculatus) | fish_type_burera_haplo_check | Type Check |
| FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/Alluaud's haplo (Astatoreochromis alluaudi) - used to control snails/ molluscs | fish_type_alluaud_haplo_check | Type Check |
| FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/perch (Lates niloticus) | fish_type_perch_check | Type Check |
| FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/Marbled lungfish (Protopterus aethiopicus) | fish_type_lungfish_check | Type Check |
| FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/Elephant-snout fish (Mormyrus kannume) | fish_type_elephant_snout_check | Type Check |
| FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/Common carp (Cyprinus carpio) | fish_type_common_carp_check | Type Check |
| FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/Rwandese carp (Varicorhinus ruandae / [Labeo]barbus ruandae and Varicorhinus platystoma species) | fish_type_rwandese_carp_check | Type Check |
| FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/Longtail spinyeel (Mastacembelus frenatus) | fish_type_longtail_spinyeel_check | Type Check |
| FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/barb (Barbus genus) | fish_type_barb_check | Type Check |
| FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/Mudfish / common catfish / sharptooth catfish (Clarias gariepinus) | fish_type_mudfish_catfish_check | Type Check |
| FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/Smoothhead catfish (Clarias liocephalus) | fish_type_smoothhead_catfish_check | Type Check |
| FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/other fish | fish_type_other_check | Type Check |
| --- | --- | --- |
| LIVESTOCK KEEPING (Selection Checklist) |  |  |
| LIVESTOCK KEEPING/Which animals do you keep (domesticate)? | livestock_kept_list | Animals Kept |
| LIVESTOCK KEEPING/Which animals do you keep (domesticate)?/cattle | livestock_kept_cattle_check | Animals Kept |
| LIVESTOCK KEEPING/Which animals do you keep (domesticate)?/goat | livestock_kept_goat_check | Animals Kept |
| LIVESTOCK KEEPING/Which animals do you keep (domesticate)?/sheep | livestock_kept_sheep_check | Animals Kept |
| LIVESTOCK KEEPING/Which animals do you keep (domesticate)?/rabbit | livestock_kept_rabbit_check | Animals Kept |
| LIVESTOCK KEEPING/Which animals do you keep (domesticate)?/dog | livestock_kept_dog_check | Animals Kept |

''')

st.markdown("## 🔄 Renaming Column  — Part 3")

# Dictionary mapping Old Column Names to New Short Column Names
rename_map = {
    # RESPONDENT'S IDENTIFICATION
    "RESPONDENT'S IDENTIFICATION/What is the phone number of the respondent?": 'resp_phone_number',

    # BENEFITS AWARENESS / IMPORTANCE
    'ECOSYSTEM SERVICES BENEFITED/If it is not beneficial, why do you think the forest is not important?': 'forest_not_important_reason',
    'benefits_wetland_important': 'wetland_important_check',
    'ECOSYSTEM SERVICES BENEFITED/If it is not beneficial, why do you think the wetland is not important?': 'wetland_not_important_reason',

    # FOREST BENEFITS (Initial List & Explain)
    'ECOSYSTEM SERVICES BENEFITED/You said "Other". Please mention what "other food" you get from this forest': 'forest_other_food_specify',
    'ECOSYSTEM SERVICES BENEFITED/You said "Other". Please explain the benefits you get from this forest': 'forest_other_benefit_explain',

    # WETLAND BENEFITS (Initial List - Checklists)
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?': 'wetland_benefit_initial_list',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/fish for food': 'wetland_benefit_fish_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/snail': 'wetland_benefit_snail_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/other food for humans': 'wetland_benefit_other_food_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/provide refuge/habitat to animal species': 'wetland_benefit_habitat_animal_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/provide refuge/habitat to plant species': 'wetland_benefit_habitat_plant_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/income generation': 'wetland_benefit_income_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/tourism': 'wetland_benefit_tourism_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/beauty, aesthetics': 'wetland_benefit_aesthetics_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/recreation': 'wetland_benefit_recreation_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/air pollution control': 'wetland_benefit_air_control_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/water for livestock': 'wetland_benefit_water_livestock_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/water for industrial use': 'wetland_benefit_water_industrial_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/water for domestic use': 'wetland_benefit_water_domestic_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/water for making local beer': 'wetland_benefit_water_beer_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/agricultural production': 'wetland_benefit_agri_prod_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/sleeping mat': 'wetland_benefit_mats_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/water purification': 'wetland_benefit_water_purif_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/hydroelectric benefits': 'wetland_benefit_hydro_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/soil erosion control': 'wetland_benefit_erosion_control_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/carbon sequestration': 'wetland_benefit_carbon_seq_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/scientific research': 'wetland_benefit_research_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/cultural activities': 'wetland_benefit_cultural_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/medicaments': 'wetland_benefit_medicaments_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/hunting (!)': 'wetland_benefit_hunting_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/transport': 'wetland_benefit_transport_check',
    'ECOSYSTEM SERVICES BENEFITED/What services / benefits do you get from this wetland?/OTHER': 'wetland_benefit_other_check',
    'ECOSYSTEM SERVICES BENEFITED/You said "Other food". Please mention what "other food" you get from this wetland': 'wetland_other_food_specify',
    'ECOSYSTEM SERVICES BENEFITED/You said "Other". Please explain the benefits you get from this wetland': 'wetland_other_benefit_explain',

    # FOREST BENEFITS (Confirmation List - Checklists)
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?': 'forest_benefit_confirmation_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/wood provision': 'forest_benefit_wood_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/timber': 'forest_benefit_timber_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/income generation': 'forest_benefit_income_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/provide refuge/habitat to animal species': 'forest_benefit_habitat_animal_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/provide refuge/habitat to plant species': 'forest_benefit_habitat_plant_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/tourism': 'forest_benefit_tourism_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/beauty, aesthetics': 'forest_benefit_aesthetics_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/recreation': 'forest_benefit_recreation_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/air regulation': 'forest_benefit_air_reg_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/flood control': 'forest_benefit_flood_control_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/climate regulation': 'forest_benefit_climate_reg_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/food for livestock': 'forest_benefit_food_livestock_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/agricultural production': 'forest_benefit_agri_prod_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/fishery': 'forest_benefit_fishery_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/provide honey': 'forest_benefit_honey_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/we get mushroom': 'forest_benefit_mushroom_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/provide fruits': 'forest_benefit_fruits_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/snail': 'forest_benefit_snail_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/other food for humans': 'forest_benefit_other_food_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/charcoal provision': 'forest_benefit_charcoal_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/water regulation': 'forest_benefit_water_reg_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/soil erosion control': 'forest_benefit_erosion_control_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/carbon sequestration': 'forest_benefit_carbon_seq_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/scientific research': 'forest_benefit_research_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/medicaments': 'forest_benefit_medicaments_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/hunting (!)': 'forest_benefit_hunting_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/cultural activities': 'forest_benefit_cultural_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this forest?/OTHER': 'forest_benefit_other_check',

    # WETLAND BENEFITS (Confirmation List - Checklists) - Renamed with '_conf'
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?': 'wetland_benefit_confirmation_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/fish for food': 'wetland_conf_benefit_fish_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/snail': 'wetland_conf_benefit_snail_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/other food for humans': 'wetland_conf_benefit_other_food_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/provide refuge/habitat to animal species': 'wetland_conf_benefit_habitat_animal_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/provide refuge/habitat to plant species': 'wetland_conf_benefit_habitat_plant_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/income generation': 'wetland_conf_benefit_income_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/tourism': 'wetland_conf_benefit_tourism_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/beauty, aesthetics': 'wetland_conf_benefit_aesthetics_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/recreation': 'wetland_conf_benefit_recreation_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/air pollution control': 'wetland_conf_benefit_air_control_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/water for livestock': 'wetland_conf_benefit_water_livestock_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/water for industrial use': 'wetland_conf_benefit_water_industrial_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/water for domestic use': 'wetland_conf_benefit_water_domestic_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/water for making local beer': 'wetland_conf_benefit_water_beer_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/agricultural production': 'wetland_conf_benefit_agri_prod_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/sleeping mat': 'wetland_conf_benefit_mats_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/water purification': 'wetland_conf_benefit_water_purif_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/hydroelectric benefits': 'wetland_conf_benefit_hydro_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/soil erosion control': 'wetland_conf_benefit_erosion_control_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/carbon sequestration': 'wetland_conf_benefit_carbon_seq_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/scientific research': 'wetland_conf_benefit_research_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/cultural activities': 'wetland_conf_benefit_cultural_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/medicaments': 'wetland_conf_benefit_medicaments_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/hunting (!)': 'wetland_conf_benefit_hunting_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/transport': 'wetland_conf_benefit_transport_check',
    'ECOSYSTEM SERVICES BENEFITED/Sorry, in the following list, is there any service you get from this wetland?/OTHER': 'wetland_conf_benefit_other_check',

    # ATMOSPHERIC REGULATION / AESTHETICS / SENSE OF PLACE
    'ATMOSPHERIC REGULATION AWARENESS/Please elaborate:.1': 'air_reg_elaborate',
    'AESTHETICS / BEAUTY/Please elaborate how beautiful the wetland is in your perception': 'wetland_beauty_elaborate',
    'Please rate how beautiful the wetland is': 'wetland_beauty_rating',
    "SENSE OF PLACE & BELONGINGNESS/Please explain why you don't feel well to be residing in the surroundings of this forest": 'sense_place_forest_not_well_explain',
    'sense_place_feel_wetland': 'sense_place_wetland_feel_check',
    "SENSE OF PLACE & BELONGINGNESS/Please explain why you don't feel well to be residing in the surroundings of this wetland": 'sense_place_wetland_not_well_explain',

    # CONSEQUENCES OF ABSENSE / REDUCTION
    'CONSEQUENCES OF ABSENSE / REDUCTION/Please elaborate how you could be affected by the depletion of the forest': 'cons_absense_forest_elaborate',
    'CONSEQUENCES OF ABSENSE / REDUCTION/Please elaborate how you could be affected by the depletion of the wetland': 'cons_absense_wetland_elaborate',
    'CONSEQUENCES OF ABSENSE / REDUCTION/Please explain': 'cons_explain_1',
    'CONSEQUENCES OF ABSENSE / REDUCTION/Please explain.1': 'cons_explain_2',
    'CONSEQUENCES OF ABSENSE / REDUCTION/But then, Rugezi marshland has been partly degraded. How does the degradation affect you?': 'cons_degrad_affect_you_list',
    'CONSEQUENCES OF ABSENSE / REDUCTION/But then, Rugezi marshland has been partly degraded. How does the degradation affect you?/My whole life has been affected': 'cons_degrad_life_affected_check',
    'CONSEQUENCES OF ABSENSE / REDUCTION/But then, Rugezi marshland has been partly degraded. How does the degradation affect you?/It reduces my income since I depend on the wetland for livelihood': 'cons_degrad_income_reduced_check',
    'CONSEQUENCES OF ABSENSE / REDUCTION/But then, Rugezi marshland has been partly degraded. How does the degradation affect you?/I think I should shift to another province or district': 'cons_degrad_shift_district_check',
    'CONSEQUENCES OF ABSENSE / REDUCTION/But then, Rugezi marshland has been partly degraded. How does the degradation affect you?/I feel I should shift to a neighboring country': 'cons_degrad_shift_country_check',
    "CONSEQUENCES OF ABSENSE / REDUCTION/But then, Rugezi marshland has been partly degraded. How does the degradation affect you?/It doesn't affect my life": 'cons_degrad_no_effect_check',
    'CONSEQUENCES OF ABSENSE / REDUCTION/But then, Rugezi marshland has been partly degraded. How does the degradation affect you?/Other effects': 'cons_degrad_other_check',
    'CONSEQUENCES OF ABSENSE / REDUCTION/specify:': 'cons_degrad_other_specify',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What do you think is / are the reason(s) for the experienced decreasing water level of Rugezi wetland?': 'cons_water_level_decrease_reasons_list',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What do you think is / are the reason(s) for the experienced decreasing water level of Rugezi wetland?/Water drainage by Electrogaz to lake Burera & Ruhondo': 'cons_water_drainage_check',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What do you think is / are the reason(s) for the experienced decreasing water level of Rugezi wetland?/human activities  (unsustainable land use practices)': 'cons_water_human_activities_check',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What do you think is / are the reason(s) for the experienced decreasing water level of Rugezi wetland?/climate change': 'cons_water_climate_change_check',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What do you think is / are the reason(s) for the experienced decreasing water level of Rugezi wetland?/deforestation': 'cons_water_deforestation_check',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What do you think is / are the reason(s) for the experienced decreasing water level of Rugezi wetland?/increase of population size (demographic factors)': 'cons_water_pop_increase_check',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What do you think is / are the reason(s) for the experienced decreasing water level of Rugezi wetland?/soil erosion on surrounding valleys': 'cons_water_soil_erosion_check',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What do you think is / are the reason(s) for the experienced decreasing water level of Rugezi wetland?/geological reasons': 'cons_water_geological_check',
    'CONSEQUENCES OF ABSENSE / REDUCTION/What do you think is / are the reason(s) for the experienced decreasing water level of Rugezi wetland?/other': 'cons_water_other_check',
    'CONSEQUENCES OF ABSENSE / REDUCTION/specify:.1': 'cons_water_other_specify',

    # BENEFITS TO THE SOCIETY
    'BENEFITS TO THE SOCIETY/explain:': 'society_benefit_forest_explain',
    'BENEFITS TO THE SOCIETY/How do your neighbours and the society as a whole in this area benefit from the wetland?': 'society_benefit_wetland_list',
    'BENEFITS TO THE SOCIETY/How do your neighbours and the society as a whole in this area benefit from the wetland?/Sometimes we meet as a society in the "open spaces" provided by the wetland, so the wetland is so beneficial to the entire society': 'society_wetland_meet_open_space_check',
    'BENEFITS TO THE SOCIETY/How do your neighbours and the society as a whole in this area benefit from the wetland?/We have a lot of fish, water, etc... in the wetland and we take it as a privilege as a society because at other places they pay a lot of money to get what we get here almost for free of charge': 'society_wetland_privilege_check',
    'BENEFITS TO THE SOCIETY/How do your neighbours and the society as a whole in this area benefit from the wetland?/It makes our society to get a lot of visitors and connections since people from far away come here for research, tourism, etc...': 'society_wetland_visitors_check',
    'BENEFITS TO THE SOCIETY/How do your neighbours and the society as a whole in this area benefit from the wetland?/other': 'society_wetland_other_check',
    'BENEFITS TO THE SOCIETY/explain:.1': 'society_wetland_other_explain',
    'BENEFITS TO THE SOCIETY/Do you benefit from the Ntaruka and Mukungwa hydroelectric power plants?': 'society_benefit_hydro_plants_check',
    'BENEFITS TO THE SOCIETY/specify:': 'society_benefit_hydro_specify',

    # STATED / DECLARED INCOME
    'STATED / DECLARED INCOME/Earlier, you also mentioned "income generation" among benefits you get from the forest. Generally, how much (Rwandan Francs) in total do you get from the forest monthly?': 'stated_income_forest_monthly_RWF',
    'STATED / DECLARED INCOME/income_generated_forest_year': 'stated_income_forest_annual_RWF',
    'STATED / DECLARED INCOME/Earlier, you also mentioned "income generation" among benefits you get from the wetland. Generally, how much (Rwandan Francs) in total do you get from the wetland monthly?': 'stated_income_wetland_monthly_RWF',
    'STATED / DECLARED INCOME/income_generated_wetland_year': 'stated_income_wetland_annual_RWF',

    # WATER FOR DOMESTIC USES
    'WATER FOR DOMESTIC USES/What time do you take to access water from the wetland? Time in minutes:': 'water_domestic_access_time_min',
    'WATER FOR DOMESTIC USES/You fetch water from the wetland every:': 'water_domestic_frequency',
    'WATER FOR DOMESTIC USES/water_domestic_frequency_year_equivalency': 'water_domestic_freq_year_equiv',
    'WATER FOR DOMESTIC USES/unit for fetching/measuring water:': 'water_domestic_unit',
    'WATER FOR DOMESTIC USES/One ${water_domestic_unit} is equivalent to how many litres ?': 'water_domestic_unit_to_L',
    'WATER FOR DOMESTIC USES/Please estimate how many ${water_domestic_unit}s of water you fetch / use every ${water_domestic_frequency}': 'water_domestic_quantity',
    'WATER FOR DOMESTIC USES/If not fetched from the wetland, how much (RWF) does one jerrycan of water cost?': 'water_domestic_alt_cost_jerrycan_RWF',
    'WATER FOR DOMESTIC USES/How much costs (if any) do you incur to get the ${water_domestic_quantity} - ${water_domestic_unit}s of water that you get every ${water_domestic_frequency}?': 'water_domestic_incurred_cost_RWF',
    'WATER FOR DOMESTIC USES/Value of water in Rwandan Francs per year:': 'water_domestic_value_year_RWF',

    # MATS VALUE / PRACTICE
    'MATS/What is the use of the mats you make?': 'mats_use_list',
    'MATS/What is the use of the mats you make?/for our own use (e.g. at home: sleeping, etc...) and not for sale': 'mats_use_own_check',
    'MATS/What is the use of the mats you make?/for sale': 'mats_use_sale_check',
    'MATS/Ok, so, you know something about mats making practice!': 'mats_aware_note',
    'MATS/What materials are used to make mats called "ibirago"?': 'mats_materials_ibirago',
    'MATS/Apart from the *${mats_materials}*, is there any other materials you use for making any model/type of local local mats?': 'mats_materials_alt_check',
    'MATS/What is the name of the other material or other grass/weed/sedge used?': 'mats_materials_alt_name',
    'MATS/Do you use the  *${mats_materials_alternative}* for making mats which are different (type) from the mats model made from *${mats_materials}*?': 'mats_alt_materials_type_diff_check',
    'MATS/What other model of mats do you make from *${mats_materials_alternative}*?': 'mats_alt_model_list',
    'MATS/What other model of mats do you make from *${mats_materials_alternative}*?/sleeping mats (*ibirago*)': 'mats_alt_model_ibirago_check',
    'MATS/What other model of mats do you make from *${mats_materials_alternative}*?/imikeka': 'mats_alt_model_imikeka_check',
    'MATS/What other model of mats do you make from *${mats_materials_alternative}*?/rug (*imisambi*)': 'mats_alt_model_imisambi_check',
    'MATS/What other model of mats do you make from *${mats_materials_alternative}*?/"ibidasesa" (woven grass mat for dying things outside)': 'mats_alt_model_ibidasesa_check',
    'MATS/Where do the "_**${mats_materials}**_"  materials come from?': 'mats_materials_origin_list',
    'MATS/Where do the "_**${mats_materials}**_"  materials come from?/from the wetland': 'mats_materials_wetland_check',
    'MATS/Where do the "_**${mats_materials}**_"  materials come from?/not from the wetland': 'mats_materials_not_wetland_check',
    'MATS/Where do the "_**${mats_materials_alternative}**_"  materials come from?': 'mats_materials_alt_origin_list',
    'MATS/Where do the "_**${mats_materials\_alternative}**_"  materials come from?/from the wetland': 'mats_materials_alt_wetland_check',
    'MATS/Where do the "_**${mats_materials\_alternative}**_"  materials come from?/not from the wetland': 'mats_materials_alt_not_wetland_check',
    'MATS/Are there any mats (_already fabricated_ or "ready-made") FOR SALE which originate from somewhere else apart from being made here using the local materials that you have just mentioned?': 'mats_ready_made_for_sale_check',
    'MATS/Where do the mats originate from?': 'mats_origin_list',
    'MATS/Where do the mats originate from?/other provinces in Rwanda': 'mats_origin_provinces_check',
    'MATS/Where do the mats originate from?/Uganda': 'mats_origin_uganda_check',
    'MATS/Where do the mats originate from?/Burundi': 'mats_origin_burundi_check',
    'MATS/Where do the mats originate from?/Tanzania': 'mats_origin_tanzania_check',
    'MATS/Where do the mats originate from?/Congo (DRC)': 'mats_origin_congo_check',
    'MATS/Where do the mats originate from?/other place': 'mats_origin_other_check',
    'MATS/Please rate what you think is the proportion of the mats locally-made and those coming from ${mats_origin}': 'mats_proportion_local_imported',
    'MATS/The *${mats_materials}* are taken for making mats every:': 'mats_materials_frequency',
    'MATS/unit of measuring the *${mats_materials}*:': 'mats_materials_unit',
    'MATS/One ${unit_mats_materials} is equivalent to how many kilograms by estimate?': 'mats_materials_unit_to_kg',
    'MATS/How many ${unit_mats_materials}s of *${mats_materials}* are used to make mats every ${frequency_mats}?': 'mats_materials_quantity',
    'MATS/How many [sleeping] mats are made out of the ${quantity_mats_materials} - ${unit_mats_materials}s of *${mats_materials}* every ${frequency_mats}?': 'mats_quantity_made',
    'MATS/How much cost (RWF) do you incur until you fabricate the ${quantity_mats} mats every ${frequency_mats}?': 'mats_fabrication_cost_RWF',
    'MATS/Where is the market for mats located?': 'mats_market_location',
    'MATS/Do you think those making mats for selling get much money from the business?': 'mats_business_profitable_check',
    'MATS/please elaborate:': 'mats_business_profitable_elaborate',
    'MATS/How much do you estimate they make in 3 months?': 'mats_income_3_months_RWF',
    'MATS/Where do the "_**${mats_materials_alternative}**_"  materials come from?/from the wetland': 'mats_materials_alt_wetland_check',
    'MATS/Where do the "_**${mats_materials_alternative}**_"  materials come from?/not from the wetland': 'mats_materials_alt_not_wetland_check',

    # FOREST VALUE (WOOD, TIMBER, HONEY, MUSHROOMS)
    'VALUE: WOOD/Wood is taken from the forest (per concerned household) every:': 'value_wood_frequency',
    'VALUE: TIMBER/Timber is taken from the forest (per concerned household) every:': 'value_timber_frequency',
    'VALUE: TIMBER/One ${unit_timber} is equivalent to how many kilograms?': 'value_timber_unit_to_kg',
    'VALUE: TIMBER/How many ${unit_timber}s of timber do you get from the forest every ${frequency_timber}?': 'value_timber_quantity',
    'VALUE: TIMBER/Its market price in RWF per ${unit_timber} is:': 'value_timber_market_price_RWF',
    'VALUE: TIMBER/How much cost (RWF) do you incur in order to get the ${quantity_timber} ${unit_timber}s of timber every ${frequency_timber}?': 'value_timber_cost_RWF',
    'VALUE: HONEY/Ok, so, you know something about honey practice!': 'value_honey_aware_note',
    'VALUE: HONEY/Honey is made from the forest (per concerned household) every:': 'value_honey_frequency',
    'VALUE: HONEY/One ${unit_honey} is equivalent to how many litres?': 'value_honey_unit_to_L',
    'VALUE: HONEY/How many ${unit_honey}s of honey do you get from the forest every ${frequency_honey}?': 'value_honey_quantity',
    'VALUE: HONEY/Its market price in RWF per ${unit_honey} is:': 'value_honey_market_price_RWF',
    'VALUE: HONEY/How much cost (RWF) do you incur in order to make the ${quantity_honey} - ${unit_honey}s of honey every ${frequency_honey}?': 'value_honey_cost_RWF',
    'VALUE: MUSHROOMS/Ok, so, you know something about mushroom provision!': 'value_mushroom_aware_note',
    'VALUE: MUSHROOMS/Mushroom is obtained from the forest (per concerned household) every:': 'value_mushroom_frequency',
    'VALUE: MUSHROOMS/One ${unit_mushroom} is equivalent to how many kilograms?': 'value_mushroom_unit_to_kg',
    'VALUE: MUSHROOMS/How many ${unit_mushroom}s of mushrooms do you get from the forest every ${frequency_mushroom}?': 'value_mushroom_quantity',
    'VALUE: MUSHROOMS/Its market price in RWF per ${unit_mushroom} is:': 'value_mushroom_market_price_RWF',
    'VALUE: MUSHROOMS/How much cost (RWF) do you incur in order to get the ${quantity_mushroom} ${unit_mushroom}s of mushroom every ${frequency_mushroom}?': 'value_mushroom_cost_RWF',
    'VALUE: MUSHROOMS/value_mushroom': 'value_mushroom_annual_RWF',

    # WETLAND VALUE (FISH)
    'VALUE: FISH/Ok, so, you know something about fishery in the wetland!': 'value_fish_aware_note',
    'VALUE: FISH/Fresh fish is obtained from the wetland (per concerned household) every:': 'value_fish_frequency',
    'VALUE: FISH/you measure the fish in:': 'value_fish_unit',
    'VALUE: FISH/One ${unit_fish} of fish is equivalent to how many kilograms (kg)?': 'value_fish_unit_to_kg',
    'VALUE: FISH/How many ${unit_fish}s of fish do you get every ${frequency_fish} from the wetland?': 'value_fish_quantity',
    'VALUE: FISH/You get the ${quantity_fish} fish ${unit_fish} every ${frequency_fish}. As you know, the number of ${frequency_fish}s in a year is:': 'value_fish_freq_year_note',
    'VALUE: FISH/So, every year, the number of kilograms of fish you get from the wetland is:': 'value_fish_annual_kg_note',
    'VALUE: FISH/Its market price in RWF per ${unit_fish} is:': 'value_fish_market_price_RWF',
    'VALUE: FISH/Do you incur any cost (RWF) in order to get the ${quantity_fish} - ${unit_fish} of fish every ${frequency_fish}?': 'value_fish_cost_check',
    'VALUE: FISH/So, the money (Rwandan Francs) so obtained from fishing per ${frequency_fish}:': 'value_fish_income_per_freq_RWF',

    # FISHING PRACTICE & FISH NAMES
    'FISHING PRACTICE & FISH NAMES/Do you know some types (genera or specific names) of fish found in the wetland?': 'fish_know_types_check',
    'FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?': 'fish_types_list',
    'FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/tilapia': 'fish_type_tilapia_check',
    'FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/Burera haplo (*Haplochromis erythromaculatus*)': 'fish_type_burera_haplo_check',
    "FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/Alluaud's haplo (*Astatoreochromis alluaudi*) - used to control snails/ molluscs": 'fish_type_alluaud_haplo_check',
    'FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/perch *(Lates niloticus)*': 'fish_type_perch_check',
    'FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/Marbled lungfish *(Protopterus aethiopicus)*': 'fish_type_lungfish_check',
    'FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/Elephant-snout fish *(Mormyrus kannume)*': 'fish_type_elephant_snout_check',
    'FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/Common carp *(Cyprinus carpio)*': 'fish_type_common_carp_check',
    'FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/Rwandese carp (*Varicorhinus ruandae* / *[Labeo]barbus ruandae* and *Varicorhinus platystoma* species)': 'fish_type_rwandese_carp_check',
    'FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/Longtail spinyeel (*Mastacembelus frenatus*)': 'fish_type_longtail_spinyeel_check',
    'FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/barb *(Barbus* genus)': 'fish_type_barb_check',
    'FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/Mudfish / common catfish / sharptooth catfish (*Clarias gariepinus*)': 'fish_type_mudfish_catfish_check',
    'FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/Smoothhead catfish *(Clarias liocephalus)*': 'fish_type_smoothhead_catfish_check',
    'FISHING PRACTICE & FISH NAMES/What types of fish are normally obtained from the wetland fishery?/other fish': 'fish_type_other_check',

    # LIVESTOCK KEEPING (Initial Selection)
    'LIVESTOCK KEEPING/Which animals do you keep (domesticate)?': 'livestock_kept_list',
    'LIVESTOCK KEEPING/Which animals do you keep (domesticate)?/cattle': 'livestock_kept_cattle_check',
    'LIVESTOCK KEEPING/Which animals do you keep (domesticate)?/goat': 'livestock_kept_goat_check',
    'LIVESTOCK KEEPING/Which animals do you keep (domesticate)?/sheep': 'livestock_kept_sheep_check',
    'LIVESTOCK KEEPING/Which animals do you keep (domesticate)?/rabbit': 'livestock_kept_rabbit_check',
    'LIVESTOCK KEEPING/Which animals do you keep (domesticate)?/dog': 'livestock_kept_dog_check'
}

df.rename(columns=column_rename_map_part2, inplace=True)
st.success("✅ All main column renaming complete")
st.markdown("---")

# -----------------------------------------------------------
# ⏱️ Dynamic Current Year
# -----------------------------------------------------------
current_year = datetime.now().year
st.info(f"📅 Calculations use current year: **{current_year}** (auto-updates each run)")

# -----------------------------------------------------------
# ⏱️ Process start/end times (Rwanda timezone)
# -----------------------------------------------------------
# (Your existing datetime conversion code – unchanged except using Africa/Kigali)

# -----------------------------------------------------------
# 🎂 Age & Years Lived (Dynamic with current_year)
# -----------------------------------------------------------
st.markdown("## 🎂 Age & Years Lived Calculations")

# Birth year → age
df['resp_age'] = current_year - df['resp_birth_year']

# Years in area (wetland/forest) – dynamic conversion
def convert_years(val):
    if pd.isna(val):
        return np.nan
    if val > 1900:  # Likely a start year
        return current_year - val
    if 0 <= val <= 150:  # Reasonable years of experience
        return val
    return np.nan

df['resp_years_area_wetland'] = df['resp_years_area_wetland'].apply(convert_years)
df['resp_years_area_forest'] = df['resp_years_area_forest'].apply(convert_years)

# Clean negative values
df['resp_years_area_wetland'] = df['resp_years_area_wetland'].clip(lower=0)
df['resp_years_area_forest'] = df['resp_years_area_forest'].clip(lower=0)

st.success("✅ Age & years lived calculated using current year")
st.dataframe(df[['resp_age', 'resp_years_area_wetland', 'resp_years_area_forest']].head(10))
st.markdown("---")

# -----------------------------------------------------------
# 🛰️ Automatic GPS Precision Fix (common typo: extra zeros)
# -----------------------------------------------------------
st.markdown("## 🛰️ GPS Precision Auto-Correction")
if df['gps_precision'].max() > 100:
    st.warning(f"High gps_precision detected (max: {df['gps_precision'].max():.1f}). Likely typos – dividing values >100 by 100.")
    df['gps_precision'] = df['gps_precision'].apply(lambda x: x / 100 if x > 100 else x)

if (df['gps_altitude'] == 0).any():
    st.warning("GPS altitude = 0 detected (likely error) – setting to NaN")
    df.loc[df['gps_altitude'] == 0, 'gps_altitude'] = np.nan

st.dataframe(df[['gps_precision', 'gps_altitude']].describe())
st.markdown("---")

# -----------------------------------------------------------
# 📊 Dynamic Outlier Detection (Key Columns)
# -----------------------------------------------------------
st.markdown("## 📊 Dynamic Outlier Overview (Key Columns)")
key_cols = ['gps_precision', 'gps_altitude', 'gps_latitude', 'gps_longitude',
            'resp_age', 'resp_years_area_wetland', 'resp_years_area_forest',
            'resp_serial_no']

st.dataframe(df[key_cols].describe())

fig, ax = plt.subplots(figsize=(12, 8))
sns.boxplot(data=df[key_cols], orient='h', ax=ax)
ax.set_title("Boxplots of Key Columns")
st.pyplot(fig)
st.markdown("---")

# -----------------------------------------------------------
# 🌾 Crop Sheet Processing 
# -----------------------------------------------------------
# -----------------------------------------------------------
# 🌾 Crop Sheet Processing (Dynamic from Uploaded File)
# -----------------------------------------------------------
st.markdown("## 🌾 Crop Sheet Processing")

crop_df = None
crop_loaded = False

if uploaded_file is not None:
    try:
        # Reset file pointer and load crop sheet
        uploaded_file.seek(0)
        crop_df = pd.read_excel(uploaded_file, sheet_name="crop", engine='openpyxl')
        crop_loaded = True
        st.success("✅ Crop sheet loaded successfully from uploaded file.")
        st.markdown("### 🧾 Crop Sheet Preview")
        st.dataframe(crop_df.head())
        st.write("**Initial shape:**", crop_df.shape)
    except ValueError:
        st.warning("⚠️ No sheet named 'crop' found in the uploaded file. Skipping all crop-related processing.")
    except Exception as e:
        st.warning(f"⚠️ Error loading crop sheet: {e}. Skipping crop processing.")

if crop_loaded and crop_df is not None:
    # --- Drop completely empty columns ---
    crop_df = crop_df.dropna(axis=1, how='all')
    st.write(f"**Shape after dropping empty columns:** {crop_df.shape}")
    
    # --- Column renaming map (traceability table shown for reference) ---
    st.markdown('''
    We’ll create clean, conventional names while keeping a reference dictionary to preserve the original column names for traceability
    
    | New Column Name              | Original Column Full Name                                                                 |
    |------------------------------|-------------------------------------------------------------------------------------------|
    | crop_type                    | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Which crop do you cultivate?    |
    | crop_cycle_duration          | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/From farm preparation...        |
    | crop_area_unit               | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/You measure farm in:            |
    | crop_area_hectare_equiv      | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/unit_farming_area_hectare_equivalency |
    | crop_area_size               | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Your farm is how many...        |
    | crop_yield_unit              | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Harvested ${crops_wetland}...   |
    | crop_yield_quantity          | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Normally, how many...           |
    | crop_harvest_frequency       | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/You harvest ${crops_wetland}... |
    | crop_unit_to_kg              | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/If measured on a balance...     |
    | crop_yield_kg_ha_year        | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/quantity_farming_kg_ha_year     |
    | crop_yield_calc              | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/This means that, per year...    |
    | crop_market_price            | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Market price: If you sell...    |
    | crop_fertilizer_use          | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Do you use fertilizer...        |
    | crop_cost_incurred           | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Do you incur any costs...       |
    | crop_expense_amount          | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/How much are those expenses?    |
    | crop_zero_cost_entry         | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Please write zero (0)...        |
    | crop_cost_rent_land          | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Cost of renting land:           |
    | crop_cost_manpower           | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Cost of manpower...             |
    | crop_labor_count             | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/How many persons...             |
    | crop_no_fertilizer_flag      | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/You even said you don't...      |
    | crop_cost_fertilizer         | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Cost of fertilizer: RWF         |
    | crop_cost_seeds              | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Cost of buying seeds: RWF       |
    | crop_cost_pesticides         | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Cost of fumigation...           |
    | crop_cost_other              | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Other costs in RWF:             |
    | crop_expenses_total          | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/expenses_farming                |
    | crop_expenses_total_rwf      | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Total expenses (RWF)...         |
    | crop_expenses_ref            | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/${expenses_farming}             |
    | crop_annual_profit           | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/So, the money you benefit...    |
    | crop_annual_profit_rwf       | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/So, the money you benefit... ${value_farming_rwf_year} RWF |
    | crop_value_per_ha            | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Value: money... per hectare...  |
    | crop_value_per_ha_rwf        | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Value: money... ${value_farming_rwf_ha_year} RWF |
    | crop_current_type            | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/crops_wetland_current           |
    | crop_list                    | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Which crop(s) do you cultivate? |
    | crop_area_equiv_calc         | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/unit_farming_area_hectare_equivalency_calculation |
    | crop_hectare_equiv_note      | crop grown by your household/VALUE OF CROPS YOU CULTIVATE/The equivalency of one hectare... |
    ''')
    
    column_map = {
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Which crop do you cultivate?": "crop_type",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/From farm preparation to harvesting the crops (yield of ${crops_wetland}), it takes you one:": "crop_cycle_duration",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/You measure farm in:": "crop_area_unit",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/unit_farming_area_hectare_equivalency": "crop_area_hectare_equiv",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Your farm is how many ${unit_farming_area}s?": "crop_area_size",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Harvested ${crops_wetland} crops is measured in:": "crop_yield_unit",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Normally, how many ${unit_farming}s of havested ${crops_wetland} do you get every ${frequency_farming} for all the ${size_land_farming} - ${unit_farming_area}s that you cultivate?": "crop_yield_quantity",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/You harvest ${crops_wetland} every ${frequency_fish}. As you know, the number of ${frequency_farming}s in a year is:": "crop_harvest_frequency",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/If measured on a balance, one ${unit_farming} of ${crops_wetland} is equal to how many kilograms?": "crop_unit_to_kg",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/quantity_farming_kg_ha_year": "crop_yield_kg_ha_year",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/This means that, per year, the ${crops_wetland} yied in kilograms per hectare (kg/ha/year) is: ${quantity_farming_kg_ha_year} kg/ha/year": "crop_yield_calc",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Market price: If you sell one ${unit_farming} of harvested ${crops_wetland}, you get how much money (RWF)?": "crop_market_price",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Do you use fertilizer for growing ${crops_wetland}?": "crop_fertilizer_use",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Do you incur any costs from farm preparation until you get the havested ${quantity_farming} - ${unit_farming}s of ${crops_wetland} every ${frequency_farming}?": "crop_cost_incurred",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/How much are those expenses?": "crop_expense_amount",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Please write zero (0) an an answer to each cost in the question below (expenses incurred)": "crop_zero_cost_entry",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Cost of renting land:": "crop_cost_rent_land",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Cost of manpower: RWF per person per ${frequency_farming}": "crop_cost_manpower",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/How many persons do you use for manpower for one ${frequency_farming}?": "crop_labor_count",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/You even said you don't use fertilizer. So, I put zero cost for fertilizer...": "crop_no_fertilizer_flag",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Cost of fertilizer: RWF": "crop_cost_fertilizer",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Cost of buying seeds: RWF": "crop_cost_seeds",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Cost of fumigation / pesticides: RWF": "crop_cost_pesticides",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Other costs in RWF:": "crop_cost_other",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/expenses_farming": "crop_expenses_total",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Total expenses (RWF) you incur every ${frequency_farming} for growing the ${crops_wetland} = **RWF **": "crop_expenses_total_rwf",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/${expenses_farming}": "crop_expenses_ref",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/So, the money you benefit every year from ${crops_wetland} is:": "crop_annual_profit",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/So, the money you benefit every year from ${crops_wetland} is: ${value_farming_rwf_year} RWF": "crop_annual_profit_rwf",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Value: money (Rwandan Francs) you benefit per hectare per year is:": "crop_value_per_ha",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Value: money (Rwandan Francs) you benefit per hectare per year is: ${value_farming_rwf_ha_year} RWF": "crop_value_per_ha_rwf",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/crops_wetland_current": "crop_current_type",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/Which crop(s) do you cultivate?": "crop_list",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/unit_farming_area_hectare_equivalency_calculation": "crop_area_equiv_calc",
        "crop grown by your household/VALUE OF CROPS YOU CULTIVATE/The equivalency of one hectare in ${unit_farming_area} is:": "crop_hectare_equiv_note"
    }
    
    # Safe rename: only apply to columns that actually exist
    existing_mappings = {old: new for old, new in column_map.items() if old in crop_df.columns}
    if existing_mappings:
        crop_df.rename(columns=existing_mappings, inplace=True)
        st.success(f"✅ Renamed {len(existing_mappings)} crop columns successfully.")
    else:
        st.warning("⚠️ None of the expected crop columns found – rename skipped.")
    
    st.dataframe(crop_df.head())
    st.write("**Shape after rename:**", crop_df.shape)
    
    # --- Continue with the rest of your crop processing ---
    # Find columns with no data
    st.markdown("## **1️⃣ Find Columns With No Data**")
    empty_cols = crop_df.columns[crop_df.isna().all()].tolist()
    empty_compare = pd.DataFrame({
        "Empty Columns": pd.Series(empty_cols)
    })
    st.dataframe(empty_compare)
    st.write(f"**Number of empty columns:** {len(empty_cols)}")
    
    # Drop empty columns
    st.markdown("## **2️⃣ Drop Columns With No Data**")
    crop_df = crop_df.dropna(axis=1, how='all')
    st.write("**Remaining columns:**", len(crop_df.columns))
    st.write(crop_df.columns.tolist())
    st.dataframe(crop_df.head())
    
    # Create submission date & time
    st.markdown("## 3️⃣ Create Submission Date & Time (UTC+2)")
    if '_submission__submission_time' in crop_df.columns:
        crop_df['_submission__submission_time'] = pd.to_datetime(
            crop_df['_submission__submission_time'], errors='coerce', utc=True
        ).dt.tz_convert('Africa/Kigali')
        crop_df['submission_date'] = crop_df['_submission__submission_time'].dt.date
        crop_df['submission_time'] = crop_df['_submission__submission_time'].dt.strftime('%H:%M:%S')
        crop_df.drop(columns=['_submission__submission_time'], inplace=True)
        st.dataframe(crop_df[['submission_date', 'submission_time']].head())
    else:
        st.warning("Column '_submission__submission_time' not found – skipping submission time processing.")
    
    # Standardize crop cycle duration
    st.markdown("## **4️⃣ Standardize Crop Cycle Duration**")
    if 'crop_cycle_duration' in crop_df.columns:
        crop_df['crop_cycle_duration_clean'] = crop_df['crop_cycle_duration'].str.lower().map({
            'week': 'Week', 'month': 'Month', 'quarter (3 months)': 'Quarter',
            'semester (6 months)': 'Semester', 'year': 'Year'
        })
    
    # Replace 'are' → 'acre'
    if 'crop_area_unit' in crop_df.columns:
        crop_df['crop_area_unit'] = crop_df['crop_area_unit'].replace('are', 'acre')
        st.write("Unique crop_area_unit values:", crop_df['crop_area_unit'].unique())
    
    st.dataframe(crop_df.head())
    
    # --- Identify few unique values, numeric summary, outliers, winsorization, etc. ---
    # (All your existing crop outlier code here – unchanged)
    
    # --- Merge with main df ---
    st.markdown("## 🔹 Merge Crop Data with Main DataFrame")
    cols_to_keep = [ ... ]  # your list
    if all(col in crop_df.columns for col in cols_to_keep):
        crop_df_subset = crop_df[cols_to_keep]
        # aggregation & merge as before
        merged_df = pd.merge(df, crop_df_unique, on='submission_time', how='left')
        st.success("✅ Crop data merged successfully")
    else:
        st.warning("Some expected columns missing – merge skipped.")
        merged_df = df.copy()
    
else:
    merged_df = df.copy()
    st.info("📌 No crop sheet – final dataframe is main data only.")

# -----------------------------------------------------------
# Final Download
# -----------------------------------------------------------
st.subheader("📥 Download Final Dataset")
@st.cache_data
def convert_df_to_csv(data):
    return data.to_csv(index=False).encode('utf-8')

csv = convert_df_to_csv(merged_df)
st.download_button(
    label="Download cleaned & merged data as CSV",
    data=csv,
    file_name=f'rwanda_ecosystem_cleaned_{datetime.now().year}.csv',
    mime='text/csv'
)
