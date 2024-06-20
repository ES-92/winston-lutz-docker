from flask import Flask, request, jsonify, send_from_directory
import os
import json
from pylinac import WinstonLutz
import matplotlib.pyplot as plt

# Verwenden eines nicht-interaktiven Matplotlib-Backends
plt.switch_backend('Agg')

app = Flask(__name__)

CONFIG_PATH = 'config.json'
UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def load_config():
    if not os.path.exists(CONFIG_PATH):
        default_config = {
            "max_2d_cax_to_bb_mm": 1.8,
            "median_2d_cax_to_bb_mm": 1.5,
            "mean_2d_cax_to_bb_mm": 1.5,
            "max_2d_cax_to_epid_mm": 2.0,
            "median_2d_cax_to_epid_mm": 2.0,
            "mean_2d_cax_to_epid_mm": 2.0,
            "gantry_3d_iso_diameter_mm": 1.5,
            "max_gantry_rms_deviation_mm": 2.0,
            "max_epid_rms_deviation_mm": 2.0,
            "gantry_coll_3d_iso_diameter_mm": 2.0,
            "coll_2d_iso_diameter_mm": 2.0,
            "max_coll_rms_deviation_mm": 2.0,
            "couch_2d_iso_diameter_mm": 2.0,
            "max_couch_rms_deviation_mm": 2.0,
            "bb_size_mm": 5.0,
            "output_path": UPLOAD_FOLDER  
        }
        with open(CONFIG_PATH, 'w') as f:
            json.dump(default_config, f, indent=4)
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

def cleanup_files(folder):
    print(f"Cleaning up files in folder: {folder}")
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        print(f"Attempting to delete file: {file_path}")
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            else:
                print(f"Skipped non-file: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

@app.route('/api/config', methods=['GET'])
def get_config():
    config = load_config()
    return jsonify(config)

@app.route('/api/config', methods=['POST'])
def update_config():
    config = request.json
    save_config(config)
    return jsonify({'status': 'success'})

@app.route('/api/analyze', methods=['POST'])
def analyze_images():
    data = request.json
    dicom_files = data.get('dicom_files', [])
    config = load_config()
    bb_size = config.get('bb_size_mm', 5)
    try:
        wl = WinstonLutz(dicom_files, use_filenames=True)
        wl.analyze(bb_size_mm=bb_size)
        results = wl.results_data(as_dict=True)
        plt.close('all')  # Schließen Sie alle geöffneten Figuren
        return jsonify(results)
    except Exception as e:
        plt.close('all')  # Schließen Sie alle geöffneten Figuren bei einem Fehler
        return jsonify({'error': str(e)}), 500

@app.route('/api/view_isocenter', methods=['POST'])
def view_isocenter():
    data = request.json
    dicom_files = data.get('dicom_files', [])
    config = load_config()
    bb_size = config.get('bb_size_mm', 5)
    try:
        wl = WinstonLutz(dicom_files, use_filenames=True)
        wl.analyze(bb_size_mm=bb_size)
        plot_path = os.path.join(UPLOAD_FOLDER, "isocenter.png")

        plt.figure()
        wl.plot_location()
        plt.savefig(plot_path)
        plt.close('all')  # Schließen Sie alle geöffneten Figuren

        return jsonify({"status": "success", "plot_path": plot_path})
    except Exception as e:
        plt.close('all')  # Schließen Sie alle geöffneten Figuren bei einem Fehler
        return jsonify({'error': str(e)}), 500

@app.route('/api/view_plane_image', methods=['POST'])
def view_plane_image():
    data = request.json
    dicom_files = data.get('dicom_files', [])
    config = load_config()
    bb_size = config.get('bb_size_mm', 5)
    try:
        wl = WinstonLutz(dicom_files, use_filenames=True)
        wl.analyze(bb_size_mm=bb_size)
        plot_path = os.path.join(UPLOAD_FOLDER, "plane_image.png")

        plt.figure()
        wl.plot_images()
        plt.savefig(plot_path)
        plt.close('all')  # Schließen Sie alle geöffneten Figuren
        
        return jsonify({"status": "success", "plot_path": plot_path})
    except Exception as e:
        plt.close('all')  # Schließen Sie alle geöffneten Figuren bei einem Fehler
        return jsonify({'error': str(e)}), 500

@app.route('/api/report', methods=['POST'])
def generate_report():
    data = request.json
    dicom_files = data.get('dicom_files', [])
    config = load_config()
    output_folder = config.get('output_path', UPLOAD_FOLDER)
    bb_size = config.get('bb_size_mm', 5)
    try:
        wl = WinstonLutz(dicom_files, use_filenames=True)
        wl.analyze(bb_size_mm=bb_size)
        report_path = os.path.join(output_folder, 'winston_lutz_report.pdf')
        wl.publish_pdf(report_path)
        plt.close('all')  # Schließen Sie alle geöffneten Figuren
        
        return send_from_directory(output_folder, 'winston_lutz_report.pdf', as_attachment=True)
    except Exception as e:
        plt.close('all')  # Schließen Sie alle geöffneten Figuren bei einem Fehler
        return jsonify({'error': str(e)}), 500

@app.route('/api/shift_instructions', methods=['POST'])
def shift_instructions():
    data = request.json
    dicom_files = data.get('dicom_files', [])
    config = load_config()
    bb_size = config.get('bb_size_mm', 5)
    try:
        wl = WinstonLutz(dicom_files, use_filenames=True)
        wl.analyze(bb_size_mm=bb_size)
        instructions = wl.bb_shift_instructions()
        plt.close('all')  # Schließen Sie alle geöffneten Figuren
            
        return jsonify({"instructions": instructions})
    except Exception as e:
        plt.close('all')  # Schließen Sie alle geöffneten Figuren bei einem Fehler
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    response = send_from_directory(UPLOAD_FOLDER, filename)
    return response

@app.route('/api/clean_session', methods=['DELETE'])
def clean_session():
    cleanup_files(UPLOAD_FOLDER)
    return jsonify({'status': 'session cleaned'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
