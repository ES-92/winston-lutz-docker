import streamlit as st
import requests
import json
import os
import pandas as pd
import time

# Set the page layout to wide
st.set_page_config(page_title="WinstonLutz", page_icon="favicon.ico", layout="wide", menu_items={
    
    'About': '''
    Winston-Lutz Test App zur Analyse und Darstellung von WL DICOM-Dateien.
    Author von Erik Schröder.
    '''
})

API_URL = "http://flask:5000/api"

# Define the allowed configuration parameters and their German mappings
CONFIG_PARAMS = {
    "bb_size_mm": "Ballbearing Größe [mm]",
    "coll_2d_iso_diameter_mm": "Collimator 2D Iso Durchmesser [mm]",
    "couch_2d_iso_diameter_mm": "Couch 2D Iso Durchmesser [mm]",
    "gantry_3d_iso_diameter_mm": "Gantry 3D Iso Durchmesser [mm]",
    "gantry_coll_3d_iso_diameter_mm": "Gantry-Collimator 3D Iso Durchmesser [mm]",
    "max_2d_cax_to_bb_mm": "Max 2D CAX zu BB [mm]",
    "max_2d_cax_to_epid_mm": "Max 2D CAX zu EPID [mm]",
    "max_coll_rms_deviation_mm": "Max Collimator RMS Abweichung [mm]",
    "max_couch_rms_deviation_mm": "Max Couch RMS Abweichung [mm]",
    "max_epid_rms_deviation_mm": "Max EPID RMS Abweichung [mm]",
    "max_gantry_rms_deviation_mm": "Max Gantry RMS Abweichung [mm]",
    "mean_2d_cax_to_bb_mm": "Mean 2D CAX zu BB [mm]",
    "mean_2d_cax_to_epid_mm": "Mean 2D CAX zu EPID [mm]",
    "median_2d_cax_to_bb_mm": "Median 2D CAX zu BB [mm]",
    "median_2d_cax_to_epid_mm": "Median 2D CAX zu EPID [mm]",
    "output_path": "PDF-Bericht Speicherort:"
}

def load_config():
    response = requests.get(f"{API_URL}/config")
    return response.json()

def map_results_to_dataframe(results, tolerances):
    data = {
        "Parameter": ["Datum", "Gantry 3D Iso [mm]", "Gantry-Coll 3D Iso [mm]", "Max 2D BB->CAX [mm]"],
        "Wert": [
            str(results.get("date_of_analysis")),
            str(results.get("gantry_3d_iso_diameter_mm")),
            str(results.get("gantry_coll_3d_iso_diameter_mm")),
            str(results.get("max_2d_cax_to_bb_mm"))
        ],
        "Toleranz": [
            None,
            str(tolerances.get("gantry_3d_iso_diameter_mm")),
            str(tolerances.get("gantry_coll_3d_iso_diameter_mm")),
            str(tolerances.get("max_2d_cax_to_bb_mm"))
        ]
    }
    
    status = []
    for value, tol in zip(data["Wert"], data["Toleranz"]):
        if tol is not None and isinstance(value, str) and value.replace('.', '', 1).isdigit():
            status.append("Pass" if float(value) <= float(tol) else "Fail")
        else:
            status.append("")
    data["Status"] = status
    
    return pd.DataFrame(data)

st.title("Winston-Lutz Test")

st.write(st.__version__)
# Main content for upload and displaying results
st.header("Upload")
uploaded_files = st.file_uploader("Laden Sie DICOM-Dateien hoch", accept_multiple_files=True)
dicom_files = []
if uploaded_files:
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    for file in uploaded_files:
        file_path = os.path.join("uploads", file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        dicom_files.append(file_path)

st.header("Ergebnisse")

# Sidebar for configuration button
with st.sidebar:
    st.header("Aktionen")
    if st.button("Quick Check") and dicom_files:
        with st.spinner('Analyse läuft...'):
            response = requests.post(f"{API_URL}/analyze", json={"dicom_files": dicom_files})
            if response.status_code == 200:
                st.session_state.analysis_results = response.json()
                st.session_state.show_analysis_results = True
                st.session_state.show_shift_instructions = False
                st.session_state.show_2d_image = False
                st.session_state.show_3d_image = False
            else:
                st.error(response.json().get('error', 'Unknown error'))

    if st.button("Verschiebung") and dicom_files:
        with st.spinner('Verschiebeanweisungen werden abgerufen...'):
            response = requests.post(f"{API_URL}/shift_instructions", json={"dicom_files": dicom_files})
            if response.status_code == 200:
                st.session_state.shift_instructions = response.json().get('instructions')
                st.session_state.show_shift_instructions = True
                st.session_state.show_analysis_results = False
                st.session_state.show_2d_image = False
                st.session_state.show_3d_image = False
            else:
                st.error(response.json().get('error', 'Unknown error'))

    if st.button("2D Aufnahmen") and dicom_files:
        with st.spinner('2D-Ebenenbild wird erstellt...'):
            response = requests.post(f"{API_URL}/view_plane_image", json={"dicom_files": dicom_files})
            if response.status_code == 200:
                st.session_state.plot_path_2d = response.json().get("plot_path")
                st.session_state.show_2d_image = True
                st.session_state.show_analysis_results = False
                st.session_state.show_shift_instructions = False
                st.session_state.show_3d_image = False
            else:
                st.error(response.json().get('error', 'Unknown error'))

    if st.button("3D Iso Visualisierung") and dicom_files:
        with st.spinner('3D-Isocenter wird erstellt...'):
            response = requests.post(f"{API_URL}/view_isocenter", json={"dicom_files": dicom_files})
            if response.status_code == 200:
                st.session_state.plot_path_3d = response.json().get("plot_path")
                st.session_state.show_3d_image = True
                st.session_state.show_analysis_results = False
                st.session_state.show_shift_instructions = False
                st.session_state.show_2d_image = False
            else:
                st.error(response.json().get('error', 'Unknown error'))

    if st.button("PDF-Bericht erstellen") and dicom_files:
        with st.spinner('PDF-Bericht wird erstellt...'):
            response = requests.post(f"{API_URL}/report", json={"dicom_files": dicom_files})
            if response.status_code == 200:
                st.session_state.pdf_report = response.content
                st.session_state.show_3d_image = False
                st.session_state.show_analysis_results = False
                st.session_state.show_shift_instructions = False
                st.session_state.show_2d_image = False
                st.success("PDF-Bericht erstellt")
            else:
                st.error(response.json().get('error', 'Unknown error'))
        
    if st.button("Clean Session"):
        with st.spinner('Session wird gereinigt...'):
            try:
                response = requests.delete(f"{API_URL}/clean_session")
                if response.status_code == 200:
                    st.session_state.clear()
                    st.success("Session cleaned")
                else:
                    st.error(f"Error cleaning session: {response.status_code}")
            except Exception as e:
                st.error(f"Exception cleaning session: {e}")
    
  
    st.header("Konfiguration")
    if st.button("Konfiguration bearbeiten"):
        st.session_state.show_config = True
    

# Display results and images
if "show_analysis_results" in st.session_state and st.session_state.show_analysis_results:
    config = load_config()
    results_df = map_results_to_dataframe(st.session_state.analysis_results, config)
    st.write(results_df)

if "show_shift_instructions" in st.session_state and st.session_state.show_shift_instructions:
    st.text(st.session_state.shift_instructions)

if "show_2d_image" in st.session_state and st.session_state.show_2d_image:
    st.image(f"{API_URL.replace('/api', '')}app/uploads/{os.path.basename(st.session_state.plot_path_2d)}")

if "show_3d_image" in st.session_state and st.session_state.show_3d_image:
    st.image(f"{API_URL.replace('/api', '')}app/uploads/{os.path.basename(st.session_state.plot_path_3d)}")

if "pdf_report" in st.session_state:
    st.download_button("Download Bericht", data=st.session_state.pdf_report, file_name="winston_lutz_report.pdf")

# Display configuration in a modal
if "show_config" in st.session_state and st.session_state.show_config:
    st.header("Konfiguration bearbeiten")
    try:
        config = load_config()
        
        # Map the keys to their German labels
        config_df = pd.DataFrame(list(config.items()), columns=["Parameter", "Wert"])
        config_df["Parameter"] = config_df["Parameter"].map(CONFIG_PARAMS)
        config_df["Wert"] = config_df["Wert"].astype(str)
        
        edited_config_df = st.data_editor(config_df, hide_index=True, num_rows="16", use_container_width=True)
        
        if st.button("Konfiguration speichern"):
            new_config = {key: row["Wert"] for key, row in zip(config.keys(), edited_config_df.to_dict('records'))}
            
            for key, value in new_config.items():
                try:
                    if '.' in value or 'e' in value.lower():
                        new_config[key] = float(value)
                    else:
                        new_config[key] = int(value)
                except ValueError:
                    pass
            
            response = requests.post(f"{API_URL}/config", json=new_config)
            st.success("Konfiguration gespeichert")
            st.session_state.show_config = False
    except requests.ConnectionError:
        st.error("Konnte keine Verbindung zum Flask-Backend herstellen.")
