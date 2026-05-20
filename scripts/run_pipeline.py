from lumi_analysis.core.pipeline import run_lumi_pipeline
from scripts.load_settings import load_settings


# ==================================================================================================================== #
# USER SETTINGS
# Edit only the xlsx settings file before running the pipeline.
# Do not change anything within this, or any other code.
# ==================================================================================================================== #

config = load_settings("settings.xlsx")
print(config)

if __name__ == "__main__":
    result = run_lumi_pipeline(config)

    print("\nPipeline finished successfully.")

    print("\nGroups analysed:")
    for group_name in result.group_results.keys():
        print(f"    {group_name}")

    if result.condensed_df is not None:
        print("\nCondensed dataframe preview:")
        print(result.condensed_df.head())
