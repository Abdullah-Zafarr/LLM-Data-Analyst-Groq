"use client";

import React, { useState } from "react";

interface ChartProps {
  type?: "bar" | "line" | "scatter" | "pie" | "box";
  title: string;
  data: Record<string, any>[];
  xKey: string;
  yKey?: string;
  color?: string;
}

export default function ChartRenderer({
  type = "bar",
  title,
  data,
  xKey,
  yKey,
  color = "#06B6D4",
}: ChartProps) {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  if (!data || data.length === 0) {
    return (
      <div className="p-4 rounded-xl border border-white/10 bg-slate-900/50 text-slate-400 text-xs text-center font-mono">
        No data available for chart rendering
      </div>
    );
  }

  // Extract values
  const validData = data.slice(0, 20); // Top 20 for clean rendering
  const labels = validData.map((d) => String(d[xKey] ?? ""));
  const values = yKey
    ? validData.map((d) => Number(d[yKey]) || 0)
    : validData.map((_, i) => i + 1);

  const maxVal = Math.max(...values, 1);
  const minVal = Math.min(...values, 0);
  const range = maxVal - minVal || 1;

  // Chart Dimensions
  const width = 650;
  const height = 280;
  const padding = { top: 35, right: 30, bottom: 50, left: 60 };
  const innerWidth = width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;

  return (
    <div className="my-3 p-4 rounded-xl border border-cyan-500/20 bg-slate-950/80 backdrop-blur-md shadow-lg shadow-cyan-950/20">
      <div className="flex items-center justify-between mb-3">
        <div className="font-mono text-sm font-semibold text-cyan-400 flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          {title}
        </div>
        <div className="font-mono text-[11px] text-slate-400 uppercase tracking-wider px-2 py-0.5 rounded bg-white/5 border border-white/10">
          {type} chart · {validData.length} records
        </div>
      </div>

      <div className="w-full overflow-x-auto">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-auto max-h-[320px] select-none"
        >
          {/* Grid Lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((ratio, i) => {
            const yPos = padding.top + innerHeight * (1 - ratio);
            const valLabel = (minVal + range * ratio).toFixed(1);
            return (
              <g key={i}>
                <line
                  x1={padding.left}
                  y1={yPos}
                  x2={padding.left + innerWidth}
                  y2={yPos}
                  stroke="rgba(255,255,255,0.06)"
                  strokeDasharray="4 4"
                />
                <text
                  x={padding.left - 10}
                  y={yPos + 4}
                  fill="#64748B"
                  fontSize="10"
                  fontFamily="monospace"
                  textAnchor="end"
                >
                  {valLabel}
                </text>
              </g>
            );
          })}

          {/* Bar Chart Mode */}
          {type === "bar" && (
            <g>
              {validData.map((d, i) => {
                const barWidth = Math.max(
                  8,
                  (innerWidth / validData.length) * 0.7
                );
                const step = innerWidth / validData.length;
                const x = padding.left + i * step + (step - barWidth) / 2;
                const val = values[i];
                const barHeight = Math.max(
                  4,
                  ((val - minVal) / range) * innerHeight
                );
                const y = padding.top + innerHeight - barHeight;
                const isHovered = hoveredIdx === i;

                return (
                  <g
                    key={i}
                    onMouseEnter={() => setHoveredIdx(i)}
                    onMouseLeave={() => setHoveredIdx(null)}
                    className="cursor-pointer transition-all"
                  >
                    <rect
                      x={x}
                      y={y}
                      width={barWidth}
                      height={barHeight}
                      rx={3}
                      fill={isHovered ? "#38BDF8" : color}
                      opacity={isHovered ? 1 : 0.85}
                      className="transition-all duration-150"
                    />
                    {/* X-axis label */}
                    <text
                      x={x + barWidth / 2}
                      y={height - padding.bottom + 18}
                      fill={isHovered ? "#38BDF8" : "#94A3B8"}
                      fontSize="10"
                      fontFamily="monospace"
                      textAnchor="middle"
                      className="truncate"
                    >
                      {labels[i].length > 8
                        ? labels[i].slice(0, 7) + "…"
                        : labels[i]}
                    </text>
                  </g>
                );
              })}
            </g>
          )}

          {/* Line / Scatter Chart Mode */}
          {(type === "line" || type === "scatter") && (
            <g>
              {type === "line" && validData.length > 1 && (
                <polyline
                  fill="none"
                  stroke={color}
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  points={validData
                    .map((_, i) => {
                      const step = innerWidth / (validData.length - 1 || 1);
                      const x = padding.left + i * step;
                      const y =
                        padding.top +
                        innerHeight -
                        ((values[i] - minVal) / range) * innerHeight;
                      return `${x},${y}`;
                    })
                    .join(" ")}
                />
              )}

              {validData.map((d, i) => {
                const step =
                  innerWidth /
                  (validData.length > 1 ? validData.length - 1 : 1);
                const x = padding.left + i * step;
                const y =
                  padding.top +
                  innerHeight -
                  ((values[i] - minVal) / range) * innerHeight;
                const isHovered = hoveredIdx === i;

                return (
                  <g
                    key={i}
                    onMouseEnter={() => setHoveredIdx(i)}
                    onMouseLeave={() => setHoveredIdx(null)}
                    className="cursor-pointer"
                  >
                    <circle
                      cx={x}
                      cy={y}
                      r={isHovered ? 6 : 4}
                      fill={isHovered ? "#38BDF8" : color}
                      stroke="#06090F"
                      strokeWidth="2"
                    />
                    <text
                      x={x}
                      y={height - padding.bottom + 18}
                      fill={isHovered ? "#38BDF8" : "#94A3B8"}
                      fontSize="10"
                      fontFamily="monospace"
                      textAnchor="middle"
                    >
                      {labels[i].length > 7
                        ? labels[i].slice(0, 6) + "…"
                        : labels[i]}
                    </text>
                  </g>
                );
              })}
            </g>
          )}
        </svg>
      </div>

      {/* Interactive Tooltip Card */}
      {hoveredIdx !== null && (
        <div className="mt-2 text-xs font-mono bg-cyan-950/60 border border-cyan-500/30 text-cyan-200 px-3 py-1.5 rounded-lg flex items-center justify-between">
          <span>
            <b>{xKey}:</b> {labels[hoveredIdx]}
          </span>
          <span>
            <b>{yKey || "Value"}:</b> {values[hoveredIdx].toLocaleString()}
          </span>
        </div>
      )}
    </div>
  );
}
