import xml.etree.ElementTree as ET
from pathlib import Path

def local(tag):  # strip namespace
    return tag.rsplit('}', 1)[-1]

def page_text(xml_path):
    root = ET.parse(xml_path).getroot()
    blocks = []
    for tb in root.iter():
        if local(tb.tag) != "TextBlock":
            continue
        lines = []
        for tl in tb.iter():
            if local(tl.tag) != "TextLine":
                continue
            words = []
            for el in tl:
                if local(el.tag) != "String":
                    continue
                subs = el.get("SUBS_TYPE")
                if subs == "HypPart1":
                    c = el.get("SUBS_CONTENT", el.get("CONTENT", ""))
                elif subs == "HypPart2":
                    c = ""
                else:
                    c = el.get("CONTENT", "")
                if c:
                    words.append(c)
            if words:
                lines.append(" ".join(words))
        if lines:
            blocks.append("\n".join(lines))
    return "\n\n".join(blocks)

if __name__ == "__main__":
    out = Path("ocr_txt"); out.mkdir(exist_ok=True)
    files = sorted(Path("data").glob("*.xml"))
    ok = 0
    for f in files:
        try:
            txt = page_text(f); ok += 1
        except Exception as e:
            txt = f"[parse error: {e}]"
        (out / (f.stem + ".txt")).write_text(txt, encoding="utf-8")
    print(f"Parsed {ok}/{len(files)} pages")
