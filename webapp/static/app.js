(() => {
  const form = document.getElementById("game-form");
  const exampleSelect = document.getElementById("example");
  const playerName = document.getElementById("player-name");
  const opponentName = document.getElementById("opponent-name");
  const rowCount = document.getElementById("row-count");
  const colCount = document.getElementById("col-count");
  const matrixEditor = document.getElementById("matrix-editor");
  const mixedMethod = document.getElementById("mixed-method");
  const useWeakly = document.getElementById("use-weakly");
  const solveButton = document.getElementById("solve-button");
  const resetButton = document.getElementById("reset-button");
  const results = document.getElementById("results");
  const alertRegion = document.getElementById("alert-region");

  const DEFAULT_GAME = {
    player_name: "P",
    opponent_name: "O",
    player_strategies: ["P_S0", "P_S1"],
    opponent_strategies: ["O_S0", "O_S1"],
    cells: [
      [
        [1, 0],
        [0, 1],
      ],
      [
        [0, 1],
        [1, 0],
      ],
    ],
  };

  let rowNames = DEFAULT_GAME.player_strategies.slice();
  let colNames = DEFAULT_GAME.opponent_strategies.slice();
  let cells = DEFAULT_GAME.cells.map((row) => row.map((cell) => cell.slice()));

  function clampSize(value) {
    const size = Number.parseInt(value, 10);
    if (!Number.isFinite(size)) {
      return 2;
    }
    return Math.min(8, Math.max(1, size));
  }

  function resizeMatrix(rows, cols) {
    const nextCells = [];
    const nextRowNames = [];
    const nextColNames = [];
    for (let i = 0; i < rows; i += 1) {
      nextRowNames.push(rowNames[i] || `${playerName.value.trim() || "P"}_S${i}`);
      const row = [];
      for (let j = 0; j < cols; j += 1) {
        row.push(cells[i] && cells[i][j] ? cells[i][j] : [0, 0]);
      }
      nextCells.push(row);
    }
    for (let j = 0; j < cols; j += 1) {
      nextColNames.push(colNames[j] || `${opponentName.value.trim() || "O"}_S${j}`);
    }
    rowNames = nextRowNames;
    colNames = nextColNames;
    cells = nextCells;
  }

  function readEditor() {
    const rows = clampSize(rowCount.value);
    const cols = clampSize(colCount.value);
    const nextCells = [];
    const nextRowNames = [];
    const nextColNames = [];
    for (let j = 0; j < cols; j += 1) {
      const input = document.getElementById(`col-name-${j}`);
      nextColNames.push(input ? input.value.trim() : colNames[j]);
    }
    for (let i = 0; i < rows; i += 1) {
      const nameInput = document.getElementById(`row-name-${i}`);
      nextRowNames.push(nameInput ? nameInput.value.trim() : rowNames[i]);
      const row = [];
      for (let j = 0; j < cols; j += 1) {
        const playerInput = document.getElementById(`cell-${i}-${j}-p`);
        const opponentInput = document.getElementById(`cell-${i}-${j}-o`);
        row.push([
          playerInput ? Number(playerInput.value) : 0,
          opponentInput ? Number(opponentInput.value) : 0,
        ]);
      }
      nextCells.push(row);
    }
    rowNames = nextRowNames;
    colNames = nextColNames;
    cells = nextCells;
  }

  function renderEditor() {
    const table = document.createElement("table");
    table.className = "pf-v5-c-table pf-m-compact";
    table.setAttribute("role", "grid");
    const thead = document.createElement("thead");
    const headRow = document.createElement("tr");
    headRow.appendChild(document.createElement("th"));
    colNames.forEach((name, j) => {
      const th = document.createElement("th");
      const input = document.createElement("input");
      input.id = `col-name-${j}`;
      input.className = "app-name-input";
      input.type = "text";
      input.maxLength = 16;
      input.size = 6;
      input.value = name;
      input.setAttribute("aria-label", `Column strategy ${j + 1} name`);
      th.appendChild(input);
      headRow.appendChild(th);
    });
    thead.appendChild(headRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    cells.forEach((row, i) => {
      const tr = document.createElement("tr");
      const th = document.createElement("th");
      const nameInput = document.createElement("input");
      nameInput.id = `row-name-${i}`;
      nameInput.className = "app-name-input";
      nameInput.type = "text";
      nameInput.maxLength = 16;
      nameInput.size = 6;
      nameInput.value = rowNames[i];
      nameInput.setAttribute("aria-label", `Row strategy ${i + 1} name`);
      th.appendChild(nameInput);
      tr.appendChild(th);
      row.forEach((cell, j) => {
        const td = document.createElement("td");
        const wrap = document.createElement("div");
        wrap.className = "app-cell";
        const playerInput = document.createElement("input");
        playerInput.id = `cell-${i}-${j}-p`;
        playerInput.type = "number";
        playerInput.step = "any";
        playerInput.value = cell[0];
        playerInput.setAttribute("aria-label", `Row payoff ${i + 1},${j + 1}`);
        const sep = document.createElement("span");
        sep.textContent = "|";
        const opponentInput = document.createElement("input");
        opponentInput.id = `cell-${i}-${j}-o`;
        opponentInput.type = "number";
        opponentInput.step = "any";
        opponentInput.value = cell[1];
        opponentInput.setAttribute("aria-label", `Column payoff ${i + 1},${j + 1}`);
        wrap.append(playerInput, sep, opponentInput);
        td.appendChild(wrap);
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    matrixEditor.replaceChildren(table);
  }

  function showAlert(message, variant) {
    const alert = document.createElement("div");
    alert.className = `pf-v5-c-alert pf-m-${variant}`;
    const title = document.createElement("div");
    title.className = "pf-v5-c-alert__title";
    title.textContent = message;
    alert.appendChild(title);
    alertRegion.replaceChildren(alert);
  }

  function clearAlert() {
    alertRegion.replaceChildren();
  }

  function applyGame(game) {
    playerName.value = game.player_name;
    opponentName.value = game.opponent_name;
    rowNames = game.player_strategies;
    colNames = game.opponent_strategies;
    cells = game.cells;
    rowCount.value = String(cells.length);
    colCount.value = String(cells[0].length);
    renderEditor();
  }

  function card(titleText) {
    const cardEl = document.createElement("div");
    cardEl.className = "pf-v5-c-card";
    const header = document.createElement("div");
    header.className = "pf-v5-c-card__header";
    const title = document.createElement("div");
    title.className = "pf-v5-c-card__title";
    const heading = document.createElement("h2");
    heading.className = "pf-v5-c-card__title-text";
    heading.textContent = titleText;
    title.appendChild(heading);
    header.appendChild(title);
    const body = document.createElement("div");
    body.className = "pf-v5-c-card__body";
    cardEl.append(header, body);
    return { card: cardEl, body };
  }

  function labels(items, emptyText) {
    const wrap = document.createElement("div");
    wrap.className = "app-label-list";
    if (!items.length) {
      wrap.textContent = emptyText;
      return wrap;
    }
    items.forEach((item) => {
      const label = document.createElement("span");
      label.className = "pf-v5-c-label";
      const content = document.createElement("span");
      content.className = "pf-v5-c-label__content";
      content.textContent = item;
      label.appendChild(content);
      wrap.appendChild(label);
    });
    return wrap;
  }

  function percent(value) {
    return `${Math.round(value * 1000) / 10}%`;
  }

  function renderEmptyResults() {
    const empty = document.createElement("div");
    empty.className = "pf-v5-c-empty-state pf-m-lg";
    const content = document.createElement("div");
    content.className = "pf-v5-c-empty-state__content";
    const header = document.createElement("div");
    header.className = "pf-v5-c-empty-state__header";
    const title = document.createElement("div");
    title.className = "pf-v5-c-empty-state__title";
    const heading = document.createElement("h2");
    heading.className = "pf-v5-c-title pf-m-lg";
    heading.textContent = "No analysis yet";
    title.appendChild(heading);
    const body = document.createElement("div");
    body.className = "pf-v5-c-empty-state__body";
    body.textContent = "Load an example or enter a payoff matrix, then solve.";
    header.append(title, body);
    content.appendChild(header);
    empty.appendChild(content);
    results.replaceChildren(empty);
  }

  function resetGame() {
    exampleSelect.value = "";
    mixedMethod.value = "support";
    useWeakly.checked = false;
    applyGame({
      player_name: DEFAULT_GAME.player_name,
      opponent_name: DEFAULT_GAME.opponent_name,
      player_strategies: DEFAULT_GAME.player_strategies.slice(),
      opponent_strategies: DEFAULT_GAME.opponent_strategies.slice(),
      cells: DEFAULT_GAME.cells.map((row) => row.map((cell) => cell.slice())),
    });
    renderEmptyResults();
    clearAlert();
  }

  function renderBestResponseGrid(grid) {
    const wrap = document.createElement("div");
    wrap.className = "app-result-matrix";
    const table = document.createElement("table");
    table.className = "pf-v5-c-table pf-m-compact";
    table.setAttribute("aria-label", "Pure Nash best-response grid");
    const thead = document.createElement("thead");
    const head = document.createElement("tr");
    const corner = document.createElement("th");
    corner.textContent = "P \\ O";
    head.appendChild(corner);
    grid.opponent_strategies.forEach((name) => {
      const th = document.createElement("th");
      th.textContent = name;
      head.appendChild(th);
    });
    thead.appendChild(head);
    table.appendChild(thead);
    const tbody = document.createElement("tbody");
    grid.cells.forEach((row, i) => {
      const tr = document.createElement("tr");
      const th = document.createElement("th");
      th.textContent = grid.player_strategies[i];
      tr.appendChild(th);
      row.forEach((cell) => {
        const td = document.createElement("td");
        if (cell.pure_ne) {
          td.className = "app-pure-ne";
        }
        td.textContent = `P ${cell.player_br ? "True" : "False"}, O ${cell.opponent_br ? "True" : "False"}`;
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    wrap.appendChild(table);
    return wrap;
  }

  function renderMatrix(game) {
    const wrap = document.createElement("div");
    wrap.className = "app-result-matrix";
    const table = document.createElement("table");
    table.className = "pf-v5-c-table pf-m-compact";
    const thead = document.createElement("thead");
    const head = document.createElement("tr");
    head.appendChild(document.createElement("th"));
    game.opponent_strategies.forEach((name) => {
      const th = document.createElement("th");
      th.textContent = name;
      head.appendChild(th);
    });
    thead.appendChild(head);
    table.appendChild(thead);
    const tbody = document.createElement("tbody");
    game.cells.forEach((row, i) => {
      const tr = document.createElement("tr");
      const th = document.createElement("th");
      th.textContent = game.player_strategies[i];
      tr.appendChild(th);
      row.forEach((cell) => {
        const td = document.createElement("td");
        td.textContent = `(${cell[0]} | ${cell[1]})`;
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    wrap.appendChild(table);
    return wrap;
  }

  function renderResults(data) {
    const stack = document.createElement("div");
    stack.className = "pf-v5-l-stack pf-m-gutter";

    const matrixCard = card("Payoff matrix");
    matrixCard.body.appendChild(renderMatrix(data.game));
    if (data.constant_sum) {
      const note = document.createElement("p");
      note.textContent = "This game is constant-sum.";
      matrixCard.body.appendChild(note);
    }
    stack.appendChild(matrixCard.card);

    const dominanceCard = card("Dominance");
    ["player", "opponent"].forEach((role) => {
      const heading = document.createElement("h3");
      heading.className = "pf-v5-c-title pf-m-md";
      heading.textContent = role === "player" ? data.game.player_name : data.game.opponent_name;
      dominanceCard.body.appendChild(heading);
      const list = document.createElement("dl");
      [
        ["Strictly dominant", data.dominance[role].strictly_dominant],
        ["Strictly dominated", data.dominance[role].strictly_dominated],
        ["Weakly dominant", data.dominance[role].weakly_dominant],
        ["Weakly dominated", data.dominance[role].weakly_dominated],
      ].forEach(([label, items]) => {
        const dt = document.createElement("dt");
        dt.textContent = label;
        const dd = document.createElement("dd");
        dd.appendChild(labels(items, "none"));
        list.append(dt, dd);
      });
      dominanceCard.body.appendChild(list);
    });
    stack.appendChild(dominanceCard.card);

    const pureCard = card("Pure Nash equilibria");
    const legend = document.createElement("p");
    legend.textContent =
      data.pure_ne_grid && data.pure_ne_grid.legend
        ? data.pure_ne_grid.legend
        : "P = row-player best response, O = column-player best response.";
    pureCard.body.appendChild(legend);
    if (data.pure_ne_grid) {
      pureCard.body.appendChild(renderBestResponseGrid(data.pure_ne_grid));
    }
    if (!data.pure_ne.length) {
      const empty = document.createElement("p");
      empty.textContent = "None identified.";
      pureCard.body.appendChild(empty);
    } else {
      const list = document.createElement("ul");
      data.pure_ne.forEach((eq) => {
        const item = document.createElement("li");
        item.textContent = `${eq.player} and ${eq.opponent}`;
        list.appendChild(item);
      });
      pureCard.body.appendChild(list);
    }
    stack.appendChild(pureCard.card);

    const iedsCard = card("Iterated deletion");
    const log = document.createElement("ul");
    data.ieds.log.forEach((line) => {
      const item = document.createElement("li");
      item.textContent = line;
      log.appendChild(item);
    });
    iedsCard.body.appendChild(log);
    iedsCard.body.appendChild(renderMatrix(data.ieds.reduced));
    stack.appendChild(iedsCard.card);

    const mixedCard = card("Mixed strategies");
    const message = document.createElement("p");
    message.textContent = data.mixed.message;
    mixedCard.body.appendChild(message);
    if (data.mixed.profile) {
      const profile = document.createElement("p");
      profile.textContent = `${data.mixed.profile.player} vs ${data.mixed.profile.opponent}`;
      mixedCard.body.appendChild(profile);
    }
    data.mixed.equilibria.forEach((eq, index) => {
      const heading = document.createElement("h3");
      heading.className = "pf-v5-c-title pf-m-md";
      heading.textContent =
        data.mixed.equilibria.length > 1 ? `Equilibrium ${index + 1}` : "Mix";
      mixedCard.body.appendChild(heading);
      const list = document.createElement("ul");
      eq.player.forEach((item) => {
        const li = document.createElement("li");
        li.textContent = `${data.game.player_name}: ${item.strategy} ${percent(item.probability)}`;
        list.appendChild(li);
      });
      eq.opponent.forEach((item) => {
        const li = document.createElement("li");
        li.textContent = `${data.game.opponent_name}: ${item.strategy} ${percent(item.probability)}`;
        list.appendChild(li);
      });
      mixedCard.body.appendChild(list);
    });
    stack.appendChild(mixedCard.card);

    results.replaceChildren(stack);
  }

  async function loadExample(exampleId) {
    if (!exampleId) {
      return;
    }
    const response = await fetch(`/api/examples/${encodeURIComponent(exampleId)}`);
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Could not load example");
    }
    applyGame(data);
  }

  async function solve(event) {
    event.preventDefault();
    clearAlert();
    readEditor();
    solveButton.disabled = true;
    try {
      const response = await fetch("/api/solve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          player_name: playerName.value,
          opponent_name: opponentName.value,
          player_strategies: rowNames,
          opponent_strategies: colNames,
          cells,
          use_weakly: useWeakly.checked,
          mixed_method: mixedMethod.value,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Solve failed");
      }
      renderResults(data);
    } catch (error) {
      showAlert(error.message, "danger");
    } finally {
      solveButton.disabled = false;
    }
  }

  rowCount.addEventListener("change", () => {
    readEditor();
    resizeMatrix(clampSize(rowCount.value), clampSize(colCount.value));
    rowCount.value = String(cells.length);
    colCount.value = String(cells[0].length);
    renderEditor();
  });
  colCount.addEventListener("change", () => {
    readEditor();
    resizeMatrix(clampSize(rowCount.value), clampSize(colCount.value));
    rowCount.value = String(cells.length);
    colCount.value = String(cells[0].length);
    renderEditor();
  });
  exampleSelect.addEventListener("change", async () => {
    clearAlert();
    try {
      await loadExample(exampleSelect.value);
    } catch (error) {
      showAlert(error.message, "danger");
    }
  });
  resetButton.addEventListener("click", resetGame);
  document.querySelectorAll("[data-theme-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      if (window.GameTheme) {
        window.GameTheme.apply(button.getAttribute("data-theme-mode"));
      }
    });
  });
  if (window.GameTheme) {
    window.GameTheme.apply(window.GameTheme.getMode());
  }
  form.addEventListener("submit", solve);

  renderEditor();
})();
