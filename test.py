from markitdown import MarkItDown

md = MarkItDown(enable_plugins=False) # Set to True to enable plugins

result = md.convert("resume.pdf")
with open("resume.md", "w") as f:
    f.write(result.text_content)

result = md.convert("job_description.pdf")
with open("job_description.md", "w") as f:
    f.write(result.text_content)