repo_sketch

{
    "readme": readme_content,
    "instruction": TEMPLATE_DICT["repo_sketch.json"].format_map(
        {"readme": readme_content}
    ),
}

file_sketch

{
    "readme": readme_content,
    "repo_sketch": each["parsed"],
    "file_path": path,
    "instruction": template.format_map(
        {
            "readme": readme_content,
            "repo_sketch": each["parsed"],
            "file_path": path,
        }
    ),
}