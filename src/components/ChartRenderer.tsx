"use client";

import React, { useMemo, useState } from "react";

interface ChartProps {
  type?: "bar" | "line" | "scatter" | "pie" | "box";
  title: string;
  data: Record<string, any>[];
  xKey: string;
  yKey?: string;
  color?: string;
}

const PALETTE = ["#506f48", "#8fa982", "#718c9a", "#b6c4a4", "#9b8c77", "#699188", "#b5a777", "#a8afa1"];

function polarPoint(cx: number, cy: number, radius: number, angle: number) {
  const radians = ((angle - 90) * Math.PI) / 180;
  return { x: cx + radius * Math.cos(radians), y: cy + radius * Math.sin(radians) };
}

function donutArc(cx: number, cy: number, outer: number, inner: number, startAngle: number, endAngle: number) {
  const outerStart = polarPoint(cx, cy, outer, endAngle);
  const outerEnd = polarPoint(cx, cy, outer, startAngle);
  const innerStart = polarPoint(cx, cy, inner, startAngle);
  const innerEnd = polarPoint(cx, cy, inner, endAngle);
  const largeArc = endAngle - startAngle <= 180 ? 0 : 1;
  return [
    `M ${outerStart.x} ${outerStart.y}`,
    `A ${outer} ${outer} 0 ${largeArc} 0 ${outerEnd.x} ${outerEnd.y}`,
    `L ${innerStart.x} ${innerStart.y}`,
    `A ${inner} ${inner} 0 ${largeArc} 1 ${innerEnd.x} ${innerEnd.y}`,
    "Z",
  ].join(" ");
}

export default function ChartRenderer({
  type = "bar",
  title,
  data,
  xKey,
  yKey,
  color = "#506f48",
}: ChartProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  const chartData = useMemo(() => data?.slice(0, type === "pie" ? 8 : 16) || [], [data, type]);
  const labels = chartData.map((row) => String(row[xKey] ?? ""));
  const values = yKey ? chartData.map((row) => Number(row[yKey]) || 0) : chartData.map((_, index) => index + 1);

  if (!chartData.length) {
    return <div className="chart-empty">No chartable data is available.</div>;
  }

  const maxValue = Math.max(...values, 1);
  const minValue = Math.min(...values, 0);
  const range = maxValue - minValue || 1;
  const width = 760;
  const height = 320;
  const padding = { top: 24, right: 28, bottom: 60, left: 66 };
  const innerWidth = width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;
  const chartType = type === "box" ? "bar" : type;
  const total = values.reduce((sum, value) => sum + Math.abs(value), 0) || 1;

  return (
    <article className="chart-shell">
      <div className="chart-header">
        <div>
          <span className="eyebrow">Visual read</span>
          <h3>{title}</h3>
        </div>
        <span className="chart-type">{type} · {chartData.length} points</span>
      </div>

      <div className="chart-scroll">
        <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={title}>
          {chartType !== "pie" && [0, 0.25, 0.5, 0.75, 1].map((ratio) => {
            const y = padding.top + innerHeight * (1 - ratio);
            const label = minValue + range * ratio;
            return (
              <g key={ratio}>
                <line x1={padding.left} y1={y} x2={padding.left + innerWidth} y2={y} stroke="#ded8cd" strokeWidth="1" />
                <text x={padding.left - 12} y={y + 4} fill="#817c73" fontSize="10" textAnchor="end">
                  {Math.abs(label) >= 1000 ? `${(label / 1000).toFixed(1)}k` : label.toFixed(label % 1 ? 1 : 0)}
                </text>
              </g>
            );
          })}

          {chartType === "bar" && chartData.map((_, index) => {
            const step = innerWidth / chartData.length;
            const barWidth = Math.max(9, step * 0.62);
            const x = padding.left + index * step + (step - barWidth) / 2;
            const barHeight = Math.max(3, ((values[index] - minValue) / range) * innerHeight);
            const y = padding.top + innerHeight - barHeight;
            const active = hoveredIndex === index;
            return (
              <g
                key={index}
                className="chart-mark"
                onMouseEnter={() => setHoveredIndex(index)}
                onMouseLeave={() => setHoveredIndex(null)}
              >
                <rect
                  x={x}
                  y={y}
                  width={barWidth}
                  height={barHeight}
                  rx="2"
                  fill={active ? "#ff6b4a" : color}
                  opacity={active ? 1 : 0.9}
                />
                <text x={x + barWidth / 2} y={height - 30} fill={active ? "#151b2b" : "#817c73"} fontSize="9" textAnchor="middle">
                  {labels[index].length > 9 ? `${labels[index].slice(0, 8)}…` : labels[index]}
                </text>
              </g>
            );
          })}

          {(chartType === "line" || chartType === "scatter") && (
            <g>
              {chartType === "line" && chartData.length > 1 && (
                <polyline
                  fill="none"
                  stroke={color}
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  points={chartData.map((_, index) => {
                    const step = innerWidth / Math.max(chartData.length - 1, 1);
                    const x = padding.left + index * step;
                    const y = padding.top + innerHeight - ((values[index] - minValue) / range) * innerHeight;
                    return `${x},${y}`;
                  }).join(" ")}
                />
              )}
              {chartData.map((_, index) => {
                const step = innerWidth / Math.max(chartData.length - 1, 1);
                const x = padding.left + index * step;
                const y = padding.top + innerHeight - ((values[index] - minValue) / range) * innerHeight;
                const active = hoveredIndex === index;
                return (
                  <g
                    key={index}
                    className="chart-mark"
                    onMouseEnter={() => setHoveredIndex(index)}
                    onMouseLeave={() => setHoveredIndex(null)}
                  >
                    <circle cx={x} cy={y} r={active ? 7 : 5} fill={active ? "#ff6b4a" : color} stroke="#fffdf8" strokeWidth="3" />
                    <text x={x} y={height - 30} fill={active ? "#151b2b" : "#817c73"} fontSize="9" textAnchor="middle">
                      {labels[index].length > 8 ? `${labels[index].slice(0, 7)}…` : labels[index]}
                    </text>
                  </g>
                );
              })}
            </g>
          )}

          {chartType === "pie" && (
            <g>
              {chartData.map((_, index) => {
                const before = values.slice(0, index).reduce((sum, value) => sum + Math.abs(value), 0);
                const start = (before / total) * 360;
                const end = start + (Math.abs(values[index]) / total) * 360;
                const active = hoveredIndex === index;
                return (
                  <path
                    key={index}
                    d={donutArc(260, 160, active ? 112 : 106, 61, start, Math.min(end, 359.999))}
                    fill={PALETTE[index % PALETTE.length]}
                    opacity={hoveredIndex === null || active ? 1 : 0.4}
                    className="chart-mark"
                    onMouseEnter={() => setHoveredIndex(index)}
                    onMouseLeave={() => setHoveredIndex(null)}
                  />
                );
              })}
              <text x="260" y="153" textAnchor="middle" fill="#777168" fontSize="10">TOTAL</text>
              <text x="260" y="177" textAnchor="middle" fill="#151b2b" fontFamily="Georgia, serif" fontWeight="700" fontSize="22">
                {total.toLocaleString(undefined, { maximumFractionDigits: 1 })}
              </text>
              {chartData.map((_, index) => (
                <g
                  key={`legend-${index}`}
                  onMouseEnter={() => setHoveredIndex(index)}
                  onMouseLeave={() => setHoveredIndex(null)}
                  className="chart-mark"
                >
                  <rect x="430" y={70 + index * 24} width="9" height="9" rx="2" fill={PALETTE[index % PALETTE.length]} />
                  <text x="448" y={79 + index * 24} fill="#4e4e4a" fontSize="10">
                    {labels[index].length > 22 ? `${labels[index].slice(0, 21)}…` : labels[index]}
                  </text>
                  <text x="700" y={79 + index * 24} fill="#151b2b" fontSize="10" fontWeight="700" textAnchor="end">
                    {((Math.abs(values[index]) / total) * 100).toFixed(1)}%
                  </text>
                </g>
              ))}
            </g>
          )}
        </svg>
      </div>

      <div className={`chart-tooltip ${hoveredIndex === null ? "is-idle" : ""}`}>
        {hoveredIndex === null ? (
          <span>Hover a mark to inspect the value</span>
        ) : (
          <>
            <span>{xKey}<strong>{labels[hoveredIndex]}</strong></span>
            <span>{yKey || "Value"}<strong>{values[hoveredIndex].toLocaleString()}</strong></span>
          </>
        )}
      </div>
    </article>
  );
}
