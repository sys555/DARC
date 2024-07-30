# repo_sketch

{
    "readme": readme_content,
    "instruction": TEMPLATE_DICT["repo_sketch.json"].format_map(
        {"readme": readme_content}
    ),
}

repo_sketch input:
"instruction"

# file_sketch

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

file_sketch intput:
"instruction"

"repo_sketch"
each["generated"] = repo_sketch_response
each["parsed"] = utils.parse_reponse(each["generated"])

"file_path"
repo_sketch_tree = parse_repo_sketch(each["parsed"])
repo_sketch_paths = repo_sketch_tree.get_paths()
for path in repo_sketch_paths:
    if not path.endswith(".py"):
        continue

# function_body
{
    "readme": readme_summary,
    "repo_sketch": repo_sketch,
    "file_sketches": relevant_file_sketch_content,
    "function_signature": function_header_content,
}

"readme"
readme = readme_content
readme_summary = sketch_utils.extract_summary_from_readme(readme)

"repo_sketch"

