import { useState } from 'react';

/**
 * Lightweight, zero-dependency SVG Bar Chart
 * Beautiful, responsive, and tailored for SaaS metrics display.
 */
export default function SimpleBarChart({
  data = [],
  xKey = 'label',
  yKey = 'value',
  height = 220,
  barColor = '#2563EB',
  title = '',
}) {
  const [hoveredIndex, setHoveredIndex] = useState(null);

  if (!data || data.length === 0) {
    return (
      <div className="flex h-40 items-center justify-center text-xs text-slate-400">
        No chart data available
      </div>
    );
  }

  // Safe numerical extraction
  const chartData = data.slice(0, 12).map((item) => ({
    label: String(item[xKey] ?? ''),
    value: Number(item[yKey]) || 0,
  }));

  const maxValue = Math.max(...chartData.map((d) => d.value), 1);
  const paddingBottom = 30;
  const paddingTop = 20;
  const paddingLeft = 40;
  const paddingRight = 20;

  const chartWidth = 500;
  const usableWidth = chartWidth - paddingLeft - paddingRight;
  const usableHeight = height - paddingTop - paddingBottom;
  const barWidth = Math.min(36, Math.max(12, usableWidth / chartData.length - 12));

  return (
    <div className="w-full">
      {title && <h4 className="text-xs font-semibold text-slate-700 mb-2">{title}</h4>}
      <div className="relative w-full overflow-hidden">
        <svg
          viewBox={`0 0 ${chartWidth} ${height}`}
          className="w-full h-auto overflow-visible select-none"
        >
          {/* Horizontal grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((ratio, idx) => {
            const y = paddingTop + usableHeight * (1 - ratio);
            const val = Math.round(maxValue * ratio);
            return (
              <g key={idx}>
                <line
                  x1={paddingLeft}
                  y1={y}
                  x2={chartWidth - paddingRight}
                  y2={y}
                  stroke="#F1F5F9"
                  strokeWidth="1"
                />
                <text
                  x={paddingLeft - 8}
                  y={y + 3}
                  textAnchor="end"
                  className="text-[10px] fill-slate-400 font-mono"
                >
                  {val > 9999 ? `${(val / 1000).toFixed(0)}k` : val}
                </text>
              </g>
            );
          })}

          {/* Bars */}
          {chartData.map((item, index) => {
            const totalSlots = chartData.length;
            const slotWidth = usableWidth / totalSlots;
            const x = paddingLeft + index * slotWidth + (slotWidth - barWidth) / 2;
            const barHeight = Math.max(3, (item.value / maxValue) * usableHeight);
            const y = paddingTop + usableHeight - barHeight;
            const isHovered = hoveredIndex === index;

            return (
              <g
                key={index}
                onMouseEnter={() => setHoveredIndex(index)}
                onMouseLeave={() => setHoveredIndex(null)}
                className="cursor-pointer transition-opacity"
              >
                {/* Bar rectangle */}
                <rect
                  x={x}
                  y={y}
                  width={barWidth}
                  height={barHeight}
                  rx="3"
                  fill={isHovered ? '#1D4ED8' : barColor}
                  className="transition-all duration-150"
                />

                {/* Value label on hover or if room */}
                {isHovered && (
                  <text
                    x={x + barWidth / 2}
                    y={y - 6}
                    textAnchor="middle"
                    className="text-[10px] font-semibold fill-slate-800"
                  >
                    {item.value}
                  </text>
                )}

                {/* X axis category label */}
                <text
                  x={x + barWidth / 2}
                  y={height - 10}
                  textAnchor="middle"
                  className="text-[10px] fill-slate-500 truncate"
                  style={{ maxWidth: slotWidth }}
                >
                  {item.label.length > 8 ? `${item.label.slice(0, 7)}…` : item.label}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
