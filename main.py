import streamlit as st
import pandas as pd
import os
import shutil
import glob
import re
import zipfile
from io import BytesIO


# Funktion zum Lesen der CSV-Datei mit ISO-8859-1 Kodierung
def read_csv_with_encoding(file_path):
    try:
        return pd.read_csv(file_path, sep=';', encoding='ISO-8859-1', dtype=str)
    except Exception as e:
        st.error(f"Fehler beim Lesen der Datei {file_path}: {e}")
        return None


# Funktion zum Kopieren der Ordnerstruktur und der Dateien
def copy_structure(src_path):
    transformed_path = os.path.join(src_path, 'Transformed')
    if not os.path.exists(transformed_path):
        os.mkdir(transformed_path)

    for folder_name in os.listdir(src_path):
        folder_path = os.path.join(src_path, folder_name)
        if os.path.isdir(folder_path) and folder_name != 'Transformed':
            dest_path = os.path.join(transformed_path, folder_name)
            if not os.path.exists(dest_path):
                shutil.copytree(folder_path, dest_path)
    st.success("Ordnerstruktur wurde in 'Transformed' kopiert.")
    return transformed_path


# Funktion, um Koordinaten von DMS in Dezimalgrad umzuwandeln
def dms_to_dd(dms):
    if pd.isna(dms) or not isinstance(dms, str):
        return dms
    try:
        parts = re.match(r"(\d+)°(\d+)'(\d+\.\d+)\"", dms)
        if parts:
            degrees, minutes, seconds = map(float, parts.groups())
            return round(degrees + minutes / 60 + seconds / 3600, 5)
    except Exception as e:
        return None  # Rückgabe von None bei Fehler

# Funktion zum Lesen der CSV-Datei mit ISO-8859-1 Kodierung und Semikolon als Trennzeichen
def read_csv_with_encoding(file_path):
    try:
        return pd.read_csv(file_path, sep=';', encoding='ISO-8859-1', dtype=str)
    except Exception as e:
        st.error(f"Fehler beim Lesen der Datei {file_path}: {e}")
        return None
    

def process_csv_files(transformed_path):
    for root, dirs, files in os.walk(transformed_path):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                df = read_csv_with_encoding(file_path)
                if df is not None:
                    try:
                        # Identifiziere die relevanten Spalten für die Umwandlung
                        col_11 = "Res._ _ _ _11"
                        col_12 = "Res._ _ _ _12"

                        if col_11 in df.columns and col_12 in df.columns:
                            df[col_11] = df[col_11].apply(dms_to_dd)
                            df[col_12] = df[col_12].apply(dms_to_dd)
                            df.to_csv(file_path, index=False, sep=';', encoding='ISO-8859-1')
                            st.success(f'Datei "{file}" im Ordner "{root}" wurde erfolgreich transformiert.')
                        else:
                            st.error(f"Die erforderlichen Spalten sind in der Datei {file} im Ordner {root} nicht vorhanden.")
                    except Exception as e:
                        st.error(f"Fehler beim Verarbeiten der Datei {file} im Ordner {root}: {e}")
                else:
                    st.error(f"Die Datei {file} im Ordner {root} konnte nicht gelesen werden.")


def unzip_files(zip_file, extract_to):
    """Entpackt die ZIP-Datei in den angegebenen Ordner."""
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def zip_files(directory, zip_name):
    """Erstellt eine ZIP-Datei aus dem angegebenen Ordner."""
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory):
            for file in files:
                zipf.write(os.path.join(root, file), 
                           os.path.relpath(os.path.join(root, file), 
                                           os.path.join(directory, '..')))



def main():
    st.title('CSV Koordinatentransformations-Tool')

    uploaded_file = st.file_uploader("Wählen Sie eine ZIP-Datei aus", type="zip")
    if uploaded_file is not None:
        # Temporäres Verzeichnis für das Entpacken
        extract_to = "temp_dir"
        os.makedirs(extract_to, exist_ok=True)
        
        # Entpacken der ZIP-Datei
        unzip_files(uploaded_file, extract_to)
        
        # Verarbeiten der CSV-Dateien
        process_csv_files(extract_to)
        
        # ZIP-Datei mit transformierten Daten erstellen
        zip_name = "transformed_data.zip"
        zip_files(extract_to, zip_name)
        
        # ZIP-Datei zum Download anbieten
        with open(zip_name, "rb") as f:
            bytes = f.read()
            b_io = BytesIO(bytes)
            st.download_button(label="Download ZIP mit transformierten Daten",
                               data=b_io,
                               file_name=zip_name,
                               mime="application/zip")
        
        # Aufräumen: Temporäres Verzeichnis und ZIP-Datei löschen
        shutil.rmtree(extract_to)
        os.remove(zip_name)

if __name__ == "__main__":
    main()
