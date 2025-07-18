import os


def combine_env_files(root_directory, output_filename=".env"):
    """
    Finds all .env files in the subdirectories of a given root directory,
    and combines their contents into a single .env file in the current
    working directory.

    Args:
        root_directory (str): The absolute path to the directory to search in.
        output_filename (str): The name of the file to save the combined
                                 content to. Defaults to ".env".
    """
    # Ensure the provided root directory exists
    if not os.path.isdir(root_directory):
        print(
            f"Error: The specified directory does not exist: {root_directory}")
        return

    combined_content = []

    print(f"Searching for .env files in: {root_directory}\n")

    # os.walk recursively explores the directory tree
    for dirpath, _, filenames in os.walk(root_directory):
        if ".env" in filenames:
            env_path = os.path.join(dirpath, ".env")
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Add a header to indicate the origin of the following variables
                    header = f"\n# --- Variables from: {env_path} ---\n"
                    combined_content.append(header + content)
                    print(f"Found and read: {env_path}")
            except Exception as e:
                print(f"Error reading file {env_path}: {e}")

    if not combined_content:
        print("No .env files were found in any subdirectories.")
        return

    # Write the combined content to the output file in the current directory
    output_path = os.path.join(os.getcwd(), output_filename)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(combined_content).strip())
        print(f"\nSuccessfully combined all .env files into: {output_path}")
    except Exception as e:
        print(f"Error writing to output file {output_path}: {e}")


if __name__ == "__main__":
    # --- IMPORTANT ---
    # Set the path to the root folder you want to search.
    # The 'r' before the string is important for Windows paths to handle backslashes correctly.
    target_root_directory = r"D:\LichNH\coding\Experimental"

    combine_env_files(target_root_directory)
