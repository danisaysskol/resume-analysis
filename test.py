from markitdown import MarkItDown

md = MarkItDown(enable_plugins=False) # Set to True to enable plugins
result = md.convert("job_description.pdf")

with open("markdown.md", "w") as f:
    f.write(result.text_content)