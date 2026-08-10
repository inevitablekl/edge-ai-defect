#!/usr/bin/env python3
"""Generate the deterministic, non-final Phase 5 conceptual Figure 2 preview."""

from pathlib import Path


OUT = Path(__file__).resolve().parents[1] / "fig2_e2e_intervention_scope_preview.svg"


def esc(value: str) -> str:
    return (value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def text(x: int, y: int, value: str, size: int = 17, anchor: str = "middle") -> str:
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
        f'font-family="Noto Serif CJK SC,SimSun,serif" font-size="{size}">{esc(value)}</text>'
    )


def main() -> None:
    labels = [
        ("数据源获取", "与解码"),
        ("主机暂存", "/输入准备"),
        ("预处理", ""),
        ("必要数据移动", ""),
        ("TensorRT INT8", "推理与同步"),
        ("后处理", "/结果构造"),
    ]
    xs = [45, 230, 415, 600, 785, 970]
    w, h, gap_y = 150, 78, 33
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="510" viewBox="0 0 1200 510">',
        '<!-- PHASE5_PREPARATION_ONLY: deterministic non-final preview -->',
        '<rect width="1200" height="510" fill="white"/>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#222"/></marker></defs>',
        text(45, 58, "概念性E2E组成", 18, "start"),
    ]
    for i, ((line1, line2), x) in enumerate(zip(labels, xs)):
        parts.append(f'<rect x="{x}" y="90" width="{w}" height="{h}" fill="white" stroke="#222" stroke-width="1.5"/>')
        parts.append(text(x + w // 2, 126 if line2 else 136, line1))
        if line2:
            parts.append(text(x + w // 2, 149, line2))
        if i < len(xs) - 1:
            parts.append(f'<line x1="{x+w}" y1="129" x2="{xs[i+1]-10}" y2="129" stroke="#222" stroke-width="1.5" marker-end="url(#arrow)"/>')
    parts.extend([
        text(45, 230, "受控比较", 17, "start"),
        '<rect x="230" y="202" width="520" height="62" rx="5" fill="none" stroke="#555" stroke-width="2" stroke-dasharray="10 6"/>',
        text(490, 239, "V0→V2R：较宽的结构/配置干预", 17),
        '<rect x="230" y="292" width="150" height="62" rx="5" fill="none" stroke="#555" stroke-width="2" stroke-dasharray="2 6"/>',
        text(398, 317, "V2R→V3R：较窄的结构/配置干预", 17, "start"),
        text(398, 342, "（仅主机原始图像暂存分配类型）", 15, "start"),
        '<line x1="45" y1="395" x2="1120" y2="395" stroke="#999" stroke-width="1"/>',
        text(45, 432, "边界：较宽/较窄仅描述受控变量覆盖的结构与配置范围，", 16, "start"),
        text(45, 460, "不表示 Amdahl α 大小，也不预测实际加速比。", 16, "start"),
        '</svg>\n',
    ])
    OUT.write_text("\n".join(parts), encoding="utf-8")


if __name__ == "__main__":
    main()
