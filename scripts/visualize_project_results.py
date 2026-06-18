"""Generate polished project result figures for the Lawrence Strike causal-framing project.

This script is optional. The core analysis pipeline does not require matplotlib,
but these figures make the README/report easier to understand.
"""
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

# Korean font support when available
for fp in [
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]:
    if Path(fp).exists():
        fm.fontManager.addfont(fp)
        plt.rcParams["font.family"] = fm.FontProperties(fname=fp).get_name()
        break
plt.rcParams["axes.unicode_minus"] = False


def savefig(name: str):
    plt.tight_layout()
    plt.savefig(FIG / name, dpi=200, bbox_inches="tight")
    plt.close()


def real_corpus_distribution():
    contexts = ["order_focused", "mixed", "institutional"]
    y1 = [0, 7, 2]
    y2 = [2, 3, 0]
    x = range(len(contexts))
    width = 0.35
    plt.figure(figsize=(8, 4.5))
    plt.bar([i - width/2 for i in x], y1, width, label="Y1 개선")
    plt.bar([i + width/2 for i in x], y2, width, label="Y2 통제")
    plt.xticks(list(x), contexts, rotation=15, ha="right")
    plt.ylabel("추출 단위 수")
    plt.title("실제 corpus 프레임 분포")
    plt.legend()
    plt.grid(axis="y", alpha=0.25)
    savefig("real_corpus_frame_distribution.png")


def demo_effects():
    outcomes = ["Y1 개선", "Y2 통제"]
    naive = [0.022, 0.195]
    adjusted = [0.101, 0.121]
    x = range(len(outcomes))
    width = 0.35
    plt.figure(figsize=(7.5, 4.5))
    plt.bar([i - width/2 for i in x], naive, width, label="Naive")
    plt.bar([i + width/2 for i in x], adjusted, width, label="Z 보정 후")
    plt.axhline(0, linewidth=0.8)
    plt.xticks(list(x), outcomes)
    plt.ylabel("효과값")
    plt.title("Demo effect: 보정 전후 비교")
    plt.legend()
    plt.grid(axis="y", alpha=0.25)
    for i, val in enumerate(naive):
        plt.text(i - width/2, val + 0.005, f"+{val:.3f}", ha="center", fontsize=9)
    for i, val in enumerate(adjusted):
        plt.text(i + width/2, val + 0.005, f"+{val:.3f}", ha="center", fontsize=9)
    savefig("demo_effect_naive_vs_adjusted.png")


def sensitivity():
    settings = ["baseline", "observed share", "Z 2-level"]
    y1 = [0.101, 0.124, 0.080]
    y2 = [0.121, 0.116, 0.138]
    plt.figure(figsize=(8, 4.5))
    plt.plot(settings, y1, marker="o", label="Y1 개선")
    plt.plot(settings, y2, marker="o", label="Y2 통제")
    plt.axhline(0, linewidth=0.8)
    plt.ylabel("효과값")
    plt.title("민감도 분석: 설정을 바꿔도 부호 유지")
    plt.legend()
    plt.grid(axis="y", alpha=0.25)
    savefig("sensitivity_effects.png")


def demo_cell_counts():
    rows = [
        ("order_focused", "X=1", 30, 8, 24),
        ("order_focused", "X=0", 10, 3, 6),
        ("mixed", "X=1", 44, 26, 22),
        ("mixed", "X=0", 36, 16, 14),
        ("institutional", "X=1", 16, 13, 5),
        ("institutional", "X=0", 24, 16, 6),
    ]
    labels = [f"{z}\n{x}" for z, x, *_ in rows]
    n = [r[2] for r in rows]
    y1 = [r[3] for r in rows]
    y2 = [r[4] for r in rows]
    x = range(len(rows))
    width = 0.25
    plt.figure(figsize=(10, 4.8))
    plt.bar([i - width for i in x], n, width, label="n")
    plt.bar(list(x), y1, width, label="Y1")
    plt.bar([i + width for i in x], y2, width, label="Y2")
    plt.xticks(list(x), labels, rotation=25, ha="right")
    plt.ylabel("단위 수")
    plt.title("Demo-coded data cell counts")
    plt.legend()
    plt.grid(axis="y", alpha=0.25)
    savefig("demo_cell_counts.png")


def kg_structure():
    plt.figure(figsize=(9.5, 3.6))
    ax = plt.gca()
    ax.axis("off")
    nodes = [
        ("Issue", 0.08, 0.6),
        ("Article", 0.28, 0.6),
        ("Extraction", 0.50, 0.6),
        ("SupportingQuote", 0.75, 0.6),
        ("AssertedCausalClaim", 0.40, 0.25),
        ("AnalystAssumption", 0.62, 0.25),
    ]
    for label, x, y in nodes:
        ax.text(x, y, label, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="black"), fontsize=10)
    arrows = [
        ((0.14, 0.6), (0.22, 0.6)),
        ((0.35, 0.6), (0.44, 0.6)),
        ((0.58, 0.6), (0.67, 0.6)),
        ((0.50, 0.52), (0.42, 0.34)),
        ((0.54, 0.52), (0.61, 0.34)),
    ]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", lw=1.4))
    ax.text(0.5, 0.92, "Knowledge Graph evidence-tracing structure", ha="center", fontsize=13, fontweight="bold")
    ax.text(0.5, 0.05, "신문이 주장한 인과와 분석자 가정을 분리하고, 모든 추출을 원문 quote로 추적", ha="center", fontsize=10)
    savefig("kg_evidence_structure.png")


if __name__ == "__main__":
    real_corpus_distribution()
    demo_effects()
    sensitivity()
    demo_cell_counts()
    kg_structure()
    print(f"Saved figures to {FIG}")
