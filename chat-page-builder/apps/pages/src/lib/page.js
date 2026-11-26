// The look every published page shares. Pages load it after tailwind.js,
// chart.js and lucide.js (see page-examples/dashboard/index.html). Pages load
// it from this build, so a change here restyles every page on the next deploy.

const colors = {
  background: "#f7f7f5",
  foreground: "#0b0b0b",
  card: "#ffffff",
  muted: "#f0efec",
  mutedForeground: "#6b6a64",
  border: "#e7e6e1",
  primary: "#256abf",
  primaryForeground: "#ffffff",
  success: "#006300",
  warning: "#a15c00",
  destructive: "#d03b3b",
};

// Categorical order validated for color-blind separation; keep the order.
const series = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"];

const kebab = (name) => name.replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`);

const theme = document.createElement("style");
theme.type = "text/tailwindcss";
theme.textContent = `
@theme {
  --font-sans: "Inter Variable", ui-sans-serif, system-ui, sans-serif;
${Object.entries(colors).map(([name, value]) => `  --color-${kebab(name)}: ${value};`).join("\n")}
${series.map((value, index) => `  --color-chart-${index + 1}: ${value};`).join("\n")}
}
@layer base {
  *, ::before, ::after { border-color: var(--color-border); }
  body {
    background: var(--color-background);
    color: var(--color-foreground);
    -webkit-font-smoothing: antialiased;
  }
}
body { opacity: 1; }
`;
document.head.append(theme);

window.theme = { colors, series };

function withAlpha(hex, alpha) {
  const value = Number.parseInt(hex.slice(1), 16);
  return `rgba(${value >> 16}, ${(value >> 8) & 255}, ${value & 255}, ${alpha})`;
}

if (window.Chart) {
  const { defaults } = Chart;
  defaults.font.family = '"Inter Variable", ui-sans-serif, system-ui, sans-serif';
  defaults.font.size = 12;
  defaults.color = colors.mutedForeground;
  defaults.borderColor = colors.border;
  defaults.maintainAspectRatio = false;
  defaults.animation.duration = 500;
  defaults.interaction.mode = "index";
  defaults.interaction.intersect = false;

  defaults.plugins.colors.enabled = false;
  Object.assign(defaults.plugins.legend, { position: "top", align: "end" });
  Object.assign(defaults.plugins.legend.labels, {
    usePointStyle: true,
    pointStyle: "circle",
    boxWidth: 8,
    boxHeight: 8,
    padding: 16,
    color: colors.foreground,
  });
  Object.assign(defaults.plugins.tooltip, {
    backgroundColor: "#1a1a19",
    titleColor: "#ffffff",
    bodyColor: "#e7e6e1",
    titleFont: { weight: "600" },
    padding: 10,
    cornerRadius: 8,
    boxPadding: 4,
    usePointStyle: true,
  });

  Object.assign(defaults.elements.line, { borderWidth: 2, tension: 0.3, borderCapStyle: "round", borderJoinStyle: "round" });
  Object.assign(defaults.elements.point, { radius: 0, hoverRadius: 5, hitRadius: 12, borderWidth: 2, hoverBorderWidth: 2 });
  Object.assign(defaults.elements.bar, { borderRadius: 4, borderSkipped: "start" });
  Object.assign(defaults.elements.arc, { borderWidth: 2, borderColor: colors.card });
  defaults.datasets.bar.maxBarThickness = 24;
  defaults.datasets.doughnut.cutout = "68%";

  defaults.scale.border.display = false;
  defaults.scale.grid.color = colors.border;
  defaults.scale.ticks.padding = 8;
  defaults.set("scales.category", { grid: { display: false } });

  // Series colors in palette order for datasets that set none of their own.
  Chart.register({
    id: "pageColors",
    beforeUpdate(chart) {
      const radial = ["doughnut", "pie", "polarArea"].includes(chart.config.type);
      chart.data.datasets.forEach((dataset, index) => {
        if (radial) {
          dataset.backgroundColor ??= dataset.data.map((_, slice) => series[slice % series.length]);
          return;
        }
        const color = series[index % series.length];
        const line = (dataset.type ?? chart.config.type) === "line";
        dataset.borderColor ??= color;
        dataset.backgroundColor ??= line ? withAlpha(color, 0.1) : color;
        if (line) {
          dataset.pointBackgroundColor ??= dataset.borderColor;
          dataset.pointBorderColor ??= colors.card;
        }
      });
    },
  });

  // Charts drawn before the font arrived would keep the fallback font.
  document.fonts.load('500 12px "Inter Variable"').then(() => {
    for (const chart of Object.values(Chart.instances)) chart.update("none");
  });
}

// <i data-lucide="name"></i> becomes an SVG icon, also when added later.
// Rendered icons keep data-lucide, so only <i> placeholders trigger a pass.
if (window.lucide) {
  let frame = 0;
  const render = () => {
    frame = 0;
    if (document.querySelector("i[data-lucide]")) lucide.createIcons({ attrs: { "stroke-width": 1.75 } });
  };
  new MutationObserver(() => {
    frame ||= requestAnimationFrame(render);
  }).observe(document.documentElement, { childList: true, subtree: true });
  document.addEventListener("DOMContentLoaded", render);
}
