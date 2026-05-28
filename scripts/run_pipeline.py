from pathlib import Path
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
    "rich": "rich"
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
from rich import print


# ==================================================================================================================== #
# USER SETTINGS
# Edit only the xlsx settings file before running the pipeline.
# Do not change anything within this, or any other code files.
# ==================================================================================================================== #

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SETTINGS_PATH = PROJECT_ROOT / "settings.xlsx"

config = load_settings(SETTINGS_PATH)


if __name__ == "__main__":
    result = run_lumi_pipeline(config)

    print("\n[green]Success:[/green] pipeline finished successfully.")

    print("\n[green]Groups analysed:")
    for group_name in result.group_results.keys():
        print(f"    {group_name}")

    if result.condensed_df is not None:
        print("\n[green]Data preview:")
        print(result.condensed_df.head())
