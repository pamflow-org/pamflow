"""
Tkinter GUI for pamflow
Facilitates setting files and parameters:
    - audio root directory: allows to open system explorer to find the location of root audio files and updates the first line of configuration file ../conf/local/parameters.yml with audio_root_directory: <path>
    - field_deployments_sheet.xlsx: checks if file is at "../data/input/field_deployments/field_deployments_sheet.xlsx". If not, requests to upload the file.

And allows to easily compute:
    - kedro run --pipeline data_preparation     | button Prepare Data
    - kedro run --pipeline quality_control      | button Quality Control
    - kedro run --pipeline species_detection    | button Species Detection

"""
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import os
import yaml
import subprocess
import shutil
import sys

def resource_path(relative_path):
    # Helper for OS-independent paths (PyInstaller compatibility)
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.normpath(os.path.join(base_path, relative_path))

# Paths for configuration and input files
PARAMS_PATH = resource_path(os.path.join("..", "conf", "local", "parameters.yml"))
FIELD_DEPLOYMENTS_PATH = resource_path(os.path.join("..", "data", "input", "field_deployments", "field_deployments_sheet.xlsx"))
TARGET_SPECIES_PATH = resource_path(os.path.join("..", "data", "input", "target_species", "target_species.csv"))
CONF_BASE_DIR = resource_path(os.path.join("..", "conf", "base", "parameters"))
OUTPUT_DIR = resource_path(os.path.join("..", "data", "output"))

class PamflowGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("pamflow minimal GUI")
        self.geometry("520x500")
        self.configure(bg="#181818")  # Dark background
        self.status_labels = {}       # Store status indicators for each action
        self.create_widgets()         # Build GUI elements
        self.check_field_deployments(initial=True)  # Check field deployments file on startup
        self.check_target_species_file(initial=True)  # Check field deployments file on startup
        
        # --- Style configuration (do this once here) ---
        style = ttk.Style(self)
        style.theme_use("clam")  # more customizable than "aqua"

        style.configure(
            "Dark.TButton",
            background="#4C4C4C",
            foreground="#f7f7f7",
            relief="flat",
            borderwidth=0,
            focusthickness=0,
            padding=6
        )
        style.map(
            "Dark.TButton",
            background=[("active", "#5C5C5C")],
            foreground=[("disabled", "#aaaaaa")]
        )

    def create_widgets(self):
        # Define colors and styles
        label_fg = "#e8e7e7"
        frame_bg = "#181818"

        tk.Label(self, text="pamflow: simplified analisys for PAM", font=("Arial", 16), bg="#181818", fg=label_fg).pack(pady=20)

        # ---- Section Configuration  ---- #
        tk.Label(self, text="-- Set Configuration --", font=("Arial", 14), bg="#181818", fg=label_fg).pack(pady=10)

        frame = tk.Frame(self, bg="#181818")
        frame.pack(pady=5)

        # Button: Set Audio Root Directory
        btn_audio = ttk.Button(
            frame, text="Set Audio Root Directory", command=self.set_audio_root, width=28, style="Dark.TButton"
        )
        btn_audio.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.status_labels["audio_root"] = tk.Label(frame, text="", bg=frame_bg, fg=label_fg, font=("Arial", 14))
        self.status_labels["audio_root"].grid(row=0, column=1, padx=5)

        # Button: Upload Field Deployments Sheet
        btn_field = ttk.Button(
            frame, text="Upload Field Deployments Sheet", command=self.check_field_deployments, width=28, style="Dark.TButton"
        )
        btn_field.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.status_labels["field_deployments"] = tk.Label(frame, text="", bg=frame_bg, fg=label_fg, font=("Arial", 14))
        self.status_labels["field_deployments"].grid(row=1, column=1, padx=5)

        # Button: Upload target species file
        btn_spfile = ttk.Button(
            frame, text="Upload Target Species File", command=self.check_target_species_file, width=28, style="Dark.TButton"
        )
        btn_spfile.grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.status_labels["target_species"] = tk.Label(frame, text="", bg=frame_bg, fg=label_fg, font=("Arial", 14))
        self.status_labels["target_species"].grid(row=2, column=1, padx=5)

        # Button: Open Configuration Directory
        btn_conf = ttk.Button(
            frame, text="Check Configuration", command=self.open_conf_base, width=28, style="Dark.TButton"
        )
        btn_conf.grid(row=3, column=0, padx=5, pady=2, sticky="w")
        
        
        # ---- Section Run Pipelines  ---- #
        tk.Label(self, text="-- Run Pipelines --", font=("Arial", 14), bg="#181818", fg=label_fg).pack(pady=10)

        pipe_frame = tk.Frame(self, bg="#181818")
        pipe_frame.pack(pady=5)

        # Button: Prepare Data pipeline
        btn_prepare = ttk.Button(
            pipe_frame, text="Prepare Data", command=lambda: self.run_kedro("data_preparation"), width=28, style="Dark.TButton"
        )
        btn_prepare.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.status_labels["data_preparation"] = tk.Label(
            pipe_frame, text="", bg="#181818", fg=label_fg, font=("Arial", 14)
        )
        self.status_labels["data_preparation"].grid(row=0, column=1, padx=5)

        # Button: Quality Control pipeline
        btn_quality = ttk.Button(
            pipe_frame, text="Quality Control", command=lambda: self.run_kedro("quality_control"), width=28, style="Dark.TButton"
        )
        btn_quality.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.status_labels["quality_control"] = tk.Label(
            pipe_frame, text="", bg="#181818", fg=label_fg, font=("Arial", 14)
        )
        self.status_labels["quality_control"].grid(row=1, column=1, padx=5)

        # Button: Species Detection pipeline
        btn_species = ttk.Button(
            pipe_frame, text="Species Detection", command=lambda: self.run_kedro("species_detection"), width=28, style="Dark.TButton"
        )
        btn_species.grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.status_labels["species_detection"] = tk.Label(
            pipe_frame, text="", bg="#181818", fg=label_fg, font=("Arial", 14)
        )
        self.status_labels["species_detection"].grid(row=2, column=1, padx=5)

        # Button: Open Output Directory
        btn_output = ttk.Button(
            pipe_frame, text="Check Results", command=self.open_pamflow_output, width=28, style="Dark.TButton"
        )
        btn_output.grid(row=3, column=0, padx=5, pady=2, sticky="w")


    def set_audio_root(self):
        # Select directory and update YAML config
        path = filedialog.askdirectory(title="Select Audio Root Directory")
        if path:
            try:
                with open(PARAMS_PATH, "r") as f:
                    params = yaml.safe_load(f)
                params["audio_root_directory"] = path
                with open(PARAMS_PATH, "w") as f:
                    yaml.dump(params, f)
                self.status_labels["audio_root"].config(text="✅")
            except Exception:
                self.status_labels["audio_root"].config(text="❌")

    def check_field_deployments(self, initial=False):
        # Check if field deployments file exists, prompt upload if missing
        if not os.path.exists(FIELD_DEPLOYMENTS_PATH):
            if not initial:
                file_path = filedialog.askopenfilename(
                    title="Select field_deployments_sheet.xlsx",
                    filetypes=[("Excel files", "*.xlsx")]
                )
                if file_path:
                    try:
                        os.makedirs(os.path.dirname(FIELD_DEPLOYMENTS_PATH), exist_ok=True)
                        shutil.copy(file_path, FIELD_DEPLOYMENTS_PATH)
                        self.status_labels["field_deployments"].config(text="✅")
                        return
                    except Exception:
                        self.status_labels["field_deployments"].config(text="❌")
                        return
            self.status_labels["field_deployments"].config(text="❌")
        else:
            self.status_labels["field_deployments"].config(text="✅")
    
    def check_target_species_file(self, initial=False):
        # Check if target species file exists, prompt upload if missing
        if not os.path.exists(TARGET_SPECIES_PATH):
            if not initial:
                file_path = filedialog.askopenfilename(
                    title="Select target_species.csv",
                    filetypes=[("CSV", "*.csv")]
                )
                if file_path:
                    try:
                        os.makedirs(os.path.dirname(TARGET_SPECIES_PATH), exist_ok=True)
                        shutil.copy(file_path, TARGET_SPECIES_PATH)
                        self.status_labels["target_species"].config(text="✅")
                        return
                    except Exception:
                        self.status_labels["target_species"].config(text="❌")
                        return
            self.status_labels["target_species"].config(text="❌")
        else:
            self.status_labels["target_species"].config(text="✅")

    def run_kedro(self, pipeline):
        # Run kedro pipeline and update status
        self.status_labels[pipeline].config(text="⏳")
        self.update_idletasks()
        try:
            subprocess.run(["kedro", "run", "--pipeline", pipeline], check=True)
            self.status_labels[pipeline].config(text="✅")
        except subprocess.CalledProcessError:
            self.status_labels[pipeline].config(text="❌")

    def open_conf_base(self):
        # Open configuration directory in system file explorer
        path = os.path.abspath(CONF_BASE_DIR)
        try:
            if sys.platform.startswith("darwin"):
                subprocess.Popen(["open", path])
            elif os.name == "nt":
                os.startfile(path)
            elif os.name == "posix":
                subprocess.Popen(["xdg-open", path])
        except Exception:
            pass

    def open_pamflow_output(self):
        # Open output directory
        path = os.path.abspath(OUTPUT_DIR)
        try:
            if sys.platform.startswith("darwin"):
                subprocess.Popen(["open", path])
            elif os.name == "nt":
                os.startfile(path)
            elif os.name == "posix":
                subprocess.Popen(["xdg-open", path])
        except Exception:
            pass

if __name__ == "__main__":
    # Start the GUI application
    app = PamflowGUI()
    app.mainloop()