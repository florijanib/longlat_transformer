import streamlit as st
import pandas as pd
import os
import shutil
import glob
import re


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


# Streamlit App Definition
def main():
    st.title('CSV Koordinatentransformations-Tool')

    # Eingabefeld für den Quellpfad
    src_path = st.text_input('Geben Sie den Quellpfad ein (z.B. "E:/MaisNet_import Files"):')

    # Button zum Starten der Transformation
    if st.button('Starte Transformation'):
        if src_path:  # Nur fortfahren, wenn ein Pfad eingegeben wurde
            transformed_path = copy_structure(src_path)
            process_csv_files(transformed_path)  # Hier wird 'st' nicht mehr als Argument übergeben
        else:
            st.error("Bitte geben Sie einen gültigen Quellpfad ein.")

if __name__ == "__main__":
    main()
