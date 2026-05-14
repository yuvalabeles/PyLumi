from lumi_analysis.core.pipeline import run_lumi_pipeline


config = {
    # Input data
    "input_folder": (
        r"C:/Users/yuval/OneDrive/Desktop/Lumi/"
        r"control males 5.4.26/Analysis/"
    ),

    # Grouping
    "replicates_per_group": 5,
    "sample_tags": [
        "Liver1",
        "Liver2",
        "Kid1",
        "Kid2",
        "Lung1",
        "Lung2",
    ],
    "include_extra_group": False,

    # File parsing
    "extension": ".csv",
    "suffix_to_remove": "_Raw",
    "file_suffix": "_Raw.csv",

    # Analysis
    "experiment_type": "tissue",
    "save_file": True,

    # Output
    "output_folder": "test_output",
}


if __name__ == "__main__":
    result = run_lumi_pipeline(config)

    print("\nPipeline finished successfully.")

    if isinstance(result, dict):
        print("\nReturned objects:")

        for key in result.keys():
            print(f"    {key}")
