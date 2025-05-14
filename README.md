# 🔤 Grammar Checker: Verificación de Equivalencia de Gramáticas 📏🔍

Compara dos gramáticas libres de contexto y verifica (aproximadamente) si generan el mismo lenguaje, mediante generación de cadenas y búsqueda de mapeos entre no terminales. Todo de forma interactiva con **Streamlit**.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://grammar-checker.streamlit.app/) <!-- Reemplaza el enlace con el de tu app -->

---

## 🌟 Características Principales

* 🧩 **Análisis de Equivalencia Aproximada:**

  * Genera cadenas terminales hasta una profundidad y longitud definidas para ambas gramáticas.
  * Compara conjuntos de cadenas para determinar equivalencia.
* 🔄 **Búsqueda de Mapeos de No Terminales:**

  * Intenta permutaciones de mapeo entre símbolos no terminales para igualar los lenguajes.
  * Presenta el mapeo sugerido y reevalúa tras aplicar la correspondencia.
* ⚙️ **Configuración Avanzada:**

  * Ajusta manualmente la profundidad máxima de derivación y la longitud máxima de las cadenas.
  * Modalidad automática para definir parámetros según el tamaño de las gramáticas.
* 🔡 **Soporte de Sintaxis Flexible:**

  * Acepta `→` o `->` para producciones.
  * Usa `|` para separar alternativas y `*` o `ε` para epsilon.
* 💻 **Visualización Clara:**

  * Muestra cadenas generadas para cada gramática.
  * Destaca diferencias y reporta si son equivalentes con o sin mapeo.
* 🎨 **Interfaz Intuitiva:**

  * Diseño limpio, dos paneles para ingresar las gramáticas y ajustes en la barra lateral.

---

## 🚀 Cómo Empezar

### 1. Prerrequisitos

* Python 3.8 o superior
* Git

### 2. Clonar el Repositorio

```bash
git clone https://github.com/thezulux24/grammar_checker.git
cd grammar_checker
```

### 3. Crear un Entorno Virtual (Recomendado)

```bash
python -m venv venv
# En Windows
venv\\Scripts\\activate
# En macOS/Linux
source venv/bin/activate
```

### 4. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 5. Ejecutar la Aplicación

```bash
streamlit run app.py
```

Abre tu navegador en `http://localhost:8501` (o la URL que indique Streamlit).

---

## 📝 Formato de Entrada

* Usa `→` o `->` para separar cabeza y producciones.
* Separa alternativas con `|`.
* Representa epsilon con `*` o `ε`.

**Ejemplo Gramática:**

```text
D -> DA | DE | b | CA | DD | a
E -> AD
S -> DA | * | DS | DE | b | CA | DD | a
C -> b
A -> a | DA | DE | DD
```

---

## 🔧 Configuraciones

* **Profundidad Máxima (max\_depth):** Número de derivaciones recursivas (por defecto 10).
* **Longitud Máxima (max\_len):** Longitud de las cadenas generadas (por defecto 20).
* Modo automático ajusta estas variables según el número de no terminales.

---

## 📌 Estado Actual

* ✅ Generación y comparación de cadenas (completo)
* ✅ Búsqueda de mapeos de no terminales
* 🔧 Ajuste automático de parámetros

---

## 🧠 ¿Para qué sirve?

Ideal para profesores y estudiantes de **Teoría de Lenguajes** y **Compiladores**, facilita:

1. Verificar si dos gramáticas definen el mismo lenguaje.
2. Explorar divergencias y diferencias en producciones.
3. Entender correspondencias entre símbolos no terminales.

---

## 📬 Contribuciones

¡Contribuye con mejoras y nuevos casos de prueba!

1. Haz un fork del proyecto.
2. Crea tu branch: `git checkout -b feature/tu-feature`.
3. Haz commit: `git commit -m "Describe tu cambio"`.
4. Envía tu branch: `git push origin feature/tu-feature`.
5. Abre un Pull Request.

---

## 👨‍💻 Autor

**Brayan Zuluaga**
💼 [Looplink](https://looplink.co) — Desarrollo web y consultoría.
