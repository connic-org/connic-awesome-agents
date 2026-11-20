const money = new Intl.NumberFormat("en", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });
const moneyCompact = new Intl.NumberFormat("en", { style: "currency", currency: "EUR", notation: "compact", maximumFractionDigits: 1 });
const count = new Intl.NumberFormat("en");
const countCompact = new Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 1 });
const change = new Intl.NumberFormat("en", { style: "percent", maximumFractionDigits: 1, signDisplay: "exceptZero" });
const percent = new Intl.NumberFormat("en", { style: "percent", maximumFractionDigits: 1 });
const share = new Intl.NumberFormat("en", { style: "percent", maximumFractionDigits: 0 });
const monthShort = new Intl.DateTimeFormat("en", { month: "short", year: "2-digit", timeZone: "UTC" });
const monthLong = new Intl.DateTimeFormat("en", { month: "long", year: "numeric", timeZone: "UTC" });

const $ = (id) => document.getElementById(id);
const escape = (value) => String(value).replace(/[&<>"']/g, (char) => `&#${char.charCodeAt(0)};`);
const sum = (rows, key) => rows.reduce((total, row) => total + row[key], 0);
const ratio = (current, previous) => (previous ? current / previous - 1 : 0);
const monthDate = (month) => new Date(`${month}-01T00:00:00Z`);

function showStatus(kind, title, detail = "") {
  const icon = { loading: "loader-circle", empty: "inbox", error: "triangle-alert" }[kind];
  const tone = kind === "error" ? "text-destructive" : "text-muted-foreground";
  $("content").hidden = true;
  $("status").innerHTML = `
    <div class="flex flex-col items-center rounded-xl border border-dashed bg-card px-6 py-16 text-center">
      <i data-lucide="${icon}" class="size-6 ${tone} ${kind === "loading" ? "animate-spin" : ""}"></i>
      <p class="mt-3 text-sm font-medium">${escape(title)}</p>
      <p class="mt-1 max-w-sm text-sm text-muted-foreground">${escape(detail)}</p>
    </div>`;
}

function delta(value, upIsGood = true) {
  const good = value === 0 ? null : (value > 0) === upIsGood;
  const tone = good === null ? "text-muted-foreground" : good ? "text-success" : "text-destructive";
  const icon = value > 0 ? "arrow-up-right" : value < 0 ? "arrow-down-right" : "minus";
  return `<span class="inline-flex items-center gap-0.5 font-medium tabular-nums ${tone}"><i data-lucide="${icon}" class="size-3.5"></i>${change.format(value)}</span>`;
}

function stat({ label, icon, value, comparison, note = "vs last year" }) {
  return `
    <div class="rounded-xl border bg-card p-5">
      <div class="flex items-center justify-between text-sm text-muted-foreground">
        <span>${escape(label)}</span><i data-lucide="${icon}" class="size-4"></i>
      </div>
      <p class="mt-2 truncate text-3xl font-semibold tracking-tight tabular-nums">${escape(value)}</p>
      <p class="mt-1 flex items-center gap-1.5 text-sm">${comparison ?? ""}<span class="text-muted-foreground">${escape(note)}</span></p>
    </div>`;
}

function renderHeader(data) {
  const { months, stores } = data;
  const growth = ratio(sum(months, "revenue"), sum(months, "previous_revenue"));
  $("eyebrow").textContent = `${data.company} · Sales`;
  $("headline").textContent = `Revenue is ${growth >= 0 ? "up" : "down"} ${percent.format(Math.abs(growth))} on last year`;
  $("period").textContent =
    `${monthLong.format(monthDate(months[0].month))} to ${monthLong.format(monthDate(months.at(-1).month))}, ${stores.length} stores`;
}

function renderStats({ months, stores }) {
  const revenue = sum(months, "revenue");
  const orders = sum(months, "orders");
  const previousRevenue = sum(months, "previous_revenue");
  const previousOrders = sum(months, "previous_orders");
  const best = stores.reduce((top, store) => (store.revenue > top.revenue ? store : top));
  $("stats").innerHTML = [
    stat({ label: "Revenue", icon: "euro", value: moneyCompact.format(revenue), comparison: delta(ratio(revenue, previousRevenue)) }),
    stat({ label: "Orders", icon: "receipt", value: countCompact.format(orders), comparison: delta(ratio(orders, previousOrders)) }),
    stat({
      label: "Average order",
      icon: "shopping-bag",
      value: new Intl.NumberFormat("en", { style: "currency", currency: "EUR" }).format(revenue / orders),
      comparison: delta(ratio(revenue / orders, previousRevenue / previousOrders)),
    }),
    stat({ label: "Top store", icon: "store", value: best.name, note: `${share.format(best.revenue / revenue)} of revenue` }),
  ].join("");
}

let trend;

function renderTrend(months, metric) {
  const format = metric === "revenue" ? money : count;
  const axis = metric === "revenue" ? moneyCompact : countCompact;
  $("trend-title").textContent = `Monthly ${metric}`;
  for (const button of $("metric").querySelectorAll("button")) {
    button.setAttribute("aria-pressed", String(button.dataset.metric === metric));
  }

  const datasets = [
    { label: "This year", data: months.map((row) => row[metric]), fill: true },
    {
      label: "Last year",
      data: months.map((row) => row[`previous_${metric}`]),
      borderColor: "#c3c2b7",
      pointBackgroundColor: "#c3c2b7",
      borderDash: [4, 4],
    },
  ];
  const options = {
    scales: { y: { ticks: { callback: (value) => axis.format(value) } } },
    plugins: {
      tooltip: { callbacks: { label: (item) => ` ${item.dataset.label}: ${format.format(item.parsed.y)}` } },
    },
  };

  if (trend) {
    trend.data.datasets.forEach((dataset, index) => (dataset.data = datasets[index].data));
    trend.options.scales.y.ticks.callback = options.scales.y.ticks.callback;
    trend.options.plugins.tooltip.callbacks.label = options.plugins.tooltip.callbacks.label;
    trend.update();
    return;
  }
  trend = new Chart($("trend"), {
    type: "line",
    data: { labels: months.map((row) => monthShort.format(monthDate(row.month))), datasets },
    options,
  });
}

function renderProducts(products) {
  const sorted = [...products].sort((a, b) => b.revenue - a.revenue);
  new Chart($("products"), {
    type: "bar",
    data: { labels: sorted.map((row) => row.name), datasets: [{ label: "Revenue", data: sorted.map((row) => row.revenue) }] },
    options: {
      indexAxis: "y",
      interaction: { axis: "y" },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (item) => ` ${money.format(item.parsed.x)}` } },
      },
      scales: { x: { ticks: { callback: (value) => moneyCompact.format(value), maxTicksLimit: 5 } } },
    },
  });
}

let storeSort = { key: "revenue", direction: -1 };

function renderStores(stores) {
  const total = sum(stores, "revenue");
  const rows = stores.map((store) => ({ ...store, change: ratio(store.revenue, store.previous_revenue) }));
  const { key, direction } = storeSort;
  rows.sort((a, b) => (typeof a[key] === "string" ? a[key].localeCompare(b[key]) : a[key] - b[key]) * direction);

  $("stores").innerHTML = rows
    .map(
      (store) => `
      <tr class="border-b last:border-0 hover:bg-muted/50">
        <td class="px-5 py-3">
          <div class="font-medium">${escape(store.name)}</div>
          <div class="text-muted-foreground">${escape(store.city)}</div>
        </td>
        <td class="px-5 py-3 text-right tabular-nums">${money.format(store.revenue)}</td>
        <td class="px-5 py-3 text-right">${delta(store.change)}</td>
        <td class="hidden px-5 py-3 sm:table-cell">
          <div class="flex items-center gap-3">
            <div class="h-1.5 w-full max-w-40 rounded-full bg-muted">
              <div class="h-1.5 rounded-full bg-primary" style="width: ${((store.revenue / total) * 100).toFixed(1)}%"></div>
            </div>
            <span class="w-9 text-right tabular-nums text-muted-foreground">${share.format(store.revenue / total)}</span>
          </div>
        </td>
      </tr>`,
    )
    .join("");

  for (const header of document.querySelectorAll("th[aria-sort]")) {
    const sortKey = header.querySelector("button").dataset.sort;
    header.setAttribute("aria-sort", sortKey === key ? (direction > 0 ? "ascending" : "descending") : "none");
  }
}

async function main() {
  showStatus("loading", "Loading sales");
  let data;
  try {
    const response = await fetch("./data.json");
    if (!response.ok) throw new Error(`The data could not be loaded (${response.status}).`);
    data = await response.json();
  } catch (error) {
    showStatus("error", "Sales could not be loaded", error.message);
    return;
  }
  if (!data.months?.length) {
    showStatus("empty", "No sales yet", "Once the first month is recorded, revenue and orders show up here.");
    return;
  }

  $("status").replaceChildren();
  $("content").hidden = false;
  renderHeader(data);
  renderStats(data);
  renderTrend(data.months, "revenue");
  renderProducts(data.products);
  renderStores(data.stores);

  $("metric").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-metric]");
    if (button) renderTrend(data.months, button.dataset.metric);
  });
  document.querySelector("thead").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-sort]");
    if (!button) return;
    const key = button.dataset.sort;
    storeSort = { key, direction: storeSort.key === key ? -storeSort.direction : key === "name" ? 1 : -1 };
    renderStores(data.stores);
  });
}

main();
