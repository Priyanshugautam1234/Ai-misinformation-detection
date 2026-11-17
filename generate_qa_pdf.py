import sys
import os
from fpdf import FPDF

class InterviewGuidePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.current_section_name = ""
        self.set_auto_page_break(auto=True, margin=20)
        self.alias_nb_pages()

    def header(self):
        # Skip header on the cover page (page 1)
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, "AI Misinformation Detection Platform - Technical Q&A Guide", align="L")
        self.set_x(-100)
        self.cell(0, 10, f"Section: {self.current_section_name}", align="R")
        self.ln(10)
        # Horizontal line below header
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.line(15, 20, 195, 20)
        self.ln(2)

    def footer(self):
        # Skip footer on the cover page (page 1)
        if self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()} of {{nb}}", align="C")

    def chapter_title(self, num, label):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(26, 54, 93)  # Dark Blue
        self.cell(0, 10, f"Section {num}: {label}", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.current_section_name = label

    def ask_question(self, q_num, question_text):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(45, 55, 72)  # Charcoal
        # Use multi_cell to handle line breaks in question
        self.multi_cell(0, 6, f"Q{q_num}. {question_text}")
        self.ln(1)

    def give_answer(self, answer_text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(74, 85, 104)  # Slate Gray
        self.multi_cell(0, 5, f"Answer: {answer_text}")
        self.ln(5)

def clean_text(text):
    # Standardize characters to avoid fpdf encoding issues
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('‘', "'").replace('’', "'")
    text = text.replace('—', '-').replace('–', '-')
    text = text.replace('•', '-')
    text = text.replace('é', 'e').replace('ó', 'o').replace('á', 'a').replace('í', 'i').replace('ú', 'u')
    return text

def main():
    pdf = InterviewGuidePDF()
    pdf.add_page()
    
    # --- COVER PAGE ---
    pdf.set_y(40)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(26, 54, 93)
    pdf.multi_cell(0, 12, "AI Misinformation &\nScam Detection Platform", align="C")
    
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(74, 85, 104)
    pdf.cell(0, 10, "Comprehensive Technical Q&A & Interview Guide", align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(15)
    pdf.set_draw_color(26, 54, 93)
    pdf.set_line_width(1)
    pdf.line(40, pdf.get_y(), 170, pdf.get_y())
    
    pdf.ln(20)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(113, 128, 150)
    desc = (
        "An end-to-end technical documentation covering system design, "
        "FastAPI asynchronous backend, React functional frontend components, NLP claim and scam "
        "classifiers, multi-modal image forensics (EXIF, ELA, Splicing), CNN deep learning architectures, "
        "and hybrid scoring engines. Designed for interview preparation from a software engineering "
        "and machine learning perspective."
    )
    pdf.multi_cell(0, 6, desc, align="C")
    
    pdf.set_y(-40)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(45, 55, 72)
    pdf.cell(0, 5, "Candidate Preparation Resource", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, "Generated for Live Verification & Code Review", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "System Version: 1.0.0", align="C", new_x="LMARGIN", new_y="NEXT")

    # --- Q&A DATA ---
    sections = [
        # SECTION 1
        ("Project Overview Questions", [
            ("Explain your project end-to-end.", 
             "The platform is a multi-modal misinformation and scam detection system. It features a React dashboard on the frontend that interacts with a FastAPI backend. Users can input a text claim, scan a URL, or upload an image. The backend evaluates each input: text is classified using an NLP pipeline and a Logistic Regression scam model; URLs are scraped and checked against reputation directories and DNS/WHOIS records; images undergo detailed forensics, including EXIF extraction, Error Level Analysis (ELA), splicing checks, and neural classification via a PyTorch ResNet-18 model. The results are unified into a final trust score and logged to a MongoDB registry."),
            ("What problem does your project solve?", 
             "It counters digital deception, media manipulation, and online fraud. Fake news, scams, and deepfakes are increasingly complex and multi-modal. This project aggregates multiple analytical layers (deep learning, metadata telemetry, reputation scoring) to give users a clear, verified trust rating for suspect text, images, and links on a single platform."),
            ("Why did you build this project?", 
             "To demonstrate how machine learning (NLP and computer vision) can combine with traditional forensics (EXIF headers, ELA, WHOIS lookup) to address modern trust verification. Relying on a single model (like a CNN or an LLM) creates vulnerabilities; a hybrid heuristics-and-neural approach is far more transparent and robust against adversarial manipulation."),
            ("What is misinformation?", 
             "Misinformation refers to false, inaccurate, or misleading information shared regardless of malicious intent (e.g., rumors or misreported facts). Disinformation is intentionally crafted to deceive (e.g., phishing scams, political deepfakes). The platform identifies hallmarks of both, such as clickbait markers, spoofed domains, and image manipulation artifacts."),
            ("What are the major modules?", 
             "1) NLP Claim & Scam Analyzer: Evaluates clickbait, bias, sentiment, and matches claims against debunked databases, classifying spam via a trained Logistic Regression model.\n2) URL Scan Engine: Checks security parameters (SSL, redirects), WHOIS registration dates, TLD safety, and scrapes title text for clickbait patterns.\n3) Image Forensics Engine: Combines EXIF parsing, ELA map generation, noise texture variance, blur detection, and ResNet-18 CNN image classification.\n4) Reporting Dashboard: CRUD system for user-reported scams via a FastAPI/MongoDB pipeline.\n5) Glassmorphic UI: High-performance dashboard in React + Vite + TypeScript."),
            ("What is the project architecture?", 
             "It uses a decoupled client-server architecture. The frontend is built on Vite, React, and TypeScript, styled with a custom CSS variable-driven dark-mode glassmorphic system. The backend is a FastAPI ASGI app served by Uvicorn. Models (PyTorch ResNet-18 and Scikit-Learn Logistic Regression) are loaded at startup. Data is persisted in MongoDB, with a transparent in-memory mock fallback class for offline execution."),
            ("How does data flow from frontend to backend?", 
             "For text/URLs, the React client sends a POST request with a JSON body. FastAPI validates the request using Pydantic, performs analysis, and sends back a structured JSON response. For images, the client uploads a file via FormData to the backend. The backend reads the bytes, generates ELA and texture statistics in-memory, runs PyTorch inference on CPU, and returns a JSON payload including a base64-encoded ELA map for side-by-side rendering."),
            ("Why did you choose FastAPI?", 
             "FastAPI was selected for three primary reasons: 1) Performance: Built on Starlette and Pydantic, it is one of the fastest Python frameworks available, matching Node.js and Go. 2) Native Async: Allows non-blocking operations, which is crucial for scraping URLs and performing multiple forensic checks. 3) Auto-Documentation: Generates OpenAPI/Swagger interactive docs automatically, accelerating development and testing."),
            ("Why did you choose React?", 
             "React was chosen for its virtual DOM rendering, which allows the dashboard to update dynamically upon file drop or input analysis without reloading. Functional components combined with React hooks (useState, useEffect) provide a modular, maintainable structure that maps well to our dashboard components."),
            ("What challenges did you face?", 
             "1) Version conflicts with precompiled torchvision binaries on the local CPU environment. We solved this by defining the ResNet-18 layers natively in pure PyTorch and loading the weights manually. 2) False positives on blurry or highly compressed images (e.g., from WhatsApp or screenshots). We resolved this by implementing an edge-variance blur checker and dynamically reducing heuristics penalties for compressed files. 3) Database dependency: designed a robust in-memory mock database layer to prevent server crashes when MongoDB is offline.")
        ]),
        
        # SECTION 2
        ("System Design Questions", [
            ("Draw the architecture.", 
             "[React Frontend (Vite/TS)]  <-- Asynchronous HTTP REST Requests (fetch) -->  [FastAPI Backend Gateway (Uvicorn)]\n"
             "                                                                           |\n"
             "     +----------------------------------+----------------------------------+----------------------------------+\n"
             "     |                                  |                                  |                                  |\n"
             "[NLP Pipeline]                  [URL Scanner]                      [Image Forensics]                  [Report DB Manager]\n"
             " - Spam Classifier (LR)          - BeautifulSoup Scraper            - EXIF Metadata Reader             - PyMongo Client\n"
             " - Clickbait / Bias RegEx        - HTTPX Redirect Tracer            - ELA Map Generator                - MongoDB / In-memory Fallback\n"
             " - Debunk DB Lookup              - RDAP/WHOIS Domain Age            - ResNet-18 PyTorch CNN Classifier"),
            ("How does frontend communicate with backend?", 
             "The React client uses standard async/fetch calls to communicate with the FastAPI backend. Text and URL analyses use JSON request bodies. Image analysis uses multipart/form-data to stream image bytes to the backend. All responses are structured as standard JSON objects."),
            ("Why use REST APIs?", 
             "REST APIs provide a stateless, standardized, and decoupled interface between the client and server. This allows the backend models to be updated, optimized, or scaled independently of the user interface, and enables integration with other clients (e.g., mobile apps, browser extensions) in the future."),
            ("Why separate modules?", 
             "Separating modules (NLP, URL scanner, image forensics, database) aligns with the Single Responsibility Principle. It ensures the codebase remains maintainable, allows developers to work on different engines in parallel without merge conflicts, and simplifies debugging and unit testing."),
            ("How would you scale this project?", 
             "To scale horizontally: 1) Deploy the FastAPI backend inside Docker containers managed by Kubernetes. 2) Use a load balancer (like Nginx) to distribute requests. 3) Extract heavy ML inference tasks (PyTorch ResNet-18) out of the main API gateway into separate worker nodes using a task queue like Celery with Redis, or deploy them via a dedicated model serving tool like Triton or TorchServe."),
            ("How would you handle 10,000 requests/min?", 
             "1) Implement a cache layer (like Redis) for duplicate URL/Text lookups. 2) Separate the lightweight API routing from heavy CPU-bound image forensics. 3) Run uvicorn with multiple worker processes (`uvicorn --workers N`). 4) Autoscale instances using Kubernetes HPA based on CPU/Memory thresholds. 5) Use MongoDB sharding to distribute database write loads."),
            ("How would you deploy it?", 
             "Deploy the frontend as a static build to a CDN (Vercel, Netlify, or AWS S3 + CloudFront) for global low-latency delivery. Deploy the FastAPI backend on an AWS ECS (Elastic Container Service) cluster or an EKS (Kubernetes) cluster, with a managed MongoDB database hosted on MongoDB Atlas."),
            ("How would you make it production-ready?", 
             "1) Implement user authentication (JWT/OAuth2) and rate-limiting. 2) Replace development CORS wildcards with explicit domain origins. 3) Connect a resilient, replicated MongoDB database. 4) Use production-grade logging (Structured JSON logs) and error tracking (Sentry). 5) Add robust validation checks for uploaded files (limiting file size and verifying magic numbers)."),
            ("What bottlenecks exist?", 
             "1) Heavy model inference: Running PyTorch ResNet-18 on CPU for every image upload is CPU-bound. 2) Network latency: The URL scanner calls external RDAP/WHOIS servers, which can hang. We mitigated this with async network calls, timeout limits, and curated lists of popular domains."),
            ("How would you add caching?", 
             "I would introduce Redis in the backend. When a URL or text claim is scanned, the result would be stored in Redis with the domain/text MD5 hash as the key and a Time-To-Live (TTL) of 24 hours. Subsequent requests for the same content would be served directly from Redis, bypassing web scraping, database queries, and model inference.")
        ]),

        # SECTION 3
        ("FastAPI Questions", [
            ("What is FastAPI?", 
             "FastAPI is a modern, high-performance web framework for building APIs with Python 3.7+ based on standard Python type hints. It is built on top of Starlette (for web parts) and Pydantic (for data validation), supporting asynchronous execution natively."),
            ("Why FastAPI over Flask?", 
             "FastAPI provides native support for asynchronous code (`async/await`), automated request validation/serialization out of the box via Pydantic, and automatic Swagger UI generation. In contrast, Flask is synchronous by default, requiring external libraries (like Marshmallow or Flask-RESTful) to achieve similar validation features."),
            ("What is ASGI?", 
             "Asynchronous Server Gateway Interface (ASGI) is the spiritual successor to WSGI. It provides a standard interface for asynchronous Python web servers and applications, enabling them to handle concurrent connections, WebSockets, and long-lived HTTP requests concurrently."),
            ("What is Uvicorn?", 
             "Uvicorn is an ASGI web server implementation for Python. It is used to run FastAPI applications, utilizing `uvloop` (a fast, drop-in replacement for the asyncio event loop) to achieve high performance."),
            ("What are Pydantic models?", 
             "Pydantic models are Python classes that inherit from `pydantic.BaseModel`. They define the structure and data types of request/response payloads. Pydantic enforces type hints at runtime, raising validation errors if data doesn't match the schema."),
            ("What is request validation?", 
             "Request validation is the process of checking if the client's input meets the API's constraints (e.g., correct data type, string length, email format). FastAPI uses Pydantic to automatically validate incoming JSON bodies, returning a 422 Unprocessable Entity error if validation fails."),
            ("How does dependency injection work?", 
             "FastAPI features a built-in Dependency Injection system using `Depends()`. It allows declaring parameters that the framework evaluates and injects at runtime, simplifying code reuse (e.g., database sessions, security authentication, shared configurations)."),
            ("How are file uploads handled?", 
             "FastAPI handles file uploads using `UploadFile` and the python-multipart library. `UploadFile` stores files in memory if they are small, or rolls them over to disk if they exceed a threshold, preventing high memory usage. File bytes are accessed via `await file.read()`."),
            ("How does CORS work?", 
             "Cross-Origin Resource Sharing (CORS) is a security feature enforced by browsers that restricts web pages from making requests to a different domain. FastAPI handles this by applying `CORSMiddleware`, defining allowed origins, headers, and HTTP methods."),
            ("What are middleware components?", 
             "Middleware is a function or class that runs before every request is processed by a specific route, and after every response is generated. Examples include loggers, compression tools, CORS handlers, and session managers."),
            ("Difference between GET and POST?", 
             "GET requests retrieve data from the server. Parameters are sent in the URL query string. POST requests send data to the server to create or update resources. Data is sent in the HTTP request body, which is more secure and supports larger payloads."),
            ("How are exceptions handled?", 
             "FastAPI provides built-in exception handlers that capture errors and return standard JSON formats. Custom handlers can be registered using `@app.exception_handler()`, allowing developers to map specific Python exceptions to custom HTTP responses."),
            ("What is HTTPException?", 
             "HTTPException is an exception class provided by FastAPI to return HTTP error status codes (e.g., 400 Bad Request, 404 Not Found, 403 Forbidden) along with a descriptive text detail back to the client."),
            ("What are status codes?", 
             "Standardized three-digit numbers returned by HTTP servers to indicate the result of a request. Examples include 200 OK (success), 400 Bad Request (client error), 401 Unauthorized, 404 Not Found, and 500 Internal Server Error."),
            ("How would you secure APIs?", 
             "1) Use HTTPS/TLS. 2) Implement token-based authentication (OAuth2 with JWT tokens). 3) Apply CORS policies restricting access to trusted frontend origins. 4) Use rate-limiting middleware. 5) Perform strict request validation to prevent SQL/NoSQL injection and buffer overflows.")
        ]),

        # SECTION 4
        ("NLP Questions", [
            ("How does your text analyzer work?", 
             "The text analyzer uses a regex-driven pipeline to calculate political bias, clickbait density, and emotional intensity. For scam classification, it vectorizes the input text using a TF-IDF vectorizer and passes the features to a pre-trained Logistic Regression model, yielding a probability score."),
            ("What is NLP?", 
             "Natural Language Processing (NLP) is a subfield of artificial intelligence focused on the interaction between computers and human language. It involves tasks like text classification, sentiment analysis, entity extraction, and language translation."),
            ("What is TF-IDF?", 
             "Term Frequency-Inverse Document Frequency (TF-IDF) is a statistical measure that evaluates how important a word is to a document in a collection. It increases proportionally with the number of times a word appears in the document but is offset by the frequency of the word in the corpus."),
            ("Why TF-IDF?", 
             "It is lightweight, fast, and highly effective for keyword-based classification tasks (like identifying scam templates). It filters out common words (like 'the', 'is') and highlights unique words (like 'miracle', 'bank', 'verify') that carry strong class indicators."),
            ("What is feature extraction?", 
             "Feature extraction in NLP is the process of transforming raw text into a numerical format (features) that machine learning models can understand. In this project, TF-IDF vectorization performs this task."),
            ("What is tokenization?", 
             "Tokenization is the process of breaking a stream of text into smaller units, called tokens (usually individual words or punctuation marks), which serve as the basic inputs for subsequent processing."),
            ("What is stop-word removal?", 
             "Stop-word removal is the process of filtering out common words (e.g., 'and', 'but', 'of') that appear frequently in language but contain little semantic information for classification tasks, reducing noise in the model."),
            ("What is stemming?", 
             "Stemming is an NLP preprocessing step that chops off the ends of words to reduce them to their base or root form (e.g., 'running' and 'runs' both become 'run'). It uses simple heuristic rules, which can sometimes result in non-words."),
            ("What is lemmatization?", 
             "Lemmatization is the process of grouping together the inflected forms of a word so they can be analyzed as a single item, identified by the word's lemma (e.g., 'better' becomes 'good'). It uses vocabulary and morphological analysis, making it more accurate than stemming."),
            ("What is vectorization?", 
             "Vectorization is the general term for converting textual tokens into numerical vectors. Examples include Bag-of-Words, TF-IDF, and word embeddings (such as Word2Vec or GloVe)."),
            ("Why Logistic Regression?", 
             "Logistic Regression is highly interpretable, fast to train, and requires very little CPU memory during inference. For sparse TF-IDF vectors, it generalizes well without overfitting, making it ideal for lightweight backend systems."),
            ("How does Logistic Regression work?", 
             "It models the probability of a binary outcome (e.g., scam vs clean) by fitting the input features to a linear equation. The output of the linear equation is then passed through the logistic (sigmoid) function to map it to a probability value between 0 and 1."),
            ("What is the sigmoid function?", 
             "The sigmoid function is defined as S(z) = 1 / (1 + e^-z). It maps any real-valued number to a probability value between 0 and 1, creating an S-shaped curve."),
            ("Why not Random Forest?", 
             "Random Forests struggle with high-dimensional, sparse data like TF-IDF vectors. They tend to overfit on vocabulary terms and have a much larger file size compared to Logistic Regression models, which slows down API startups."),
            ("Why not SVM?", 
             "Support Vector Machines (SVM) can be slow to train on large datasets, and extracting clean, calibrated probability scores (via Platt scaling) is computationally expensive compared to Logistic Regression, which computes probabilities naturally."),
            ("What is overfitting?", 
             "Overfitting occurs when a model learns the training data too well, including its noise and outliers. This leads to high accuracy on the training set but poor generalization and low accuracy on unseen testing data."),
            ("What is underfitting?", 
             "Underfitting occurs when a model is too simple to capture the underlying structure of the data. This results in poor performance on both the training data and the testing data."),
            ("How did you evaluate the model?", 
             "I evaluated the model using a classification report containing precision, recall, F1-score, and an accuracy score computed on a held-out test dataset."),
            ("What was the dataset size?", 
             "The model was trained on a labeled dataset of roughly 5,500 messages (the SMS Spam Collection and custom scam claims), split into training and testing sets."),
            ("What is train-test split?", 
             "A technique where the labeled dataset is divided into two subsets: a training set (to train the model parameters) and a testing set (to evaluate the model's performance on unseen data)."),
            ("Why use 80-20 split?", 
             "An 80-20 split is an industry standard that balances the need for a large training set (to learn robust features) with a sufficiently large testing set (to get statistically reliable evaluation metrics)."),
            ("What is precision?", 
             "Precision measures the accuracy of positive predictions: Precision = TP / (TP + FP). It answers: 'Out of all messages flagged as scams, how many were actually scams?'"),
            ("What is recall?", 
             "Recall measures the model's ability to find all positive instances: Recall = TP / (TP + FN). It answers: 'Out of all actual scams in the dataset, how many did the model detect?'"),
            ("What is F1 score?", 
             "F1 score is the harmonic mean of precision and recall: F1 = 2 * (Precision * Recall) / (Precision + Recall). It provides a single balanced metric, especially useful when dealing with imbalanced datasets."),
            ("Difference between precision and recall?", 
             "Precision focuses on minimizing False Positives (avoiding flagging safe messages as scams), whereas Recall focuses on minimizing False Negatives (avoiding missing actual scams).")
        ]),

        # SECTION 5
        ("Scam Detection Model Questions", [
            ("How did you train the scam model?", 
             "1) Preprocessed raw text by lowercasing and removing punctuation. 2) Extracted features using a TF-IDF vectorizer. 3) Split the dataset 80/20. 4) Trained a Logistic Regression classifier on the training set. 5) Serialized the trained model and vectorizer using Joblib."),
            ("Which dataset did you use?", 
             "We used the SMS Spam Collection dataset combined with custom labeled clickbait and financial fraud datasets, providing a balanced distribution of spam, scam, and regular (ham) text."),
            ("How did you clean the dataset?", 
             "1) Removed HTML tags and special characters using regex. 2) Converted all text to lowercase. 3) Standardized spelling variants. 4) Removed duplicate entries to prevent bias during training."),
            ("How did you handle null values?", 
             "We dropped rows with null or empty text values during the preprocessing pipeline, ensuring that the vectorizer only processes valid, non-empty string sequences."),
            ("Why convert labels to 0 and 1?", 
             "Logistic Regression models require numerical targets for optimization. We mapped the target class 'ham/clean' to 0 and 'spam/scam' to 1 to align with binary cross-entropy loss criteria."),
            ("How is inference performed?", 
             "When an API request is received, the text is preprocessed. It is then vectorized using the loaded `vectorizer.pkl` to produce a sparse feature vector, which is passed to `spam_model.predict_proba()` to compute probability scores."),
            ("Why save model using Joblib?", 
             "Joblib is optimized for serializing Python objects that contain large numpy arrays (which scikit-learn models use). It is faster and creates smaller files on disk than standard Python pickle."),
            ("What is model serialization?", 
             "Model serialization is the process of converting a trained model object (stored in RAM) into a byte stream that can be saved to disk. This allows the model to be loaded quickly during API startup without needing retraining."),
            ("How does vectorizer.pkl work?", 
             "It stores the vocabulary mapping (words to feature indices) and document frequency weights learned during training. It ensures that incoming text is transformed into the exact same vector structure that the model expects."),
            ("What happens if vectorizer is missing?", 
             "The application fails to start or raises an error during inference. The model cannot process raw strings directly; it requires the vectorizer to map strings into the matching numerical features.")
        ]),

        # SECTION 6
        ("Image Detection Questions", [
            ("Explain image analysis workflow.", 
             "1) Image bytes are uploaded via FastAPI. 2) EXIF headers are parsed for processing software and camera details. 3) ELA is performed by resaving the image as a JPEG at 95% quality and calculating the absolute pixel difference. 4) Grid-based splicing checks identify localized ELA variances. 5) Edge variance is calculated for blur detection. 6) The image is preprocessed and passed to a PyTorch ResNet-18 model on CPU. 7) Results are unified into a final trust score."),
            ("What is EXIF metadata?", 
             "Exchangeable Image File Format (EXIF) is a standard that specifies the formats for images, sound, and ancillary tags used by digital cameras and smartphones. It stores camera model, lens settings, timestamps, GPS locations, and editing software."),
            ("Why analyze EXIF?", 
             "EXIF metadata can provide direct proof of tampering. If standard fields (like Make/Model) are missing or if tags show editing software (like 'Photoshop' or 'Canva'), it suggests the image is not an original camera capture."),
            ("What is Error Level Analysis (ELA)?", 
             "Error Level Analysis is a forensic technique that identifies areas within an image that have different compression rates. It is highly effective for detecting composite images (spliced areas) where different elements have been saved multiple times."),
            ("How does ELA work?", 
             "JPEG images compress grid blocks at a uniform rate. When an image is modified, the new elements have different compression histories. ELA saves the image at a known quality (usually 95%) and compares the new file with the original. Spliced areas show up as high-contrast hotspots in the difference map."),
            ("Why save image at JPEG quality 95?", 
             "Saving at 95% quality provides a baseline for compression error. It is high enough to preserve original compression details while introducing a predictable, measurable amount of new error, highlighting discrepancies without obliterating fine textures."),
            ("What is image recompression?", 
             "Image recompression occurs when a JPEG image is saved multiple times. Each save introduces new compression artifacts. Forensics analyzes these artifacts to determine if an image has been cropped, edited, or passed through messaging platforms (like WhatsApp)."),
            ("What is splicing detection?", 
             "Splicing detection focuses on finding composited regions where pixels from one source have been pasted into another. Our platform uses grid-based ELA variance analysis to flag individual 8x8 block regions that compress at abnormal rates compared to the global average."),
            ("What is anomaly detection?", 
             "Anomaly detection in image forensics is the process of identifying localized patterns (in ELA density, noise levels, or metadata structure) that deviate significantly from standard camera characteristics, signaling manual edits."),
            ("What is pixel variance?", 
             "Pixel variance measures the spread of pixel values in a local region. In graphics forensics, high variance indicates detail and texture, while extremely low variance indicates flat, smooth regions, which can point to AI generation or editing."),
            ("Why calculate local texture variance?", 
             "Generative AI models (and manual edit tools like clone-stamps) often produce artificially smooth regions (like skin smoothing). Calculating the variance of a 16x16 center patch helps flag abnormally low texture signatures typical of synthetic generation."),
            ("What is blur detection?", 
             "Blur detection determines if an image is out-of-focus or motion-blurred. We calculate the variance of the image gradients (using numpy differences) to estimate sharpness."),
            ("How does blur detection work?", 
             "Sharp images have sharp transitions (edges) where pixel values change rapidly. Blurry images have gradual transitions. By calculating the absolute difference between adjacent pixels horizontally and vertically, we get an 'edge score' representing sharpness."),
            ("What is edge score?", 
             "The edge score is the mean value of horizontal and vertical pixel differences. In our backend, if the edge score falls below 6.0, the image is classified as blurry."),
            ("Why can blurry images cause false positives?", 
             "Blurry or highly compressed images lack high-frequency details. This lack of texture can mimic the smooth characteristics of generative AI or trigger ELA compression block disparities, leading to false positives. The platform mitigates this by lowering heuristic penalties for blurry inputs."),
            ("What is metadata integrity score?", 
             "A rating (0-100) calculated by checking for the presence of standard camera tags (Make, Model, DateTimeOriginal) and subtracting points for editing software signatures, indicating the trustworthiness of the file headers."),
            ("What are forensic heuristics?", 
             "Heuristics are rule-based checks derived from domain expertise (e.g., checking for the 'Software' EXIF tag, calculating ELA standard deviation, identifying low resolution). They complement neural networks by providing deterministic, transparent, and auditable reasons for flags.")
        ]),

        # SECTION 7
        ("CNN / Deep Learning Questions", [
            ("Why did you use ResNet18?", 
             "ResNet-18 is a lightweight convolutional neural network with 18 layers. It uses residual connections (skip connections) to mitigate the vanishing gradient problem. It strikes an optimal balance between accuracy and computational cost, making it ideal for real-time CPU-bound inference in a FastAPI backend compared to heavier models like ResNet-50."),
            ("What is a CNN?", 
             "A Convolutional Neural Network (CNN) is a deep learning architecture designed to process grid-like data such as images. It uses convolutional layers to extract spatial features while preserving the relative positions of pixels."),
            ("What is convolution?", 
             "Convolution is a mathematical operation where a kernel (a small weight matrix) slides across the input image pixels, computing dot products to generate a feature map. This process extracts local patterns like edges, corners, and textures."),
            ("What is pooling?", 
             "Pooling is a downsampling operation that reduces the spatial dimensions of feature maps. This reduces computational complexity, controls overfitting, and extracts dominant features that are translation-invariant (e.g., Max Pooling)."),
            ("What is ReLU?", 
             "Rectified Linear Unit (ReLU) is an activation function defined as f(x) = max(0, x). It introduces non-linearity into the network, allowing it to learn complex non-linear patterns, and speeds up training by preventing gradients from saturating."),
            ("What is dropout?", 
             "Dropout is a regularization technique where randomly selected neurons are ignored (set to zero) during training steps. This prevents the network from co-adapting and forces it to learn robust, generalizable features, reducing overfitting."),
            ("Why use dropout?", 
             "To prevent overfitting. In our model, we use a dropout rate of 0.5 in the fully connected classification head, which ensures the classifier doesn't memorize the training set representation."),
            ("What is softmax?", 
             "Softmax is an activation function applied to the output layer of a classification network. It normalizes the raw logits into a probability distribution over the target classes, ensuring they sum to 1."),
            ("What is cross entropy loss?", 
             "It is the standard loss function used for multi-class classification. It measures the performance of a classification model whose output is a probability value between 0 and 1. It penalizes predictions that are confident but wrong."),
            ("What is transfer learning?", 
             "It is a machine learning technique where a model developed for a task is reused as the starting point for a model on a second task. In our case, a ResNet-18 pre-trained on ImageNet is fine-tuned on the REAL vs FAKE image dataset, saving time and training data."),
            ("Why ResNet18 over ResNet50?", 
             "ResNet-18 has ~11 million parameters compared to ResNet-50's ~25 million parameters. Since the backend runs on CPU, ResNet-18 offers faster inference times (~30-50ms per image) with only a minimal trade-off in validation accuracy compared to the heavier ResNet-50."),
            ("What are residual connections?", 
             "Skip connections that bypass one or more layers. They feed the output of an earlier layer directly to a later layer, formulated as H(x) = F(x) + x. This allows gradients to flow directly back through the network without degradation."),
            ("What is vanishing gradient?", 
             "During backpropagation, gradients are multiplied by weights. In deep networks, repeatedly multiplying small gradients causes them to shrink exponentially towards zero, preventing early layers from updating. Residual connections solve this by adding the identity x."),
            ("What is batch normalization?", 
             "A technique to standardize the inputs to a layer for each mini-batch. It stabilizes the learning process, reduces the number of training epochs required to train deep networks, and acts as a mild regularizer."),
            ("How did you preprocess images?", 
             "Bilinear interpolation resize to 128x128, conversion of values to float tensor scaled between 0 and 1, and normalization using ImageNet means ([0.485, 0.456, 0.406]) and standard deviations ([0.229, 0.224, 0.225])."),
            ("Why resize to 128x128?", 
             "It balances fine texture extraction with inference performance. Smaller sizes (64x64) lose forensic compression artifacts, while larger sizes (256x256) dramatically slow down CPU inference and increase model size."),
            ("Why normalize using ImageNet mean/std?", 
             "Since the model weights were initialized from a checkpoint pre-trained on ImageNet, we must align the distribution of our input image channels with the original training set to make the pre-trained weights effective."),
            ("How does model inference work?", 
             "The preprocessed image tensor is passed through the model's forward path, generating logits. A softmax function scales these logits into probabilities, yielding ai_real_probability and ai_fake_probability."),
            ("What is model confidence?", 
             "The probability of the predicted class (i.e. max(P(real), P(fake)))."),
            ("What is overfitting in CNNs?", 
             "When the CNN learns details and noise in the training set to the extent that it negatively impacts the performance of the model on new data. Indicators are low training loss but high validation loss."),
            ("What is a confusion matrix?", 
             "A table used to describe the performance of a classification model. It shows True Positives, False Positives, True Negatives, and False Negatives.")
        ]),

        # SECTION 8
        ("Hybrid Scoring Questions", [
            ("Why combine AI and heuristics?", 
             "AI classifiers (like ResNet-18) are powerful at detecting abstract texture patterns but can be tricked by noise, blur, or compression. Heuristics (like EXIF tags and ELA) are deterministic and easy to audit. Combining them provides a balanced, multi-layered defense."),
            ("Why not rely only on CNN?", 
             "CNNs are susceptible to 'adversarial attacks' and false positives on normal, heavily compressed images. They cannot explain *why* an image is flagged. Heuristics supply auditability, explaining if metadata was stripped or photoshop was used."),
            ("Why not rely only on ELA?", 
             "ELA is highly dependent on compression quality. An unedited image saved multiple times can show ELA variance, causing false positives. AI models detect structural anomalies that ELA misses, such as synthetic facial features."),
            ("Explain trust score formula.", 
             "The platform uses a balanced combination: trust_score = 0.5 * heuristic_score + 0.5 * (ai_real_probability * 100). This weights structural rules and neural network texture predictions equally."),
            ("Why use weighted scoring?", 
             "Weighted scoring allows us to balance the influence of different engines. By giving equal weight to heuristics and deep learning, we ensure that a single anomaly doesn't cause a massive drop in score, leading to stable classifications."),
            ("How is threat level determined?", 
             "1) Trustworthy: final_score >= 75, anomaly_count == 0, and AI prediction is REAL. 2) High Risk: final_score < 50, anomaly_count >= 2, and AI prediction is FAKE. 3) Suspicious: Default fallback for cases with single anomalies or moderate scores."),
            ("What is anomaly count?", 
             "A counter incremented when a critical forensic flag is triggered: 1) Splicing detected. 2) Processing software (like Photoshop) in EXIF. 3) High ELA rating. 4) AI prediction is FAKE (with confidence > 55%) or SUSPICIOUS."),
            ("Why reduce false positives?", 
             "High false positive rates cause 'alert fatigue,' leading users to ignore genuine warnings. By adjusting penalties for compressed/blurry photos and requiring multiple anomalies for a High Risk flag, we ensure that normal user photos are not incorrectly flagged."),
            ("What is confidence calibration?", 
             "Adjusting the raw model confidence scores so that the predicted probabilities align with actual empirical frequencies. In our pipeline, we use uncertainty thresholding to map moderate-confidence predictions to 'SUSPICIOUS'.")
        ]),

        # SECTION 9
        ("URL Analysis Questions", [
            ("How does URL scanning work?", 
             "1) URL is parsed to extract the domain. 2) Checked against curated lists of trusted/satirical/malicious sites. 3) Scanned for suspicious TLDs (.xyz, .gq) and phishing keywords. 4) HTTPX traces the redirect path and checks SSL. 5) WHOIS/RDAP checks domain age. 6) BeautifulSoup extracts page metadata for clickbait scanning."),
            ("What is web scraping?", 
             "Web scraping is the automated extraction of data from websites. The URL scanner scrapes the HTML content of target links to inspect headings and metadata for sensationalism and clickbait patterns."),
            ("Why BeautifulSoup?", 
             "BeautifulSoup is a Python library for parsing HTML documents. It is lightweight, fast, and makes it easy to extract page titles, meta tags, and headings for clickbait evaluation without the overhead of a headless browser."),
            ("What is HTTPX?", 
             "HTTPX is a fully featured HTTP client for Python 3. It supports HTTP/1.1 and HTTP/2, providing both synchronous and asynchronous APIs. It is used to asynchronously trace URL redirect paths and check SSL certificates."),
            ("What is domain reputation?", 
             "A score representing the trustworthiness of a domain based on age, SSL configuration, TLD type, presence on blocklists, and historical validation records."),
            ("What is SSL validation?", 
             "Checking if a website uses a secure connection (HTTPS) and possesses a valid SSL certificate. Insecure HTTP connections or invalid certificates are flagged as security risks."),
            ("What is WHOIS?", 
             "A query and response protocol widely used for querying databases that store the registered users or assignees of an Internet resource, such as a domain name. We use it to check the age of a domain, as new domains are riskier."),
            ("How can malicious URLs be detected?", 
             "1) Check for security protocols (HTTP vs HTTPS). 2) Analyze domain age (recently registered domains are often used for phishing). 3) Match against known phishing lexicons (e.g., 'verify-bank-login'). 4) Check for suspicious TLDs."),
            ("What is clickbait detection?", 
             "Analyzing the language patterns of page titles and meta-descriptions (scraped via BeautifulSoup) to identify sensationalism, exaggeration, or curiosity loops that indicate clickbait."),
            ("How would you improve URL analysis?", 
             "1) Integrate Google Safe Browsing API. 2) Implement a headless browser (like Playwright) to capture screenshots of the page and run visual similarity checks to detect phishing clones. 3) Add IP reputation and DNS record checks.")
        ]),

        # SECTION 10
        ("Database Questions", [
            ("Why MongoDB?", 
             "MongoDB is a NoSQL document database. Our forensic reports vary in structure (some have EXIF metadata, others have URL redirect paths or text highlights). MongoDB's flexible schema allows us to store these diverse records without complex migrations."),
            ("Why NoSQL?", 
             "NoSQL databases handle unstructured or semi-structured data exceptionally well. They scale horizontally easily, provide high write speeds, and bypass the rigid table schemas of traditional SQL databases."),
            ("Difference between SQL and MongoDB?", 
             "SQL databases are relational, use tables/rows, have fixed schemas, and support ACID transactions. MongoDB is non-relational, stores data in JSON-like documents, has dynamic schemas, and scales horizontally via sharding."),
            ("What is a document database?", 
             "A type of NoSQL database that stores data in JSON, BSON, or XML documents. Documents contain key-value pairs, arrays, or nested documents, mapping directly to object structures in application code."),
            ("What collections would you create?", 
             "1) `user_reports`: stores the generated forensic analysis reports (claims, URLs, images). 2) `users` (for production): stores user credentials and roles. 3) `threat_logs`: stores real-time API detection events."),
            ("How would you index reports?", 
             "I would create a single-field index on `timestamp` (for fast sorting), a text index on `title` and `description` (for searching), and a unique index on `id` (for fast single-record lookups)."),
            ("Why provide in-memory fallback?", 
             "To ensure the application remains functional in offline or development environments where MongoDB is not installed, allowing developers to run tests and verify pipelines with zero configuration.")
        ]),

        # SECTION 11
        ("React Questions", [
            ("Why React?", 
             "React allows us to build a dynamic, high-performance user interface. Its component-driven architecture makes it easy to manage complex UI elements like ELA visualizers, trust meters, and metadata inspectors."),
            ("What are components?", 
             "Components are the building blocks of a React application. They are self-contained, reusable pieces of UI that manage their own state and rendering logic, returning React elements (JSX)."),
            ("Functional vs class components?", 
             "Functional components are JavaScript functions that accept props and return JSX. They use React Hooks (like useState) to manage state. Class components are ES6 classes that extend `React.Component` and use lifecycle methods. Functional components are now the modern standard."),
            ("What are props?", 
             "Short for properties, props are read-only inputs passed from a parent component to a child component, allowing components to share data and remain dynamic."),
            ("What is state?", 
             "State is a built-in React object used to store data or assets that are local to a component and can change over time. When state updates, the component re-renders to reflect the change."),
            ("What is useState?", 
             "A React hook that allows functional components to declare and update local state variables. It returns a pair: the current state value and a function to update it."),
            ("What is useEffect?", 
             "A React hook used to perform side effects in functional components, such as data fetching, subscription setup, or manual DOM updates. It replaces lifecycle methods like componentDidMount."),
            ("How do API calls work?", 
             "React makes asynchronous API calls using HTTP clients inside hooks (like useEffect) or event handlers. The client sends a request and uses state setters to store the returned data, triggering a re-render."),
            ("What is Axios/fetch?", 
             "Fetch is the built-in browser API for making network requests. Axios is a popular third-party library that automatically handles JSON transformation, request/response interceptors, and better error handling."),
            ("How does file upload work?", 
             "An `<input type='file'>` captures the file. React stores it in state. An event handler wraps the file in a `FormData` object and sends it to the server via a POST request with multipart/form-data headers."),
            ("What is TypeScript?", 
             "TypeScript is a strongly typed programming language that builds on JavaScript, adding static type definitions. It compiles to plain JavaScript for browser execution."),
            ("Why TypeScript over JavaScript?", 
             "TypeScript catches type errors at compile time, improves code auto-completion, makes refactoring safer, and serves as self-documentation, which is vital for managing complex API response interfaces in React.")
        ]),

        # SECTION 12
        ("Advanced Questions", [
            ("How would you improve image detection accuracy?", 
             "1) Fine-tune the ResNet-18 model on a larger, domain-specific dataset. 2) Implement metadata alignment checks between the EXIF capture date and file system timestamps. 3) Apply advanced noise-inconsistency algorithms (like PRNU - Photo Response Non-Uniformity) to detect camera sensor fingerprints."),
            ("Why did ChatGPT-generated images bypass detection?", 
             "Generative models (like DALL-E 3) do not use typical copy-paste splicing techniques, meaning they lack high-contrast ELA boundaries. Furthermore, ChatGPT strips EXIF headers automatically, which triggers minor metadata flags but hides original generation software traces. The model must rely on texture analysis to detect them."),
            ("What limitations exist?", 
             "1) CPU inference: Running neural networks on CPU limits throughput. 2) Satire detection: Satirical sites (like The Onion) are flagged as misinformation because the NLP model cannot detect humor or context. 3) File stripping: Messaging platforms strip EXIF metadata, reducing metadata forensics utility."),
            ("How would you support video deepfake detection?", 
             "I would extract frames from uploaded videos at a rate of 3-5 frames/second and pass them through our ResNet-18 pipeline. To capture temporal anomalies (like unnatural eye blinking or lip movement), I would feed the frame feature sequences into an LSTM network or a 3D-CNN model."),
            ("How would you retrain with larger datasets?", 
             "Set up a pipeline to save analyzed images and user reports to S3. I would periodically run an offline training script on a GPU instance, using PyTorch to train a newer model, validating it on a held-out test set, and swapping the `.pth` file via a CI/CD pipeline."),
            ("How would you use BERT instead of TF-IDF?", 
             "I would replace the scikit-learn models with a HuggingFace Transformer model (like DistilBERT). The text would be tokenized using the BERT tokenizer, and the embeddings would be passed to the transformer. This allows the model to capture context and semantic meaning, rather than just keyword frequencies."),
            ("How would you deploy on AWS?", 
             "1) Package the FastAPI backend as a Docker image and host it on AWS ECS. 2) Serve the React frontend as static files on AWS S3, distributed via CloudFront. 3) Use AWS DocumentDB as our managed MongoDB database. 4) Use AWS Application Load Balancer to route client requests."),
            ("How would you implement authentication?", 
             "I would use FastAPI's OAuth2 password flow with JWT tokens. When users log in, the backend verifies credentials, generates a signed JWT, and returns it. The frontend stores this token and sends it in the Authorization header for protected routes."),
            ("How would you add real-time monitoring?", 
             "I would integrate Prometheus to collect API metrics (request rate, latency, error rates, CPU/Memory usage) and Grafana to visualize them in real-time dashboards, alongside Sentry for application error tracking."),
            ("If accuracy drops in production, how would you debug it?", 
             "1) Monitor user feedback and flag discrepancy rates. 2) Analyze log files to identify input distribution shifts (e.g., users uploading new types of generative AI formats). 3) Log prediction inputs and run offline evaluations to compare production inference with baseline validation sets. 4) Retrain the model on the new edge cases.")
        ]),

        # SECTION 13
        ("Vector RAG, Embeddings, Vector DBs (FAISS & Qdrant), Reranker & Evaluation", [
            ("What are dense embeddings and why are they used in this platform?", 
             "Dense embeddings are numerical vector representations (in our system, 384-dimensional continuous vectors) where semantically similar texts map to neighboring points in vector space. Unlike sparse keyword matching (TF-IDF), dense embeddings capture underlying semantic meaning, synonyms, and subword morphology, allowing the platform to match claims even if phrasing differs."),
            ("Why use both FAISS and Qdrant in your architecture?", 
             "1) FAISS (Facebook AI Similarity Search) is an ultra-fast in-memory vector index optimized for exact C++ inner product calculations (IndexFlatIP), providing sub-millisecond retrieval on local CPU hardware. 2) Qdrant is a production-ready vector database supporting rich JSON payload schemas and payload-based filtering. Providing an adapter for both allows seamless transitions between edge/local inference (FAISS) and distributed cloud storage (Qdrant)."),
            ("How does your two-stage retrieval and reranker work?", 
             "First-stage retrieval uses bi-encoder dense vector similarity to fetch the top-6 candidate passages from FAISS or Qdrant. Second-stage reranking evaluates the candidates using a hybrid cross-scoring engine that combines lexical overlap with dense similarity via Reciprocal Rank Fusion (RRF): RRF(d) = (w_dense / (60 + rank_dense)) + (w_lex / (60 + rank_lex)). This eliminates dense-retrieval false positives where words look semantically close but contradict the factual premise."),
            ("What is RAGAS and what metrics does it track?", 
             "RAGAS (Retrieval Augmented Generation Assessment) is an evaluation framework for RAG pipelines. We implemented its core metrics: 1) Faithfulness: measures whether the generated synthesis is strictly grounded in the retrieved context without hallucination. 2) Answer Relevance: measures semantic alignment between the claim and the generated output. 3) Context Precision@K: measures if the most relevant documents appear at the top ranks. 4) Context Recall: measures if the retrieved context contains all facts needed to verify the ground truth."),
            ("What is DeepEval and how does it measure hallucinations?", 
             "DeepEval is an LLM/RAG evaluation framework focusing on unit testing and production guardrails. In our platform, DeepEval metrics include: 1) Hallucination Metric: defined as 1.0 - Faithfulness, measuring the fraction of assertions ungrounded in context. 2) Contextual Relevancy: evaluates the signal-to-noise ratio by measuring what proportion of sentences in the retrieved context directly contribute to the answer."),
            ("What is Reciprocal Rank Fusion (RRF) and why use k=60?", 
             "RRF is an algorithm that combines the rank positions of documents from multiple independent retrieval methods (e.g., dense vector search and lexical keyword matching). The constant k=60 is the industry standard established by Cormack et al.; it prevents top-ranked documents from dominating the score while smoothly penalizing lower-ranked candidates."),
            ("How does your RAG verification pipeline work end-to-end?", 
             "1) The user submits a suspect claim. 2) The claim is embedded into a 384-dimensional vector. 3) FAISS/Qdrant retrieves top candidate passages from our verified knowledge corpus. 4) The hybrid Reranker re-scores and re-orders the candidates using RRF. 5) A grounded fact-check synthesis is produced with source citations. 6) The RAGAS and DeepEval evaluation suite automatically calculates Faithfulness, Answer Relevance, Context Precision, and Hallucination scores to ensure the output is reliable.")
        ])
    ]

    # Write each section to PDF
    sect_num = 1
    for title, qa_pairs in sections:
        pdf.add_page()
        pdf.chapter_title(sect_num, clean_text(title))
        
        q_num = 1
        for q, a in qa_pairs:
            # We check if page needs a break before drawing to avoid leaving a lonely question at bottom
            # Estimate height: question (~10-15pt), answer (~30-50pt)
            estimated_height = 40  # 40mm
            if pdf.get_y() + estimated_height > 270:
                pdf.add_page()
            
            pdf.ask_question(q_num, clean_text(q))
            pdf.give_answer(clean_text(a))
            q_num += 1
            
        sect_num += 1

    output_path = "q:/Ai scam detection/AI_Misinformation_Detection_Interview_Guide.pdf"
    pdf.output(output_path)
    print(f"PDF successfully generated at {output_path}")

if __name__ == "__main__":
    main()
