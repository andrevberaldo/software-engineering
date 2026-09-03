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


# ---------------------------------------------------------------------------
# 5. Comprar uma solução pronta vs. construir a própria
# ---------------------------------------------------------------------------
def diagram_comprar_construir():
    w, h = 12.0, 5.0
    fig, ax = new_fig(w, h)

    ax.plot([w / 2, w / 2], [0.3, h - 0.3], color=ICE, linewidth=2)

    # --- Left: comprar (gift-box icon) ---
    cx1 = w / 4
    box_cx, box_cy, bs = cx1, 1.25, 1.7
    ax.add_patch(
        FancyBboxPatch(
            (box_cx - bs / 2, box_cy - bs / 2 + 0.15), bs, bs * 0.75,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            facecolor=ICE_SOFT, edgecolor=NAVY, linewidth=1.6, zorder=2,
        )
    )
    ax.add_patch(
        FancyBboxPatch(
            (box_cx - bs / 2, box_cy - bs / 2 - 0.18), bs, 0.35,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            facecolor=WHITE, edgecolor=NAVY, linewidth=1.6, zorder=3,
        )
    )
    ax.plot([box_cx, box_cx], [box_cy - bs / 2 - 0.18, box_cy + bs / 2 - 0.1],
             color=AMBER, linewidth=5, zorder=4, solid_capstyle="round")
    ax.add_patch(Circle((box_cx - 0.18, box_cy - bs / 2 - 0.3), 0.14,
                         facecolor=AMBER, edgecolor="none", zorder=4))
    ax.add_patch(Circle((box_cx + 0.18, box_cy - bs / 2 - 0.3), 0.14,
                         facecolor=AMBER, edgecolor="none", zorder=4))

    ax.text(cx1, 2.75, "Comprar uma solução pronta", ha="center", fontsize=15.5,
            fontweight="bold", color=NAVY)
    ax.text(cx1, 3.65,
            "Uma empresa especializada já\nconstruiu, mantém e melhora o\nproduto. Você paga para usar.",
            ha="center", va="top", fontsize=11.5, color=GRAY, linespacing=1.6)

    # --- Right: construir (building blocks icon) ---
    cx2 = 3 * w / 4
    block_specs = [(-0.55, 0.35, NAVY), (0.15, 0.35, ICE), (-0.2, -0.15, NAVY_SOFT)]
    for dx, dy, color in block_specs:
        ax.add_patch(
            FancyBboxPatch(
                (cx2 + dx - 0.42, 1.25 + dy - 0.35), 0.84, 0.7,
                boxstyle="round,pad=0.02,rounding_size=0.09",
                facecolor=color, edgecolor=WHITE, linewidth=2, zorder=3 + dy,
            )
        )

    ax.text(cx2, 2.75, "Construir a própria solução", ha="center", fontsize=15.5,
            fontweight="bold", color=NAVY)
    ax.text(cx2, 3.65,
            "O time da empresa desenha e\nmantém a solução, sob medida\npara a sua necessidade.",
            ha="center", va="top", fontsize=11.5, color=GRAY, linespacing=1.6)

    save(fig, "diagrama_comprar_construir.png")


# ---------------------------------------------------------------------------
# 6. O ciclo de renovação de uma assinatura (SaaS)
# ---------------------------------------------------------------------------
def diagram_ciclo_assinatura():
    w, h = 12.0, 5.4
    fig, ax = new_fig(w, h)
    # Data units in this axes are ~0.78x a real inch (default matplotlib
    # subplot margins), while fontsize is in true points/inches. Labels set
    # inside the circles below were sized against that mismatch and spilled
    # past the circle edge, going invisible where white text crossed onto
    # the white page background. Filling the full figure with the axes
    # makes 1 data unit == 1 real inch, matching the radius/fontsize math.
    ax.set_position([0, 0, 1, 1])

    cx, cy = w / 2, 2.55
    radius = 1.55

    nodes = [
        ("Usa o produto\ne recebe valor", (cx, cy - radius)),
        ("Chega a data\nde renovação", (cx + radius * 1.05, cy + radius * 0.35)),
        ("Renova", (cx - radius * 1.05, cy + radius * 0.35)),
    ]
    r = 0.82

    for label, (x, y) in nodes:
        ax.add_patch(Circle((x, y), r, facecolor=NAVY, edgecolor="none", zorder=3))
        ax.text(x, y, label, ha="center", va="center", fontsize=11, fontweight="bold",
                color=WHITE, linespacing=1.3, zorder=4)

    (x1, y1), (x2, y2), (x3, y3) = [n[1] for n in nodes]

    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), connectionstyle="arc3,rad=-0.25",
                                  arrowstyle="-|>", mutation_scale=18, linewidth=2.4,
                                  color=AMBER, zorder=2))
    ax.add_patch(FancyArrowPatch((x2, y2), (x3, y3), connectionstyle="arc3,rad=-0.25",
                                  arrowstyle="-|>", mutation_scale=18, linewidth=2.4,
                                  color=AMBER, zorder=2))
    ax.add_patch(FancyArrowPatch((x3, y3), (x1, y1), connectionstyle="arc3,rad=-0.25",
                                  arrowstyle="-|>", mutation_scale=18, linewidth=2.4,
                                  color=AMBER, zorder=2))

    entry_x, entry_y = cx, cy - radius - 1.35
    ax.text(entry_x, entry_y, "Cliente\nassina", ha="center", va="center", fontsize=11.5,
            fontweight="bold", color=NAVY, linespacing=1.3)
    ax.add_patch(FancyArrowPatch((entry_x, entry_y - 0.35 + 0.55), (x1, y1 - r - 0.05),
                                  arrowstyle="-|>", mutation_scale=16, linewidth=2,
                                  color=NAVY_SOFT, zorder=2))

    cancel_x, cancel_y = x2 + 1.9, y2 + 0.85
    ax.add_patch(
        FancyBboxPatch((cancel_x - 1.1, cancel_y - 0.35), 2.2, 0.7,
                        boxstyle="round,pad=0.02,rounding_size=0.1",
                        facecolor=ICE_SOFT, edgecolor=GRAY, linewidth=1.4, zorder=2)
    )
    ax.text(cancel_x, cancel_y, "Cancela\n(minoria dos casos)", ha="center", va="center",
            fontsize=10.5, color=GRAY, linespacing=1.3, zorder=3)
    ax.add_patch(FancyArrowPatch((x2 + r * 0.7, y2 + r * 0.5), (cancel_x - 1.0, cancel_y - 0.1),
                                  arrowstyle="-|>", mutation_scale=13, linewidth=1.6,
                                  color=GRAY, linestyle=(0, (4, 3)), zorder=1))

    ax.text(cx, h - 0.25,
            "Cada renovação soma à receita recorrente do negócio",
            ha="center", va="bottom", fontsize=12.5, color=NAVY_SOFT, style="italic")

    save(fig, "diagrama_ciclo_assinatura.png")


# ---------------------------------------------------------------------------
# 7. Fluxo de caixa: venda única vs. assinatura recorrente
# ---------------------------------------------------------------------------
def diagram_fluxo_caixa_saas():
    w, h = 12.0, 6.2
    fig, ax = plt.subplots(figsize=(w, h), dpi=200)

    anos = [0, 1, 2, 3, 4, 5]
    licenca = [400, 400, 400, 400, 400, 400]
    assinatura = [0, 120, 240, 360, 480, 600]

    ax.plot(anos, licenca, color=NAVY, linewidth=2.5, marker="o", markersize=6,
            zorder=3, label="licenca")
    ax.plot(anos, assinatura, color=AMBER, linewidth=2.5, marker="o", markersize=6,
            zorder=3, label="assinatura")

    # crossover point (linear interpolation between year 3 and year 4)
    y3, y4 = assinatura[3], assinatura[4]
    frac = (400 - y3) / (y4 - y3)
    cross_x = 3 + frac
    ax.plot([cross_x], [400], marker="o", markersize=10, markerfacecolor=WHITE,
            markeredgecolor=INK, markeredgewidth=2, zorder=5)
    ax.annotate("A partir daqui, a assinatura\njá vale mais que a venda única",
                xy=(cross_x, 400), xytext=(cross_x - 0.15, 560),
                fontsize=11, color=INK, ha="center", linespacing=1.5,
                arrowprops=dict(arrowstyle="-", color=INK, linewidth=1.2))

    ax.text(anos[-1] + 0.12, licenca[-1], "Venda única\n(pagamento uma vez)",
            va="center", ha="left", fontsize=11.5, fontweight="bold", color=NAVY)
    ax.text(anos[-1] + 0.12, assinatura[-1], "Assinatura\n(cresce a cada renovação)",
            va="center", ha="left", fontsize=11.5, fontweight="bold", color=AMBER)

    ax.set_xlim(-0.3, 7.3)
    ax.set_ylim(-40, 680)
    ax.set_xticks(anos)
    ax.set_xticklabels([f"Ano {a}" if a > 0 else "Início" for a in anos], fontsize=11,
                        color=GRAY)
    ax.set_yticks([])
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(ICE)
    ax.tick_params(axis="x", length=0)
    ax.set_title("Receita acumulada por cliente, ao longo do tempo",
                  fontsize=15, fontweight="bold", color=NAVY, loc="left", pad=18)

    fig.tight_layout()
    save(fig, "diagrama_fluxo_caixa_saas.png")


# ---------------------------------------------------------------------------
# 8. Três grupos de métricas de sucesso
# ---------------------------------------------------------------------------
def diagram_metricas_sucesso():
    w, h = 12.0, 5.6
    fig, ax = new_fig(w, h)

    groups = [
        ("USO", "Uso e adoção", [
            "Licenças ou usuários ativos",
            "Uso real, não só a compra",
            "Frequência de uso",
        ]),
        ("R$", "Receita e retenção", [
            "% de renovação",
            "Receita recorrente",
            "Taxa de cancelamento",
        ]),
        ("NPS", "Satisfação do cliente", [
            "Nota de satisfação (NPS)",
            "Tempo até o primeiro valor",
            "Volume de chamados de suporte",
        ]),
    ]
    n = len(groups)
    margin = 1.7
    usable = w - 2 * margin
    xs = [margin + usable * i / (n - 1) for i in range(n)]
    cy = 1.15
    r = 0.72

    for (initials, title, items), x in zip(groups, xs):
        ax.add_patch(Circle((x, cy), r, facecolor=NAVY, edgecolor="none", zorder=2))
        ax.text(x, cy, initials, ha="center", va="center", fontsize=17,
                fontweight="bold", color=WHITE, zorder=3)
        ax.text(x, cy + r + 0.4, title, ha="center", va="center", fontsize=15,
                fontweight="bold", color=NAVY)
        item_y = cy + r + 0.85
        for item in items:
            ax.add_patch(Circle((x - 1.3, item_y), 0.05, facecolor=AMBER,
                                 edgecolor="none", zorder=2))
            ax.text(x - 1.15, item_y, item, ha="left", va="center", fontsize=10.5,
                    color=GRAY)
            item_y += 0.5

    save(fig, "diagrama_metricas_sucesso.png")


# ---------------------------------------------------------------------------
# 9. Métricas de vaidade vs. métricas que importam
# ---------------------------------------------------------------------------
def diagram_metricas_vaidade():
    w, h = 12.0, 5.4
    fig, ax = new_fig(w, h)

    ax.plot([w / 2, w / 2], [0.3, h - 0.3], color=ICE, linewidth=2)

    # --- Left: vanity metrics, ascending bars that look good but are hollow ---
    cx1 = w / 4
    bar_heights = [0.5, 0.9, 1.4]
    bar_w = 0.42
    base_y = 1.75
    for i, bh in enumerate(bar_heights):
        bx = cx1 - 0.75 + i * (bar_w + 0.2)
        ax.add_patch(
            FancyBboxPatch((bx, base_y - bh), bar_w, bh,
                            boxstyle="round,pad=0.01,rounding_size=0.04",
                            facecolor=ICE, edgecolor=NAVY_SOFT, linewidth=1.3, zorder=2)
        )
    ax.plot([cx1 - 0.95, cx1 + 0.95], [base_y + 0.05, base_y + 0.05],
             color=GRAY, linewidth=1.5, zorder=1)

    ax.text(cx1, 2.85, "Métricas de vaidade", ha="center", fontsize=15.5,
            fontweight="bold", color=NAVY)
    ax.text(cx1, 3.7,
            "Impressionam à primeira vista (downloads,\nvisitas, seguidores), mas não dizem se o\ncliente está satisfeito ou vai continuar pagando.",
            ha="center", va="top", fontsize=11, color=GRAY, linespacing=1.6)

    # --- Right: metrics that matter, a bullseye/target ---
    cx2 = 3 * w / 4
    target_cy = 1.15
    for rr, color in [(0.75, ICE), (0.5, NAVY_SOFT), (0.25, AMBER)]:
        ax.add_patch(Circle((cx2, target_cy), rr, facecolor=color, edgecolor="none",
                             zorder=2))
    ax.add_patch(Circle((cx2, target_cy), 0.08, facecolor=NAVY, edgecolor="none",
                         zorder=3))

    ax.text(cx2, 2.85, "Métricas que importam", ha="center", fontsize=15.5,
            fontweight="bold", color=NAVY)
    ax.text(cx2, 3.7,
            "Mostram se o produto resolve o problema de\nverdade: % de renovação, uso recorrente e\nreceita por cliente.",
            ha="center", va="top", fontsize=11, color=GRAY, linespacing=1.6)

    save(fig, "diagrama_metricas_vaidade.png")


# ---------------------------------------------------------------------------
# 10. Antecipação automatizada de renovação (previsão de churn/receita)
# ---------------------------------------------------------------------------
def diagram_previsao_renovacao():
    w, h = 12.0, 5.8
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

    top_y = 0.85
    box(6.0, top_y, 6.4, 1.0,
        "Sinais de uso, contato e sinistros de cada cliente",
        ICE_SOFT, NAVY, fs=12.5, bold=True)

    mid_y = 2.35
    box(6.0, mid_y, 6.8, 1.15,
        "IA estima o risco de cancelamento\ne projeta a receita futura",
        NAVY, WHITE, fs=13.5, bold=True)

    ax.add_patch(FancyArrowPatch((6.0, top_y + 0.52), (6.0, mid_y - 0.6),
                                  arrowstyle="-|>", mutation_scale=16, linewidth=2,
                                  color=AMBER, zorder=1))

    branch_y = 4.35
    left_x, right_x = 3.2, 8.8

    ax.add_patch(FancyArrowPatch((6.0, mid_y + 0.58), (left_x, branch_y - 0.6),
                                  connectionstyle="arc3,rad=-0.15",
                                  arrowstyle="-|>", mutation_scale=15, linewidth=1.8,
                                  color=NAVY_SOFT, zorder=1))
    ax.add_patch(FancyArrowPatch((6.0, mid_y + 0.58), (right_x, branch_y - 0.6),
                                  connectionstyle="arc3,rad=0.15",
                                  arrowstyle="-|>", mutation_scale=15, linewidth=1.8,
                                  color=NAVY_SOFT, zorder=1))

    ax.text(left_x, branch_y - 1.0, "Risco baixo", ha="center", fontsize=12,
            fontweight="bold", color=NAVY_SOFT)
    ax.text(right_x, branch_y - 1.0, "Risco alto", ha="center", fontsize=12,
            fontweight="bold", color=AMBER)

    box(left_x, branch_y, 4.6, 1.35,
        "Sistema envia um lembrete e\ndestaca vantagens da apólice\ndireto ao cliente",
        ICE_SOFT, NAVY, fs=11.5, ec=ICE, lw=1.8)
    box(right_x, branch_y, 4.6, 1.35,
        "Corretor humano é avisado\npara uma conversa prioritária\ncom o cliente",
        WHITE, INK, fs=11.5, ec=AMBER, lw=2)

    ax.text(6.0, h - 0.15,
            "A tecnologia age antes da data de vencimento chegar",
            ha="center", va="bottom", fontsize=12.5, color=NAVY_SOFT, style="italic")

    save(fig, "diagrama_previsao_renovacao.png")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    diagram_lifecycle()
    diagram_roles()
    diagram_ai_flow()
    diagram_rag_vs_graphrag()
    diagram_comprar_construir()
    diagram_ciclo_assinatura()
    diagram_fluxo_caixa_saas()
    diagram_metricas_sucesso()
    diagram_metricas_vaidade()
    diagram_previsao_renovacao()
