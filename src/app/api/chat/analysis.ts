type Row = Record<string, unknown>;

export function queryDataset(rows: Row[], args: Record<string, unknown>) {
  const columns = [...new Set(rows.flatMap(Object.keys))];
  const operation = String(args.operation || "profile");
  if (operation === "profile") {
    return { rows: rows.length, columns: columns.map((column) => {
      const values = rows.map(row => row[column]);
      const present = values.filter(value => value !== null && value !== undefined && value !== "");
      const numeric = present.length > 0 && present.every(value => typeof value === "number" && Number.isFinite(value));
      const numbers = numeric ? present as number[] : [];
      return { name: column, missing: values.length - present.length,
        unique: new Set(present.map(value => JSON.stringify(value))).size,
        examples: [...new Set(present.map(String))].slice(0, 5),
        ...(numeric ? { min: Math.min(...numbers), max: Math.max(...numbers),
          sum: numbers.reduce((a, b) => a + b, 0), mean: numbers.reduce((a, b) => a + b, 0) / numbers.length } : {}) };
    }) };
  }
  if (!["count", "sum", "mean", "min", "max"].includes(operation)) throw new Error("Unsupported operation. Use profile, count, sum, mean, min, or max.");
  const column = String(args.column || "");
  const groupBy = String(args.group_by || "");
  if (operation !== "count" && !columns.includes(column)) throw new Error("Choose an existing numeric column.");
  if (groupBy && !columns.includes(groupBy)) throw new Error("Group column does not exist.");
  const groups = new Map<unknown, Row[]>();
  for (const row of rows) {
    const key = groupBy ? row[groupBy] ?? null : "all";
    groups.set(key, [...(groups.get(key) || []), row]);
  }
  if (!groupBy && !rows.length) groups.set("all", []);
  return { operation, column, group_by: groupBy || null, results: [...groups].map(([group, entries]) => {
    const present = entries.map(row => row[column]).filter(value => value !== null && value !== undefined && value !== "");
    if (operation !== "count" && present.some(value => typeof value !== "number" || !Number.isFinite(value))) throw new Error("This operation requires a numeric column.");
    const values = present as number[];
    const sum = values.reduce((a, b) => a + b, 0);
    const value = operation === "count" ? entries.length : !values.length ? null : operation === "sum" ? sum : operation === "mean" ? sum / values.length : operation === "min" ? Math.min(...values) : Math.max(...values);
    return { group, value };
  }) };
}
