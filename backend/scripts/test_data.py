"""
scripts/test_data.py
--------------------
Resets the local database and loads rich, fully linked demo data across all core tables.
Each workshop has domain-specific questions, detailed module materials, explicit educator
assignments, varied attendance patterns, and comprehensive fee/payment history.

Run: python -m scripts.test_data
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from app.core.security import hash_password
from app.db import AsyncSessionLocal, engine
from app.models import (Assessment, Attendance, Base, Certificate, Enrollment,
                        EnrollmentStatus, FeePlan, Institution, Module,
                        Notification, NotificationStatus, NotificationType,
                        Payment, Question, QuestionType, Session, StudentFee,
                        Submission, User, UserRole, Workshop)
from app.services.certificate import generate_certificate_pdf

UTC = timezone.utc

# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------

PASSWORDS = {
    "admin@eduflow.edu": "admin123",
    "institution.admin@eduflow.edu": "institution123",
    "educator@eduflow.edu": "educator123",
    "student@eduflow.edu": "student123",
    "support@eduflow.edu": "support123",
}
DEFAULT_PASSWORD = "demo123"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def dt(days_from_now: int, hour: int = 10) -> datetime:
    base = datetime.now(tz=UTC).replace(minute=0, second=0, microsecond=0)
    return base + timedelta(days=days_from_now, hours=hour - base.hour)


# ---------------------------------------------------------------------------
# Domain-specific module materials
# ---------------------------------------------------------------------------

WORKSHOP_MATERIALS: dict[str, list[list[dict]]] = {
    "Full Stack Web Bootcamp": [
        [
            {
                "id": "fswb-m1-video",
                "title": "Lesson 1: How the Web Works — HTTP, DNS & Browsers",
                "type": "video",
                "content": "https://example.com/fswb/lesson-1-how-web-works",
                "created_at": dt(-28).isoformat(),
            },
            {
                "id": "fswb-m1-notes",
                "title": "Module 1 Notes: Client-Server Architecture",
                "type": "text",
                "content": (
                    "The web is built on a client-server model. When you type a URL, "
                    "your browser sends an HTTP request to a server resolved via DNS. "
                    "The server responds with HTML, CSS, and JavaScript that the browser renders. "
                    "Key concepts: HTTP verbs (GET, POST, PUT, DELETE), status codes (200, 301, 404, 500), "
                    "and the role of CDNs in caching static assets."
                ),
                "created_at": dt(-28).isoformat(),
            },
            {
                "id": "fswb-m1-resource",
                "title": "MDN: HTTP Overview",
                "type": "link",
                "content": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview",
                "created_at": dt(-27).isoformat(),
            },
        ],
        [
            {
                "id": "fswb-m2-video",
                "title": "Lesson 2: Building REST APIs with Node.js & Express",
                "type": "video",
                "content": "https://example.com/fswb/lesson-2-rest-express",
                "created_at": dt(-21).isoformat(),
            },
            {
                "id": "fswb-m2-notes",
                "title": "Module 2 Notes: Express Routing & Middleware",
                "type": "text",
                "content": (
                    "Express.js is a minimal Node.js web framework. Routes are defined using "
                    "app.get(), app.post() etc. Middleware functions have access to req, res, and next. "
                    "Middleware is executed in the order it is registered. Common middleware: "
                    "express.json() for parsing bodies, cors() for cross-origin requests, "
                    "and helmet() for securing HTTP headers. Error-handling middleware takes four arguments: "
                    "(err, req, res, next)."
                ),
                "created_at": dt(-21).isoformat(),
            },
            {
                "id": "fswb-m2-exercise",
                "title": "Exercise: Build a CRUD API for a Todo List",
                "type": "link",
                "content": "https://example.com/fswb/exercise-todo-crud",
                "created_at": dt(-20).isoformat(),
            },
        ],
        [
            {
                "id": "fswb-m3-video",
                "title": "Lesson 3: React Fundamentals — Components, Props & State",
                "type": "video",
                "content": "https://example.com/fswb/lesson-3-react-basics",
                "created_at": dt(-14).isoformat(),
            },
            {
                "id": "fswb-m3-notes",
                "title": "Module 3 Notes: React Component Lifecycle & Hooks",
                "type": "text",
                "content": (
                    "React builds UIs from reusable components. Functional components with Hooks are "
                    "the modern standard. useState manages local state; useEffect handles side effects "
                    "like data fetching. Props are read-only inputs passed from parent to child. "
                    "The virtual DOM diffs changes and only updates what changed in the real DOM, "
                    "making React highly performant."
                ),
                "created_at": dt(-14).isoformat(),
            },
            {
                "id": "fswb-m3-resource",
                "title": "React Official Docs",
                "type": "link",
                "content": "https://react.dev",
                "created_at": dt(-13).isoformat(),
            },
        ],
    ],
    "Python for Data Analysis": [
        [
            {
                "id": "pda-m1-video",
                "title": "Lesson 1: NumPy Arrays & Vectorised Operations",
                "type": "video",
                "content": "https://example.com/pda/lesson-1-numpy",
                "created_at": dt(-19).isoformat(),
            },
            {
                "id": "pda-m1-notes",
                "title": "Module 1 Notes: NumPy Essentials",
                "type": "text",
                "content": (
                    "NumPy is the foundation of scientific Python. ndarray is a fixed-type, "
                    "N-dimensional array stored in contiguous memory. Key operations: broadcasting "
                    "(operations on arrays of different shapes), fancy indexing, boolean masking, "
                    "and universal functions (ufuncs) that operate element-wise. "
                    "Always prefer vectorised operations over Python loops for performance."
                ),
                "created_at": dt(-19).isoformat(),
            },
            {
                "id": "pda-m1-notebook",
                "title": "Starter Notebook: NumPy Exercises",
                "type": "link",
                "content": "https://example.com/pda/numpy-starter-notebook",
                "created_at": dt(-18).isoformat(),
            },
        ],
        [
            {
                "id": "pda-m2-video",
                "title": "Lesson 2: Pandas — DataFrames, Groupby & Merge",
                "type": "video",
                "content": "https://example.com/pda/lesson-2-pandas",
                "created_at": dt(-12).isoformat(),
            },
            {
                "id": "pda-m2-notes",
                "title": "Module 2 Notes: Pandas Data Wrangling",
                "type": "text",
                "content": (
                    "Pandas provides Series (1D) and DataFrame (2D) data structures. "
                    "Reading data: pd.read_csv(), pd.read_excel(). "
                    "Selecting: df['col'], df.loc[row, col] (label-based), df.iloc[r, c] (position-based). "
                    "Groupby splits the data, applies an aggregation (sum, mean, count), and combines results. "
                    "pd.merge() joins DataFrames on keys — inner, left, right, and outer joins are supported."
                ),
                "created_at": dt(-12).isoformat(),
            },
            {
                "id": "pda-m2-dataset",
                "title": "Dataset: Indian Weather 2023 CSV",
                "type": "link",
                "content": "https://example.com/pda/indian-weather-2023.csv",
                "created_at": dt(-11).isoformat(),
            },
        ],
        [
            {
                "id": "pda-m3-video",
                "title": "Lesson 3: Matplotlib & Seaborn Visualisations",
                "type": "video",
                "content": "https://example.com/pda/lesson-3-visualisation",
                "created_at": dt(-6).isoformat(),
            },
            {
                "id": "pda-m3-notes",
                "title": "Module 3 Notes: Choosing the Right Chart",
                "type": "text",
                "content": (
                    "Use line charts for time-series, bar charts for categorical comparison, "
                    "scatter plots for correlation, histograms for distribution, and heatmaps for "
                    "correlation matrices. Seaborn wraps Matplotlib with statistical defaults. "
                    "Always label axes and include a title. Use plt.tight_layout() to prevent overlap. "
                    "Save figures with plt.savefig('name.png', dpi=150, bbox_inches='tight')."
                ),
                "created_at": dt(-6).isoformat(),
            },
            {
                "id": "pda-m3-resource",
                "title": "Seaborn Gallery",
                "type": "link",
                "content": "https://seaborn.pydata.org/examples/index.html",
                "created_at": dt(-5).isoformat(),
            },
        ],
    ],
    "Machine Learning Basics": [
        [
            {
                "id": "mlb-m1-video",
                "title": "Lesson 1: Supervised vs Unsupervised Learning",
                "type": "video",
                "content": "https://example.com/mlb/lesson-1-supervised-unsupervised",
                "created_at": dt(-23).isoformat(),
            },
            {
                "id": "mlb-m1-notes",
                "title": "Module 1 Notes: ML Problem Taxonomy",
                "type": "text",
                "content": (
                    "Supervised learning uses labelled data (input→output pairs) to learn a mapping function. "
                    "Regression predicts continuous values; classification predicts discrete classes. "
                    "Unsupervised learning finds hidden patterns in unlabelled data — clustering (k-means, DBSCAN) "
                    "and dimensionality reduction (PCA, t-SNE) are the main families. "
                    "Reinforcement learning trains an agent to maximise cumulative reward via interaction with an environment. "
                    "Always start with a simple baseline before complex models."
                ),
                "created_at": dt(-23).isoformat(),
            },
            {
                "id": "mlb-m1-resource",
                "title": "Scikit-learn User Guide",
                "type": "link",
                "content": "https://scikit-learn.org/stable/user_guide.html",
                "created_at": dt(-22).isoformat(),
            },
        ],
        [
            {
                "id": "mlb-m2-video",
                "title": "Lesson 2: Bias-Variance Tradeoff & Model Evaluation",
                "type": "video",
                "content": "https://example.com/mlb/lesson-2-bias-variance",
                "created_at": dt(-15).isoformat(),
            },
            {
                "id": "mlb-m2-notes",
                "title": "Module 2 Notes: Metrics & Cross-Validation",
                "type": "text",
                "content": (
                    "High bias (underfitting) means the model is too simple to capture the data. "
                    "High variance (overfitting) means it memorises the training set but generalises poorly. "
                    "Regularisation (L1/Lasso, L2/Ridge) penalises large weights to reduce variance. "
                    "For classification: accuracy, precision, recall, F1-score, ROC-AUC. "
                    "For regression: MAE, MSE, RMSE, R². "
                    "k-Fold cross-validation gives a more reliable estimate of generalisation performance "
                    "than a single train/test split."
                ),
                "created_at": dt(-15).isoformat(),
            },
            {
                "id": "mlb-m2-notebook",
                "title": "Notebook: Iris Classification End-to-End",
                "type": "link",
                "content": "https://example.com/mlb/iris-classification-notebook",
                "created_at": dt(-14).isoformat(),
            },
        ],
        [
            {
                "id": "mlb-m3-video",
                "title": "Lesson 3: Decision Trees, Random Forests & Gradient Boosting",
                "type": "video",
                "content": "https://example.com/mlb/lesson-3-tree-ensembles",
                "created_at": dt(-8).isoformat(),
            },
            {
                "id": "mlb-m3-notes",
                "title": "Module 3 Notes: Ensemble Methods",
                "type": "text",
                "content": (
                    "A decision tree splits data on the feature that maximises information gain (entropy) or "
                    "minimises Gini impurity. Random Forests train many trees on random subsets of data and "
                    "features (bagging), then aggregate predictions by majority vote or averaging. "
                    "Gradient Boosting (XGBoost, LightGBM) trains trees sequentially, each correcting the "
                    "residual errors of the previous. Boosting generally outperforms bagging but is more "
                    "sensitive to hyperparameters and noisy labels."
                ),
                "created_at": dt(-8).isoformat(),
            },
            {
                "id": "mlb-m3-resource",
                "title": "XGBoost Documentation",
                "type": "link",
                "content": "https://xgboost.readthedocs.io/en/stable/",
                "created_at": dt(-7).isoformat(),
            },
        ],
    ],
    "Cloud Fundamentals": [
        [
            {
                "id": "cf-m1-video",
                "title": "Lesson 1: IaaS vs PaaS vs SaaS & the Shared Responsibility Model",
                "type": "video",
                "content": "https://example.com/cf/lesson-1-cloud-models",
                "created_at": dt(-8).isoformat(),
            },
            {
                "id": "cf-m1-notes",
                "title": "Module 1 Notes: Cloud Service Models Explained",
                "type": "text",
                "content": (
                    "IaaS (Infrastructure as a Service) gives raw VMs, storage, and networking — you manage the OS and above. "
                    "PaaS (Platform as a Service) provides a managed runtime; you deploy code without managing servers. "
                    "SaaS (Software as a Service) is fully managed software accessed via browser. "
                    "In the Shared Responsibility Model, the cloud provider secures the infrastructure; "
                    "the customer is responsible for data, identity, and application security. "
                    "Major providers: AWS, Azure, GCP. Each has a free tier suitable for learning."
                ),
                "created_at": dt(-8).isoformat(),
            },
            {
                "id": "cf-m1-resource",
                "title": "AWS Well-Architected Framework",
                "type": "link",
                "content": "https://aws.amazon.com/architecture/well-architected/",
                "created_at": dt(-7).isoformat(),
            },
        ],
        [
            {
                "id": "cf-m2-video",
                "title": "Lesson 2: Virtual Machines, Containers & Serverless",
                "type": "video",
                "content": "https://example.com/cf/lesson-2-compute-options",
                "created_at": dt(-3).isoformat(),
            },
            {
                "id": "cf-m2-notes",
                "title": "Module 2 Notes: Compute Options & When to Use Each",
                "type": "text",
                "content": (
                    "Virtual machines emulate physical hardware — good for lift-and-shift migrations. "
                    "Containers (Docker) package the app + dependencies but share the host OS kernel — "
                    "lightweight and portable. Kubernetes orchestrates containers at scale. "
                    "Serverless (AWS Lambda, Cloud Functions) executes code in response to events with no server management — "
                    "ideal for event-driven, bursty workloads. Cold starts can add latency. "
                    "Choose VMs for stateful workloads, containers for microservices, serverless for short-lived tasks."
                ),
                "created_at": dt(-3).isoformat(),
            },
            {
                "id": "cf-m2-resource",
                "title": "Docker Getting Started Guide",
                "type": "link",
                "content": "https://docs.docker.com/get-started/",
                "created_at": dt(-2).isoformat(),
            },
        ],
    ],
    "UI UX Design Sprint": [
        [
            {
                "id": "uiux-m1-video",
                "title": "Lesson 1: Design Thinking — Empathise, Define, Ideate",
                "type": "video",
                "content": "https://example.com/uiux/lesson-1-design-thinking",
                "created_at": dt(-13).isoformat(),
            },
            {
                "id": "uiux-m1-notes",
                "title": "Module 1 Notes: The 5-Stage Design Thinking Process",
                "type": "text",
                "content": (
                    "Design Thinking is a human-centred problem-solving framework. "
                    "Stage 1 — Empathise: conduct user interviews, observation, and surveys to understand needs. "
                    "Stage 2 — Define: synthesise findings into a problem statement (Point of View). "
                    "Stage 3 — Ideate: brainstorm without judgment; use techniques like Crazy 8s or mind mapping. "
                    "Stage 4 — Prototype: build low-fidelity mock-ups quickly. "
                    "Stage 5 — Test: validate with real users and iterate. Failure is expected and valued."
                ),
                "created_at": dt(-13).isoformat(),
            },
            {
                "id": "uiux-m1-resource",
                "title": "IDEO Design Thinking Toolkit",
                "type": "link",
                "content": "https://www.designkit.org/methods",
                "created_at": dt(-12).isoformat(),
            },
        ],
        [
            {
                "id": "uiux-m2-video",
                "title": "Lesson 2: Figma Prototyping — Components, Auto-layout & Variants",
                "type": "video",
                "content": "https://example.com/uiux/lesson-2-figma",
                "created_at": dt(-7).isoformat(),
            },
            {
                "id": "uiux-m2-notes",
                "title": "Module 2 Notes: Figma Best Practices",
                "type": "text",
                "content": (
                    "Use components for repeated UI elements — changes to the main component propagate to all instances. "
                    "Auto layout arranges items like CSS Flexbox — horizontal, vertical, with spacing and padding controls. "
                    "Variants let a single component hold multiple states (default, hover, disabled). "
                    "Constraints determine how elements resize when the frame changes. "
                    "Design tokens (colour styles, text styles) ensure consistency and simplify handoff to developers."
                ),
                "created_at": dt(-7).isoformat(),
            },
            {
                "id": "uiux-m2-resource",
                "title": "Figma Community — Free UI Kits",
                "type": "link",
                "content": "https://www.figma.com/community",
                "created_at": dt(-6).isoformat(),
            },
        ],
    ],
    "Cybersecurity Essentials": [
        [
            {
                "id": "cse-m1-video",
                "title": "Lesson 1: The CIA Triad & Common Threat Vectors",
                "type": "video",
                "content": "https://example.com/cse/lesson-1-cia-triad",
                "created_at": dt(-16).isoformat(),
            },
            {
                "id": "cse-m1-notes",
                "title": "Module 1 Notes: Foundations of Information Security",
                "type": "text",
                "content": (
                    "The CIA Triad underpins all of information security: "
                    "Confidentiality — only authorised parties can access data (encryption, access controls). "
                    "Integrity — data is not tampered with (hashing, digital signatures). "
                    "Availability — systems are accessible when needed (redundancy, DDoS protection). "
                    "Common threats: phishing (social engineering), SQL injection (untrusted input in queries), "
                    "XSS (injecting scripts into web pages), MITM (intercepting communications), "
                    "and ransomware (encrypting files for extortion). "
                    "Defence in depth uses multiple overlapping controls so no single failure compromises the system."
                ),
                "created_at": dt(-16).isoformat(),
            },
            {
                "id": "cse-m1-resource",
                "title": "OWASP Top 10",
                "type": "link",
                "content": "https://owasp.org/www-project-top-ten/",
                "created_at": dt(-15).isoformat(),
            },
        ],
        [
            {
                "id": "cse-m2-video",
                "title": "Lesson 2: Encryption, PKI & Secure Protocols",
                "type": "video",
                "content": "https://example.com/cse/lesson-2-encryption",
                "created_at": dt(-10).isoformat(),
            },
            {
                "id": "cse-m2-notes",
                "title": "Module 2 Notes: Symmetric vs Asymmetric Encryption",
                "type": "text",
                "content": (
                    "Symmetric encryption uses the same key to encrypt and decrypt (AES-256). Fast, but key distribution is hard. "
                    "Asymmetric encryption uses a public/private key pair (RSA, ECC). The public key encrypts; only the private key decrypts. "
                    "TLS (HTTPS) uses asymmetric cryptography to exchange a session key, then switches to symmetric for speed. "
                    "Hashing (SHA-256) is a one-way function — you cannot reverse a hash to get the original input. "
                    "Salted password hashing (bcrypt, Argon2) prevents rainbow table attacks. "
                    "Certificates issued by Certificate Authorities (CAs) bind a public key to an identity."
                ),
                "created_at": dt(-10).isoformat(),
            },
            {
                "id": "cse-m2-resource",
                "title": "Cloudflare Learning: What is TLS?",
                "type": "link",
                "content": "https://www.cloudflare.com/learning/ssl/transport-layer-security-tls/",
                "created_at": dt(-9).isoformat(),
            },
        ],
    ],
    "DevOps in Practice": [
        [
            {
                "id": "dop-m1-video",
                "title": "Lesson 1: CI/CD Pipelines with GitHub Actions",
                "type": "video",
                "content": "https://example.com/dop/lesson-1-cicd",
                "created_at": dt(-10).isoformat(),
            },
            {
                "id": "dop-m1-notes",
                "title": "Module 1 Notes: CI/CD Concepts & Workflow",
                "type": "text",
                "content": (
                    "Continuous Integration (CI) automatically builds and tests code on every push. "
                    "Continuous Delivery (CD) ensures the artifact is always in a deployable state; "
                    "Continuous Deployment automatically ships every green build to production. "
                    "A GitHub Actions workflow is a YAML file in .github/workflows/. "
                    "Key concepts: triggers (on: push, pull_request), jobs (run in parallel by default), "
                    "steps (sequential shell commands or actions), and environments (staging, production). "
                    "Secrets are stored encrypted and injected as environment variables at runtime."
                ),
                "created_at": dt(-10).isoformat(),
            },
            {
                "id": "dop-m1-resource",
                "title": "GitHub Actions Documentation",
                "type": "link",
                "content": "https://docs.github.com/en/actions",
                "created_at": dt(-9).isoformat(),
            },
        ],
        [
            {
                "id": "dop-m2-video",
                "title": "Lesson 2: Infrastructure as Code with Terraform",
                "type": "video",
                "content": "https://example.com/dop/lesson-2-terraform",
                "created_at": dt(-5).isoformat(),
            },
            {
                "id": "dop-m2-notes",
                "title": "Module 2 Notes: Terraform Workflow & State Management",
                "type": "text",
                "content": (
                    "Terraform defines infrastructure in HCL (HashiCorp Configuration Language). "
                    "Workflow: terraform init → terraform plan (preview changes) → terraform apply (provision). "
                    "State (terraform.tfstate) tracks real-world resource status. "
                    "Store state remotely (S3 + DynamoDB lock, Terraform Cloud) for team use. "
                    "Modules are reusable infrastructure units. Variables and outputs make them configurable. "
                    "Workspaces allow multiple environments (dev, staging, prod) from one codebase."
                ),
                "created_at": dt(-5).isoformat(),
            },
            {
                "id": "dop-m2-resource",
                "title": "Terraform Registry — AWS Provider",
                "type": "link",
                "content": "https://registry.terraform.io/providers/hashicorp/aws/latest/docs",
                "created_at": dt(-4).isoformat(),
            },
        ],
    ],
    "Data Visualization Studio": [
        [
            {
                "id": "dvs-m1-video",
                "title": "Lesson 1: Principles of Effective Data Visualisation",
                "type": "video",
                "content": "https://example.com/dvs/lesson-1-principles",
                "created_at": dt(-6).isoformat(),
            },
            {
                "id": "dvs-m1-notes",
                "title": "Module 1 Notes: Tufte's Data-Ink Ratio & Chartjunk",
                "type": "text",
                "content": (
                    "Edward Tufte's core principle: maximise the data-ink ratio. "
                    "Every pixel should encode information; remove gridlines, borders, and 3D effects that distort. "
                    "Chartjunk includes decorative fills, unnecessary legends, and dual y-axes that mislead. "
                    "Pre-attentive attributes (colour, size, shape) are processed instantly — use them to guide attention. "
                    "Choose colour scales carefully: sequential for ordered data, diverging for data around a midpoint, "
                    "qualitative for categorical data. Always account for colour-blindness (use ColorBrewer palettes)."
                ),
                "created_at": dt(-6).isoformat(),
            },
            {
                "id": "dvs-m1-resource",
                "title": "ColorBrewer 2.0",
                "type": "link",
                "content": "https://colorbrewer2.org/",
                "created_at": dt(-5).isoformat(),
            },
        ],
        [
            {
                "id": "dvs-m2-video",
                "title": "Lesson 2: Interactive Dashboards with Plotly & Dash",
                "type": "video",
                "content": "https://example.com/dvs/lesson-2-plotly-dash",
                "created_at": dt(-2).isoformat(),
            },
            {
                "id": "dvs-m2-notes",
                "title": "Module 2 Notes: Building Dash Apps",
                "type": "text",
                "content": (
                    "Dash is a Python framework for building reactive web apps with no JavaScript. "
                    "Layout is defined using Dash HTML and core components (dcc.Graph, dcc.Slider, dcc.Dropdown). "
                    "Callbacks link Input and Output components — when an input changes, the callback re-runs and updates the output. "
                    "Use dcc.Store to persist data between callbacks without re-fetching. "
                    "Deploy Dash apps to Heroku, Render, or any WSGI-compatible host. "
                    "Plotly Express provides one-line chart creation for most common chart types."
                ),
                "created_at": dt(-2).isoformat(),
            },
            {
                "id": "dvs-m2-resource",
                "title": "Dash Documentation",
                "type": "link",
                "content": "https://dash.plotly.com/",
                "created_at": dt(-1).isoformat(),
            },
        ],
    ],
    "Communication for Engineers": [
        [
            {
                "id": "cfe-m1-video",
                "title": "Lesson 1: Writing Clear Technical Documentation",
                "type": "video",
                "content": "https://example.com/cfe/lesson-1-tech-writing",
                "created_at": dt(-3).isoformat(),
            },
            {
                "id": "cfe-m1-notes",
                "title": "Module 1 Notes: Principles of Technical Writing",
                "type": "text",
                "content": (
                    "Good technical writing is clear, concise, and accurate. "
                    "Know your audience: write differently for a junior engineer vs a non-technical stakeholder. "
                    "Use active voice: 'The function returns a list' not 'A list is returned by the function.' "
                    "Structure documents with headings, short paragraphs, and code blocks. "
                    "README files should include: purpose, prerequisites, installation, usage, examples, and contribution guidelines. "
                    "API documentation should describe every endpoint, parameter, response schema, and error code."
                ),
                "created_at": dt(-3).isoformat(),
            },
            {
                "id": "cfe-m1-resource",
                "title": "Google Developer Documentation Style Guide",
                "type": "link",
                "content": "https://developers.google.com/style",
                "created_at": dt(-2).isoformat(),
            },
        ],
        [
            {
                "id": "cfe-m2-video",
                "title": "Lesson 2: Presenting Technical Work to Non-Technical Stakeholders",
                "type": "video",
                "content": "https://example.com/cfe/lesson-2-presentations",
                "created_at": dt(0).isoformat(),
            },
            {
                "id": "cfe-m2-notes",
                "title": "Module 2 Notes: Storytelling with Data",
                "type": "text",
                "content": (
                    "Stakeholders care about business outcomes, not technical details. "
                    "Lead with the insight, not the methodology: 'Our model will reduce churn by 12%', not 'We trained an XGBoost classifier.' "
                    "Use the Pyramid Principle: state your conclusion first, then support it. "
                    "Slides should have one idea per slide, a clear headline, and minimal text. "
                    "Anticipate objections: prepare a backup slide with methodology details. "
                    "Practice the 3-minute version: can you explain the project in three minutes to someone unfamiliar with it?"
                ),
                "created_at": dt(0).isoformat(),
            },
            {
                "id": "cfe-m2-resource",
                "title": "Storytelling with Data Book Summary",
                "type": "link",
                "content": "https://www.storytellingwithdata.com/chart-guide",
                "created_at": dt(1).isoformat(),
            },
        ],
    ],
    "Mobile App Prototyping": [
        [
            {
                "id": "map-m1-video",
                "title": "Lesson 1: React Native — Setup, Navigation & Core Components",
                "type": "video",
                "content": "https://example.com/map/lesson-1-rn-setup",
                "created_at": dt(-12).isoformat(),
            },
            {
                "id": "map-m1-notes",
                "title": "Module 1 Notes: React Native Architecture",
                "type": "text",
                "content": (
                    "React Native renders native UI components (not WebViews) using JavaScript. "
                    "The JS thread runs business logic; the native thread handles rendering. "
                    "The new architecture (JSI + Fabric) reduces bridge overhead significantly. "
                    "Core components: View, Text, Image, ScrollView, FlatList (virtualised lists), TextInput. "
                    "Navigation: React Navigation is the de-facto library. Stack, Tab, and Drawer navigators. "
                    "Expo is a managed workflow that simplifies setup and provides a device-testing app."
                ),
                "created_at": dt(-12).isoformat(),
            },
            {
                "id": "map-m1-resource",
                "title": "React Native Docs",
                "type": "link",
                "content": "https://reactnative.dev/docs/getting-started",
                "created_at": dt(-11).isoformat(),
            },
        ],
        [
            {
                "id": "map-m2-video",
                "title": "Lesson 2: State Management with Zustand & Async Storage",
                "type": "video",
                "content": "https://example.com/map/lesson-2-state-management",
                "created_at": dt(-6).isoformat(),
            },
            {
                "id": "map-m2-notes",
                "title": "Module 2 Notes: Offline-First Data Patterns",
                "type": "text",
                "content": (
                    "Zustand is a lightweight state management library with a simple hook-based API. "
                    "Define a store with create(), access state with useStore(). "
                    "AsyncStorage persists key-value pairs to device storage — always use try/catch. "
                    "For offline-first apps, maintain a local cache and sync with the server when connectivity is restored. "
                    "React Query (or TanStack Query) handles server state: caching, background refetching, and error states. "
                    "Optimistic updates improve perceived performance by updating UI before the server confirms."
                ),
                "created_at": dt(-6).isoformat(),
            },
            {
                "id": "map-m2-resource",
                "title": "Zustand Documentation",
                "type": "link",
                "content": "https://docs.pmnd.rs/zustand/getting-started/introduction",
                "created_at": dt(-5).isoformat(),
            },
        ],
    ],
    "AI Productivity Lab": [
        [
            {
                "id": "apl-m1-video",
                "title": "Lesson 1: Prompt Engineering — Zero-shot, Few-shot & Chain-of-Thought",
                "type": "video",
                "content": "https://example.com/apl/lesson-1-prompt-engineering",
                "created_at": dt(-5).isoformat(),
            },
            {
                "id": "apl-m1-notes",
                "title": "Module 1 Notes: Effective Prompting Techniques",
                "type": "text",
                "content": (
                    "Zero-shot prompting asks the model to perform a task with no examples. "
                    "Few-shot prompting provides 2-5 input/output examples before the actual query — "
                    "dramatically improves performance on structured tasks. "
                    "Chain-of-Thought (CoT) prompting adds 'Let's think step by step' to trigger reasoning. "
                    "Instruction fine-tuning has made most frontier models responsive to direct instructions. "
                    "Role prompting ('You are an expert tax attorney') sets context and tone. "
                    "Avoid ambiguous pronouns, be explicit about format (JSON, markdown table, bullet list), "
                    "and specify length constraints to get consistent outputs."
                ),
                "created_at": dt(-5).isoformat(),
            },
            {
                "id": "apl-m1-resource",
                "title": "Anthropic Prompt Engineering Guide",
                "type": "link",
                "content": "https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview",
                "created_at": dt(-4).isoformat(),
            },
        ],
        [
            {
                "id": "apl-m2-video",
                "title": "Lesson 2: Building AI Workflows with LangChain & Agents",
                "type": "video",
                "content": "https://example.com/apl/lesson-2-langchain",
                "created_at": dt(-1).isoformat(),
            },
            {
                "id": "apl-m2-notes",
                "title": "Module 2 Notes: RAG, Agents & Tool Use",
                "type": "text",
                "content": (
                    "Retrieval-Augmented Generation (RAG) retrieves relevant documents from a vector store "
                    "and appends them to the prompt, grounding responses in factual source material. "
                    "Vector stores (Pinecone, FAISS, Chroma) index document embeddings for similarity search. "
                    "Agents use tool-calling to take actions: web search, code execution, database queries. "
                    "LangChain provides abstractions for chains, memory, and tool integration. "
                    "LlamaIndex specialises in document ingestion pipelines and structured retrieval. "
                    "Always evaluate agent outputs — hallucination risk increases with longer reasoning chains."
                ),
                "created_at": dt(-1).isoformat(),
            },
            {
                "id": "apl-m2-resource",
                "title": "LangChain Documentation",
                "type": "link",
                "content": "https://python.langchain.com/docs/introduction/",
                "created_at": dt(0).isoformat(),
            },
        ],
    ],
    "Digital Marketing Foundations": [
        [
            {
                "id": "dmf-m1-video",
                "title": "Lesson 1: SEO — On-page, Off-page & Technical",
                "type": "video",
                "content": "https://example.com/dmf/lesson-1-seo",
                "created_at": dt(-7).isoformat(),
            },
            {
                "id": "dmf-m1-notes",
                "title": "Module 1 Notes: Search Engine Optimisation Fundamentals",
                "type": "text",
                "content": (
                    "On-page SEO: keyword research (Google Keyword Planner, Ahrefs), title tags (<60 chars), "
                    "meta descriptions (<160 chars), header hierarchy (H1 → H2 → H3), and internal linking. "
                    "Off-page SEO: earning backlinks from authoritative sites signals trust to Google. "
                    "Technical SEO: page speed (Core Web Vitals — LCP, CLS, INP), mobile-friendliness, "
                    "crawlability (sitemap.xml, robots.txt), and structured data (Schema.org). "
                    "Content is still king — produce original, helpful, E-E-A-T compliant content."
                ),
                "created_at": dt(-7).isoformat(),
            },
            {
                "id": "dmf-m1-resource",
                "title": "Google Search Central — SEO Starter Guide",
                "type": "link",
                "content": "https://developers.google.com/search/docs/fundamentals/seo-starter-guide",
                "created_at": dt(-6).isoformat(),
            },
        ],
        [
            {
                "id": "dmf-m2-video",
                "title": "Lesson 2: Google Ads & Meta Ads — Campaign Structure",
                "type": "video",
                "content": "https://example.com/dmf/lesson-2-paid-ads",
                "created_at": dt(-2).isoformat(),
            },
            {
                "id": "dmf-m2-notes",
                "title": "Module 2 Notes: Paid Media Fundamentals",
                "type": "text",
                "content": (
                    "Google Ads hierarchy: Account → Campaign → Ad Group → Ad. "
                    "Bidding strategies: Manual CPC, Target CPA, Target ROAS, Maximise Conversions. "
                    "Quality Score (1-10) is based on CTR, ad relevance, and landing page experience — "
                    "a higher score lowers your cost per click. "
                    "Meta Ads target by demographics, interests, and lookalike audiences. "
                    "Pixel tracking enables retargeting and conversion measurement. "
                    "Always A/B test creatives, headlines, and audiences. ROAS (Return on Ad Spend) = Revenue / Ad Spend."
                ),
                "created_at": dt(-2).isoformat(),
            },
            {
                "id": "dmf-m2-resource",
                "title": "Google Ads Help Centre",
                "type": "link",
                "content": "https://support.google.com/google-ads/",
                "created_at": dt(-1).isoformat(),
            },
        ],
    ],
    "Career Readiness Program": [
        [
            {
                "id": "crp-m1-video",
                "title": "Lesson 1: Resume Writing & LinkedIn Optimisation",
                "type": "video",
                "content": "https://example.com/crp/lesson-1-resume",
                "created_at": dt(-14).isoformat(),
            },
            {
                "id": "crp-m1-notes",
                "title": "Module 1 Notes: ATS-Friendly Resume Best Practices",
                "type": "text",
                "content": (
                    "Applicant Tracking Systems (ATS) parse resumes before a human sees them. "
                    "Use a single-column, clean format — avoid tables, columns, and graphics. "
                    "Mirror keywords from the job description (skills, tools, verbs). "
                    "Quantify achievements: 'Reduced API latency by 35% by introducing Redis caching.' "
                    "LinkedIn: use a professional photo, write a first-person summary, request recommendations. "
                    "Keep the Experience section focused on impact, not duties. "
                    "Tailor your resume for every application — a generic resume performs poorly against ATS."
                ),
                "created_at": dt(-14).isoformat(),
            },
            {
                "id": "crp-m1-resource",
                "title": "Harvard OCS Resume Guide",
                "type": "link",
                "content": "https://ocs.fas.harvard.edu/resumes-cvs",
                "created_at": dt(-13).isoformat(),
            },
        ],
        [
            {
                "id": "crp-m2-video",
                "title": "Lesson 2: Technical Interview Preparation — DSA & System Design",
                "type": "video",
                "content": "https://example.com/crp/lesson-2-interviews",
                "created_at": dt(-7).isoformat(),
            },
            {
                "id": "crp-m2-notes",
                "title": "Module 2 Notes: Cracking the Coding Interview",
                "type": "text",
                "content": (
                    "For DSA rounds: master arrays, strings, hashmaps, linked lists, trees, graphs, and dynamic programming. "
                    "Solve 150-200 LeetCode problems focusing on medium difficulty. "
                    "Always clarify the problem, discuss brute force first, then optimise. "
                    "Communicate your thought process aloud — interviewers evaluate reasoning, not just the answer. "
                    "System design: practice designing URL shorteners, chat systems, ride-sharing apps, and news feeds. "
                    "Cover: requirements, capacity estimation, API design, database schema, high-level architecture, "
                    "and bottlenecks (caching, sharding, load balancing)."
                ),
                "created_at": dt(-7).isoformat(),
            },
            {
                "id": "crp-m2-resource",
                "title": "Neetcode — DSA Roadmap",
                "type": "link",
                "content": "https://neetcode.io/roadmap",
                "created_at": dt(-6).isoformat(),
            },
        ],
    ],
    "Financial Literacy Workshop": [
        [
            {
                "id": "flw-m1-video",
                "title": "Lesson 1: Personal Budgeting — 50/30/20 Rule & Zero-Based Budgeting",
                "type": "video",
                "content": "https://example.com/flw/lesson-1-budgeting",
                "created_at": dt(-9).isoformat(),
            },
            {
                "id": "flw-m1-notes",
                "title": "Module 1 Notes: Budgeting Frameworks",
                "type": "text",
                "content": (
                    "The 50/30/20 rule allocates 50% of after-tax income to needs, 30% to wants, and 20% to savings/debt. "
                    "Zero-based budgeting assigns every rupee a job so income − expenses = 0. "
                    "Track spending with apps (YNAB, Walnut, Money Manager). "
                    "Emergency fund: 3-6 months of expenses in a liquid savings account. "
                    "Automate savings by setting up recurring transfers on payday. "
                    "Distinguish between good debt (low interest, appreciating asset) and bad debt (high interest, depreciating)."
                ),
                "created_at": dt(-9).isoformat(),
            },
            {
                "id": "flw-m1-resource",
                "title": "RBI Financial Literacy Week Resources",
                "type": "link",
                "content": "https://www.rbi.org.in/scripts/FinancialLiteracy.aspx",
                "created_at": dt(-8).isoformat(),
            },
        ],
        [
            {
                "id": "flw-m2-video",
                "title": "Lesson 2: Investing Basics — Mutual Funds, SIP & Equity",
                "type": "video",
                "content": "https://example.com/flw/lesson-2-investing",
                "created_at": dt(-4).isoformat(),
            },
            {
                "id": "flw-m2-notes",
                "title": "Module 2 Notes: Indian Investment Landscape",
                "type": "text",
                "content": (
                    "Mutual funds pool money from many investors and are managed by an AMC. "
                    "SIP (Systematic Investment Plan) invests a fixed amount monthly — leverages rupee cost averaging. "
                    "Equity funds invest in stocks — higher risk, higher potential return. "
                    "Debt funds invest in bonds — lower risk, stable returns. "
                    "Index funds (Nifty 50 ETFs) passively track an index with low expense ratios. "
                    "ELSS (Equity Linked Savings Scheme) offers tax benefits under Section 80C with a 3-year lock-in. "
                    "Rule of 72: divide 72 by annual return rate to estimate years to double your money."
                ),
                "created_at": dt(-4).isoformat(),
            },
            {
                "id": "flw-m2-resource",
                "title": "SEBI Investor Education Portal",
                "type": "link",
                "content": "https://investor.sebi.gov.in/",
                "created_at": dt(-3).isoformat(),
            },
        ],
    ],
    "Research Writing Intensive": [
        [
            {
                "id": "rwi-m1-video",
                "title": "Lesson 1: Formulating a Research Question & Literature Review",
                "type": "video",
                "content": "https://example.com/rwi/lesson-1-research-question",
                "created_at": dt(-18).isoformat(),
            },
            {
                "id": "rwi-m1-notes",
                "title": "Module 1 Notes: Research Methodology Primer",
                "type": "text",
                "content": (
                    "A strong research question is specific, measurable, and contributes new knowledge. "
                    "Use the PICOT framework for empirical studies (Population, Intervention, Comparison, Outcome, Time). "
                    "A literature review synthesises existing work — use Google Scholar, Semantic Scholar, and IEEE Xplore. "
                    "Citation managers (Zotero, Mendeley) import references and auto-format bibliographies. "
                    "Understand the difference between primary (original data) and secondary sources (reviews, meta-analyses). "
                    "Systematic reviews and meta-analyses are at the top of the evidence hierarchy."
                ),
                "created_at": dt(-18).isoformat(),
            },
            {
                "id": "rwi-m1-resource",
                "title": "Purdue OWL — Research & Citation",
                "type": "link",
                "content": "https://owl.purdue.edu/owl/research_and_citation/index.html",
                "created_at": dt(-17).isoformat(),
            },
        ],
        [
            {
                "id": "rwi-m2-video",
                "title": "Lesson 2: Academic Writing Structure & Avoiding Plagiarism",
                "type": "video",
                "content": "https://example.com/rwi/lesson-2-academic-writing",
                "created_at": dt(-11).isoformat(),
            },
            {
                "id": "rwi-m2-notes",
                "title": "Module 2 Notes: IMRaD Structure & Referencing",
                "type": "text",
                "content": (
                    "Most empirical papers follow IMRaD: Introduction, Methods, Results, and Discussion. "
                    "Abstract: 150-250 words covering objective, methods, results, and conclusions. "
                    "Introduction: establish context, identify the gap, and state the research objective. "
                    "Methods: detailed enough for replication — participants, instruments, procedure, analysis. "
                    "Results: report findings objectively with tables and figures; no interpretation. "
                    "Discussion: interpret results, relate to prior work, acknowledge limitations, suggest future research. "
                    "Plagiarism is academic dishonesty — paraphrase, quote sparingly, and always cite. "
                    "Use Turnitin or iThenticate to check similarity before submission."
                ),
                "created_at": dt(-11).isoformat(),
            },
            {
                "id": "rwi-m2-resource",
                "title": "Elsevier Researcher Academy — Free Courses",
                "type": "link",
                "content": "https://researcheracademy.elsevier.com/",
                "created_at": dt(-10).isoformat(),
            },
        ],
    ],
}


def get_materials(workshop_title: str, module_index: int) -> list[dict]:
    """Return domain-specific materials if available, else generate generic ones."""
    material_list = WORKSHOP_MATERIALS.get(workshop_title)
    if material_list and module_index - 1 < len(material_list):
        return material_list[module_index - 1]
    slug = workshop_title.lower().replace(" ", "-")
    return [
        {
            "id": f"{slug}-m{module_index}-video",
            "title": f"Lesson {module_index}: Core Concepts",
            "type": "video",
            "content": f"https://example.com/{slug}/lesson-{module_index}",
            "created_at": dt(-14 + module_index).isoformat(),
        },
        {
            "id": f"{slug}-m{module_index}-notes",
            "title": f"Module {module_index} Lecture Notes",
            "type": "text",
            "content": f"Comprehensive notes covering all key topics for {workshop_title}, Module {module_index}.",
            "created_at": dt(-14 + module_index).isoformat(),
        },
        {
            "id": f"{slug}-m{module_index}-resource",
            "title": f"Module {module_index} Reference Material",
            "type": "link",
            "content": "https://eduflow.local/resource",
            "created_at": dt(-13 + module_index).isoformat(),
        },
    ]


# ---------------------------------------------------------------------------
# Domain-specific assessment questions
# ---------------------------------------------------------------------------

ASSESSMENT_QUESTIONS: dict[str, list[dict]] = {
    "Full Stack Web Bootcamp": [
        {
            "text": "Which HTTP method is idempotent and should be used to fully replace a resource?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "fswb-q1-a", "text": "POST", "is_correct": False},
                {"id": "fswb-q1-b", "text": "PUT", "is_correct": True},
                {"id": "fswb-q1-c", "text": "PATCH", "is_correct": False},
                {"id": "fswb-q1-d", "text": "DELETE", "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are valid HTTP 2xx success status codes?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "fswb-q2-a", "text": "200 OK", "is_correct": True},
                {"id": "fswb-q2-b", "text": "201 Created", "is_correct": True},
                {"id": "fswb-q2-c", "text": "301 Moved Permanently",
                    "is_correct": False},
                {"id": "fswb-q2-d", "text": "204 No Content", "is_correct": True},
            ],
        },
        {
            "text": "In React, which Hook should you use to perform a data fetch after a component mounts?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "fswb-q3-a", "text": "useState", "is_correct": False},
                {"id": "fswb-q3-b", "text": "useRef", "is_correct": False},
                {"id": "fswb-q3-c", "text": "useEffect", "is_correct": True},
                {"id": "fswb-q3-d", "text": "useContext", "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are true about Express.js middleware?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "fswb-q4-a", "text": "Middleware functions receive req, res, and next",
                    "is_correct": True},
                {"id": "fswb-q4-b", "text": "Middleware executes in the order it is registered",
                    "is_correct": True},
                {"id": "fswb-q4-c", "text": "Middleware can only be applied to POST routes",
                    "is_correct": False},
                {"id": "fswb-q4-d", "text": "Error-handling middleware takes four arguments",
                    "is_correct": True},
            ],
        },
        {
            "text": "What does the CSS box model property 'box-sizing: border-box' do?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "fswb-q5-a", "text": "Adds padding outside the element's width",
                    "is_correct": False},
                {"id": "fswb-q5-b", "text": "Includes padding and border in the element's total width/height", "is_correct": True},
                {"id": "fswb-q5-c", "text": "Removes all default margin from the element",
                    "is_correct": False},
                {"id": "fswb-q5-d", "text": "Makes the element's border invisible",
                    "is_correct": False},
            ],
        },
        {
            "text": "Which of the following best describes a REST API constraint?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "fswb-q6-a", "text": "The server must store session state between requests",
                    "is_correct": False},
                {"id": "fswb-q6-b", "text": "Requests must be stateless — each contains all info needed", "is_correct": True},
                {"id": "fswb-q6-c", "text": "All responses must be in XML format",
                    "is_correct": False},
                {"id": "fswb-q6-d", "text": "Only GET and POST methods are allowed",
                    "is_correct": False},
            ],
        },
    ],
    "Python for Data Analysis": [
        {
            "text": "Which NumPy operation avoids a Python for-loop by operating element-wise on arrays?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "pda-q1-a", "text": "list comprehension", "is_correct": False},
                {"id": "pda-q1-b",
                    "text": "ufunc (universal function)", "is_correct": True},
                {"id": "pda-q1-c", "text": "lambda expression", "is_correct": False},
                {"id": "pda-q1-d", "text": "generator expression", "is_correct": False},
            ],
        },
        {
            "text": "Which pandas methods are label-based (not position-based) for indexing?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "pda-q2-a", "text": "df.loc[]", "is_correct": True},
                {"id": "pda-q2-b", "text": "df.iloc[]", "is_correct": False},
                {"id": "pda-q2-c", "text": "df.at[]", "is_correct": True},
                {"id": "pda-q2-d", "text": "df.iat[]", "is_correct": False},
            ],
        },
        {
            "text": "What does the pandas groupby().agg() method do?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "pda-q3-a", "text": "Filters rows matching a condition",
                    "is_correct": False},
                {"id": "pda-q3-b", "text": "Joins two DataFrames on a common key",
                    "is_correct": False},
                {"id": "pda-q3-c", "text": "Applies one or more aggregation functions to grouped data",
                    "is_correct": True},
                {"id": "pda-q3-d", "text": "Sorts a DataFrame by one or more columns",
                    "is_correct": False},
            ],
        },
        {
            "text": "Which Seaborn plot is best suited for visualising the distribution of a single continuous variable?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "pda-q4-a", "text": "sns.barplot()", "is_correct": False},
                {"id": "pda-q4-b", "text": "sns.scatterplot()", "is_correct": False},
                {"id": "pda-q4-c", "text": "sns.histplot() or sns.kdeplot()",
                 "is_correct": True},
                {"id": "pda-q4-d", "text": "sns.heatmap()", "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are true about NumPy broadcasting?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "pda-q5-a", "text": "Arrays must have the same number of dimensions to broadcast",
                    "is_correct": False},
                {"id": "pda-q5-b", "text": "A dimension of size 1 can be stretched to match the other array", "is_correct": True},
                {"id": "pda-q5-c", "text": "Broadcasting avoids making copies of data in memory",
                    "is_correct": True},
                {"id": "pda-q5-d", "text": "Broadcasting only works with 1D arrays",
                    "is_correct": False},
            ],
        },
        {
            "text": "What is the correct pandas method to detect missing values in a DataFrame?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "pda-q6-a", "text": "df.null()", "is_correct": False},
                {"id": "pda-q6-b", "text": "df.isnull() or df.isna()",
                 "is_correct": True},
                {"id": "pda-q6-c", "text": "df.empty()", "is_correct": False},
                {"id": "pda-q6-d", "text": "df.notna()", "is_correct": False},
            ],
        },
    ],
    "Machine Learning Basics": [
        {
            "text": "Which regularisation technique produces sparse models by driving some coefficients to exactly zero?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "mlb-q1-a", "text": "L2 (Ridge)", "is_correct": False},
                {"id": "mlb-q1-b", "text": "L1 (Lasso)", "is_correct": True},
                {"id": "mlb-q1-c", "text": "Dropout", "is_correct": False},
                {"id": "mlb-q1-d", "text": "Batch Normalisation", "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are ensemble methods that combine multiple decision trees?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "mlb-q2-a", "text": "Random Forest", "is_correct": True},
                {"id": "mlb-q2-b", "text": "XGBoost", "is_correct": True},
                {"id": "mlb-q2-c", "text": "K-Nearest Neighbours", "is_correct": False},
                {"id": "mlb-q2-d", "text": "LightGBM", "is_correct": True},
            ],
        },
        {
            "text": "In k-fold cross-validation with k=5, how many times is each data point used for validation?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "mlb-q3-a", "text": "5 times", "is_correct": False},
                {"id": "mlb-q3-b", "text": "Never", "is_correct": False},
                {"id": "mlb-q3-c", "text": "Exactly once", "is_correct": True},
                {"id": "mlb-q3-d", "text": "k−1 times", "is_correct": False},
            ],
        },
        {
            "text": "Which metric should you prioritise when false negatives are extremely costly (e.g., cancer screening)?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "mlb-q4-a", "text": "Precision", "is_correct": False},
                {"id": "mlb-q4-b", "text": "Accuracy", "is_correct": False},
                {"id": "mlb-q4-c",
                    "text": "Recall (Sensitivity)", "is_correct": True},
                {"id": "mlb-q4-d", "text": "Specificity", "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are correct statements about Random Forests?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "mlb-q5-a", "text": "Each tree is trained on a random subset of features",
                    "is_correct": True},
                {"id": "mlb-q5-b", "text": "Trees are trained sequentially to correct errors of previous trees", "is_correct": False},
                {"id": "mlb-q5-c", "text": "Random Forests are less prone to overfitting than a single decision tree", "is_correct": True},
                {"id": "mlb-q5-d", "text": "Each tree sees a bootstrapped sample of the training data",
                    "is_correct": True},
            ],
        },
        {
            "text": "What does PCA (Principal Component Analysis) primarily accomplish?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "mlb-q6-a", "text": "Classifies data into predefined categories",
                    "is_correct": False},
                {"id": "mlb-q6-b", "text": "Reduces dimensionality while preserving maximum variance",
                    "is_correct": True},
                {"id": "mlb-q6-c", "text": "Clusters data into k groups",
                    "is_correct": False},
                {"id": "mlb-q6-d", "text": "Handles class imbalance in datasets",
                    "is_correct": False},
            ],
        },
    ],
    "Cloud Fundamentals": [
        {
            "text": "In the Shared Responsibility Model, who is responsible for encrypting data at rest?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "cf-q1-a", "text": "Always the cloud provider",
                    "is_correct": False},
                {"id": "cf-q1-b", "text": "Always the customer", "is_correct": False},
                {"id": "cf-q1-c", "text": "The customer, though providers offer encryption tools to help", "is_correct": True},
                {"id": "cf-q1-d", "text": "Neither — data in transit only needs encryption",
                    "is_correct": False},
            ],
        },
        {
            "text": "Which cloud compute options eliminate server management entirely?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "cf-q2-a",
                    "text": "AWS Lambda (Serverless)", "is_correct": True},
                {"id": "cf-q2-b",
                    "text": "Amazon EC2 (Virtual Machine)", "is_correct": False},
                {"id": "cf-q2-c",
                    "text": "Google Cloud Run (Serverless Containers)", "is_correct": True},
                {"id": "cf-q2-d", "text": "Azure Virtual Machines", "is_correct": False},
            ],
        },
        {
            "text": "What is the primary advantage of cloud object storage (e.g., AWS S3) over block storage?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "cf-q3-a", "text": "Lower latency for random read/write operations",
                    "is_correct": False},
                {"id": "cf-q3-b", "text": "Virtually unlimited scalability and pay-per-use pricing",
                    "is_correct": True},
                {"id": "cf-q3-c", "text": "Better suited for OS and database storage",
                    "is_correct": False},
                {"id": "cf-q3-d", "text": "Can be mounted directly as a file system without any configuration", "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are characteristics of a serverless architecture?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "cf-q4-a", "text": "No server provisioning or patching required",
                    "is_correct": True},
                {"id": "cf-q4-b", "text": "Billing is based on actual execution time",
                    "is_correct": True},
                {"id": "cf-q4-c", "text": "Functions can hold state between invocations natively",
                    "is_correct": False},
                {"id": "cf-q4-d", "text": "Can experience cold start latency",
                    "is_correct": True},
            ],
        },
        {
            "text": "What does a VPC (Virtual Private Cloud) provide in a cloud environment?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "cf-q5-a", "text": "A managed Kubernetes cluster",
                    "is_correct": False},
                {"id": "cf-q5-b", "text": "An isolated network segment with control over IP ranges and routing", "is_correct": True},
                {"id": "cf-q5-c", "text": "Automatic database backups",
                    "is_correct": False},
                {"id": "cf-q5-d", "text": "A globally distributed CDN",
                    "is_correct": False},
            ],
        },
        {
            "text": "Which cloud pricing model charges you only for resources consumed with no upfront commitment?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "cf-q6-a", "text": "Reserved Instances", "is_correct": False},
                {"id": "cf-q6-b", "text": "Spot / Preemptible Instances",
                    "is_correct": False},
                {"id": "cf-q6-c", "text": "On-Demand Pricing", "is_correct": True},
                {"id": "cf-q6-d", "text": "Dedicated Hosts", "is_correct": False},
            ],
        },
    ],
    "UI UX Design Sprint": [
        {
            "text": "Which stage of Design Thinking involves building low-fidelity representations of your ideas?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "uiux-q1-a", "text": "Empathise", "is_correct": False},
                {"id": "uiux-q1-b", "text": "Define", "is_correct": False},
                {"id": "uiux-q1-c", "text": "Prototype", "is_correct": True},
                {"id": "uiux-q1-d", "text": "Ideate", "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are accessibility guidelines designers should follow?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "uiux-q2-a",
                    "text": "Minimum 4.5:1 colour contrast ratio for normal text (WCAG AA)", "is_correct": True},
                {"id": "uiux-q2-b", "text": "All interactive elements must be keyboard-navigable",
                    "is_correct": True},
                {"id": "uiux-q2-c", "text": "Use red and green as the only indicators for error vs success",
                    "is_correct": False},
                {"id": "uiux-q2-d", "text": "Provide alt text for all meaningful images",
                    "is_correct": True},
            ],
        },
        {
            "text": "In Figma, what does 'Auto layout' most closely correspond to in CSS?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "uiux-q3-a", "text": "CSS Grid", "is_correct": False},
                {"id": "uiux-q3-b", "text": "CSS Flexbox", "is_correct": True},
                {"id": "uiux-q3-c", "text": "CSS Absolute Positioning",
                    "is_correct": False},
                {"id": "uiux-q3-d", "text": "CSS Float", "is_correct": False},
            ],
        },
        {
            "text": "What is Fitts's Law in the context of UI design?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "uiux-q4-a", "text": "Users read web pages in an F-shaped pattern",
                    "is_correct": False},
                {"id": "uiux-q4-b", "text": "Time to acquire a target is a function of distance and target size", "is_correct": True},
                {"id": "uiux-q4-c", "text": "Short-term memory holds 7 ± 2 chunks of information",
                    "is_correct": False},
                {"id": "uiux-q4-d", "text": "Users prefer familiar interface patterns",
                    "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are valid usability testing methods?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "uiux-q5-a", "text": "Moderated think-aloud sessions",
                    "is_correct": True},
                {"id": "uiux-q5-b",
                    "text": "Unmoderated remote testing (e.g., Maze, Useberry)", "is_correct": True},
                {"id": "uiux-q5-c", "text": "A/B testing with live users",
                    "is_correct": True},
                {"id": "uiux-q5-d", "text": "Asking the design team to self-review without user involvement", "is_correct": False},
            ],
        },
        {
            "text": "What is the primary purpose of a 'wireframe' in the design process?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "uiux-q6-a", "text": "To specify exact colours, fonts, and visual style",
                    "is_correct": False},
                {"id": "uiux-q6-b", "text": "To layout the structure and information hierarchy without visual decoration", "is_correct": True},
                {"id": "uiux-q6-c", "text": "To provide final developer handoff specifications",
                    "is_correct": False},
                {"id": "uiux-q6-d", "text": "To create an animated prototype for user testing",
                    "is_correct": False},
            ],
        },
    ],
    "Cybersecurity Essentials": [
        {
            "text": "Which attack type injects malicious SQL through unsanitised user input fields?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "cse-q1-a",
                    "text": "Cross-Site Scripting (XSS)", "is_correct": False},
                {"id": "cse-q1-b", "text": "SQL Injection", "is_correct": True},
                {"id": "cse-q1-c",
                    "text": "CSRF (Cross-Site Request Forgery)", "is_correct": False},
                {"id": "cse-q1-d", "text": "Directory Traversal", "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are properties of the CIA Triad?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "cse-q2-a", "text": "Confidentiality", "is_correct": True},
                {"id": "cse-q2-b", "text": "Integrity", "is_correct": True},
                {"id": "cse-q2-c", "text": "Interoperability", "is_correct": False},
                {"id": "cse-q2-d", "text": "Availability", "is_correct": True},
            ],
        },
        {
            "text": "What hashing algorithm is recommended for securely storing user passwords?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "cse-q3-a", "text": "MD5", "is_correct": False},
                {"id": "cse-q3-b", "text": "SHA-1", "is_correct": False},
                {"id": "cse-q3-c", "text": "bcrypt or Argon2", "is_correct": True},
                {"id": "cse-q3-d", "text": "BASE64 encoding", "is_correct": False},
            ],
        },
        {
            "text": "In TLS (HTTPS), which cryptographic mechanism is used to establish the session key?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "cse-q4-a", "text": "Symmetric key exchange via AES",
                    "is_correct": False},
                {"id": "cse-q4-b",
                    "text": "Asymmetric key exchange (RSA or ECDHE) to agree on a symmetric key", "is_correct": True},
                {"id": "cse-q4-c", "text": "Password-based key derivation only",
                    "is_correct": False},
                {"id": "cse-q4-d", "text": "MD5 hash of the server certificate",
                    "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are effective defences against phishing attacks?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "cse-q5-a",
                    "text": "Multi-factor authentication (MFA)", "is_correct": True},
                {"id": "cse-q5-b", "text": "Security awareness training for employees",
                    "is_correct": True},
                {"id": "cse-q5-c", "text": "Email filtering with anti-phishing heuristics",
                    "is_correct": True},
                {"id": "cse-q5-d", "text": "Using a longer password without MFA",
                    "is_correct": False},
            ],
        },
        {
            "text": "What does 'defence in depth' mean in a security context?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "cse-q6-a", "text": "Using the strongest possible single security control",
                    "is_correct": False},
                {"id": "cse-q6-b", "text": "Encrypting all traffic at the deepest network layer",
                    "is_correct": False},
                {"id": "cse-q6-c", "text": "Applying multiple overlapping security controls so no single failure is catastrophic", "is_correct": True},
                {"id": "cse-q6-d",
                    "text": "Hiding system details from external users (security by obscurity)", "is_correct": False},
            ],
        },
    ],
    "DevOps in Practice": [
        {
            "text": "What is the key difference between Continuous Delivery and Continuous Deployment?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "dop-q1-a", "text": "Continuous Delivery skips testing; Continuous Deployment does not", "is_correct": False},
                {"id": "dop-q1-b", "text": "Continuous Delivery requires manual approval before production; Continuous Deployment ships automatically", "is_correct": True},
                {"id": "dop-q1-c", "text": "Continuous Deployment is only for small teams",
                    "is_correct": False},
                {"id": "dop-q1-d", "text": "They are synonyms", "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are valid Terraform workflow commands in the correct order?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "dop-q2-a", "text": "terraform init", "is_correct": True},
                {"id": "dop-q2-b", "text": "terraform plan", "is_correct": True},
                {"id": "dop-q2-c", "text": "terraform build", "is_correct": False},
                {"id": "dop-q2-d", "text": "terraform apply", "is_correct": True},
            ],
        },
        {
            "text": "In GitHub Actions, where are workflow definitions stored?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "dop-q3-a", "text": ".github/actions/", "is_correct": False},
                {"id": "dop-q3-b", "text": ".github/workflows/", "is_correct": True},
                {"id": "dop-q3-c", "text": "ci/", "is_correct": False},
                {"id": "dop-q3-d", "text": "Stored in the GitHub UI only",
                    "is_correct": False},
            ],
        },
        {
            "text": "What problem does Docker primarily solve for developers?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "dop-q4-a", "text": "Automatically writing unit tests",
                    "is_correct": False},
                {"id": "dop-q4-b", "text": "Packaging an application with all its dependencies so it runs consistently anywhere", "is_correct": True},
                {"id": "dop-q4-c", "text": "Providing a cloud database management service",
                    "is_correct": False},
                {"id": "dop-q4-d", "text": "Monitoring application performance in production",
                    "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are benefits of Infrastructure as Code (IaC)?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "dop-q5-a", "text": "Infrastructure changes are version-controlled and reviewable", "is_correct": True},
                {"id": "dop-q5-b", "text": "Environments are reproducible and consistent",
                    "is_correct": True},
                {"id": "dop-q5-c", "text": "It eliminates the need for cloud provider accounts",
                    "is_correct": False},
                {"id": "dop-q5-d", "text": "Reduces manual configuration drift",
                    "is_correct": True},
            ],
        },
        {
            "text": "What is a 'blue-green deployment' strategy?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "dop-q6-a", "text": "Deploying to 10% of users first, then gradually increasing",
                    "is_correct": False},
                {"id": "dop-q6-b", "text": "Running two identical production environments and switching traffic atomically", "is_correct": True},
                {"id": "dop-q6-c", "text": "Deploying only to a single region for cost savings",
                    "is_correct": False},
                {"id": "dop-q6-d", "text": "Colour-coding different microservices for observability",
                    "is_correct": False},
            ],
        },
    ],
    "AI Productivity Lab": [
        {
            "text": "What technique improves LLM performance on complex reasoning tasks by prompting it to show intermediate steps?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "apl-q1-a", "text": "Zero-shot prompting", "is_correct": False},
                {"id": "apl-q1-b", "text": "Role prompting", "is_correct": False},
                {"id": "apl-q1-c",
                    "text": "Chain-of-Thought (CoT) prompting", "is_correct": True},
                {"id": "apl-q1-d", "text": "Retrieval-Augmented Generation",
                    "is_correct": False},
            ],
        },
        {
            "text": "In a RAG (Retrieval-Augmented Generation) pipeline, what is the role of the vector store?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "apl-q2-a", "text": "Fine-tuning the language model on new data",
                    "is_correct": False},
                {"id": "apl-q2-b", "text": "Storing document embeddings for similarity-based retrieval", "is_correct": True},
                {"id": "apl-q2-c", "text": "Hosting the language model weights",
                    "is_correct": False},
                {"id": "apl-q2-d", "text": "Rate-limiting API calls to the LLM provider",
                    "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are valid strategies to reduce hallucination in LLM applications?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "apl-q3-a",
                    "text": "Ground responses in retrieved source documents (RAG)", "is_correct": True},
                {"id": "apl-q3-b", "text": "Instruct the model to say 'I don't know' when uncertain",
                    "is_correct": True},
                {"id": "apl-q3-c", "text": "Increase model temperature to get more creative answers",
                    "is_correct": False},
                {"id": "apl-q3-d", "text": "Implement output validation or fact-checking layers",
                    "is_correct": True},
            ],
        },
        {
            "text": "What does 'temperature' control in an LLM generation call?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "apl-q4-a", "text": "The maximum number of tokens generated",
                    "is_correct": False},
                {"id": "apl-q4-b", "text": "The randomness/creativity of the output — higher = more varied", "is_correct": True},
                {"id": "apl-q4-c", "text": "The context window size",
                    "is_correct": False},
                {"id": "apl-q4-d", "text": "The hardware clock speed of the inference server",
                    "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are true about LLM agents with tool use?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "apl-q5-a", "text": "Agents can call external APIs or run code to complete tasks", "is_correct": True},
                {"id": "apl-q5-b", "text": "The model decides which tool to call based on the task",
                    "is_correct": True},
                {"id": "apl-q5-c", "text": "Tool results are always 100% accurate and need no validation",
                    "is_correct": False},
                {"id": "apl-q5-d", "text": "Agents can use memory to retain context across multi-step tasks", "is_correct": True},
            ],
        },
        {
            "text": "What is 'few-shot prompting'?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "apl-q6-a", "text": "Fine-tuning a model on a small labelled dataset",
                    "is_correct": False},
                {"id": "apl-q6-b", "text": "Providing 2-5 input/output examples in the prompt before the actual query", "is_correct": True},
                {"id": "apl-q6-c", "text": "Asking the model the same question multiple times and voting",
                    "is_correct": False},
                {"id": "apl-q6-d", "text": "Limiting the model to short responses only",
                    "is_correct": False},
            ],
        },
    ],
    "Data Visualization Studio": [
        {
            "text": "According to Edward Tufte, what should the data-ink ratio ideally be?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "dvs-q1-a", "text": "As low as possible to keep charts minimal",
                    "is_correct": False},
                {"id": "dvs-q1-b", "text": "As high as possible — every pixel should encode data",
                    "is_correct": True},
                {"id": "dvs-q1-c", "text": "Exactly 0.5 — balance decoration and data",
                    "is_correct": False},
                {"id": "dvs-q1-d", "text": "It depends on the audience's technical background",
                    "is_correct": False},
            ],
        },
        {
            "text": "Which colour scale types are correctly matched to their use case?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "dvs-q2-a",
                    "text": "Sequential — ordered numerical data (e.g., temperature gradient)", "is_correct": True},
                {"id": "dvs-q2-b",
                    "text": "Diverging — data with a meaningful midpoint (e.g., profit/loss)", "is_correct": True},
                {"id": "dvs-q2-c", "text": "Qualitative — categorical data with no inherent order",
                    "is_correct": True},
                {"id": "dvs-q2-d", "text": "Sequential — categorical data like country names",
                    "is_correct": False},
            ],
        },
        {
            "text": "In Plotly Dash, what mechanism updates a graph when a dropdown value changes?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "dvs-q3-a", "text": "JavaScript event listeners written by the developer",
                    "is_correct": False},
                {"id": "dvs-q3-b", "text": "A Python @app.callback decorator linking Input and Output components", "is_correct": True},
                {"id": "dvs-q3-c", "text": "Websocket connections managed by the browser",
                    "is_correct": False},
                {"id": "dvs-q3-d", "text": "Periodic polling configured in dash.json",
                    "is_correct": False},
            ],
        },
        {
            "text": "Which chart type is most appropriate for showing part-to-whole relationships across multiple categories?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "dvs-q4-a", "text": "Line chart", "is_correct": False},
                {"id": "dvs-q4-b", "text": "Scatter plot", "is_correct": False},
                {"id": "dvs-q4-c", "text": "100% stacked bar chart", "is_correct": True},
                {"id": "dvs-q4-d", "text": "Box plot", "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are pre-attentive visual attributes processed almost instantly?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "dvs-q5-a", "text": "Colour hue", "is_correct": True},
                {"id": "dvs-q5-b", "text": "Element size", "is_correct": True},
                {"id": "dvs-q5-c", "text": "Exact numerical labels",
                    "is_correct": False},
                {"id": "dvs-q5-d",
                    "text": "Orientation (angle)", "is_correct": True},
            ],
        },
        {
            "text": "Why should dual y-axes on a single chart generally be avoided?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "dvs-q6-a", "text": "They require too much processing power to render",
                    "is_correct": False},
                {"id": "dvs-q6-b", "text": "They can mislead viewers by implying a relationship or correlation that may not exist", "is_correct": True},
                {"id": "dvs-q6-c", "text": "They are not supported by most charting libraries",
                    "is_correct": False},
                {"id": "dvs-q6-d", "text": "They only work in PDF format",
                    "is_correct": False},
            ],
        },
    ],
    "Communication for Engineers": [
        {
            "text": "Which voice is preferred in technical writing for clarity and directness?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "cfe-q1-a", "text": "Passive voice — 'The bug was fixed by the engineer'",
                    "is_correct": False},
                {"id": "cfe-q1-b", "text": "Active voice — 'The engineer fixed the bug'",
                    "is_correct": True},
                {"id": "cfe-q1-c", "text": "Third person impersonal throughout",
                    "is_correct": False},
                {"id": "cfe-q1-d",
                    "text": "First person plural ('we') exclusively", "is_correct": False},
            ],
        },
        {
            "text": "Which of the following should a good software README always include?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "cfe-q2-a", "text": "Installation instructions",
                    "is_correct": True},
                {"id": "cfe-q2-b", "text": "Usage examples with code snippets",
                    "is_correct": True},
                {"id": "cfe-q2-c", "text": "The author's home address",
                    "is_correct": False},
                {"id": "cfe-q2-d", "text": "Contribution guidelines", "is_correct": True},
            ],
        },
        {
            "text": "What does the Pyramid Principle recommend for structuring communication to stakeholders?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "cfe-q3-a", "text": "Start with detailed methodology, then reveal the conclusion at the end", "is_correct": False},
                {"id": "cfe-q3-b", "text": "Present the conclusion first, then support it with arguments and data", "is_correct": True},
                {"id": "cfe-q3-c", "text": "Use equal time for context, methodology, and results",
                    "is_correct": False},
                {"id": "cfe-q3-d", "text": "Open with a joke to establish rapport before the main message",
                    "is_correct": False},
            ],
        },
        {
            "text": "When presenting technical results to a non-technical stakeholder, you should lead with:",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "cfe-q4-a", "text": "The model architecture and hyperparameters used",
                    "is_correct": False},
                {"id": "cfe-q4-b", "text": "The business outcome or impact of the work",
                    "is_correct": True},
                {"id": "cfe-q4-c", "text": "A full walkthrough of the training data pipeline",
                    "is_correct": False},
                {"id": "cfe-q4-d", "text": "The list of libraries and frameworks used",
                    "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are hallmarks of well-written API documentation?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "cfe-q5-a", "text": "Clear description of every endpoint and its parameters",
                    "is_correct": True},
                {"id": "cfe-q5-b", "text": "Example requests and responses for each endpoint",
                    "is_correct": True},
                {"id": "cfe-q5-c", "text": "List of possible error codes and their meanings",
                    "is_correct": True},
                {"id": "cfe-q5-d", "text": "Internal server IP addresses and SSH credentials",
                    "is_correct": False},
            ],
        },
        {
            "text": "What is the recommended maximum number of ideas per slide in a technical presentation?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "cfe-q6-a", "text": "Five — to ensure full coverage",
                    "is_correct": False},
                {"id": "cfe-q6-b", "text": "Three — following the rule of three",
                    "is_correct": False},
                {"id": "cfe-q6-c", "text": "One — each slide should communicate a single clear idea",
                    "is_correct": True},
                {"id": "cfe-q6-d", "text": "As many as fit — density shows thoroughness",
                    "is_correct": False},
            ],
        },
    ],
    "Mobile App Prototyping": [
        {
            "text": "What does React Native use to render UI instead of a WebView?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "map-q1-a", "text": "HTML elements in an embedded browser",
                    "is_correct": False},
                {"id": "map-q1-b",
                    "text": "Native platform UI components (UIView on iOS, View on Android)", "is_correct": True},
                {"id": "map-q1-c", "text": "OpenGL canvas drawn by JavaScript",
                    "is_correct": False},
                {"id": "map-q1-d", "text": "Flutter engine widgets",
                    "is_correct": False},
            ],
        },
        {
            "text": "Which React Native component should be used for long, scrollable lists with many items?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "map-q2-a", "text": "ScrollView", "is_correct": False},
                {"id": "map-q2-b", "text": "View with overflow: scroll",
                    "is_correct": False},
                {"id": "map-q2-c",
                    "text": "FlatList (virtualised)", "is_correct": True},
                {"id": "map-q2-d",
                    "text": "ListView (deprecated)", "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are true about Zustand for state management?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "map-q3-a", "text": "State is accessed via a simple hook — useStore()",
                 "is_correct": True},
                {"id": "map-q3-b", "text": "It requires wrapping the app in a Provider component",
                    "is_correct": False},
                {"id": "map-q3-c", "text": "It is lighter and simpler than Redux for most use cases",
                    "is_correct": True},
                {"id": "map-q3-d", "text": "Stores can be persisted to AsyncStorage via a middleware plugin", "is_correct": True},
            ],
        },
        {
            "text": "What is an 'optimistic update' in mobile app development?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "map-q4-a", "text": "Assuming the user will give positive feedback on every screen",
                    "is_correct": False},
                {"id": "map-q4-b", "text": "Updating the UI immediately before the server confirms the action", "is_correct": True},
                {"id": "map-q4-c", "text": "Pre-fetching all data when the app starts",
                    "is_correct": False},
                {"id": "map-q4-d", "text": "Caching images for offline use",
                    "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are correct statements about Expo?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "map-q5-a", "text": "Expo Go lets you test your app on a real device without a native build", "is_correct": True},
                {"id": "map-q5-b", "text": "Expo managed workflow abstracts native build configuration", "is_correct": True},
                {"id": "map-q5-c", "text": "Expo requires macOS for all development regardless of target platform", "is_correct": False},
                {"id": "map-q5-d", "text": "EAS Build can compile native iOS and Android binaries in the cloud", "is_correct": True},
            ],
        },
        {
            "text": "What does a 'cold start' mean in the context of a React Native app?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "map-q6-a", "text": "The app loading on a device in cold weather",
                    "is_correct": False},
                {"id": "map-q6-b", "text": "The app being launched fresh from scratch with no prior state in memory", "is_correct": True},
                {"id": "map-q6-c", "text": "A crash caused by a null pointer exception",
                    "is_correct": False},
                {"id": "map-q6-d", "text": "Resuming the app from the device background",
                    "is_correct": False},
            ],
        },
    ],
    "Digital Marketing Foundations": [
        {
            "text": "What do Core Web Vitals measure in the context of SEO?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "dmf-q1-a", "text": "Number of backlinks to a page",
                    "is_correct": False},
                {"id": "dmf-q1-b", "text": "User experience signals: loading, interactivity, and visual stability", "is_correct": True},
                {"id": "dmf-q1-c", "text": "Social media engagement metrics",
                    "is_correct": False},
                {"id": "dmf-q1-d", "text": "Keyword density in the page's body text",
                    "is_correct": False},
            ],
        },
        {
            "text": "In Google Ads, what factors determine a keyword's Quality Score?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "dmf-q2-a",
                    "text": "Expected click-through rate (CTR)", "is_correct": True},
                {"id": "dmf-q2-b", "text": "Ad relevance to the keyword",
                    "is_correct": True},
                {"id": "dmf-q2-c", "text": "Landing page experience", "is_correct": True},
                {"id": "dmf-q2-d", "text": "The advertiser's total budget",
                    "is_correct": False},
            ],
        },
        {
            "text": "What is ROAS (Return on Ad Spend)?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "dmf-q3-a", "text": "Revenue minus ad spend",
                    "is_correct": False},
                {"id": "dmf-q3-b", "text": "Total impressions divided by ad spend",
                    "is_correct": False},
                {"id": "dmf-q3-c", "text": "Revenue generated divided by ad spend",
                    "is_correct": True},
                {"id": "dmf-q3-d", "text": "Clicks divided by impressions",
                    "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are off-page SEO techniques?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "dmf-q4-a", "text": "Earning backlinks from authoritative websites",
                    "is_correct": True},
                {"id": "dmf-q4-b", "text": "Guest posting on relevant industry blogs",
                    "is_correct": True},
                {"id": "dmf-q4-c", "text": "Optimising the title tag and meta description",
                    "is_correct": False},
                {"id": "dmf-q4-d", "text": "Building brand mentions and social signals",
                    "is_correct": True},
            ],
        },
        {
            "text": "In Meta Ads, what is a 'lookalike audience'?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "dmf-q5-a", "text": "Users who have already purchased from your store",
                    "is_correct": False},
                {"id": "dmf-q5-b", "text": "A new audience that shares characteristics with your existing customers or website visitors", "is_correct": True},
                {"id": "dmf-q5-c", "text": "An audience segment targeting users over 60",
                    "is_correct": False},
                {"id": "dmf-q5-d", "text": "A retargeting audience of people who abandoned a cart",
                    "is_correct": False},
            ],
        },
        {
            "text": "What does the Meta Pixel primarily enable?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "dmf-q6-a", "text": "Displaying ads on Google's Display Network",
                    "is_correct": False},
                {"id": "dmf-q6-b", "text": "Tracking user actions on your website to measure ad conversions and enable retargeting", "is_correct": True},
                {"id": "dmf-q6-c", "text": "Speeding up your website's page load time",
                    "is_correct": False},
                {"id": "dmf-q6-d", "text": "Sending push notifications to app users",
                    "is_correct": False},
            ],
        },
    ],
    "Career Readiness Program": [
        {
            "text": "What does ATS stand for, and why is it relevant to job seekers?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "crp-q1-a", "text": "Automated Task Scheduler — it schedules interview calls",
                    "is_correct": False},
                {"id": "crp-q1-b", "text": "Applicant Tracking System — it parses and filters resumes before human review", "is_correct": True},
                {"id": "crp-q1-c", "text": "Advanced Testing Suite — used in technical screenings",
                    "is_correct": False},
                {"id": "crp-q1-d", "text": "Application Transfer Service — used to send resumes to multiple companies", "is_correct": False},
            ],
        },
        {
            "text": "Which of the following make a resume more ATS-friendly?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "crp-q2-a", "text": "Using keywords from the job description",
                    "is_correct": True},
                {"id": "crp-q2-b", "text": "A clean single-column layout without tables or graphics",
                    "is_correct": True},
                {"id": "crp-q2-c", "text": "Embedding text inside images or infographic sections",
                    "is_correct": False},
                {"id": "crp-q2-d", "text": "Saving the resume as a .docx or .pdf with selectable text",
                    "is_correct": True},
            ],
        },
        {
            "text": "In a system design interview, which component is typically added first to handle increased read traffic?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "crp-q3-a",
                    "text": "A second database (write replica)", "is_correct": False},
                {"id": "crp-q3-b",
                    "text": "A caching layer (e.g., Redis)", "is_correct": True},
                {"id": "crp-q3-c", "text": "A message queue", "is_correct": False},
                {"id": "crp-q3-d", "text": "A CDN for database queries",
                    "is_correct": False},
            ],
        },
        {
            "text": "What is the recommended approach during a coding interview when you realise a brute-force solution?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "crp-q4-a", "text": "Stay silent and code silently until you find the optimal solution", "is_correct": False},
                {"id": "crp-q4-b", "text": "State the brute-force complexity, then discuss optimisation before coding", "is_correct": True},
                {"id": "crp-q4-c", "text": "Ask the interviewer to give you a hint immediately",
                    "is_correct": False},
                {"id": "crp-q4-d", "text": "Skip it and wait for the next question",
                    "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are best practices for a strong LinkedIn profile?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "crp-q5-a", "text": "A professional headshot photo",
                    "is_correct": True},
                {"id": "crp-q5-b", "text": "A first-person summary highlighting your value proposition", "is_correct": True},
                {"id": "crp-q5-c", "text": "Recommendations from colleagues or managers",
                    "is_correct": True},
                {"id": "crp-q5-d", "text": "Listing every course you ever took including unrelated hobbies",
                    "is_correct": False},
            ],
        },
        {
            "text": "What does quantifying achievements on a resume mean?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "crp-q6-a",
                    "text": "Adding numeric ratings to each skill (e.g., Python: 8/10)", "is_correct": False},
                {"id": "crp-q6-b",
                    "text": "Expressing the impact of your work with numbers (e.g., 'reduced load time by 40%')", "is_correct": True},
                {"id": "crp-q6-c", "text": "Listing the number of years at each company",
                    "is_correct": False},
                {"id": "crp-q6-d", "text": "Adding a numeric GPA next to every credential",
                    "is_correct": False},
            ],
        },
    ],
    "Financial Literacy Workshop": [
        {
            "text": "In the 50/30/20 budgeting rule, what does the 20% represent?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "flw-q1-a", "text": "Entertainment and dining out",
                    "is_correct": False},
                {"id": "flw-q1-b", "text": "Rent and utilities", "is_correct": False},
                {"id": "flw-q1-c", "text": "Savings, investments, and debt repayment",
                    "is_correct": True},
                {"id": "flw-q1-d", "text": "Insurance premiums", "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are characteristics of a SIP (Systematic Investment Plan)?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "flw-q2-a", "text": "Invests a fixed amount at regular intervals",
                    "is_correct": True},
                {"id": "flw-q2-b", "text": "Leverages rupee cost averaging to reduce timing risk",
                    "is_correct": True},
                {"id": "flw-q2-c", "text": "Requires a large lump sum upfront",
                    "is_correct": False},
                {"id": "flw-q2-d", "text": "Can be started with as little as ₹500 per month",
                    "is_correct": True},
            ],
        },
        {
            "text": "Using the Rule of 72, how many years will it take to double your money at 9% annual return?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "flw-q3-a", "text": "9 years", "is_correct": False},
                {"id": "flw-q3-b", "text": "8 years", "is_correct": True},
                {"id": "flw-q3-c", "text": "12 years", "is_correct": False},
                {"id": "flw-q3-d", "text": "6 years", "is_correct": False},
            ],
        },
        {
            "text": "What distinguishes an ELSS fund from other equity mutual funds?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "flw-q4-a", "text": "It only invests in government bonds",
                    "is_correct": False},
                {"id": "flw-q4-b", "text": "It offers a tax deduction under Section 80C with a 3-year lock-in", "is_correct": True},
                {"id": "flw-q4-c", "text": "It has a 10-year lock-in period",
                    "is_correct": False},
                {"id": "flw-q4-d", "text": "It is risk-free and guaranteed by SEBI",
                    "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are signs of 'bad debt' that should be avoided?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "flw-q5-a",
                    "text": "High interest rate (e.g., credit card at 36% p.a.)", "is_correct": True},
                {"id": "flw-q5-b",
                    "text": "Used to purchase a depreciating asset (e.g., luxury gadget)", "is_correct": True},
                {"id": "flw-q5-c", "text": "Home loan at 8.5% for a property expected to appreciate",
                    "is_correct": False},
                {"id": "flw-q5-d", "text": "Revolving balance that grows with compound interest monthly", "is_correct": True},
            ],
        },
        {
            "text": "What is the primary benefit of an index fund over an actively managed fund?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "flw-q6-a", "text": "Guaranteed returns above the market",
                    "is_correct": False},
                {"id": "flw-q6-b", "text": "Active stock selection by expert fund managers",
                    "is_correct": False},
                {"id": "flw-q6-c", "text": "Lower expense ratio and consistent market-matching returns over the long term", "is_correct": True},
                {"id": "flw-q6-d", "text": "Zero risk — index funds never lose value",
                    "is_correct": False},
            ],
        },
    ],
    "Research Writing Intensive": [
        {
            "text": "What does the IMRaD structure stand for in academic research papers?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "rwi-q1-a", "text": "Introduction, Methodology, Results, Analysis, and Discussion",
                    "is_correct": False},
                {"id": "rwi-q1-b", "text": "Introduction, Methods, Results, and Discussion",
                    "is_correct": True},
                {"id": "rwi-q1-c", "text": "Idea, Method, Research, and Delivery",
                    "is_correct": False},
                {"id": "rwi-q1-d", "text": "Introduction, Model, References, and Appendix",
                    "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are valid academic search databases for finding peer-reviewed papers?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "rwi-q2-a", "text": "Google Scholar", "is_correct": True},
                {"id": "rwi-q2-b", "text": "IEEE Xplore", "is_correct": True},
                {"id": "rwi-q2-c", "text": "Reddit r/science", "is_correct": False},
                {"id": "rwi-q2-d", "text": "Semantic Scholar", "is_correct": True},
            ],
        },
        {
            "text": "In the IMRaD structure, where should you interpret and contextualise your findings relative to prior work?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "rwi-q3-a", "text": "Results section", "is_correct": False},
                {"id": "rwi-q3-b", "text": "Methods section", "is_correct": False},
                {"id": "rwi-q3-c", "text": "Discussion section", "is_correct": True},
                {"id": "rwi-q3-d", "text": "Abstract", "is_correct": False},
            ],
        },
        {
            "text": "What does plagiarism checking software like Turnitin primarily measure?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "rwi-q4-a", "text": "Grammar and spelling errors",
                    "is_correct": False},
                {"id": "rwi-q4-b", "text": "Text similarity with existing published works and previously submitted papers", "is_correct": True},
                {"id": "rwi-q4-c", "text": "The quality and originality of research ideas",
                    "is_correct": False},
                {"id": "rwi-q4-d", "text": "Correct citation format",
                    "is_correct": False},
            ],
        },
        {
            "text": "Which of the following are characteristics of a well-formulated research question?",
            "type": QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": "rwi-q5-a", "text": "Specific and focused in scope",
                    "is_correct": True},
                {"id": "rwi-q5-b", "text": "Answerable with available methods and data",
                    "is_correct": True},
                {"id": "rwi-q5-c", "text": "Contributes new knowledge to the field",
                    "is_correct": True},
                {"id": "rwi-q5-d", "text": "As broad as possible to cover the entire field",
                    "is_correct": False},
            ],
        },
        {
            "text": "What is the difference between primary and secondary sources in academic research?",
            "type": QuestionType.MCQ,
            "marks": 10,
            "options": [
                {"id": "rwi-q6-a", "text": "Primary sources are more recent; secondary sources are older",
                    "is_correct": False},
                {"id": "rwi-q6-b", "text": "Primary sources present original data; secondary sources analyse or review existing research", "is_correct": True},
                {"id": "rwi-q6-c", "text": "Primary sources are always journal articles; secondary sources are books", "is_correct": False},
                {"id": "rwi-q6-d", "text": "Primary sources require a paywall; secondary sources are always open access", "is_correct": False},
            ],
        },
    ],
}


def get_questions(workshop_title: str, assessment_index: int) -> list[dict]:
    """Return domain-specific questions if available, else generate generic ones."""
    questions = ASSESSMENT_QUESTIONS.get(workshop_title)
    if questions:
        return questions
    # Generic fallback
    result = []
    for q_index in range(1, 7):
        ai = assessment_index
        qi = q_index
        result.append({
            "text": f"Question {qi}: Which statement about {workshop_title} is correct?",
            "type": QuestionType.MCQ if qi % 2 else QuestionType.MSQ,
            "marks": 10,
            "options": [
                {"id": f"gen-a{ai}-q{qi}-a",
                    "text": "Option A (correct)", "is_correct": True},
                {"id": f"gen-a{ai}-q{qi}-b", "text": "Option B",
                    "is_correct": qi % 2 == 0},
                {"id": f"gen-a{ai}-q{qi}-c", "text": "Option C", "is_correct": False},
                {"id": f"gen-a{ai}-q{qi}-d", "text": "Option D", "is_correct": False},
            ],
        })
    return result


# ---------------------------------------------------------------------------
# Main data loader
# ---------------------------------------------------------------------------

async def load_test_data() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:

        # ── Institutions ──────────────────────────────────────────────────
        institution_names = [
            "EduFlow HQ",
            "North Campus",
            "South Campus",
            "East Campus",
            "West Campus",
            "Central Academy",
            "Horizon Institute",
            "Summit Learning Hub",
            "Riverdale Center",
            "Future Skills School",
        ]
        institutions: list[Institution] = []
        for index, name in enumerate(institution_names, start=1):
            institutions.append(
                Institution(
                    name=name,
                    address=f"{index} Knowledge Park, Chennai",
                )
            )
        db.add_all(institutions)
        await db.flush()

        # ── Users ─────────────────────────────────────────────────────────
        users: list[User] = []

        admin = User(
            name="EduFlow Admin",
            email="admin@eduflow.edu",
            password=hash_password(PASSWORDS["admin@eduflow.edu"]),
            role=UserRole.ADMIN,
            institution_id=institutions[0].id,
            phone="+91 90000 00001",
            theme="light",
        )
        users.append(admin)

        institution_admins: list[User] = []
        for index, institution in enumerate(institutions, start=1):
            email = "institution.admin@eduflow.edu" if index == 1 else f"institution.admin{index}@eduflow.edu"
            admin_user = User(
                name=f"{institution.name} Admin",
                email=email,
                password=hash_password(PASSWORDS.get(email, DEFAULT_PASSWORD)),
                role=UserRole.INSTITUTION_ADMIN,
                institution_id=institution.id,
                phone=f"+91 91000 {index:05d}",
                theme="dark" if index % 2 == 0 else "light",
            )
            institution_admins.append(admin_user)
            users.append(admin_user)

        educator_data = [
            ("Demo Educator", 0),
            ("Asha Menon", 0),
            ("Ravi Narayan", 1),
            ("Priya Shah", 1),
            ("Karthik Iyer", 2),
            ("Meera Kulkarni", 2),
            ("Suresh Nambiar", 3),
            ("Divya Ramesh", 3),
            ("Anand Krishnan", 4),
            ("Lakshmi Varma", 5),
            ("Vikram Ghosh", 6),
            ("Pooja Agarwal", 7),
        ]
        educators: list[User] = []
        for index, (name, institution_index) in enumerate(educator_data, start=1):
            email = "educator@eduflow.edu" if index == 1 else f"educator{index}@eduflow.edu"
            # Assign different salary amounts based on index
            salary_amount = 30000 + (index * 5000)  # 30000, 35000, 40000, etc.
            salary_type = "monthly"
            educators.append(
                User(
                    name=name,
                    email=email,
                    password=hash_password(
                        PASSWORDS.get(email, DEFAULT_PASSWORD)),
                    role=UserRole.EDUCATOR,
                    institution_id=institutions[institution_index % len(
                        institutions)].id,
                    phone=f"+91 92000 {index:05d}",
                    theme="dark" if index % 2 else "light",
                    salary_amount=salary_amount,
                    salary_type=salary_type,
                )
            )
        users.extend(educators)

        student_names = [
            "Demo Student", "Arjun Rao", "Nisha Patel", "Devika Singh",
            "Rahul Nair", "Sneha Joshi", "Harish Kumar", "Ishita Ghosh",
            "Ananya Das", "Vikram Sen", "Ritika Jain", "Kabir Ali",
            "Neha Reddy", "Sanjay Pillai", "Lavanya Krishnan",
            "Tarun Mehta", "Preethi Suresh", "Aditya Bose", "Kavya Nair",
            "Rohan Desai", "Simran Kaur", "Manish Yadav", "Deepa Iyer",
            "Suraj Tiwari", "Anjali Sharma", "Nikhil Patel", "Riya Kapoor",
            "Karan Bajaj", "Shruti Menon", "Arun Pillai",
        ]
        students: list[User] = []
        for index, name in enumerate(student_names, start=1):
            email = "student@eduflow.edu" if index == 1 else f"student{index}@eduflow.edu"
            students.append(
                User(
                    name=name,
                    email=email,
                    password=hash_password(
                        PASSWORDS.get(email, DEFAULT_PASSWORD)),
                    role=UserRole.STUDENT,
                    institution_id=institutions[(
                        index - 1) % len(institutions)].id,
                    phone=f"+91 93000 {index:05d}",
                    theme="dark" if index % 3 == 0 else "light",
                )
            )
        users.extend(students)

        tech_support = User(
            name="EduFlow Support",
            email="support@eduflow.edu",
            password=hash_password(PASSWORDS.get("support@eduflow.edu", DEFAULT_PASSWORD)),
            role=UserRole.TECHNICAL_SUPPORT,
            institution_id=institutions[0].id,
            phone="+91 94000 00001",
            theme="dark",
        )
        users.append(tech_support)

        db.add_all(users)
        await db.flush()

        for institution, admin_user in zip(institutions, institution_admins):
            institution.admin_id = admin_user.id

        # ── Workshops ─────────────────────────────────────────────────────
        # (title, institution_index, educator_index, start_offset_days, duration_days)
        workshop_specs = [
            ("Full Stack Web Bootcamp",        0,  0, -30, 45),
            ("Python for Data Analysis",        0,  1, -21, 30),
            ("UI UX Design Sprint",             1,  2, -15, 20),
            ("Cloud Fundamentals",              1,  3, -10, 40),
            ("Machine Learning Basics",         2,  4, -25, 35),
            ("Data Visualization Studio",       2,  5, -8,  28),
            ("Cybersecurity Essentials",        3,  6, -18, 32),
            ("Communication for Engineers",     3,  7, -5,  18),
            ("Mobile App Prototyping",          4,  8, -14, 24),
            ("DevOps in Practice",              4,  9, -12, 26),
            ("AI Productivity Lab",             5, 10, -7,  21),
            ("Digital Marketing Foundations",   6, 11, -9,  22),
            ("Career Readiness Program",        7,  0, -16, 19),
            ("Financial Literacy Workshop",     8,  1, -11, 17),
            ("Research Writing Intensive",      9,  2, -20, 29),
        ]
        workshops: list[Workshop] = []
        workshop_educator_map: dict[str, User] = {}
        for title, inst_idx, edu_idx, start_offset, duration_days in workshop_specs:
            start_date = dt(start_offset, 9)
            workshop = Workshop(
                title=title,
                description=f"{title} — guided modules, hands-on assessments, and live instructor sessions.",
                start_date=start_date,
                end_date=start_date + timedelta(days=duration_days),
                institution_id=institutions[inst_idx].id,
            )
            workshops.append(workshop)
            workshop_educator_map[title] = educators[edu_idx % len(educators)]
        db.add_all(workshops)
        await db.flush()

        # ── Modules (3 per workshop) ───────────────────────────────────────
        modules: list[Module] = []
        modules_by_workshop: dict[str, list[Module]] = defaultdict(list)
        for workshop in workshops:
            for module_index in range(1, 4):
                module = Module(
                    workshop_id=workshop.id,
                    title=f"{workshop.title} — Module {module_index}",
                    order_index=module_index,
                    materials=get_materials(workshop.title, module_index),
                )
                modules.append(module)
                modules_by_workshop[workshop.id].append(module)
        db.add_all(modules)
        await db.flush()

        # ── Enrollments ───────────────────────────────────────────────────
        # Every student is enrolled in 3-5 workshops (round-robin + offset)
        status_cycle = [
            EnrollmentStatus.ACTIVE,
            EnrollmentStatus.COMPLETED,
            EnrollmentStatus.ACTIVE,
            EnrollmentStatus.DROPPED,
            EnrollmentStatus.COMPLETED,
        ]
        enrollments: list[Enrollment] = []
        seen_enrollments: set[tuple] = set()
        for student_index, student in enumerate(students):
            for workshop_offset in range(5):
                workshop = workshops[(
                    student_index + workshop_offset * 3) % len(workshops)]
                key = (student.id, workshop.id)
                if key in seen_enrollments:
                    continue
                seen_enrollments.add(key)
                status = status_cycle[(
                    student_index + workshop_offset) % len(status_cycle)]
                enrollments.append(
                    Enrollment(
                        student_id=student.id,
                        workshop_id=workshop.id,
                        status=status,
                        enrolled_at=workshop.start_date -
                        timedelta(days=7 - (workshop_offset % 5)),
                    )
                )
        db.add_all(enrollments)
        await db.flush()

        enrollments_by_workshop: dict[str,
                                      list[Enrollment]] = defaultdict(list)
        for enrollment in enrollments:
            enrollments_by_workshop[enrollment.workshop_id].append(enrollment)

        # ── Sessions (3 per workshop) ─────────────────────────────────────
        sessions: list[Session] = []
        for workshop in workshops:
            for session_index in range(1, 4):
                start_time = workshop.start_date + \
                    timedelta(days=session_index * 7, hours=2)
                sessions.append(
                    Session(
                        workshop_id=workshop.id,
                        title=f"{workshop.title} — Live Session {session_index}",
                        start_time=start_time,
                        end_time=start_time + timedelta(hours=2),
                    )
                )
        db.add_all(sessions)
        await db.flush()

        # ── Attendance (varied patterns) ───────────────────────────────────
        # Pattern rotates per (session_index, student_index) for realistic spread
        attendance_patterns = [
            # (present_rate, late_rate)  → remaining = absent
            ["present", "present", "present", "late"],    # mostly present
            ["present", "present", "late",    "absent"],  # occasional miss
            ["present", "late",    "absent",  "absent"],  # poor attendance
            ["present", "present", "present", "present"],  # perfect
        ]
        attendance_rows: list[Attendance] = []
        for session_index, session in enumerate(sessions):
            session_enrollments = enrollments_by_workshop[session.workshop_id]
            pattern = attendance_patterns[session_index % len(
                attendance_patterns)]
            for row_index, enrollment in enumerate(session_enrollments):
                attendance_rows.append(
                    Attendance(
                        session_id=session.id,
                        student_id=enrollment.student_id,
                        status=pattern[row_index % len(pattern)],
                    )
                )
        db.add_all(attendance_rows)
        await db.flush()

        # ── Assessments (one per workshop) ────────────────────────────────
        assessments: list[Assessment] = []
        for workshop in workshops:
            module = modules_by_workshop[workshop.id][0]
            assessments.append(
                Assessment(
                    workshop_id=workshop.id,
                    module_id=module.id,
                    title=f"{workshop.title} — Checkpoint Assessment",
                    total_marks=60,
                    pass_mark=30,
                )
            )
        db.add_all(assessments)
        await db.flush()

        # ── Questions (6 domain-specific per assessment) ───────────────────
        questions: list[Question] = []
        for assessment_index, (assessment, workshop) in enumerate(zip(assessments, workshops)):
            for q_spec in get_questions(workshop.title, assessment_index):
                questions.append(
                    Question(
                        assessment_id=assessment.id,
                        text=q_spec["text"],
                        type=q_spec["type"],
                        marks=q_spec["marks"],
                        options=q_spec["options"],
                    )
                )
        db.add_all(questions)
        await db.flush()

        questions_by_assessment: dict[str, list[Question]] = defaultdict(list)
        for question in questions:
            questions_by_assessment[question.assessment_id].append(question)

        # ── Submissions ────────────────────────────────────────────────────
        # Realistic score spread: high scorers, mid scorers, just-passing
        score_bands = [54, 48, 42, 36, 30, 24]  # out of 60
        submissions: list[Submission] = []
        for assessment_index, assessment in enumerate(assessments):
            active_enrollments = [
                e for e in enrollments_by_workshop[assessment.workshop_id]
                if e.status != EnrollmentStatus.DROPPED
            ]
            for sub_index, enrollment in enumerate(active_enrollments[:6]):
                score = score_bands[sub_index % len(score_bands)]
                submissions.append(
                    Submission(
                        student_id=enrollment.student_id,
                        assessment_id=assessment.id,
                        score=score,
                        percentage=int((score / 60) * 100),
                        pass_fail=score >= assessment.pass_mark,
                        answers=[
                            {
                                "question_id": q.id,
                                "selected_option_ids": [
                                    o["id"] for o in q.options
                                    if o["is_correct"]
                                ] if sub_index < 3 else [q.options[1]["id"]],
                            }
                            for q in questions_by_assessment[assessment.id]
                        ],
                        submitted_at=dt(-5 + (sub_index % 3)),
                    )
                )
        db.add_all(submissions)
        await db.flush()

        # ── Certificates ───────────────────────────────────────────────────
        certificates: list[Certificate] = []
        completed_enrollments = [
            e for e in enrollments if e.status == EnrollmentStatus.COMPLETED]
        for index, enrollment in enumerate(completed_enrollments, start=1):
            code = f"VIDYA-{index:04d}-CERT"
            certificates.append(
                Certificate(
                    student_id=enrollment.student_id,
                    workshop_id=enrollment.workshop_id,
                    issue_date=dt(-index),
                    verification_code=code,
                )
            )
        db.add_all(certificates)
        await db.flush()

        workshop_by_id = {w.id: w for w in workshops}
        student_by_id = {s.id: s for s in students}
        for certificate in certificates:
            student = student_by_id.get(certificate.student_id)
            workshop = workshop_by_id.get(certificate.workshop_id)
            if student and workshop:
                generate_certificate_pdf(
                    student_name=student.name or student.email,
                    workshop_title=workshop.title or "Workshop",
                    verification_code=certificate.verification_code or certificate.id,
                    certificate_id=certificate.id,
                )

        # ── Fee Plans ──────────────────────────────────────────────────────
        fee_plan_specs = [
            ("Monthly Standard",     2500,  "monthly"),
            ("Monthly Plus",         3200,  "monthly"),
            ("Quarterly Saver",      7200,  "quarterly"),
            ("Quarterly Premium",    9000,  "quarterly"),
            ("Semester Basic",      14000,  "semester"),
            ("Semester Advanced",   18000,  "semester"),
            ("Bootcamp Intensive",  22000,  "one_time"),
            ("Professional Track",  26000,  "one_time"),
            ("Certification Add-on", 3500,  "one_time"),
            ("Weekend Track",        6000,  "monthly"),
            ("Early Bird Special",   8500,  "quarterly"),
            ("Corporate Sponsored", 30000,  "one_time"),
        ]
        fee_plans: list[FeePlan] = []
        for name, amount, billing_cycle in fee_plan_specs:
            fee_plans.append(FeePlan(name=name, amount=amount,
                             billing_cycle=billing_cycle))
        db.add_all(fee_plans)
        await db.flush()

        # ── Student Fees ───────────────────────────────────────────────────
        # Each student gets 1-2 active fee records
        student_fees: list[StudentFee] = []
        for index, student in enumerate(students):
            fee_plan = fee_plans[index % len(fee_plans)]
            paid_so_far = (index % 5) * (fee_plan.amount // 5)
            student_fees.append(
                StudentFee(
                    student_id=student.id,
                    fee_plan_id=fee_plan.id,
                    balance=max(0, fee_plan.amount - paid_so_far),
                )
            )
        # Extra second fee record for first 10 students (e.g. add-on plan)
        for index, student in enumerate(students[:10]):
            addon_plan = fee_plans[(index + 8) % len(fee_plans)]
            student_fees.append(
                StudentFee(
                    student_id=student.id,
                    fee_plan_id=addon_plan.id,
                    balance=max(0, addon_plan.amount - 1000),
                )
            )
        db.add_all(student_fees)
        await db.flush()

        # ── Payments (2 rounds of payments per student, varied methods) ────
        payment_methods = ["upi", "card",
                           "bank_transfer", "cash", "upi", "card"]
        payments: list[Payment] = []
        # Round 1 — initial instalments
        for index, student in enumerate(students):
            fee_plan = fee_plans[index % len(fee_plans)]
            instalment = fee_plan.amount // 5 or 500
            payments.append(
                Payment(
                    student_id=student.id,
                    amount=instalment + (index % 4) * 200,
                    method=payment_methods[index % len(payment_methods)],
                    reference=f"PAY1-{index + 1:04d}",
                    created_at=dt(-20 + (index % 7)),
                )
            )
        # Round 2 — second instalment
        for index, student in enumerate(students):
            fee_plan = fee_plans[(index + 3) % len(fee_plans)]
            instalment = fee_plan.amount // 5 or 500
            payments.append(
                Payment(
                    student_id=student.id,
                    amount=instalment + (index % 3) * 150,
                    method=payment_methods[(index + 2) % len(payment_methods)],
                    reference=f"PAY2-{index + 1:04d}",
                    created_at=dt(-10 + (index % 5)),
                )
            )
        # Round 3 — partial/late payments for a subset
        for index, student in enumerate(students[:15]):
            payments.append(
                Payment(
                    student_id=student.id,
                    amount=800 + (index % 4) * 300,
                    method=payment_methods[(index + 1) % len(payment_methods)],
                    reference=f"PAY3-{index + 1:04d}",
                    created_at=dt(-3 + (index % 3)),
                )
            )
        db.add_all(payments)
        await db.flush()

        # ── Notifications ──────────────────────────────────────────────────
        notification_types = [
            NotificationType.GENERAL,
            NotificationType.TEST,
            NotificationType.FEES,
            NotificationType.ATTENDANCE,
            NotificationType.CERTIFICATE,
        ]
        notification_messages = {
            NotificationType.GENERAL:     "Platform maintenance scheduled for Sunday 2-4 AM.",
            NotificationType.TEST:        "Your assessment result is now available. Check your dashboard.",
            NotificationType.FEES:        "Your next fee instalment is due in 7 days. Please make the payment.",
            NotificationType.ATTENDANCE:  "Your attendance dropped below 75% this week. Please attend upcoming sessions.",
            NotificationType.CERTIFICATE: "Congratulations! Your certificate has been issued. Download it from your profile.",
        }
        notifications: list[Notification] = []
        notification_users = [
            admin, *institution_admins[:5], *educators[:8], *students]
        for index, user in enumerate(notification_users):
            ntype = notification_types[index % len(notification_types)]
            notifications.append(
                Notification(
                    user_id=user.id,
                    message=notification_messages[ntype],
                    status=NotificationStatus.READ if index % 3 == 0 else NotificationStatus.UNREAD,
                    notification_type=ntype,
                    created_at=dt(-index % 14),
                )
            )
        # A second notification for educators and admin
        for index, user in enumerate([admin, *educators[:6]]):
            ntype = notification_types[(index + 2) % len(notification_types)]
            notifications.append(
                Notification(
                    user_id=user.id,
                    message=f"Reminder: {notification_messages[ntype]}",
                    status=NotificationStatus.UNREAD,
                    notification_type=ntype,
                    created_at=dt(-(index + 1)),
                )
            )
        db.add_all(notifications)
        await db.commit()

        # ── Summary ────────────────────────────────────────────────────────
        print("[test_data] ✅ Demo database loaded successfully.\n")
        print(f"  institutions   : {len(institutions)}")
        print(
            f"  users          : {len(users)}  (1 admin, {len(institution_admins)} inst. admins, {len(educators)} educators, {len(students)} students)")
        print(f"  workshops      : {len(workshops)}")
        print(
            f"  modules        : {len(modules)}  (3 per workshop, domain-specific materials)")
        print(f"  enrollments    : {len(enrollments)}")
        print(f"  sessions       : {len(sessions)}  (3 per workshop)")
        print(f"  attendance     : {len(attendance_rows)}")
        print(f"  assessments    : {len(assessments)}")
        print(
            f"  questions      : {len(questions)}  (6 domain-specific per assessment)")
        print(f"  submissions    : {len(submissions)}")
        print(f"  certificates   : {len(certificates)}")
        print(f"  fee_plans      : {len(fee_plans)}")
        print(f"  student_fees   : {len(student_fees)}")
        print(f"  payments       : {len(payments)}")
        print(f"  notifications  : {len(notifications)}")
        print()
        print("[test_data] Demo logins:")
        print("  admin@eduflow.edu                  / admin123")
        print("  institution.admin@eduflow.edu      / institution123")
        print("  educator@eduflow.edu               / educator123")
        print("  student@eduflow.edu                / student123")


if __name__ == "__main__":
    asyncio.run(load_test_data())
