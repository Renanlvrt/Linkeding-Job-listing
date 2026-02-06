import os
import asyncio
from markdown2 import markdown
from playwright.async_api import async_playwright
from pathlib import Path

class PDFGenerator:
    """
    Converts tailored CV markdown to an ATS-compliant PDF using Playwright (Chromium).
    Replaces WeasyPrint to avoid GTK dependency issues on Windows.
    """
    
    def __init__(self, css_path: str = "c:/Users/renan/Desktop/Side_projects/Ai agent/cold email agent/CV_automation/ats_style.css"):
        self.css_path = Path(css_path)
        if not self.css_path.exists():
            # Fallback to current dir if absolute path fails
            self.css_path = Path(__file__).parent / "ats_style.css"

    async def generate_async(self, md_content: str, output_path: str):
        # 1. Convert Markdown to HTML
        html_content = markdown(md_content)
        
        # 2. Add CSS link or inject CSS
        css_style = ""
        if self.css_path.exists():
            with open(self.css_path, 'r', encoding='utf-8') as f:
                css_style = f.read()
        
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                {css_style}
            </style>
        </head>
        <body>
            <div class="container">
                {html_content}
            </div>
        </body>
        </html>
        """
        
        # 3. Use Playwright to render PDF
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_content(full_html)
            
            # ATS compliance: A4, 0.5 inch margins
            await page.pdf(
                path=output_path,
                format="A4",
                print_background=True,
                margin={"top": "0.5in", "bottom": "0.5in", "left": "0.5in", "right": "0.5in"}
            )
            await browser.close()
        return output_path

    def generate(self, md_content: str, output_path: str):
        """Sync wrapper for the async generator."""
        return asyncio.run(self.generate_async(md_content, output_path))


async def generate_sprout_pdf(md_content: str, output_path: str, css_name: str = 'ats_style.css'):
    """Async wrapper for PDF generation."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    base_path = Path(__file__).parent
    css_path = base_path / css_name
    
    gen = PDFGenerator(css_path=str(css_path))
    await gen.generate_async(md_content, output_path)

if __name__ == "__main__":
    # Test generation
    gen = PDFGenerator()
    test_md = """
# RENAN LAVIROTTE
[REDACTED_EMAIL] | [REDACTED_PHONE]

## PROFESSIONAL SUMMARY
Multidisciplinary machine learning specialist with a first-class honours degree from Durham University.
Proven track record in autonomous robotics and AI bot development for enterprise clients like IBM.

## SKILLS
- Python, C, Linux, ML, numpy, PyTorch, sklearn.
- STAR-formatted achievement drafting.

## EXPERIENCE
### IBM Project | AI Engineer | 2025
- Architected an AI bot in VR environment using Granite API.
- Optimized user engagement by 20% through real-time feedback.

## EDUCATION
### Durham University | MEng Computer Science | 2028
    """
    out = gen.generate(test_md, "test_output.pdf")
    print(f"PDF generated at {out}")
