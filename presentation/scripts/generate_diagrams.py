"""Generate the schematic diagrams used in the deck (matplotlib, no external icons)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, ConnectionPatch
from matplotlib.lines import Line2D
import matplotlib.font_manager as fm
import os

NAVY = "#1E2761"
NAVY_SOFT = "#3A4A9E"
ICE = "#CADCFC"
ICE_SOFT = "#E8F0FE"
AMBER = "#E8A33D"
INK = "#2B2B33"
GRAY = "#6B7280"
WHITE = "#FFFFFF"

plt.rcParams["font.family"] = "DejaVu Sans"

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")


def new_fig(w, h):
    fig, ax = plt.subplots(figsize=(w, h), dpi=200)
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    ax.invert_yaxis()
    return fig, ax


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, transparent=True, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print("saved", path)


# ---------------------------------------------------------------------------
# 1. Product / feature lifecycle funnel
# ---------------------------------------------------------------------------
def diagram_lifecycle():
    w, h = 12.0, 5.3
    fig, ax = new_fig(w, h)

    steps = [
        ("1", "Descoberta", "Entender o problema\ne a oportunidade"),
        ("2", "Definição", "Priorizar o que traz\nmais valor"),
        ("3", "Construção", "Times constroem em\nciclos curtos"),
        ("4", "Validação", "Testar com clientes\nreais, cedo"),
        ("5", "Lançamento", "Entregar ao\nmercado"),
        ("6", "Aprendizado", "Medir resultados e\najustar a rota"),
    ]
    n = len(steps)
    margin = 0.9
    usable = w - 2 * margin
    xs = [margin + usable * i / (n - 1) for i in range(n)]
    cy = 1.35
    r = 0.5

    for i in range(n - 1):
        ax.add_patch(
            FancyArrowPatch(
                (xs[i] + r + 0.05, cy), (xs[i + 1] - r - 0.05, cy),
                arrowstyle="-|>", mutation_scale=16, linewidth=2.2,
                color=AMBER, zorder=1,
            )
        )

    for (num, title, desc), x in zip(steps, xs):
        ax.add_patch(Circle((x, cy), r, facecolor=NAVY, edgecolor="none", zorder=2))
        ax.text(x, cy, num, ha="center", va="center", fontsize=20, fontweight="bold",
                color=WHITE, zorder=3)
        ax.text(x, cy + r + 0.38, title, ha="center", va="center", fontsize=14.5,
                fontweight="bold", color=NAVY)
        ax.text(x, cy + r + 0.85, desc, ha="center", va="top", fontsize=10.5,
                color=GRAY, linespacing=1.4)

    # Loop-back arrow: learning feeds the next opportunity.
    # Text under each circle runs up to roughly cy+r+1.5, so the loop is
    # routed below that to avoid crossing the description column.
    conn_top = cy + r + 1.65
    loop_y = conn_top + 0.55
    ax.add_patch(
        FancyArrowPatch(
            (xs[-1], conn_top), (xs[-1], loop_y),
            arrowstyle="-", linewidth=2, color=NAVY_SOFT, linestyle=(0, (5, 3)),
        )
    )
    ax.add_patch(
        FancyArrowPatch(
            (xs[-1], loop_y), (xs[0], loop_y),
            arrowstyle="-", linewidth=2, color=NAVY_SOFT, linestyle=(0, (5, 3)),
        )
    )
    ax.add_patch(
        FancyArrowPatch(
            (xs[0], loop_y), (xs[0], conn_top),
            arrowstyle="-|>", mutation_scale=16, linewidth=2, color=NAVY_SOFT,
            linestyle=(0, (5, 3)),
        )
    )
    ax.text((xs[0] + xs[-1]) / 2, loop_y + 0.2,
            "O aprendizado de cada entrega alimenta a próxima oportunidade",
            ha="center", va="top", fontsize=11, color=NAVY_SOFT, style="italic")

    save(fig, "diagrama_ciclo_vida.png")


# ---------------------------------------------------------------------------
# 2. Roles working together
# ---------------------------------------------------------------------------
def diagram_roles():
    w, h = 12.0, 4.4
    fig, ax = new_fig(w, h)

    roles = [
        ("PO", "Product Owner", "Entende o cliente e o\nnegócio. Decide o que\ntem mais valor fazer."),
        ("AS", "System Engineer", "Garante que as peças do\nsistema se encaixam e\nse conectam bem."),
        ("TL", "Tech Lead", "Lidera o time técnico e\ncuida da qualidade de\ncomo tudo é construído."),
    ]
    n = len(roles)
    margin = 1.8
    usable = w - 2 * margin
    xs = [margin + usable * i / (n - 1) for i in range(n)]
    cy = 1.35
    r = 0.75

    for i in range(n - 1):
        ax.add_patch(
            FancyArrowPatch(
                (xs[i] + r + 0.08, cy), (xs[i + 1] - r - 0.08, cy),
                arrowstyle="<|-|>", mutation_scale=14, linewidth=1.8,
                color=AMBER, zorder=1,
            )
        )

    for (initials, title, desc), x in zip(roles, xs):
        ax.add_patch(Circle((x, cy), r, facecolor=NAVY, edgecolor="none", zorder=2))
        ax.text(x, cy, initials, ha="center", va="center", fontsize=22,
                fontweight="bold", color=WHITE, zorder=3)
        ax.text(x, cy + r + 0.45, title, ha="center", va="center", fontsize=16,
                fontweight="bold", color=NAVY)
        ax.text(x, cy + r + 0.95, desc, ha="center", va="top", fontsize=11,
                color=GRAY, linespacing=1.5)

    ax.text(w / 2, h - 0.15,
            "Três olhares diferentes, uma mesma entrega",
            ha="center", va="bottom", fontsize=12.5, color=NAVY_SOFT, style="italic")

    save(fig, "diagrama_papeis.png")


# ---------------------------------------------------------------------------
# 3. Fictional AI use case flow (insurance broker)
# ---------------------------------------------------------------------------
def diagram_ai_flow():
    w, h = 12.0, 5.6
    fig, ax = new_fig(w, h)

    def box(x, y, bw, bh, text, fc, tc, fs=12, bold=False, ec="none", lw=0):
        ax.add_patch(
            FancyBboxPatch(
                (x - bw / 2, y - bh / 2), bw, bh,
                boxstyle="round,pad=0.02,rounding_size=0.12",
                facecolor=fc, edgecolor=ec, linewidth=lw, zorder=2,
            )
        )
        ax.text(x, y, text, ha="center", va="center", fontsize=fs,
                color=tc, fontweight="bold" if bold else "normal",
                linespacing=1.4, zorder=3)

    top_y = 1.0
    box(1.9, top_y, 3.2, 1.1, "Corretor pergunta em\nlinguagem natural", ICE_SOFT, NAVY, bold=True)
    box(6.0, top_y, 3.4, 1.3, "Assistente de IA\nda corretora", NAVY, WHITE, fs=13.5, bold=True)
    box(10.1, top_y, 3.2, 1.1, "Resposta clara, com\nfontes citadas", ICE_SOFT, NAVY, bold=True)

    ax.add_patch(FancyArrowPatch((3.5, top_y), (4.3, top_y), arrowstyle="-|>",
                                  mutation_scale=16, linewidth=2, color=AMBER, zorder=1))
    ax.add_patch(FancyArrowPatch((7.7, top_y), (8.5, top_y), arrowstyle="-|>",
                                  mutation_scale=16, linewidth=2, color=AMBER, zorder=1))

    src_y = 3.2
    src_positions = (4.15, 7.85)
    box(src_positions[0], src_y, 3.0, 1.25,
        "Documentos e apólices\n(base de conhecimento)", WHITE, NAVY, fs=11.5,
        ec=ICE, lw=1.8)
    box(src_positions[1], src_y, 3.0, 1.25,
        "Mapa de relações entre\nclientes, apólices e seguradoras", WHITE, NAVY, fs=11.5,
        ec=ICE, lw=1.8)

    for bx in src_positions:
        ax.add_patch(
            FancyArrowPatch((bx, src_y - 0.62), (bx, top_y + 0.7),
                             arrowstyle="-|>", mutation_scale=14, linewidth=1.8,
                             color=NAVY_SOFT, linestyle=(0, (4, 3)), zorder=1)
        )

    bottom_y = 4.9
    box(6.0, bottom_y, 5.6, 1.0,
        "Atendimento mais rápido e preciso ao cliente da corretora",
        AMBER, INK, fs=13, bold=True)
    ax.add_patch(FancyArrowPatch((10.1, top_y + 0.56), (src_positions[1], bottom_y - 0.5),
                                  connectionstyle="arc3,rad=0.15",
                                  arrowstyle="-|>", mutation_scale=14, linewidth=1.8,
                                  color=NAVY_SOFT, zorder=1))

    save(fig, "diagrama_fluxo_ia.png")


# ---------------------------------------------------------------------------
# 4. RAG vs GraphRAG comparison
# ---------------------------------------------------------------------------
def diagram_rag_vs_graphrag():
    w, h = 12.0, 5.0
    fig, ax = new_fig(w, h)

    # divider
    ax.plot([w / 2, w / 2], [0.3, h - 0.3], color=ICE, linewidth=2)

    # --- Left: RAG, stacked documents ---
    cx1 = w / 4
    doc_w, doc_h = 1.7, 2.1
    for i, dy in enumerate([0.28, 0.14, 0.0]):
        ax.add_patch(
            FancyBboxPatch(
                (cx1 - doc_w / 2 + dy * 0.5, 1.15 - doc_h / 2 + dy),
                doc_w, doc_h, boxstyle="round,pad=0.02,rounding_size=0.08",
                facecolor=WHITE if i < 2 else ICE_SOFT,
                edgecolor=NAVY, linewidth=1.6, zorder=2 + i,
            )
        )
    for ly in [-0.55, -0.25, 0.05, 0.35]:
        ax.plot([cx1 - 0.55, cx1 + 0.55], [1.15 + ly, 1.15 + ly],
                 color=ICE, linewidth=3, zorder=5, solid_capstyle="round")

    ax.text(cx1, 2.75, "Busca em documentos", ha="center", fontsize=16,
            fontweight="bold", color=NAVY)
    ax.text(cx1, 3.15, "(RAG)", ha="center", fontsize=13, color=NAVY_SOFT)
    ax.text(cx1, 3.75,
            "Consulta manuais, apólices e\ncontratos e responde citando\na fonte exata usada.",
            ha="center", va="top", fontsize=11.5, color=GRAY, linespacing=1.6)

    # --- Right: GraphRAG, connected network ---
    cx2 = 3 * w / 4
    import numpy as np
    node_pos = {
        "cliente": (cx2, 0.55),
        "apolice_a": (cx2 - 0.95, 1.35),
        "apolice_b": (cx2 + 0.95, 1.35),
        "seguradora_x": (cx2 - 1.5, 0.55),
        "cobertura": (cx2, 1.6),
        "sinistro": (cx2 + 0.4, 0.55),
    }
    edges = [
        ("cliente", "apolice_a"), ("cliente", "apolice_b"),
        ("apolice_a", "seguradora_x"), ("apolice_a", "cobertura"),
        ("apolice_b", "cobertura"), ("cliente", "sinistro"),
    ]
    for a, b in edges:
        xa, ya = node_pos[a]
        xb, yb = node_pos[b]
        ax.plot([xa, xb], [ya, yb], color=ICE, linewidth=2, zorder=2)
    for name, (x, y) in node_pos.items():
        rr = 0.16 if name != "cliente" else 0.2
        color = AMBER if name == "cliente" else NAVY
        ax.add_patch(Circle((x, y), rr, facecolor=color, edgecolor="none", zorder=3))

    ax.text(cx2, 2.75, "Mapa de relações", ha="center", fontsize=16,
            fontweight="bold", color=NAVY)
    ax.text(cx2, 3.15, "(GraphRAG)", ha="center", fontsize=13, color=NAVY_SOFT)
    ax.text(cx2, 3.75,
            "Entende como clientes, apólices,\ncoberturas e seguradoras se\nconectam para responder\nperguntas mais complexas.",
            ha="center", va="top", fontsize=11.5, color=GRAY, linespacing=1.6)

    save(fig, "diagrama_rag_graphrag.png")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    diagram_lifecycle()
    diagram_roles()
    diagram_ai_flow()
    diagram_rag_vs_graphrag()
