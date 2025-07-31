import argparse
import asyncio

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

from agents.summarize import summarize_text
from agents.format_md import format_to_markdown
from agents.write_obsidian import write_markdown_file

server_params = StdioServerParameters(
    command="uv",  # Using uv to run the server
    args=["--directory", "C:\\Users\\AKazlou\\mcp\\ebook-mcp\\src\\ebook_mcp\\", "run", "main.py"]
)

rules_path = "rules/rules.md"
style_path = "rules/style.md"

async def extract_text_via_mcp(pdf_path, start_page, end_page):
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            markdown_chunks = []
            for page in range(start_page, end_page + 1):
                result = await session.call_tool("get_pdf_page_markdown", arguments={
                    "pdf_path": pdf_path,
                    "page_number": page
                })
                for content in result.content:
                    if isinstance(content, types.TextContent):
                        #print(f"Text: {content.text}")
                        markdown_chunks.append(content.text)
            
            return "\n\n".join(markdown_chunks)


# def generate_summary(text, rules_path):
#     with open(rules_path, 'r', encoding='utf-8') as f:
#         rules = f.read()

#     response = openai.chat.completions.create(
#         model="gpt-4o-mini",  # или другой доступный тебе
#         messages=[
#             {"role": "system", "content": "Ты помощник, создающий конспекты по правилам."},
#             {"role": "user", "content": f"Вот правила:\n\n{rules}"},
#             {"role": "user", "content": f"Вот текст главы:\n\n{text}"}
#         ],
#         temperature=0.4
#     )
#     return response.choices[0].message.content


# def write_markdown_file(content, output_dir, base_filename):
#     os.makedirs(output_dir, exist_ok=True)
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     file_path = os.path.join(output_dir, f"{base_filename}_{timestamp}.md")
#     with open(file_path, 'w', encoding='utf-8') as f:
#         f.write(content)
#     print(f"[✅] Saved to {file_path}")


# 🚀 Основной код
def main():
    parser = argparse.ArgumentParser(description="Summarize PDF chapter to Obsidian.")
    parser.add_argument("--file", required=True, help="Path to the PDF file.")
    parser.add_argument("--pages", required=True, help="Page range to process (e.g., 43-58).")
    parser.add_argument("--out", required=True, help="Output directory for Obsidian.")

    args = parser.parse_args()
    start_page, end_page = map(int, args.pages.split('-'))

    print(f"[1/5] Extracting pages {start_page}-{end_page} from {args.file}...")
    raw_text = asyncio.run(extract_text_via_mcp(args.file, start_page, end_page))

    print(f"[2/5] Reading summarization rules from {rules_path}...")
    with open(rules_path, "r", encoding="utf-8") as f:
        rules_text = f.read()
    
    print(f"[3/5] Reading summarization rules from {style_path}...")
    with open(style_path, "r", encoding="utf-8") as f:
        style_text = f.read()

    print("[4/5] Summarizing content via LLM...")
    summarized = summarize_text(raw_text, rules_text, style_text)

    print("[5/5] Saving to Obsidian vault...")
    formatted = format_to_markdown(summarized)
    write_markdown_file(formatted, args.out, "summary.md")

    print("✅ Done.")


if __name__ == "__main__":
    main()