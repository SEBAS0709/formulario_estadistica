const formulas = []
const categories = [
  "Tendencia Central",
  "Medidas de Dispersión",
  "Medidas de Posición",
  "Probabilidad",
  "Distribución Binomial",
]

const formulaList = document.querySelector("#formulaList")
const categoryList = document.querySelector("#categoryList")
const favoritesList = document.querySelector("#favoritesList")
const detailCard = document.querySelector("#formulaDetail")
const searchInput = document.querySelector("#searchInput")
const themeToggle = document.querySelector("#toggle-theme")

let activeFormulaId = null
let favorites = JSON.parse(localStorage.getItem("statformula_favorites") || "[]")
let calculations = JSON.parse(localStorage.getItem("statformula_history") || "[]")
let formulaEditors = {}
let liveCalculationTimer = null
let usageChartInstance = null
let historyChartInstance = null

const parseNumericValue = (value) => {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : 0
}

const formatValue = (value) => {
  if (Array.isArray(value)) return value.join(", ")
  if (typeof value === "number") {
    return Number.isInteger(value) ? value.toString() : value.toFixed(3).replace(/\.0+$/, "").replace(/(\.\d*[1-9])0+$/, "$1")
  }
  return value
}

const parseExampleValues = (formula) => {
  if (!formula.example) return []
  return formula.example.split(",").map((item) => parseNumericValue(item.trim())).filter((value) => value !== 0 || formula.example.includes("0"))
}

const getDefaultValues = (formula) => {
  const name = formula.name.toLowerCase()
  if (name.includes("probabilidad simple")) return [3, 10]
  if (name.includes("complementaria")) return [0.7]
  if (name.includes("regla de la suma")) return [0.3, 0.5, 0.2]
  if (name.includes("probabilidad condicional")) return [0.2, 0.5]
  if (name.includes("regla del producto")) return [0.4, 0.7]
  if (name.includes("binomial")) return [4, 2, 0.5]
  const parsed = parseExampleValues(formula)
  return parsed.length ? parsed : [10, 20, 30, 40]
}

const getEditorConfig = (formula) => {
  const name = formula.name.toLowerCase()
  if (name.includes("probabilidad simple")) return { kind: "pair", labels: ["Favorable", "Total"] }
  if (name.includes("complementaria")) return { kind: "single", labels: ["P(A)"] }
  if (name.includes("regla de la suma")) return { kind: "triple", labels: ["P(A)", "P(B)", "P(A∩B)"] }
  if (name.includes("probabilidad condicional")) return { kind: "pair", labels: ["P(A∩B)", "P(B)"] }
  if (name.includes("regla del producto")) return { kind: "pair", labels: ["P(A)", "P(B|A)"] }
  if (name.includes("binomial")) return { kind: "triple", labels: ["n", "x", "p"] }
  return { kind: "list" }
}

const loadFormulas = async () => {
  const response = await fetch("/api/formulas")
  const data = await response.json()
  formulas.splice(0, formulas.length, ...data)
  renderCategories()
  renderFormulas(formulas)
}

const renderCategories = () => {
  categoryList.innerHTML = ""
  categories.forEach((category) => {
    const li = document.createElement("li")
    li.textContent = category
    li.addEventListener("click", () => {
      document.querySelectorAll(".sidebar-section li").forEach((item) => item.classList.remove("active"))
      li.classList.add("active")
      const filtered = formulas.filter((item) => item.category === category)
      renderFormulas(filtered)
    })
    categoryList.appendChild(li)
  })
}

const renderFormulas = (list) => {
  formulaList.innerHTML = ""
  list.forEach((formula) => {
    const card = document.createElement("div")
    card.className = "formula-card"
    card.innerHTML = `<h4>${formula.name}</h4><p>${formula.description}</p>`
    card.addEventListener("click", () => selectFormula(formula.id))
    if (formula.id === activeFormulaId) card.classList.add("active")
    formulaList.appendChild(card)
  })
}

const renderFavorites = () => {
  favoritesList.innerHTML = ""
  favorites.forEach((id) => {
    const formula = formulas.find((item) => item.id === id)
    if (!formula) return
    const li = document.createElement("li")
    li.textContent = formula.name
    li.addEventListener("click", () => selectFormula(formula.id))
    favoritesList.appendChild(li)
  })
}

const selectFormula = (id) => {
  activeFormulaId = id
  renderFormulas(formulas)
  const formula = formulas.find((item) => item.id === id)
  if (!formula) return

  if (!formulaEditors[formula.id]) {
    formulaEditors[formula.id] = { values: getDefaultValues(formula) }
  }

  const editor = formulaEditors[formula.id]
  detailCard.innerHTML = `
    <div class="detail-header">
      <div>
        <h2>${formula.name}</h2>
        <p>${formula.purpose}</p>
      </div>
      <button id="favoriteBtn" class="favorite-btn">${favorites.includes(id) ? "★ Favorito" : "☆ Añadir favorito"}</button>
    </div>
    <div class="detail-block">
      <h3>Fórmula</h3>
      <div class="detail-expression">
        <div class="formula-visual">${formula.expression}</div>
        <div class="formula-editor" id="formulaEditor"></div>
      </div>
    </div>
    <div class="detail-block">
      <h3>Variables</h3>
      <ul>${formula.variables.map((variable) => `<li><strong>${variable.name}:</strong> ${variable.description}</li>`).join("")}</ul>
    </div>
    <div class="detail-block">
      <h3>Descripción</h3>
      <p>${formula.description}</p>
    </div>
    <div class="result-panel" id="resultPanel" style="display:none;"></div>
  `

  document.querySelector("#favoriteBtn").addEventListener("click", () => toggleFavorite(formula.id))
  renderEditorControls(formula, editor)
  runLiveCalculation(formula)
}

const renderEditorControls = (formula, editor) => {
  const container = document.querySelector("#formulaEditor")
  const config = getEditorConfig(formula)

  if (config.kind === "list") {
    container.innerHTML = `
      <div class="formula-chip-row">
        ${editor.values.map((value, index) => `
          <label class="formula-chip">
            <span>${index + 1}</span>
            <input type="number" step="any" value="${value}" data-index="${index}" />
            <button type="button" class="chip-remove" data-action="remove" data-index="${index}">×</button>
          </label>
        `).join("")}
      </div>
      <button type="button" class="formula-action-btn" data-action="add">+ Agregar</button>
    `
  } else {
    const values = editor.values.length ? editor.values : [0]
    container.innerHTML = `
      <div class="formula-chip-row">
        ${values.map((value, index) => `
          <label class="formula-chip formula-chip-stacked">
            <span>${config.labels[index] || `Valor ${index + 1}`}</span>
            <input type="number" step="any" value="${value}" data-index="${index}" />
          </label>
        `).join("")}
      </div>
    `
  }

  container.querySelectorAll("input").forEach((input) => input.addEventListener("input", (event) => handleEditorInput(formula, event)))
  container.querySelectorAll("[data-action='add']").forEach((button) => button.addEventListener("click", () => addEditorValue(formula)))
  container.querySelectorAll("[data-action='remove']").forEach((button) => button.addEventListener("click", () => removeEditorValue(formula, Number(button.dataset.index))))
}

const handleEditorInput = (formula, event) => {
  const index = Number(event.target.dataset.index)
  const value = event.target.value
  const editor = formulaEditors[formula.id]
  if (!editor) return
  editor.values[index] = parseNumericValue(value)
  scheduleLiveCalculation(formula)
}

const addEditorValue = (formula) => {
  const editor = formulaEditors[formula.id]
  if (!editor) return
  editor.values.push(0)
  renderEditorControls(formula, editor)
  scheduleLiveCalculation(formula)
}

const removeEditorValue = (formula, index) => {
  const editor = formulaEditors[formula.id]
  if (!editor) return
  editor.values.splice(index, 1)
  renderEditorControls(formula, editor)
  scheduleLiveCalculation(formula)
}

const toggleFavorite = (id) => {
  if (favorites.includes(id)) {
    favorites = favorites.filter((item) => item !== id)
  } else {
    favorites.push(id)
  }
  localStorage.setItem("statformula_favorites", JSON.stringify(favorites))
  renderFavorites()
  selectFormula(id)
}

const validateInputs = (formula, values) => {
  const name = formula.name.toLowerCase()

  if (values.some((value) => value === "" || value === null || Number.isNaN(Number(value)))) {
    throw new Error("Ingresa solo números válidos.")
  }

  if (name.includes("probabilidad") || name.includes("complementaria") || name.includes("regla") || name.includes("binomial")) {
    if (name.includes("binomial")) {
      const [n, x, p] = values
      if (n < 0 || x < 0 || x > n) throw new Error("Para binomial, x debe estar entre 0 y n, y n debe ser válido.")
      if (p < 0 || p > 1) throw new Error("La probabilidad debe estar entre 0 y 1.")
      return
    }

    if (name.includes("probabilidad simple")) {
      const [favorable, total] = values
      if (total === 0) throw new Error("No se puede dividir entre cero.")
      if (favorable < 0 || total < 0) throw new Error("Los valores deben ser positivos.")
      return
    }

    if (name.includes("complementaria")) {
      const [probability] = values
      if (probability < 0 || probability > 1) throw new Error("La probabilidad debe estar entre 0 y 1.")
      return
    }

    if (name.includes("regla de la suma") || name.includes("probabilidad condicional") || name.includes("regla del producto")) {
      const invalid = values.some((value) => value < 0 || value > 1)
      if (invalid) throw new Error("Las probabilidades deben estar entre 0 y 1.")
      return
    }
  }

  if (values.length > 0 && values.some((value) => value === 0)) {
    return
  }
}

const scheduleLiveCalculation = (formula) => {
  clearTimeout(liveCalculationTimer)
  liveCalculationTimer = setTimeout(() => runLiveCalculation(formula), 250)
}

const runLiveCalculation = async (formula) => {
  const editor = formulaEditors[formula.id]
  if (!editor) return

  try {
    validateInputs(formula, editor.values)
    const response = await fetch("/api/calculations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ formula_id: formula.id, formula_name: formula.name, values: editor.values }),
    })
    const result = await response.json()
    if (!response.ok) throw new Error(result.error || "No se pudo calcular")
    showResult(result)
    calculations.push({
      formula_name: result.formula_name,
      input_data: result.input_data,
      result: typeof result.result === "object" ? JSON.stringify(result.result) : String(result.result),
      created_at: new Date().toISOString(),
    })
    localStorage.setItem("statformula_history", JSON.stringify(calculations))
    updateCharts()
  } catch (error) {
    showError(error.message)
  }
}

const showResult = (result) => {
  const resultPanel = document.querySelector("#resultPanel")
  if (!resultPanel) return
  resultPanel.style.display = "block"
  const displayResult = typeof result.result === "object" && result.result !== null && !Array.isArray(result.result)
    ? Object.entries(result.result)
    : [["Resultado", result.result]]

  resultPanel.innerHTML = `
    <div class="result-card">
      <div class="result-highlight">
        <span>Resultado</span>
        <strong>${displayResult.map(([label, value]) => `${label}: ${formatValue(value)}`).join(" • ")}</strong>
      </div>
      <div class="result-steps">
        ${result.steps.map((step) => `<div class="result-step">${step}</div>`).join("")}
      </div>
    </div>
  `
}

const showError = (message) => {
  const resultPanel = document.querySelector("#resultPanel")
  if (!resultPanel) return
  resultPanel.style.display = "block"
  resultPanel.innerHTML = `<div class="result-card result-error">${message}</div>`
}

const filterFormulas = () => {
  const value = searchInput.value.toLowerCase()
  renderFormulas(formulas.filter((formula) => formula.name.toLowerCase().includes(value)))
}

const updateCharts = () => {
  const formulaCounts = calculations.reduce((acc, item) => {
    acc[item.formula_name] = (acc[item.formula_name] || 0) + 1
    return acc
  }, {})

  const usageChart = document.querySelector("#usageChart")
  if (usageChartInstance) usageChartInstance.destroy()
  usageChartInstance = new Chart(usageChart, {
    type: "bar",
    data: {
      labels: Object.keys(formulaCounts),
      datasets: [{ label: "Usos", data: Object.values(formulaCounts), backgroundColor: "rgba(37, 99, 235, 0.6)" }],
    },
    options: { responsive: true, plugins: { legend: { display: false } } },
  })

  const byDay = calculations.reduce((acc, item) => {
    const day = new Date(item.created_at).toLocaleDateString()
    acc[day] = (acc[day] || 0) + 1
    return acc
  }, {})

  const historyChart = document.querySelector("#historyChart")
  if (historyChartInstance) historyChartInstance.destroy()
  historyChartInstance = new Chart(historyChart, {
    type: "line",
    data: {
      labels: Object.keys(byDay),
      datasets: [{ label: "Cálculos", data: Object.values(byDay), borderColor: "#2563eb", backgroundColor: "rgba(37, 99, 235, 0.18)", fill: true, tension: 0.4 }],
    },
    options: { responsive: true, plugins: { legend: { display: false } } },
  })
}

const setupTheme = () => {
  const currentTheme = localStorage.getItem("statformula_theme") || "light"
  document.documentElement.setAttribute("data-theme", currentTheme)
  themeToggle.textContent = currentTheme === "dark" ? "Modo claro" : "Modo oscuro"
}

const toggleTheme = () => {
  const current = document.documentElement.getAttribute("data-theme")
  const next = current === "dark" ? "light" : "dark"
  document.documentElement.setAttribute("data-theme", next)
  localStorage.setItem("statformula_theme", next)
  themeToggle.textContent = next === "dark" ? "Modo claro" : "Modo oscuro"
}

searchInput.addEventListener("input", filterFormulas)
themeToggle.addEventListener("click", toggleTheme)

loadFormulas()
renderFavorites()
setupTheme()
updateCharts()
