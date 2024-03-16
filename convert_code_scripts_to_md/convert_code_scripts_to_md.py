# When you call this script, provide a file path to your obsidian vault and it will pull out all python and R files and convert them into notes that contain the scripts as code blocks.
# I did this because I had a bunch of python and R scripts that I copy-paste code out of but wanted to be able to see, search and link them in obsidian. 

import os
import glob
import argparse
from typing import Dict

def code_to_md_converter(folder_path: str) -> None:
    """
    Convert all code files in the given folder to Markdown files with code wrapped in code blocks.

    Args:
        folder_path (str): The path to the folder containing the code files.

    Raises:
        FileNotFoundError: If the provided folder path does not exist.
        NotADirectoryError: If the provided folder path is not a directory.
    """
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"{folder_path} is not a valid directory.")

    # Mapping of file extensions to Markdown code block languages
    extension_to_language: Dict[str, str] = {
        '.py': 'python',
        '.r': 'r',
        '.R': 'r'
    }

    for extension, language in extension_to_language.items():
        print(f"looking for {extension} files now")
        code_files = glob.glob(os.path.join(folder_path, f'*{extension}'))
        for code_file in code_files:
            print(f"Converting {code_file}")
            md_file = f'{os.path.splitext(code_file)[0]}.md'
            with open(code_file, 'r') as code_file_obj, open(md_file, 'w') as md_file_obj:
                code_content = code_file_obj.read()
                md_file_obj.write(f'#code_import #{language}\n')
                md_file_obj.write(f'```{language}')
                md_file_obj.write(code_content)
                md_file_obj.write('\n```\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert code files to Markdown files with code blocks.')
    parser.add_argument('folder_path', type=str, help='Path to the folder containing code files')
    args = parser.parse_args()

    try:
        code_to_md_converter(args.folder_path)
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"Error: {e}")
