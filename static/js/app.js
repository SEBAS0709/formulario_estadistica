const formulas = []
const categories = [
  "Tendencia Central",
  "Medidas de Dispersión",
  "Medidas de Posición",
  "Probabilidad",
  "Distribución Binomial",
  "Distribución Normal",
  "Correlación y Regresión",
  "Intervalos de Confianza",
  "Pruebas de Hipótesis",
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

const loadFormulas = async () => {
  const response = await fetch("/api/formulas")
  const data = await response.json()
  formulas.push(...data)
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

  detailCard.innerHTML = `
    <div class="detail-header">
      <div>
        <h2>${formula.name}</h2>
        <p>${formula.purpose}</p>
      </div>
      <button id="favoriteBtn">${favorites.includes(id) ? "★ Favorito" : "☆ Añadir favorito"}</button>
    </div>
    <div class="detail-block">
      <h3>Fórmula</h3>
      <div class="detail-expression">${formula.expression}</div>
    </div>
    <div class="detail-block">
      <h3>Variables</h3>
      <ul>${formula.variables.map((variable) => `<li><strong>${variable.name}:</strong> ${variable.description}</li>`).join("")}</ul>
    </div>
    <div class="detail-block">
      <h3>Descripción</h3>
      <p>${formula.description}</p>
    </div>
    <form class="formulas-form" id="calculatorForm">
      ${formula.inputs.map((input) => `
        <label>${input.label}
          <input name="${input.name}" type="${input.type}" placeholder="${input.example || "Ingresa los valores"}" required />
        </label>
      `).join("")}
      <button type="submit">Calcular</button>
    </form>
    <div class="result-panel" id="resultPanel" style="display:none;"></div>
  `

  document.querySelector("#favoriteBtn").addEventListener("click", () => toggleFavorite(formula.id))
  document.querySelector("#calculatorForm").addEventListener("submit", handleCalculation)
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

const handleCalculation = async (event) => {
  event.preventDefault()
  const form = event.target
  const data = Object.fromEntries(new FormData(form).entries())
  const formulaId = activeFormulaId

  const response = await fetch("/api/calculations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ formula_id: formulaId, values: data.values }),
  })

  const result = await response.json()
  if (response.ok) {
    showResult(result)
    calculations.push({
      formula_name: result.formula_name,
      input_data: result.input_data,
      result: result.result,
      created_at: new Date().toISOString(),
    })
    localStorage.setItem("statformula_history", JSON.stringify(calculations))
    updateCharts()
  }
}

const showResult = (result) => {
  const resultPanel = document.querySelector("#resultPanel")
  resultPanel.style.display = "block"
  resultPanel.innerHTML = `
    <strong>Resultado final:</strong>
    <p>${result.result}</p>
    <strong>Procedimiento paso a paso:</strong>
    <ol class="steps-list">${result.steps.map((step) => `<li>${step}</li>`).join("")}</ol>
  `
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
  new Chart(usageChart, {
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
  new Chart(historyChart, {
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
