from datetime import datetime
import os
import shutil  # For moving files
import subprocess
from tqdm import tqdm  # Progress bar for better UX

# Define the parameters for each coach
coaches = [
    {"coach_name": "Coach A", "number": 5},
    # {"coach_name": "Coach B", "number": 10},
    # {"coach_name": "Coach C", "number": 15},
]

# Base output directory for organized coach reports
base_output_dir = "Coach_Reports"

# Quarto's specified output directory (from _quarto.yml)
quarto_output_dir = os.path.abspath("outputs")  # Ensure it matches your _quarto.yml configuration

# Loop through each coach and generate a report with a gradual progress bar
with tqdm(total=len(coaches) * 5, desc="Generating Reports", unit="step") as pbar:  # 5 steps per report
    for coach in coaches:
        # Extract parameters
        coach_name = coach["coach_name"]
        number = coach["number"]

        # Step 1: Start rendering (increment progress)
        pbar.set_postfix({"Current Coach": coach_name})
        pbar.update(1)

        # Temporary filename (just the name, no path)
        temp_output_filename = f"report_{coach_name.replace(' ', '_')}_{datetime.now():%Y-%m-%d}.pdf"
        temp_output_path = os.path.join(quarto_output_dir, temp_output_filename)  # Full path in Quarto's output directory

        # Render the file using Quarto
        result = subprocess.run([
            "quarto", "render", "parameterized-report.qmd",
            "-P", f"coach_name:'{coach_name}'",
            "-P", f"number:{number}",
            "--output", temp_output_filename  # Filename only
        ], capture_output=True, text=True)

        # Step 2: Rendering in progress
        pbar.update(1)

        # Check for Quarto render errors
        if result.returncode != 0:
            print(f"Error while rendering report for {coach_name}:")
            print(result.stderr)
            pbar.update(3)  # Skip other steps for this report
            continue  # Skip to the next coach

        # Verify if the temporary output file was created in the Quarto output directory
        if not os.path.exists(temp_output_path):
            print(f"Error: Temporary file not found for {coach_name}: {temp_output_path}")
            pbar.update(3)  # Skip other steps for this report
            continue

        # Step 3: Creating folder for the coach
        coach_folder = os.path.join(base_output_dir, coach_name.replace(" ", "_"))
        os.makedirs(coach_folder, exist_ok=True)  # Ensure the folder exists
        pbar.update(1)

        # Step 4: Moving the file to the coach's folder
        final_output_path = os.path.join(coach_folder, temp_output_filename)
        try:
            shutil.move(temp_output_path, final_output_path)
            pbar.update(1)
        except Exception as e:
            print(f"Error moving file for {coach_name}: {e}")
            pbar.update(1)  # Still increment progress

        # Step 5: Finalizing
        pbar.update(1)
        print(f" Successfully generated report for {coach_name}: {final_output_path}")
