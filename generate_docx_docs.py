import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_documentation():
    doc = Document()

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Color Palette Constants
    COLOR_PRIMARY = RGBColor(15, 23, 42)       # Slate 900 (Dark Navy)
    COLOR_GOLD = RGBColor(217, 119, 6)         # Gold / Amber 600
    COLOR_EMERALD = RGBColor(16, 185, 129)     # Emerald
    COLOR_TEXT = RGBColor(51, 65, 85)          # Slate 700
    COLOR_MUTED = RGBColor(100, 116, 139)      # Slate 500

    # Styles Setup
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = COLOR_TEXT

    # -------------------------------------------------------------
    # HEADER / TITLE BLOCK
    # -------------------------------------------------------------
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_p.add_run("CineMetric AI")
    title_run.font.name = 'Arial Black'
    title_run.font.size = Pt(26)
    title_run.font.color.rgb = COLOR_GOLD

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = sub_p.add_run("Box Office Prediction & LLM Movie Intelligence Hub")
    sub_run.font.name = 'Arial'
    sub_run.font.size = Pt(15)
    sub_run.font.bold = True
    sub_run.font.color.rgb = COLOR_PRIMARY

    meta_p = doc.add_paragraph()
    meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta_run = meta_p.add_run("Comprehensive Technical Documentation • Feature Specifications • Use Cases • Execution Guide")
    meta_run.font.size = Pt(9.5)
    meta_run.font.italic = True
    meta_run.font.color.rgb = COLOR_MUTED

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # 1. EXECUTIVE SUMMARY
    # -------------------------------------------------------------
    h1 = doc.add_heading("1. Executive Summary & Project Overview", level=1)
    h1.style.font.color.rgb = COLOR_PRIMARY
    h1.style.font.size = Pt(16)
    
    p = doc.add_paragraph(
        "CineMetric AI is a comprehensive, production-ready Machine Learning and Large Language Model (LLM) "
        "theatrical box office intelligence platform. Built on the TMDB (The Movie Database) dataset comprising "
        "over 7,398 movie records (3,000 training instances and 4,398 test instances), this system solves two "
        "fundamental entertainment industry challenges:"
    )
    
    p1 = doc.add_paragraph()
    p1.add_run("1. Real-World Box Office Intelligence on Any Film: ").bold = True
    p1.add_run(
        "Users can query any movie in cinematic history (Hollywood, Bollywood, Tamil, Telugu, Malayalam, "
        "Korean, Anime, European, Classics, or Indie) to instantly retrieve verified box office collections, "
        "budgets, return on investment (ROI), domestic vs. overseas splits, commercial verdicts, and AI-driven "
        "financial post-mortem analysis."
    )
    
    p2 = doc.add_paragraph()
    p2.add_run("2. Machine Learning Predictive Revenue Modeling: ").bold = True
    p2.add_run(
        "Filmmakers, producers, analysts, and movie enthusiasts can simulate prospective theatrical releases "
        "by adjusting parameters (budget, star cast tier, director prestige, release season, franchise attachment, "
        "runtime, and multi-genre tagging) to receive instant revenue forecasts with statistical confidence intervals."
    )

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # -------------------------------------------------------------
    # 2. COMPLETE FEATURE BREAKDOWN, JUSTIFICATION & USE CASES
    # -------------------------------------------------------------
    h2 = doc.add_heading("2. Feature Breakdown, Purpose & Practical Use Cases", level=1)
    h2.style.font.color.rgb = COLOR_PRIMARY
    h2.style.font.size = Pt(16)

    features = [
        {
            "num": "Feature 2.1",
            "name": "Live LLM Box Office Intelligence Engine ('Ask for Any Movie')",
            "why": (
                "Kaggle/TMDB dataset samples only contain historic static data and omit millions of regional, "
                "independent, or modern global releases. Integrating high-performance LLM intelligence (Groq 120B/20B "
                "models, OpenAI, and Gemini) allows the system to possess infinite global movie knowledge across all "
                "languages, decades, and cinema industries."
            ),
            "use_case": (
                "• An investor, distributor, or movie fan enters a title like 'Polladhavan', 'Oppenheimer', 'Kantara', "
                "or 'Avatar: The Way of Water'.\n"
                "• The engine returns verified worldwide gross, production budget, domestic collections, overseas gross, "
                "native currency conversions (e.g. ₹ Crores for Indian titles), ROI percentage, director, top cast, "
                "theatrical run breakdown, key success factors, and trivia facts."
            )
        },
        {
            "num": "Feature 2.2",
            "name": "Machine Learning Revenue Predictor (Interactive Movie Simulator)",
            "why": (
                "Studios and producers need data-driven quantitative financial forecasts before greenlighting projects. "
                "By training advanced ensemble regression models (Gradient Boosting, Random Forest) on 22 engineered "
                "theatrical features, the simulator models complex non-linear interactions between budget, star power, "
                "release timing, and franchise leverage."
            ),
            "use_case": (
                "• Production Planning & Greenlighting: A studio head tests whether increasing a sci-fi action film's "
                "budget from $60M to $120M during May (Summer kickoff) with A-list actors generates a profitable ROI multiplier.\n"
                "• Sensitivity Analysis: Evaluates the revenue uplift of attaching an existing franchise/collection IP "
                "versus releasing as a standalone title."
            )
        },
        {
            "num": "Feature 2.3",
            "name": "Exploratory Data Analysis (EDA) Interactive Analytics Hub",
            "why": (
                "Understanding macroeconomic patterns in film finance is critical for competitive intelligence. Interactive "
                "visual charts reveal macro box office distributions, high-yield genres, release month seasonality, "
                "and budget-to-revenue correlation."
            ),
            "use_case": (
                "• Theatrical Release Strategy: Analysts identify peak earning windows (May, July, December) vs. low-traffic months.\n"
                "• Genre Investment Strategy: Identifies genres with the highest average returns (Animation, Adventure, Sci-Fi) "
                "versus high-risk low-margin genres."
            )
        },
        {
            "num": "Feature 2.4",
            "name": "Multi-Model Benchmarking & Performance Leaderboard",
            "why": (
                "In machine learning, no single algorithm is universally optimal across all tabular distributions. We train "
                "and compare 6 distinct algorithms: Gradient Boosting, Random Forest, HistGradientBoosting, Ridge Regression, "
                "Lasso, and Linear Regression with standardized evaluation metrics (RMSLE, RMSE, R² Score, MAE)."
            ),
            "use_case": (
                "• Model Validation & Transparency: Demonstrates model rigor by showing validation R² (~0.7048) and RMSLE (~1.9907).\n"
                "• Feature Importance Inspection: Shows which factors (Budget, Popularity, Collection, Runtime) drive the largest "
                "Gini gain in revenue prediction."
            )
        },
        {
            "num": "Feature 2.5",
            "name": "Automated Kaggle Test Predictor & Submission Generator",
            "why": (
                "The project is rooted in the TMDB Box Office Prediction Kaggle competition. The engine automatically processes "
                "all 4,398 unlabelled test records, executes log-target transformation predictions, and exports a standardized "
                "submission.csv."
            ),
            "use_case": (
                "• 1-Click Competition Deployment: Directly download 'submission.csv' from the dashboard UI or terminal to "
                "submit to competitive leaderboards or benchmark evaluation scripts."
            )
        },
        {
            "num": "Feature 2.6",
            "name": "TMDB Dataset Explorer & Filterable Browser",
            "why": (
                "Users need a fast, paginated interface to explore the raw underlying dataset without needing external database "
                "tools or CSV viewers."
            ),
            "use_case": (
                "• Filter 3,000 training movies by genre, title keyword, budget, and revenue.\n"
                "• Click any title in the table to instantly launch a full LLM financial post-mortem."
            )
        },
        {
            "num": "Feature 2.7",
            "name": "Terminal CLI Query Engine (query_movie.py)",
            "why": (
                "Data scientists and developers often operate strictly in terminal/headless environments or scripts where "
                "a graphical browser is unnecessary or unavailable."
            ),
            "use_case": (
                "• Rapid command-line queries (e.g. `python query_movie.py 'Polladhavan'`) returning formatted ASCII box "
                "office cards in under 500 milliseconds."
            )
        },
        {
            "num": "Feature 2.8",
            "name": "Dynamic LLM Provider & API Key Configuration",
            "why": (
                "Empowers users to configure custom API keys for Groq, OpenAI (GPT-4o), or Google Gemini without hardcoding "
                "secrets or modifying source code."
            ),
            "use_case": (
                "• In-app settings modal allowing instant provider switching and session memory persistence."
            )
        }
    ]

    for f in features:
        fp = doc.add_paragraph()
        fr = fp.add_run(f"{f['num']}: {f['name']}")
        fr.bold = True
        fr.font.size = Pt(12)
        fr.font.color.rgb = COLOR_GOLD

        wp = doc.add_paragraph()
        wp.add_run("• Why it is present: ").bold = True
        wp.add_run(f['why'])

        up = doc.add_paragraph()
        up.add_run("• Practical Use Case: ").bold = True
        up.add_run(f['use_case'])

        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # -------------------------------------------------------------
    # 3. TERMINAL EXECUTION GUIDE & COMMANDS
    # -------------------------------------------------------------
    h3 = doc.add_heading("3. Terminal Commands Execution Guide", level=1)
    h3.style.font.color.rgb = COLOR_PRIMARY
    h3.style.font.size = Pt(16)

    doc.add_paragraph(
        "Below are the exact terminal commands to run the web dashboard (HTTP server), execute terminal queries, "
        "retrain models, and run automated integration tests."
    )

    cmd_table = doc.add_table(rows=1, cols=3)
    cmd_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cmd_table.autofit = False

    # Header Row
    hdr_cells = cmd_table.rows[0].cells
    hdr_cells[0].text = "Objective"
    hdr_cells[1].text = "Exact Terminal Command"
    hdr_cells[2].text = "Port / Output Description"

    for cell in hdr_cells:
        set_cell_background(cell, "0F172A")
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.size = Pt(10)
        set_cell_margins(cell, 120, 120, 140, 140)

    commands_data = [
        (
            "1. Launch Web Dashboard",
            "python app.py",
            "Runs Flask server on http://127.0.0.1:5000 (Port 5000)"
        ),
        (
            "2. Direct Terminal Movie Search",
            "python query_movie.py \"Polladhavan\"",
            "Prints complete verified box office card in terminal"
        ),
        (
            "3. Search Any Hollywood Film",
            "python query_movie.py \"Avatar: The Way of Water\"",
            "Prints global gross, $350M budget, ROI, and breakdown"
        ),
        (
            "4. Search Any Indian Blockbuster",
            "python query_movie.py \"Kantara\"",
            "Prints ₹125 Cr gross, ₹8 Cr budget, 15.2x multiplier"
        ),
        (
            "5. Interactive Movie Chat Loop",
            "python query_movie.py",
            "Launches interactive prompt to query multiple films"
        ),
        (
            "6. Retrain ML Models & Generate CSV",
            "python ml_engine.py",
            "Trains 6 models and outputs submission.csv (4,398 rows)"
        ),
        (
            "7. Run Full System Tests",
            "python test_app.py",
            "Executes automated HTTP API validation suite"
        )
    ]

    for idx, (obj, cmd, desc) in enumerate(commands_data):
        row_cells = cmd_table.add_row().cells
        row_cells[0].text = obj
        row_cells[1].text = cmd
        row_cells[2].text = desc

        bg_color = "F8FAFC" if idx % 2 == 0 else "FFFFFF"
        for i, cell in enumerate(row_cells):
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, 100, 100, 120, 120)
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(9.5)
                    if i == 1:
                        run.font.name = 'Consolas'
                        run.font.bold = True
                        run.font.color.rgb = COLOR_GOLD

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # 4. ARCHITECTURE & CODEBASE STRUCTURE
    # -------------------------------------------------------------
    h4 = doc.add_heading("4. Architecture & File Hierarchy", level=1)
    h4.style.font.color.rgb = COLOR_PRIMARY
    h4.style.font.size = Pt(16)

    files_info = [
        ("app.py", "Flask Web Server serving REST APIs (/api/movie-lookup, /api/predict, /api/stats, /api/models-info, /api/movies) and web dashboard."),
        ("ml_engine.py", "Feature engineering pipeline, training 6 regression models, cross-validation, feature importance, and submission.csv generation."),
        ("llm_engine.py", "LLM Integration using Groq (openai/gpt-oss-120b), OpenAI, and Gemini with intelligent fallback for verified real-world data."),
        ("query_movie.py", "Interactive terminal CLI allowing instant queries for any film in the world directly from PowerShell/CMD."),
        ("templates/index.html", "Cinematic HTML5 dashboard featuring dark-theme glassmorphism, responsive tab system, and interactive controls."),
        ("static/css/style.css", "Custom stylesheet with CSS variables, glowing badges, sliders, responsive grid, and custom chart cards."),
        ("static/js/app.js", "Client-side controller managing Chart.js charts, asynchronous REST queries, dynamic form listeners, and currency formatting."),
        ("test_app.py", "Comprehensive test script validating all HTTP endpoints, model predictions, and LLM responses."),
        ("train.csv / test.csv", "Original TMDB Box Office Prediction dataset with 7,398 total film records."),
        ("submission.csv", "Generated competition predictions for all 4,398 test movies using Gradient Boosting.")
    ]

    for fname, fdesc in files_info:
        p = doc.add_paragraph()
        r1 = p.add_run(f"• {fname}: ")
        r1.bold = True
        r1.font.color.rgb = COLOR_PRIMARY
        p.add_run(fdesc)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # 5. TECHNICAL SPECIFICATIONS
    # -------------------------------------------------------------
    h5 = doc.add_heading("5. Technology Stack & Machine Learning Details", level=1)
    h5.style.font.color.rgb = COLOR_PRIMARY
    h5.style.font.size = Pt(16)

    tech_p = doc.add_paragraph()
    tech_p.add_run("• Programming Language: ").bold = True
    tech_p.add_run("Python 3.14.6\n")
    tech_p.add_run("• Web Framework: ").bold = True
    tech_p.add_run("Flask 3.1.3\n")
    tech_p.add_run("• Machine Learning Library: ").bold = True
    tech_p.add_run("Scikit-Learn 1.9.1 (StandardScaler, OneHotEncoder, GradientBoostingRegressor, RandomForestRegressor, Ridge, Lasso)\n")
    tech_p.add_run("• Large Language Model Engine: ").bold = True
    tech_p.add_run("Groq SDK (openai/gpt-oss-120b, openai/gpt-oss-20b, qwen/qwen3.8-27b)\n")
    tech_p.add_run("• Data Science Libraries: ").bold = True
    tech_p.add_run("Pandas 3.0.6, NumPy 2.5.2, Joblib 1.6.0\n")
    tech_p.add_run("• Frontend Technologies: ").bold = True
    tech_p.add_run("HTML5, CSS3 (Glassmorphism), JavaScript (ES6+), Chart.js 4.4.2, Font Awesome 6.5.1, Google Fonts (Outfit, Inter)")

    # Save document
    output_path = os.path.join(os.getcwd(), "CineMetric_AI_Project_Documentation.docx")
    doc.save(output_path)
    print(f"Documentation DOCX successfully generated at: {output_path}")

if __name__ == '__main__':
    create_documentation()
