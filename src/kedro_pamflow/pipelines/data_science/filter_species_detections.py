import os
import pandas as pd
import glob
import argparse
from utils import merge_annot_files

def process_detections(path_detections, path_save, species_th_path):
    """
    Processes detection files and filters based on species-specific confidence thresholds.

    Parameters:
    path_detections (str): Path to the directory containing detection CSV files.
    path_save (str): Path to the directory where filtered CSV files will be saved.
    species_th_path (str): Path to the CSV file containing species-specific confidence thresholds.
    """
    print("Loading species thresholds...")
    # Load species thresholds
    species_th = pd.read_csv(species_th_path)
    species_th = species_th.set_index('species')['threshold'].to_dict()
    print("Species thresholds loaded.")

    print("Loading detection files...")
    # Load and merge detection files
    flist = glob.glob(os.path.join(path_detections, '**', '*.csv'), recursive=True)
    if not flist:
        print(f"No CSV files found in {path_detections}.")
        return
    df = merge_annot_files(flist, rtype='csv')
    print(f"Loaded {len(flist)} detection files.")

    # Ensure output directory exists
    os.makedirs(path_save, exist_ok=True)

    print("Processing detections based on species-specific thresholds...")
    # Filter detections based on species-specific thresholds and save to output directory
    for species, th in species_th.items():
        print(f"Filtering detections for species: {species} with threshold: {th}")
        df_sel = df.loc[(df['Scientific name'] == species) & (df['Confidence'] >= th)]
        if df_sel.empty:
            print(f"No detections found for species {species} meeting the threshold {th}.")
        else:
            output_file = os.path.join(path_save, f'{species}_{th}.csv')
            df_sel.to_csv(output_file, index=False)
            print(f"Saved filtered detections for {species} to {output_file}")

    print("Processing complete.")


def main():
    parser = argparse.ArgumentParser(description='Process detection files based on species-specific confidence thresholds.')
    parser.add_argument('-i', '--input', type=str, help='Path to the directory containing detection CSV files.')
    parser.add_argument('-o', '--output', type=str, help='Path to the directory where filtered CSV files will be saved.')
    parser.add_argument('-th','--threshold', type=str, help='Path to the CSV file containing species-specific confidence thresholds.')

    args = parser.parse_args()

    process_detections(args.input, args.output, args.threshold)

if __name__ == '__main__':
    main()

