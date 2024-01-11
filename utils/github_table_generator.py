import json
import os


def make_github_table(reduced_by_error):
    header = "| no. | error | status |"
    sep = "|-:|:-|:-|"
    lines = [header, sep]
    for error in reduced_by_error:
        count = reduced_by_error[error]["count"]
        line = f"| {count} | {error[:100]} |  |"
        lines.append(line)

    return "\n".join(lines)


def make_github_table_per_model(reduced_by_model):
    header = "| model | no. of errors | major error | count |"
    sep = "|-:|-:|-:|-:|"
    lines = [header, sep]
    for model in reduced_by_model:
        count = reduced_by_model[model]["count"]
        error, _count = list(reduced_by_model[model]["errors"].items())[0]
        line = f"| {model} | {count} | {error[:60]} | {_count} |"
        lines.append(line)

    return "\n".join(lines)
