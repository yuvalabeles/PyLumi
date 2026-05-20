import subprocess
import sys


REQUIRED_PACKAGES = {
    "pandas": "pandas",
    "numpy": "numpy",
    "matplotlib": "matplotlib",
    "openpyxl": "openpyxl",
    "xlsxwriter": "xlsxwriter",
    "scipy": "scipy",
    "statsmodels": "statsmodels",
}


def ensure_requirements():
    print("\nChecking required packages...\n")

    for import_name, pip_name in REQUIRED_PACKAGES.items():

        try:
            __import__(import_name)

        except ImportError:
            print(f"Installing missing package: {pip_name}")

            subprocess.check_call([
                sys.executable,
                "-m",
                "pip",
                "install",
                pip_name
            ])

    print("\nAll required packages are installed.\n")


ensure_requirements()


from lumi_analysis.core.pipeline import run_lumi_pipeline
from scripts.load_settings import load_settings


# ==================================================================================================================== #
# USER SETTINGS
# Edit only the xlsx settings file before running the pipeline.
# Do not change anything within this, or any other code.
# ==================================================================================================================== #

config = load_settings("settings.xlsx")

if __name__ == "__main__":
    result = run_lumi_pipeline(config)

    print("\nPipeline finished successfully.")

    print("\nGroups analysed:")
    for group_name in result.group_results.keys():
        print(f"    {group_name}")

    if result.condensed_df is not None:
        print("\nCondensed dataframe preview:")
        print(result.condensed_df.head())
