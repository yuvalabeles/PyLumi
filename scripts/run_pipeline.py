from lumi_analysis.core.pipeline import run_lumi_pipeline


config = {
    "input_folder": r"C:/Users/yuval/OneDrive/Desktop/Lumi/control males 5.4.26/Analysis/",
    "replicates_per_group": 5,
    "extension": ".csv",
    "suffix_to_remove": "_Raw",
    "sample_tags": ["Liver1", "Liver2", "Kid1", "Kid2", "Lung1", "Lung2"],
}


if __name__ == "__main__":
    result = run_lumi_pipeline(config)

    print("\nPipeline finished successfully.")
    print(result.keys() if isinstance(result, dict) else type(result))
