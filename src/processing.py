from percept_parser import percept
import pandas as pd
import os


def gen_dataframe(subject_id, base_dir, dates, output_dir, assets_dir):
    """
    returns a concatenated dataframe of all the dataframes from the json files in the base_dir for the specified dates.
    """

    output_path = os.path.join(assets_dir, f"preprocessed_df_{subject_id}_{dates[0]}.parquet")

    if os.path.exists(output_path):
        print(f"Preprocessed dataframe already exists at {output_path}. Loading it.")
        final_df = pd.read_parquet(output_path)
        return final_df
    
    file_list = [f for f in os.listdir(base_dir) if f.endswith(".json") if any(date in f for date in dates)]

    dfs_list = []

    for f in file_list:
        parser = percept.PerceptParser(os.path.join(base_dir, f))
        dfs_bs_td_list = parser.read_timedomain_data(False)
        print(f"File: {f}, Number of dataframes: {len(dfs_bs_td_list)}")
        
        for df in dfs_bs_td_list:
            if not any(df.equals(existing_df) for existing_df in dfs_list):
                dfs_list.append(df)

    if not dfs_list:
        print("No valid dataframes found. Exiting.")
        return None
            

    if not dfs_list:
        print("No valid dataframes found. Exiting.")
        return None

    final_df = pd.concat(dfs_list, axis=0, ignore_index=False, sort=True)
    final_df = final_df.sort_index()
    print(f"Concatenated {len(dfs_list)} dataframes into a single dataframe with shape: {final_df.shape}")

    # drop rows with any NaN values
    final_df = final_df.dropna()

    # remove all the duplicates for now
    final_df = final_df[~final_df.index.duplicated(keep=False)]

    # Convert to Central Time
    final_df.index = final_df.index.tz_convert('US/Central')

    # Save the dataframe as a parquet file
    final_df.to_parquet(output_path)
    print(f"Saved preprocessed dataframe to {output_path}")

    return final_df


 