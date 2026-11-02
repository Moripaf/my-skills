# ICT / Software Evaluation Criteria: English Translation and Technical-Complexity Playbook

Source: *معیارهای ارزیابی حوزه فناوری اطلاعات و ارتباطات رایانه‌ای و نرم‌افزار*, the evaluation criteria for ICT and computer software used to decide whether a company's software product or service qualifies as **knowledge-based** (دانش‌بنیان). The document is 47 pages, dated Tir 1405 (July 2026). The Persian original is in the file next to this one: `معیارهای ارزیابی حوزه فناوری اطلاعات و ارتباطات رایانه‌ای.md`.

This file has two parts:

- **Part A — Translation.** A section-by-section English translation of the whole document. Nothing is summarized away. Page numbers point to the original PDF. Key Persian terms are kept in brackets so you can quote them back to Persian-speaking evaluators.
- **Part B — Agent playbook.** How to find, verify and present evidence of technical complexity in a real codebase against these criteria. Part B is written to be reused on any software product, not just Bina.

> **Read this first (applies to everything below).** The document has **no numeric scores, weights, thresholds or grading scales**. Every criterion is a qualitative checklist item that evaluators *examine and ask about* (مورد بررسی و پرسش). The function-specific criteria are applied **according to what the company claims** (براساس ادعای شرکت), and **no criterion outranks another**. So the job is not to "score points". It is to make claims that are specific, true and backed by evidence, about the criteria that fit the product.

---

# Part A — Full translation

## Contents of the original (pp. 1–2)

1. Criteria for the *production stage* condition (p. 3)
2. Criteria for the *technology level* condition (p. 4)
   - General quality indicators of the product (p. 4)
   - Criteria for the technology used in the product (pp. 5–21): AI & ML; Big Data & Analytics; Cloud; IoT & Edge; Cybersecurity; Blockchain & DLT; RPA; AR/VR; Quantum (twice, §9 and §11); 5G and next-generation networks; Digital bio-tech; Green tech; Cognitive tech
3. Criteria by product function or application (pp. 22–39): about 30 categories, listed in §A.3
4. Criteria for the *mastery of technical know-how* condition (p. 40)
5. Desired national impacts of knowledge-based products and services (p. 42)

The four conditions (production stage, technology level, know-how mastery, national impact) are assessed separately. **Technical complexity** is the subject of condition 2, the technology level, and it is *proven* mainly through condition 4, know-how mastery.

---

## A.1 Condition: production stage (شرط مرحله تولید), p. 3

When software products or services are evaluated, the production stage is one of the first indicators examined. It covers how the product was built and where it stands in its development life cycle. It shows the product's **technical maturity** (بلوغ فنی), how developed its **infrastructure** is (توسعه‌یافتگی زیرساختی), and how far it is **operational** (عملیاتی شدن). The purpose is to tell apart **early prototypes**, **trial versions** and **deployed, working products**.

**Acceptable evidence that the product is in production** (مصادیق قابل قبول):

- The product has been delivered to named customers, with technical and functional documentation.
- Installation, setup and support documentation exists at the customer site.
- Sales documents exist: an official invoice or an operating contract (قرارداد بهره‌برداری).
- There is evidence of operational use, such as logs and active accounts or access.
- The product is present on operational platforms or online marketplaces.
- A **stable release** (Stable Release) exists, not an MVP or trial version.

**Rule.** The software must have an operational version or a lab prototype that can be tested. **An idea, incomplete code or an algorithm alone is not acceptable.** In other words, the product must implement **all the core modules and capabilities it claims**, and it must be at a stage where it could be offered to a potential customer.

---

## A.2 Condition: technology level (شرط سطح فناوری), pp. 4–21

### A.2.0 Definition of what is measured, p. 4

> "This section measures the **technical complexity** (پیچیدگی فنی) of a software product/service **regardless of the specific technologies used** (صرف‌نظر از فناوری‌های خاص مورد استفاده). Criteria such as the degree of **modular architecture**, **scalability**, **real-time capability**, **integration capability**, and the degree of use of **advanced design methods** are examined. The aim of assessing this condition is a deeper understanding of the product's **technical maturity** and **engineering level**."

Two consequences:

1. Complexity is judged on **engineering**, not on trendy technology. A product with no AI and no blockchain can still show high complexity.
2. Using a fashionable technology does not count by itself. What counts is the engineering that went into using it.

### A.2.1 General quality indicators of the product (معیارهای عمومی ارزیابی شاخص‌های کیفی محصول), p. 4

These 16 items are **the core definition of technical complexity**. They apply to every software product. The numbering is ours; the order follows the original.

| # | Indicator (English) | Original Persian |
|---|---|---|
| G1 | Modular design and flexible architecture (modularity, Microservices, SOA) | طراحی ماژولار و معماری منعطف |
| G2 | Complexity of the implemented algorithms and their level of optimization | پیچیدگی الگوریتم‌های پیاده‌سازی‌شده و سطح بهینگی آن‌ها |
| G3 | Automation of processing and decision-making (Rule Engine, Intelligent Automation) | خودکارسازی پردازش‌ها و تصمیم‌گیری‌ها |
| G4 | Connectivity and integration with other systems, and open APIs | قابلیت اتصال و یکپارچگی با سایر سامانه‌ها و APIهای باز |
| G5 | Tolerance of high load and processing capacity in high-traffic scenarios (Scalability, Load Handling) | تحمل بار بالا و توان پردازشی در سناریوهای پرترافیک |
| G6 | Support for data analysis: statistical, predictive, prescriptive | پشتیبانی از تحلیل داده (آماری، پیش‌بینانه، تجویزی) |
| G7 | Management of internal processes with a Workflow Engine or BPMN | مدیریت فرآیندهای داخلی با Workflow Engine یا BPMN |
| G8 | Dynamic configurability, and adaptability of the software to different environments | قابلیت پیکربندی پویا و تطبیق‌پذیری نرم‌افزار در محیط‌های مختلف |
| G9 | Management of the data and knowledge life cycle (Data Lifecycle & Knowledge Flow) | مدیریت چرخه حیات داده و دانش |
| G10 | Multi-layer security: communications, data, identity, operations | پیاده‌سازی چندلایه امنیتی (امنیت ارتباطات، داده‌ها، هویت، عملیات) |
| G11 | Horizontal and vertical scalability in the infrastructure design | قابلیت مقیاس‌پذیری افقی و عمودی در طراحی زیرساخت |
| G12 | Support for distributed, multi-user and multi-channel architectures (Multi-user, Real-time, Omni-channel) | پشتیبانی از معماری‌های توزیع‌شده، چندکاربره و چندکاناله |
| G13 | Support for event-driven logic and Real-time Event Processing | پشتیبانی از منطق رویداد-محور و Real-time Event Processing |
| G14 | Ability to define varied access levels and dynamic roles | امکان تعریف سطح دسترسی متنوع و نقش‌های پویا |
| G15 | Level of operational intelligence in how the product behaves (recommender, user-behaviour analysis) | سطح هوشمندی عملیاتی در عملکرد محصول (توصیه‌گر، تحلیل رفتار کاربر) |
| G16 | Observability: monitoring, reporting and intelligent alerting | قابلیت رصد، مانیتورینگ، گزارش‌گیری و هشداردهی هوشمند |

### A.2.2 Criteria for the technology used in the product (معیارهای ارزیابی فناوری بکاررفته در محصول), pp. 5–21

Each technology area in the original has a table of **sub-technologies** (زیرفناوری‌ها) with definitions, followed by its **evaluation criteria** (معیارهای ارزیابی). These criteria apply only if the product claims to use that technology.

#### T1. Artificial intelligence and machine learning (AI & ML), pp. 5–6

**Sub-technologies:**
- **Large language models:** deep-learning models trained on huge text corpora to understand and generate natural language.
- **Multimodal learning:** processing several data types (text, image, audio) at once and the relations between them.
- **Generative adversarial networks:** a generator and a discriminator that compete to produce realistic synthetic data.
- **Foundation models:** models pretrained on huge datasets that can be adapted to many tasks.
- **Self-supervised learning:** learning useful features from raw data without labels.
- **Transformer architecture:** attention-based, parallel processing, used for tasks such as translation and summarization.
- **Explainable AI (XAI):** making model decisions transparent.
- **Transfer learning:** reusing knowledge from one task or domain to reduce the data a new task needs.
- **Deep reinforcement learning:** agents that learn optimal strategies by interacting with an environment and receiving rewards.
- **Graph neural networks:** models built for data structured as graphs (nodes and edges).
- **Federated learning:** training on data spread across devices without centralizing it, protecting privacy.
- **Edge AI:** running models on edge devices to cut latency and bandwidth and improve security.
- **On-chip AI:** AI built directly into chip hardware for speed and energy efficiency.
- **Adaptive models:** models that adjust dynamically to changes in the environment or input.
- **Digital twin simulation:** a precise digital model of a physical system, used to monitor, analyse and optimize it.
- **AI in distributed systems:** running models in distributed computing for scale and efficiency on large data.
- **Quantum-based optimization:** quantum algorithms for optimization problems that are hard classically.
- **Continual learning:** learning new tasks without forgetting old ones.
- **Few-shot / zero-shot learning:** performing new tasks from very few or no examples.

**Evaluation criteria:**
- the types of algorithm used (e.g. CNN, RNN, Transformer);
- how the model was trained: pretrained, customized/fine-tuned, or trained from scratch;
- how much training data was used and how varied it is;
- the model's accuracy under real conditions and how it is evaluated (confusion matrix, precision/recall);
- how the model is updated and maintained in production;
- transparency of model decisions (XAI tools such as LIME and SHAP);
- real-time or offline inference;
- how far feature and model selection is automated (AutoML).

#### T2. Big data and data analytics (Big Data & Analytics), p. 6

**Sub-technologies:**
- **Distributed processing:** parallel processing of large data on server clusters.
- **Data lake:** a central store for structured and unstructured data.
- **Real-time analytics:** analysis as data arrives, for immediate decisions.
- **NoSQL databases:** non-relational stores for unstructured or semi-structured data.
- **Data governance:** managing data security, quality and access.
- **Predictive analytics:** statistical and ML models that forecast trends.
- **NLP:** extracting insight from unstructured text.
- **Data visualization:** graphical presentation of complex data.
- **Edge analytics:** processing near the data source to cut latency.
- **AutoML:** automating how ML models are built.

**Evaluation criteria:**
- types of data source: structured, semi-structured, real-time;
- volume and variety of the data coming into the system;
- use of distributed processing frameworks (Spark, Hadoop);
- ability to do predictive and prescriptive analysis;
- visualization and decision-support tools (Tableau, PowerBI);
- processing latency in real-time analytics;
- integration of internal and external data.

#### T3. Cloud computing, p. 7

**Sub-technologies:**
- IaaS, PaaS, SaaS;
- FaaS: event-driven, serverless execution, paid per event;
- cloud storage;
- containerization and orchestration, for scalable deployment;
- cloud security;
- cloud management and monitoring;
- hybrid and multi-cloud;
- cloud-native development tools (microservices).

**Evaluation criteria:**
- architecture used: Monolith, Microservices or Cloud-native;
- degree of dependence on cloud platforms (AWS, Azure, GCP);
- use of containerization and orchestration (Docker, Kubernetes);
- automatic scaling (Auto Scaling);
- use of a Serverless or FaaS architecture;
- level of virtualization, and tools for managing the life cycle of cloud services;
- cost-optimization and resource-management policies (FinOps).

#### T4. Internet of Things and edge computing (IoT & Edge), pp. 8–9

**Sub-technologies:**
- **Sensing and communication:**
  - wireless sensor networks;
  - M2M communication;
  - lightweight IoT protocols;
  - LPWAN (low-power, wide-area networks);
  - RFID and NFC;
  - 5G for IoT.
- **Platforms and software:**
  - IoT cloud platforms;
  - IoT middleware;
  - IoT operating systems;
  - IoT analytics;
  - IoT connectivity-management platforms.
- **Device management:**
  - device management;
  - over-the-air firmware updates;
  - energy harvesting and battery management.
- **Security:**
  - IoT security;
  - IoT data-security and privacy frameworks.
- **Edge processing:**
  - edge/fog processing;
  - Edge AI for IoT.
- **Applications:**
  - smart home;
  - industrial IoT;
  - wearables;
  - smart-city platforms.
- **Modelling and testing:**
  - IoT digital twins;
  - IoT simulation and test environments.

**Evaluation criteria:**
- type and variety of sensors and hardware;
- communication architecture (MQTT, CoAP, Bluetooth Low Energy, …);
- response time and network latency;
- platforms used for device management (ThingWorx, AWS IoT);
- use of Edge AI for real-time decisions;
- how the security of communications and data on the network is guaranteed.

#### T5. Cybersecurity, p. 10

**Sub-technologies:**
- **Behavioural anomaly detection and response:** analysing the behaviour of users, devices and traffic.
- **Quantum cybersecurity:** quantum key distribution.
- **AI-based security:** analysing security data at scale.
- **Autonomous security:** automatic, real-time response to threats.
- **Homomorphic encryption:** computing on data without decrypting it.
- **Cyber supply-chain security:** finding vulnerabilities in third-party and open-source components.
- **Edge security:** protecting decentralized devices.
- **Cyber-attack simulation:** synthetic attacks for training defensive systems.

**Evaluation criteria:**
- data-encryption mechanisms (AES, RSA, ECC);
- authentication level (one-time/dynamic passwords, MFA, biometrics);
- design of a Zero Trust security model and of access control;
- intrusion-detection systems (e.g. Snort, Suricata);
- how far DevSecOps is integrated into the development cycle;
- SIEM tools and systems (Splunk, ELK Stack);
- penetration tests and vulnerability analyses carried out.

#### T6. Blockchain and distributed ledgers (Blockchain & DLT), p. 11

**Sub-technologies:**
- **Contracts and consensus:**
  - smart contracts;
  - consensus protocols.
- **Scaling:**
  - side chains and parallel chains;
  - layer-2 scaling.
- **Tokens and assets:**
  - NFTs;
  - asset tokenization.
- **Finance:** DeFi.
- **Privacy and identity:**
  - privacy and advanced cryptography (zero-knowledge proofs);
  - decentralized identity.
- **Oracles:** connecting the chain to real-world data.
- **Platform and governance:**
  - enterprise blockchain;
  - DAOs;
  - hybrid chains.
- **Storage and sustainability:**
  - green blockchain;
  - decentralized storage.

**Evaluation criteria:**
- type of blockchain (Ethereum, Hyperledger, custom);
- consensus algorithm used (PoW, PoS, PBFT);
- design and implementation of smart contracts;
- level of interaction with digital wallets or tokenization;
- implementation of the blockchain standards (ISO/TC 307);
- scalability and performance mechanisms for transactions.

#### T7. Automation and software robotics (RPA), p. 12

**Sub-technologies:**
- industrial robots;
- collaborative robots (cobots);
- machine-vision robotics;
- autonomous vehicles;
- robotic process automation (RPA) of repetitive office processes;
- service robots.

**Evaluation criteria:**
- how far repetitive processes are automated (number and type of processes);
- tools used (UiPath, Automation Anywhere);
- combining RPA with NLP or machine vision to make it intelligent;
- extracting processes from data (Process Mining);
- controlling and coordinating bots (Bot Management, Orchestration);
- time and cost saved by the implementation.

#### T8. Augmented and virtual reality (AR/VR), p. 13

**Sub-technologies:**
- **Hardware:**
  - standalone VR headsets;
  - lightweight AR glasses.
- **Sensing and tracking:**
  - SLAM (simultaneous localization and mapping);
  - eye tracking.
- **Interaction:**
  - haptic feedback;
  - mixed reality.
- **Content and rendering:**
  - volumetric capture;
  - adaptive/foveated rendering.
- **Applications:**
  - social VR platforms;
  - AR for industry.

**Evaluation criteria:**
- type of experience offered (interactive AR, immersive VR, MR);
- development tools used (Unity, Unreal Engine);
- performance on mobile, headsets or the browser;
- frame rate, resolution and interaction latency;
- application in education, industry or entertainment;
- level of user interaction, and ability to measure user reactions.

#### T9. Quantum computing, p. 14

**Sub-technologies:**
- superconducting qubits;
- quantum error correction;
- quantum algorithms (Shor, Grover);
- quantum cryptography;
- quantum simulators;
- quantum communication;
- quantum annealing;
- hybrid quantum computing;
- quantum photonics;
- quantum cloud services.

**Evaluation criteria:**
- platform used (IBM Quantum, Azure Quantum);
- quantum algorithms applied to specific problems (optimization, simulation);
- ability to use quantum programming languages (Qiskit, Q#);
- experimental or production use of quantum power;
- connection with classical systems (hybrid architectures).

#### T10. 5G and next-generation networks, p. 15

**Sub-technologies:**
- **Radio and spectrum:**
  - millimetre waves (24–100 GHz);
  - massive MIMO;
  - beamforming;
  - dense networks (small cells).
- **Network architecture:**
  - network slicing;
  - 5G with edge computing;
  - private 5G;
  - open networks (Open RAN).
- **Next generation and critical use:**
  - 6G;
  - ultra-reliable low-latency communication (URLLC).

**Evaluation criteria:**
- **Performance:**
  - data capacity and bandwidth;
  - low latency;
  - reliability and stability of the connection;
  - support for large numbers of devices and users.
- **Reach and compatibility:**
  - wide-scale coverage and access;
  - flexibility and compatibility with existing infrastructure;
  - integration with complementary technologies (IoT, AI, edge).
- **Maturity and adoption:**
  - standardization status and global adoption;
  - degree of commercialization and operational use.
- **Cost and impact:**
  - deployment and operating cost at scale;
  - data security and privacy;
  - energy efficiency and environmental effects;
  - economic and industrial impact in creating new markets.

#### T11. Quantum computing (second section), p. 16

The same sub-technology table as T9. **Evaluation criteria:**
- **Hardware quality:**
  - stability and durability of qubits against noise and error;
  - accuracy and reliability of computation;
  - quantum error correction and noise reduction.
- **Scale and access:**
  - scalability of qubit count and system size;
  - availability and scale of quantum cloud services.
- **Maturity and cost:**
  - technology maturity and global standardization;
  - cost of building, maintaining and operating.
- **Application:**
  - applicability of quantum algorithms to real problems;
  - security and trustworthiness in quantum cryptography and communication;
  - integration with classical systems and hybrid models.
- **Environment:** energy efficiency and environmental requirements.

#### T12. Digital bio-technologies, p. 17

**Sub-technologies:**
- **Genomics:**
  - gene editing;
  - next-generation sequencing.
- **Bioengineering:**
  - synthetic biology;
  - 3D bioprinting of organs.
- **Computation:**
  - bioinformatics;
  - medical digital twins;
  - AI drug discovery.
- **Devices:**
  - wearable biosensors;
  - lab-on-a-chip;
  - brain–computer interfaces.
- **Care delivery:** telemedicine.

**Evaluation criteria:**
- **Quality:**
  - accuracy and correctness of results;
  - safety and reduced risk to patient or environment;
  - reliability and reproducibility of tests or treatments.
- **Maturity and cost:**
  - technology maturity and global adoption;
  - development, deployment and operating cost.
- **Scale and performance:**
  - scalability in clinical or industrial use;
  - processing speed and response time;
  - integration with complementary technologies (AI, big data, medical IoT).
- **Users and data:**
  - personalization of treatments or products;
  - security and confidentiality of health data;
  - availability across settings, from hospital to home.
- **Impact:**
  - social, ethical and legal effects;
  - sustainability and environmental effects.

#### T13. Green technologies, p. 18

**Sub-technologies:**
- renewable energy (solar/wind);
- advanced energy storage;
- decarbonization (carbon capture);
- smart low-consumption buildings;
- green hydrogen.

**Evaluation criteria:**
- **Performance:**
  - efficiency in cutting consumption or producing clean energy;
  - stable performance under varied environmental conditions;
  - efficiency of energy storage or use.
- **Cost and scale:**
  - investment, operating and maintenance cost;
  - scalability and large-scale deployment.
- **Maturity and integration:**
  - maturity and commercialization;
  - integration with existing infrastructure and grids.
- **Environmental effect:**
  - reduction of carbon and pollutant emissions;
  - environmental effects and conservation of resources.
- **Resilience and value:**
  - resilience and security against environmental or technical hazards;
  - economic value and new market opportunities.

#### T14. Cognitive technologies, p. 19

**Sub-technologies:**
- NLP;
- machine vision;
- **recommender systems**: suggesting content or products from user behaviour;
- emotion recognition;
- artificial memory.

**Evaluation criteria:**
- **Quality:**
  - accuracy and correctness of output under real conditions;
  - reliability and stable performance;
  - ability to generalize to other domains and languages;
  - transparency and explainability of algorithmic decisions.
- **Scale and integration:**
  - **scalability in processing big data and many users**;
  - **processing speed and response time**;
  - **integration with other systems and technologies**.
- **Users and adoption:**
  - **security and confidentiality of user data**;
  - maturity and industry adoption;
  - social and ethical effects on users.

---

## A.3 Criteria by product function or application (معیارهای ارزیابی محصول بر اساس کارکرد یا کاربرد آن), pp. 22–39

> **Rule (p. 22).** This section lists criteria suited to the function of each second-level category in the official list of knowledge-based goods and services. Whether each criterion is required, and how high its priority is, **will be judged against the company's own claim**. Therefore **none of these criteria takes precedence over another**, and they will be examined and asked about as the assessment requires.

So the first step is to decide **which category the product is filed under**, then answer that category's criteria. Each criterion below is translated in full.

### F1. Banking and fintech (حوزه بانکی و فین‌تک)
- **Integration:**
  - connection to banking and financial systems through APIs;
  - interaction with settlement and core-banking systems.
- **Transactions:**
  - transactions at any time and at high speed;
  - error-free recording and retrieval of transaction history;
  - fund transfers with full details and status tracking;
  - multi-currency operation (rial, dollar, crypto);
  - issuing and verifying digital financial documents;
  - online QR and NFC payments;
  - unified management of assets, accounts and capital;
  - crypto interaction, conversion and instant withdrawal.
- **Security and compliance:**
  - multi-step, secure authentication;
  - security of wallets and account information;
  - automatic detection and blocking of suspicious activity;
  - compliance with regulators' rules.
- **Real time and consistency:**
  - real-time updates of account or wallet balances;
  - data synchronization across several devices or channels.
- **Access control:** flexible definition of access levels and roles.
- **Reliability under load:**
  - many concurrent requests processed stably;
  - operation even on a weak connection.
- **Reporting and analytics:**
  - clear, accurate financial reports for users;
  - analysis of financial behaviour with intelligent suggestions.
- **Usability:**
  - a smooth user experience in complex financial operations;
  - usable without special training.
- **Business coverage:** B2B, B2C and P2P models.

### F2. Business platforms (پلتفرم‌های کسب و کاری)
- **Finding and ordering:**
  - fast search and advanced filtering among options;
  - placing and tracking an order or request without guidance;
  - cancelling or changing a request under controlled conditions;
  - uploading documents, images or related files.
- **Performance and scale:**
  - low response time in loading and interaction;
  - working on mobile and browser with no loss of performance;
  - scalability for many concurrent users.
- **Real-time status:**
  - accurate display of location and status of the service or goods;
  - real-time notification of service or order status.
- **Users and trust:**
  - user feedback and rating;
  - direct contact between provider and requester through the platform;
  - easy management of user profile and activity history;
  - simple sign-up and secure identity verification;
  - a dispute or complaint mechanism.
- **Commerce:**
  - several pricing and settlement models;
  - special features for promotion or featured placement;
  - connection to domestic and international payment systems.
- **Scheduling:** tools for automatic scheduling and coordination.
- **Administration and reporting:**
  - an admin panel to oversee transactions and users;
  - a reporting dashboard on user behaviour, sales or performance.

### F3. IoT and M2M solutions (راهکارهای اینترنت اشیا و M2M)
- **Real-time data and control:**
  - sending and receiving data in real time;
  - remote control and monitoring;
  - a live view of equipment status.
- **Device operation:**
  - efficient energy use by devices;
  - stable performance in harsh environments;
  - scalability when adding new equipment;
  - simple installation and setup;
  - support for standard communication protocols;
  - central management of several sites or operating points.
- **Security:** security of communications and data.
- **Fault handling and records:**
  - automatic alerts on abnormal conditions;
  - logging and keeping a history of events;
  - automatic detection of errors or failures.
- **Integration and analytics:**
  - integration with other systems;
  - data analysis and useful reports.

### F4. Enterprise application systems (سامانه‌های کاربردی سازمانی)
- **Data handling:**
  - recording, processing and retrieving information with high accuracy;
  - central data management and removal of duplicate entries.
- **Access and organization structure:**
  - definable access levels for different users;
  - multi-organization or multi-site structures.
- **Workflow and processes:**
  - coordination between departments through workflow;
  - definable, configurable forms and processes;
  - alerts and follow-up of overdue tasks.
- **Reporting:** fast, configurable reporting.
- **Integration:** connection to other systems through APIs or web services.
- **Audit and compliance:**
  - automatic logging of changes and tracking of activity;
  - compliance with legal requirements and internal rules.
- **Usability and access:**
  - a simple UI for non-specialist users;
  - multi-language or multi-currency support;
  - remote online access with no loss of performance.
- **Extensibility:** upgrading and adding modules later **without an overall redesign**.

### F5. Simulators (شبیه‌سازها)
- **Interaction and feedback:**
  - smooth user interaction with the simulated environment;
  - instant system feedback on user performance or data;
  - varied inputs and devices (sensors, controllers).
- **Fidelity and scenarios:**
  - accurate representation of real conditions or specific scenarios;
  - running different scenarios **without writing code**;
  - adjustable difficulty or complexity.
- **Performance and stability:**
  - efficient, lag-free management of processing resources;
  - stable, error-free execution in long sessions.
- **Records and reporting:**
  - reports on user behaviour or performance in the simulation;
  - recording, saving and replaying a simulation run.
- **Platform and extensibility:**
  - compatibility with common operating systems and hardware;
  - extensible modules and components.
- **Presentation:** smooth, understandable graphics for different audiences.

### F6. Specialized scientific/engineering software (نرم‌افزارهای تخصصی علمی/مهندسی)
- **Modelling:**
  - flexible definition of variables, models and equations;
  - modelling customized to user needs;
  - tools to validate models and input data.
- **Computation:**
  - high numeric precision in complex computation;
  - heavy processing with minimal loss of performance;
  - multi-step and parametric scenarios;
  - **running scientific code or scripts inside the software**;
  - distributed or cloud computation.
- **Results and reproducibility:**
  - configurable graphical display of outputs and results;
  - automatic documentation of the analysis or simulation process;
  - **reproducibility** of results.
- **Integration:**
  - compatibility with common data and output formats;
  - **support for common scientific languages and environments (e.g. Python, MATLAB)**;
  - combining or connecting with other analytical software.
- **Usability:** a UI that scientific and engineering users can understand.

### F7. Interactive software (نرم‌افزارهای تعاملی)
- **Messaging and collaboration:**
  - sending and receiving messages with no noticeable delay;
  - **concurrent access by several users to one workspace**;
  - group meetings or conversations;
  - simultaneous editing of shared content.
- **Search and records:**
  - fast search within conversations or documents;
  - automatic logging of activity and interaction history;
  - tracking tasks or correspondence by tag or project.
- **Sync and files:**
  - synchronization across devices;
  - file and attachment upload.
- **Access and security:**
  - definable roles and access levels;
  - secure communication and user privacy.
- **Integration and notifications:**
  - integration with other services or complementary tools;
  - configurable alerts and notifications for important events.
- **Usability:** a smooth UI usable without special training.
- **Resilience:** **stable performance under high traffic or a weak internet connection**.

### F8. Content-centred software (نرم‌افزارهای محتوا محور)
- **Formats and creation:**
  - support for many content formats;
  - creating or editing content with minimal steps and complexity;
  - good-quality output for display or print.
- **Search and storage:**
  - fast search and retrieval of stored content;
  - secure, structured storage of media data;
  - aggregating and archiving content from varied sources.
- **Analysis and classification:**
  - automatic detection of content features (text, audio, image);
  - analysis of text or multimedia content with acceptable accuracy;
  - concurrent processing of text, audio or image data;
  - filtering of inconsistent or inappropriate content;
  - automatic identification and classification of documents or files;
  - tagging and describing digital content.
- **Languages and enrichment:**
  - multi-language input or output;
  - connection to external sources to enrich content.
- **Management and access:**
  - a simple UI for managing or interacting with content;
  - versioning and change control of content;
  - managing user access to content and files.
- **Audience and reach:**
  - analytics to measure feedback or effectiveness of content;
  - interaction with the user while they consume content;
  - publishing on several channels;
  - compatibility with varied devices and platforms.

### F9. QA and software-development life-cycle tools (ابزارهای کنترل کیفیت و مدیریت چرخه توسعه نرم‌افزار)
- **Testing and code quality:**
  - fast, reliable analysis of the current state of code or system;
  - varied automated and scheduled tests;
  - complex or custom test scenarios;
  - code-quality and security checks before deployment;
  - security testing and vulnerability discovery.
- **Monitoring and alerting:**
  - real-time alerts on errors or performance drops;
  - performance analysis under high load or disruption;
  - viewing system state now and in the past;
  - integration with error and incident reporting systems.
- **Versions and deployment:**
  - easy management of versions, dependencies and changes;
  - automated deployment and update processes;
  - integration with the code repository and versioning tools;
  - tools that simplify configuration and deployment.
- **Recovery and incidents:**
  - fast recovery or rebuild in a crisis;
  - automated response to incidents and leaks.
- **Process and compliance:**
  - fit with agile processes and distributed teams;
  - checks for compliance with standards and legal requirements;
  - continuous assessment of development and operations process maturity.
- **Platform and access:**
  - scalability for changing infrastructure;
  - access management and change control in development environments;
  - low-code development;
  - compatibility with cloud and multi-platform infrastructure.
- **Reporting:** precise, configurable reports on tests and operations.

### F10. IoT platform (پلتفرم اینترنت اشیا)
- **Devices and connectivity:**
  - many concurrent device connections;
  - central device management and software updates;
  - health and performance monitoring of equipment;
  - common IoT communication protocols.
- **Data and rules:**
  - real-time ingestion and processing of sensor data;
  - definable reactive rules or automated scenarios;
  - alerting on predefined conditions;
  - flexible data model for each application;
  - virtual groupings of things (a digital model);
  - analytics for fast, practical decisions.
- **Security and access:**
  - encryption in transit and at rest;
  - user-access and role control.
- **Integration and display:**
  - easy integration with external or cloud systems;
  - graphical display of data and equipment status.
- **Scalability:** extending the infrastructure without disruption.

### F11. Data management and analysis platforms and services (پلتفرم‌ها و خدمات مدیریت و تحلیل داده‌ها)
- **Ingestion and storage:**
  - ingesting, processing and storing high volumes without disruption;
  - many data structures (relational, non-relational, graph, …);
  - fast retrieval from varied sources;
  - easy connection to internal and external sources;
  - efficient storage and compression with no loss of accuracy.
- **Processing and workflow:**
  - scheduling and automating processing;
  - workflows for organizational data flows;
  - real-time or near-real-time analysis;
  - **parallel analysis over large, distributed data**;
  - horizontal and vertical scaling of the processing infrastructure.
- **Analysis and data quality:**
  - flexible definition of analysis models and KPIs;
  - filtering, cleaning and standardizing raw data;
  - discovery of hidden patterns and relations;
  - data-quality monitoring and detection of structural errors.
- **Visualization:**
  - visual results that users can understand;
  - dynamic, interactive visualization for analysts and managers.
- **Access, tools and integration:**
  - access control by role and policy;
  - common analytics languages (SQL, Python, R);
  - fit with cloud services and open-source tools;
  - integration with operational or decision-support systems;
  - customized solutions at consulting or development level.

### F12. Application platforms (پلتفرم‌های کاربردی)
- **Architecture and deployment:**
  - fast deployment with no dependence on specific infrastructure;
  - **modular, extensible architecture**;
  - easy movement between environments (e.g. test and production).
- **Runtime and scaling:**
  - efficient resource use at runtime;
  - running several instances or processes in parallel;
  - **load balancing and automatic scaling**;
  - processing at the edge or in the cloud;
  - running complex models without special processors.
- **Development and configuration:**
  - simple tools for design and configuration;
  - model-driven or feature-driven development;
  - development or configuration without deep technical knowledge;
  - version control and change management;
  - **extending or rewriting modules without stopping the system**.
- **Integration and standards:**
  - integration with third-party services and standard APIs;
  - compliance with industry frameworks and standards.
- **Operations and security:**
  - performance monitoring and real-time reports;
  - secure, role-based implementation;
  - concurrent use by several teams or projects.

### F13. AI platforms (پلتفرم‌های هوش مصنوعی)
- **Training and data:**
  - training models with minimal expert configuration;
  - structured and unstructured data;
  - producing and using synthetic data;
  - data-labelling tools, human or machine-assisted;
  - detecting and reducing bias in data or models.
- **Deployment and operation:**
  - deployment in different environments with minimal change;
  - a dashboard of model performance at runtime;
  - managing model versions and tracking changes;
  - ready-made, reusable models;
  - an API so other systems can use the models;
  - integration with the development chain and model life cycle.
- **Evaluation and improvement:**
  - evaluation across varied scenarios;
  - feedback and automatic model improvement.
- **Governance:**
  - access levels and user control;
  - ethics and transparency in model decisions.

### F14. Geospatial systems (سامانه‌های مبتنی بر داده‌های مکانی)
- **Maps and layers:**
  - fast loading, display and panning of maps;
  - many layer types and formats;
  - drawing, labelling and editing in the client;
  - 3D or pseudo-3D display.
- **Spatial analysis:**
  - spatial processing with adjustable precision;
  - search by place, address or coordinates;
  - route analysis with obstacles and constraints;
  - aggregation and overlay with other data;
  - change detection over time;
  - combination with ML models.
- **Real time and positioning:**
  - real-time tracking of objects or users;
  - accurate indoor or non-GPS positioning;
  - connection to sensors, devices or live data sources;
  - location-based alerts and events.
- **Data management:**
  - updates without stopping the system;
  - high-volume spatial storage with good retrieval speed;
  - quality control of spatial input or measurement data;
  - cloud infrastructure for heavy processing.
- **Services, access and collaboration:**
  - spatial services through APIs;
  - access control per data set and layer;
  - customizable analytical spatial reports;
  - group collaboration and project sharing;
  - compliance with national and international spatial-data standards.

### F15. Integration and orchestration middleware (میان‌افزارهای یکپارچه‌سازی و همنواسازی)
- **Data flow:**
  - data transfer with minimal latency;
  - communication between several heterogeneous systems;
  - **concurrent processing of several information streams**;
  - **synchronous and asynchronous communication**.
- **Reliability and scale:**
  - **error handling and automatic recovery during disruption**;
  - **horizontal scaling for heavy loads**.
- **Events and workflow:**
  - **automatic coordination of data and events across locations**;
  - **rules that react to specific events**;
  - workflows for integration flows.
- **Interfaces and security:**
  - **management of different versions of services and interfaces**;
  - encryption and protection of data in transit;
  - common communication standards and protocols;
  - integration with cloud and on-premises services.
- **Operations:**
  - monitoring and system event logging;
  - simple tools to configure and supervise orchestration.

### F16. Network infrastructure services (سرویس‌های زیرساخت شبکه)
- **Delivery:**
  - fast content delivery with minimal latency across geographic locations;
  - caching of static and semi-dynamic content;
  - uninterrupted multimedia streaming;
  - optimized bandwidth use on server and client;
  - compatibility with varied devices and mobile networks.
- **Resilience and load:**
  - **service stays stable and available during traffic spikes**;
  - intelligent load distribution across network points.
- **Security and policy:**
  - encryption in transit;
  - access policies and regional zoning of distribution.
- **Operations and integration:**
  - real-time monitoring and performance reporting;
  - integration with cloud or private data centres.

### F17. Telecom infrastructure software (نرم‌افزارهای زیرساختی مخابراتی)
- **Performance and resilience:**
  - low latency for signalling or user requests;
  - stable performance under heavy or abnormal traffic;
  - **updates without service downtime**;
  - multiple network generations in parallel;
  - stable call or messaging quality.
- **Subscribers and policy:**
  - dynamic SLA policies;
  - precise, secure subscriber-profile management;
  - fast, secure access to subscriber databases;
  - complex rating and charging rules;
  - flexible definition and activation of value-added services;
  - user access control at different network layers.
- **Routing and resources:**
  - intelligent call or message routing;
  - concurrent control of several call or data paths in the core;
  - full coordination of controllers and signal processors;
  - dynamic, automatic voice or data resource allocation;
  - coordination of virtual and physical units.
- **Security:** encryption at the signalling or data layer.
- **Integration and openness:**
  - integration with OSS/BSS;
  - connection to Billing, CRM, IVR and other services;
  - APIs and open-protocol services;
  - compatibility with cloud, virtualized or edge network architectures.
- **Monitoring and records:**
  - real-time reports on network status;
  - centralized monitoring and troubleshooting across layers;
  - recording and reviewing user or system events.

### F18. Network software (نرم‌افزارهای شبکه)
- **Traffic and routing:**
  - optimized data flow for lower latency and higher speed;
  - intelligent packet routing by network state;
  - dynamic traffic policies;
  - traffic analysis to optimize performance.
- **Monitoring:**
  - graphical live view of network components;
  - real-time detection and alerting of disruption.
- **Management and scale:**
  - central management of connected devices and services;
  - configuration without stopping service;
  - scalability for large, distributed networks.

### F19. Storage software (نرم‌افزارهای ذخیره‌سازی)
- **Access and performance:**
  - fast, stable access to data under varied conditions;
  - file, block or object structures;
  - efficient use of CPU and disk;
  - acceptable performance in dense network environments.
- **Recovery and durability:**
  - recovery after failure or accidental deletion;
  - automatic or scheduled backups;
  - data reconstruction after hardware error;
  - keeping several versions of files or data.
- **Security:**
  - encryption in transit and at rest;
  - role-based access control;
  - MFA.
- **Scale and environments:**
  - capacity scaling without performance loss;
  - fit with cloud, on-premises or hybrid environments;
  - secure, uninterrupted transfer between nodes.
- **Monitoring:** real-time monitoring and reporting of data status.

### F20. Physical and virtual compute-management software (نرم‌افزارهای مدیریت پردازش فیزیکی و مجازی)
- **Setup and efficiency:**
  - fast start with minimal configuration;
  - efficient use of CPU, memory and energy;
  - stable operation under varied loads.
- **Management and scale:**
  - central management of several machines or environments;
  - horizontal and vertical scaling;
  - automatic execution of repetitive or scheduled tasks;
  - coordination between independent or virtual modules;
  - dynamic resource-allocation policies;
  - role-based access to resources or processes.
- **Infrastructure and environments:**
  - flexible connection to hardware or infrastructure layers;
  - interaction with different operating systems or environments;
  - tools to simulate or test varied environments.
- **Continuity:**
  - development or updates without stopping service;
  - fast recovery after disruption.
- **Monitoring:** real-time monitoring and reporting of performance.

### F21. Service, system and endpoint management software (نرم‌افزارهای مدیریت سرویس‌ها، سامانه‌ها و نقاط انتهایی)
- **State and monitoring:**
  - automatic periodic recording of resource and component state;
  - live view of endpoints and infrastructure;
  - trends in resource use and capacity.
- **Alerts and incidents:**
  - alerts on errors or out-of-policy changes;
  - tracking requests or incidents through to final resolution;
  - root-cause analysis of incidents.
- **Changes and assets:**
  - reports on changes made;
  - central allocation, recovery or update of assets;
  - automated patching and updates.
- **Access and audit:**
  - user access levels per operation;
  - complete history of events and user actions.
- **Service management:**
  - SLA definition and compliance monitoring;
  - integration with other IT management tools;
  - an analytical dashboard for management decisions;
  - classification and prioritization of requests and tasks.

### F22. Information security: recovery (امنیت اطلاعات – بازیابی)
- **Planning:**
  - business impact analysis (BIA);
  - RTO and RPO definitions per service;
  - drafting and providing recovery plans.
- **Recovery:**
  - recovery of all kinds of data (file, partition, application data);
  - recovery of files encrypted by ransomware.
- **Incident knowledge:**
  - recording incidents in a knowledge base;
  - a management dashboard with visual reports on incidents and responses.
- **Secure erasure:**
  - wiping a disk, drive or partition;
  - wiping a file or folder and its contents;
  - definable overwrite patterns, including US DoD, Gutmann, combined and user-defined methods.
- **Protection and audit:**
  - logs of operations done by the software;
  - hardware locks and passwords to protect execution and data;
  - audit reports and monitoring of user activity;
  - secure data transfer with selectable security level.

### F23. Information security: response (امنیت اطلاعات – پاسخگویی)
- **Data collection:**
  - ingest and analyse data from varied security sources;
  - user or member reports of threats;
  - receiving and processing network traffic for deeper analysis.
- **Response policy and automation:**
  - definable incident-response policies;
  - automatic responses to incidents or threats;
  - running commands or scripts as a response.
- **Incident tracking:**
  - recording and tracking incidents through recovery;
  - full documentation of the incident-management cycle;
  - storing and replaying incident data for analysis.
- **Investigation:**
  - search with varied filters;
  - decrypting sensitive data during investigation;
  - behavioural analysis and discovery of links between evidence;
  - correlating data from varied sources;
  - forensics of memory, files, OS and network.
- **Threat intelligence and sharing:**
  - sharing data with other security systems;
  - external threat feeds and knowledge updates;
  - standard threat-sharing formats (STIX).
- **Assessment and decisions:**
  - risk- or asset-based prioritization of threats;
  - assessing the current security posture to support decisions;
  - proactive alerts based on the current situation.
- **Reporting and visibility:**
  - an analytical dashboard of the live security posture;
  - formal and technical reports for higher authorities.
- **Access and administration:**
  - user roles and permissions;
  - secure sessions for configuration and management;
  - product customization and backup of settings.

### F24. Information security: detection (امنیت اطلاعات – تشخیص)
- **Behavioural and anomaly detection:**
  - fast detection of abnormal activity from user or system behaviour;
  - concurrent multi-source analysis to find hidden threats;
  - building and analysing behavioural profiles;
  - fraud detection in financial or transactional processes;
  - ML-based intelligent decision support.
- **File and malware analysis:**
  - static and dynamic analysis of suspicious files or code;
  - inspecting files in isolated, safe (sandbox) environments;
  - visualizing malware behaviour at runtime;
  - signature matching;
  - search by file attributes, code or hash;
  - countering obfuscation in malware;
  - high speed on large or complex files.
- **Network analysis:** traffic analysis for intrusion or malware.
- **Classification and alerting:**
  - classifying events by severity and type;
  - real-time alerts to central systems or the security team;
  - reports in varied, machine-readable formats.
- **Vulnerabilities and attack simulation:**
  - automatic vulnerability scanning;
  - attack-scenario simulation;
  - simulating vulnerable services to lure attackers (honeypots).
- **Threat data:**
  - automatic or offline threat-database updates;
  - data from external analysis services or threat platforms.
- **Investigation:**
  - discovering hidden links between suspicious entities;
  - historical tracing of files, processes or behaviour;
  - visualizing links between networks, entities and events;
  - tracing attacker activity and the intrusion path;
  - low-level analysis of OS, registry or memory;
  - a complete history of analyses and alerts.
- **Configuration and integration:**
  - targeted analysis or scan scenarios;
  - roles and access levels;
  - customizable analysis engine and detection rules;
  - compatibility with SIEM and EDR.

### F25. Information security: identification (امنیت اطلاعات – شناسایی)
- **Asset discovery:**
  - automatic, continuous discovery of assets and their changes;
  - assigning security value to assets by impact and importance;
  - discovering hidden dependencies between assets and processes.
- **Risk analysis:**
  - logical links between threats, vulnerabilities and assets;
  - analysis of the current state using predefined indicators;
  - risk-assessment scenarios;
  - multi-source data merged into the final analysis;
  - customizable indicators and parameters;
  - gap analysis against reference standards.
- **Controls and compliance:**
  - continuous assessment of control effectiveness;
  - compliance with various standards;
  - managing knowledge libraries for each industry.
- **Reporting:**
  - analytical reports for different management levels;
  - a dashboard for key indicators and risk status;
  - producing and exchanging data and reports in machine-readable formats.

### F26. Information security: protection (امنیت اطلاعات – محافظت)
- **Access and identity:**
  - role-based access levels;
  - single sign-on and central identity management;
  - MFA or biometric authentication;
  - access policies in cloud and hybrid environments;
  - infrastructure for external users or partners.
- **Encryption and data protection:**
  - varied encryption policies;
  - protection policies for data in transit, at rest and in use;
  - central key management across locations;
  - filtering, restricting or masking data by permission;
  - data-leak prevention policies;
  - secure storage and reliable recovery of sensitive data.
- **Monitoring and response:**
  - logging and reporting of sensitive activity and security events;
  - monitoring tools for user and system behaviour;
  - automatic counter-action against suspicious or unauthorized activity;
  - real-time alerts and reports to monitoring centres.
- **Compliance and integration:**
  - compliance with common standards and security requirements;
  - integration with the organization's other security systems.
- **Coverage and resilience:**
  - secure services for web and mobile applications;
  - multi-platform deployment;
  - mechanisms resistant to common threats;
  - customizable security settings and indicators.

### F27. Security management (مدیریت امنیت)
- **Tracking and documentation:**
  - recording and tracking security actions in the organization;
  - automatic documentation of actions taken.
- **Reporting:**
  - visual reports on overall risk and control status;
  - analysis of policy execution with management reports;
  - a management dashboard for key indicators.
- **Policies and projects:**
  - updating policies as the environment changes;
  - projects to improve information security;
  - custom indicators of how effective measures are.
- **Access:** customizable user access levels.
- **Continuity and backup:**
  - restoring previous settings after an error;
  - automatic, configured backup of security data.
- **Risk and compliance:**
  - periodic monitoring of vulnerabilities and patch status;
  - tools to align procedures with security frameworks;
  - risk analysis with configurable methods.
- **Integration:** integration with asset or incident management.

### F28. Technical services implementing security solutions (خدمات فنی پیاده‌سازی راهکارهای امنیت اطلاعات)
- **Assessment:**
  - precise security-status reports with prioritized risks;
  - fast identification of technical and operational weaknesses;
  - targeted tests to find vulnerabilities;
  - confidentiality of data throughout analysis.
- **Design and implementation:**
  - practical solutions sized to risk;
  - design of multi-layer defences for systems and networks;
  - continuous threat monitoring;
  - integration with existing infrastructure without disruption;
  - processes based on recognized standards;
  - security settings localized to the organization.
- **Incident investigation and response:**
  - incident analysis and extraction of valid evidence;
  - reconstruction of the attack chain;
  - 24/7 monitoring and incident response.
- **Documentation and knowledge transfer:**
  - technical and operational documentation for each stage;
  - training or knowledge transfer to the in-house team.

### F29. Information-security governance and management services (خدمات مدیریت و حاکمیت امنیت اطلاعات)
- **Assessment:**
  - asset identification and classification by sensitivity;
  - gap analysis against credible frameworks;
  - assessment of control effectiveness with corrective recommendations;
  - compliance review against legal requirements and international standards;
  - analysis of security trends with preventive recommendations.
- **Planning and policy:**
  - a prioritized roadmap to improve security;
  - business-continuity and crisis-recovery planning;
  - drafting and implementing organizational security policies and processes;
  - information-security KPIs.
- **Reporting and audit:**
  - management and technical reports suited to each audience;
  - documentation of all governance activities and decisions;
  - continuous monitoring of policy execution with regular reporting;
  - support for internal or external audits.

### F30. Comprehensive information-security solution (راهکار جامع امنیت اطلاعات)
- **Detection and analysis:**
  - filtering and analysing data by traffic content or activity type;
  - **detecting new threats without known signatures**;
  - detecting hidden or polymorphic threats with advanced analysis;
  - retrieving or inspecting data to analyse suspicious events.
- **Policy and access:**
  - flexible behaviour-based security policies;
  - role-based access management.
- **Data collection and visibility:**
  - many network protocols;
  - live monitoring of users, devices and traffic;
  - collecting and correlating logs from varied sources and formats;
  - customizable dashboards of overall security posture.
- **Updates and integration:**
  - offline and online updates of signatures, rules or configuration;
  - integration with other internal or external security systems (SIEM, ISAC, …).
- **Response and audit:**
  - automatic or guided response to detected attacks;
  - audit data and activity monitoring for later review.

### F31. Video-game industry (صنعت بازی‌های ویدئویی)
- **Scale and performance:**
  - **many concurrent users with no loss of performance**;
  - **scaling infrastructure as traffic changes**;
  - stable frame rate and good visual quality on most devices.
- **Architecture and platforms:**
  - modular, extensible structure;
  - several major platforms with minimal rewriting;
  - updating game features **without reinstalling**;
  - an engine suited to the game's style and complexity.
- **Real time and resilience:**
  - **real-time synchronization between game components**;
  - keeping data and continuing play when the connection drops.
- **Players and matching:**
  - difficulty adjusted from behaviour analysis;
  - **intelligent matching algorithms for player interaction**;
  - user interactions such as chat, ranking and grouping.
- **Data, security and integrity:**
  - data analytics to optimize level design;
  - **anti-cheat and anti-tampering techniques**;
  - security of data in transit and at rest;
  - user privacy in all processes.
- **Monetization and content:**
  - in-game campaigns and rewards;
  - integration with stores and admin panels;
  - tools to manage interactive content and user data;
  - procedural content generation.
- **Creative and cultural criteria:**
  - an Iranian story;
  - an original narrative;
  - innovative mechanics, dynamics and rules;
  - difficulty-curve design;
  - level design;
  - monetization model;
  - in-game economy and game balance;
  - watchability;
  - Iranian or distinctive art;
  - colourization;
  - procedural art tools (Houdini, Substance Designer);
  - a distinctive, coherent visual style.

### F32. Animation industry (صنعت انیمیشن)
- **Design and presentation:**
  - UI/UX aesthetics;
  - visual coherence;
  - creativity;
  - clarity;
  - cultural fit;
  - visual personalization;
  - emotion design;
  - visual storytelling;
  - accessibility.
- **Production scale and technique:**
  - project scale (characters, scenes, duration);
  - production technique (CGI, motion capture, VFX);
  - innovation in tools and plugins.
- **Technical quality:**
  - rendering quality;
  - compositing quality;
  - modelling detail.
- **Pipeline and simulation:**
  - production pipeline and render-farm management;
  - complexity of physics simulation (hair, cloth, fluids, fire).
- **Output and innovation:**
  - output standard (4K, VR, interactive rendering);
  - use of AI or new tools.

---

## A.4 Condition: mastery of technical know-how (شرط تسلط بر دانش فنی), pp. 40–41

This condition measures technical capability **beyond the product itself**. It asks how far the company masters the know-how needed to **develop, optimize, support and upgrade** the product. It also asks whether that know-how is **domestic and transferable** (بومی و قابل انتقال), or simply relies on foreign tools.

**This is where claims of technical complexity are proven.** Each row is a criterion and also a list of the evidence evaluators expect.

| # | Criterion | What evaluators look at |
|---|---|---|
| K1 | Complete design and architecture documents that follow software-development standards | Product Backlog, SRS (Software Requirements Specification), Big Picture, Technical Architecture Diagram and other recognized formats. They must clearly show the structure, key components, workflow, and the company's responsibilities in developing the product. |
| K2 | Knowledge-management infrastructure and policies | Quality and quantity of knowledge in organizational KM systems (Wikis, Confluence, Notion, …), and how documentation is updated, shared and used across development teams. |
| K3 | Technical infrastructure supporting design and development | Development tools, CI/CD environments, DevOps architecture, project and SDLC tools such as Git, Docker, Jenkins, GitLab CI and Azure DevOps. |
| K4 | Documented, traceable source-code history | Access to source versions, detailed commits, contribution trends, and documentation of version changes through Git, Bitbucket or GitHub. **Named indicators: *Git Commit Hygiene* and *Documentation per Commit*.** |
| K5 | Continuous integration and delivery (CI/CD) | Automated pipelines for Build, Test and Deployment, documentation of how they are configured, and **how much of the development process is automated**. |
| K6 | Documented release versioning and release tools | Versioning policy (e.g. Semantic Versioning), release-management tools, and use of Alpha, Beta and Stable versions. |
| K7 | QA/QC processes | Unit, automated, integration and security testing; QA tools such as Selenium, TestRail, JUnit and SonarQube; quality reports and sign-offs for each product or service. |
| K8 | Post-development support and service-management tools | Help desk and ticketing (Zendesk, Jira Service Desk, OTRS), and the processes for handling user requests and defects. |
| K9 | Automated test coverage | Unit, integration and system test coverage against the main code (code coverage), measured with tools such as Istanbul, JaCoCo or Coveralls. |
| K10 | DevOps maturity | Automated Build/Test/Deploy, container-based deployment, monitoring tools, and fast reaction to production incidents. |
| K11 | The team's technical command of the product domain and target market | Understanding of user needs, domain architecture, competitor analysis, and domestic and foreign technology trends. |
| K12 | Human-resource contribution to each product's life cycle | Number and percentage of staff assigned to each product, by role: analyst, developer, tester, DevOps, UX designer, project manager, … |
| K13 | Expertise, education and track record of key team members | Education level, relevant field, prior experience on similar projects, specialist skills (languages, tools, frameworks, …). |

---

## A.5 Desired national impacts (آثار مطلوب در سطح ملی), pp. 42–47

Many laws and regulations support knowledge-based companies, and the legislator expects certain impacts in return. **A product deserves approval and support if it achieves *some* of these impacts.** The table gives each category, the impact, and the document's IT examples.

| Category | Impact | IT examples given |
|---|---|---|
| National strength and authority | Strategic, priority products, especially for food, defence, health, industrial and security needs | Medical engineering; health and crop monitoring; agricultural IoT; production-to-consumption modelling and simulation; genetic-data analysis for food security; defence C4ISR command-and-control; AI disease diagnosis; industrial monitoring and production-fault prediction; national cybersecurity systems; national social networks and messengers |
| National strength and authority | Frontier sciences and technologies: AI, quantum, bioengineering, advanced materials and manufacturing, nano/microelectronics, neurotech and cognitive science | AI platforms (e.g. deep-learning platforms); quantum simulation; chip-design software (EDA); AR platforms for cognitive-science education; neural-data processing and analysis |
| National strength and authority | Better foreign-exchange balance (earning currency or reducing currency spending) | Exportable software; software replacing foreign products; digital export platforms for goods and services |
| National strength and authority | Removing technology bottlenecks | Platforms linking advanced-tech supply chains; blockchain supply-chain management; domestic CAD/CAM; industrial process simulation; specialist databases for localizing materials and parts |
| National strength and authority | Countering sanctions | Domestic cloud and infrastructure (IaaS, PaaS); domestic secure data exchange and email; domestic payment systems independent of the international financial system; currency-payment platforms |
| National strength and authority | Strengthening vulnerable points of the economy | Networked, distributed production platforms for micro-producers; economic risk forecasting; big-data and AI crisis management; live dashboards of production, exports and imports; production-to-consumption modelling; **platforms that teach technology skills to develop a specialist workforce** |
| Scientific and economic diplomacy | Economic ties with other countries, especially neighbours and allies | Multilingual regional e-commerce (B2B/B2C); export and international logistics; multi-unit ERP/accounting with cross-border currency exchange; regional tech-cooperation platforms |
| Scientific and economic diplomacy | Raising the standing of the Persian language | Domestic search engine with strong Persian support; Persian NLP (translation, correction, content analysis); apps teaching Persian to non-Persian speakers; intelligent Persian content production and distribution |
| Scientific and economic diplomacy | Constructive, inspiring science and technology exchange, especially with the Islamic world | Online research collaboration between universities in Islamic countries; multilingual scientific databases (Persian, Arabic, English); international research-project management; virtual scientific conferences for the Islamic world |
| Natural resources and environment | Protecting the environment | Rapid alerts for forest fires and environmental crises; live air, water and soil pollution monitoring; waste and recycling management; **environmental education platforms for schools and the public** |
| Natural resources and environment | Reducing energy and resource use | Building and industrial energy management (EMS); smart metering control of power, water and gas; AI energy analysis; apps that teach conservation |
| Natural resources and environment | Using the country's untapped capacity | **Talent-discovery and skills-training platforms**; GIS for finding natural resources; modelling of mineral, water and environmental resources; sustainable digital tourism; data-driven rural development |
| Justice and employment | Developing entrepreneurship | Freelancer platforms (domestic Upwork-like); business-skills and startup education apps; crowdfunding |
| Justice and employment | Popular participation in the economy | Crowd-investment platforms; online markets for local, rural and home products; community voting and decision-making |
| Justice and employment | Cooperation and collective work | Co-op ERP; resource-sharing platforms; collaboration tools for local or trade projects |
| Justice and employment | Raising the role and income of low- and middle-income groups | Free or cheap vocational training; micro- and home-business apps; simple accounting for small businesses |
| Justice and employment | **Empowering human capital** | **Digital learning platforms (LMS) with skills-based content**; competency assessment and development for smart hiring; data/AI-based career guidance |
| Justice and employment | Economic transparency | Public financial reporting (open budgeting); transaction recording and control (invoicing, accounting, tax); anti-corruption and whistle-blowing platforms |
| Justice and employment | Preserving human dignity | Self-employment platforms; fair, non-discriminatory welfare services; citizen complaint and legal follow-up; accessibility apps for disabled and elderly people |
| Productivity and added value | Raising productivity | ERP; employee performance and productivity analysis; task management; data analytics to optimize industrial processes |
| Productivity and added value | Developing the digital economy | Domestic marketplaces and online stores; domestic cloud; fintech apps; e-commerce and digital-payment infrastructure |
| Productivity and added value | Reforming consumption patterns | Smart metering; education on efficient use of water, power, gas and food; smart, targeted subsidy software |
| Productivity and added value | Quality and competitiveness | Digital QMS; machine-vision quality control on production lines; CRM |
| Productivity and added value | High-added-value products | Digital design and prototyping (CAD, 3D); AI combined with industrial data to create new products; open-innovation platforms |
| Productivity and added value | Avoiding raw-material sales and completing the value chain | Supply-chain management; smart production and processing in agriculture and mining; creative-industry platforms that process raw content (audio, image, data) |
| Productivity and added value | Better use of human capacity | Talent matching; project management with optimal staff allocation; **continuous-learning apps for job skills** |
| Social health, ethics and spirituality | Spiritual, physical, mental and social well-being | Health self-assessment and monitoring; healthy and Islamic lifestyle apps; telemedicine; social-health and public-hygiene education |
| Social health, ethics and spirituality | Strengthening spirituality and ethics | Ethics-oriented social networks with moderated content; games with spiritual and ethical themes; habit-building assistants; applied-ethics education by age group; prayer, Quran, virtual pilgrimage and religious multimedia apps |
| Social health, ethics and spirituality | Women, family and children; childbearing and parenting | Pregnancy health and parenting apps; support networks for mothers; **educational games for children based on local educational values**; online family counselling and life-skills training |
| Social health, ethics and spirituality | Products based on Islamic and ethical values | Commerce based on ethical values; family-centred lifestyle software; content production and sharing suitable for families, **schools** and universities; interactive Islamic-lifestyle education |

---

# Part B — Agent playbook: finding and evidencing technical complexity in a codebase

This part tells an agent how to go from a repository to a defensible list of technical-complexity claims under the criteria above. It is written to be reused.

## B.1 Mindset and rules

1. **Complexity means engineering depth, not technology names** (A.2.0). "Uses Redis" is not a claim. "A sorted leaderboard of N users is rebuilt into an immutable bitset index and filtered in O(N/64) with versioned generations shared across instances through Redis" is a claim.
2. **Every claim needs code, evidence of real use, and a reason it is hard.** Write a claim only if you can name:
   - the files or classes that implement it;
   - what makes it non-trivial, i.e. the problem it solves that a naive version would get wrong;
   - how it can be shown to work: tests, load tests, logs, metrics, production use.
3. **CRUD is not complexity.** Controllers, request/response DTOs, EF mappings, validators, admin forms, plain list/filter/paginate endpoints and auth boilerplate are the baseline, not evidence. They count only through what they add up to, for example a role system with *dynamic* permissions (G14).
4. **Configured libraries are not complexity unless you engineered around them.** Calling Hangfire, Quartz, MassTransit or Elastic counts for little. Designing idempotent consumers, an outbox, a dead-letter replay, or a custom index on top of them counts.
5. **Do not overclaim.** Evaluators ask follow-up questions (مورد بررسی و پرسش). Overclaiming hurts more than leaving a claim out. If something is partial, planned, behind a disabled flag, or exists only in a branch, say so or leave it out. Condition A.1 rejects "incomplete code or an algorithm alone".
6. **Map every claim to the evaluator's vocabulary.** Tag each with the matching G-indicator (A.2.1) and, if the product falls in a category, the F-criterion (A.3). Use the Persian term when you write for evaluators.
7. **Domestic, in-house know-how is a plus** (A.4). Point out where the team built something rather than bought it, especially as an alternative to a foreign service, for example an in-house code sandbox instead of a third-party judge API.

## B.2 Process

1. **Classify the product.** Pick the F-category or categories the company files under (A.3), plus any T-technology areas it actually uses (A.2.2). An LMS with quizzes, duels and leaderboards falls under content-centred (F8), interactive (F7), application platform (F12) and partly games (F31). Its national-impact category is "empowering human capital: LMS" (A.5).
2. **Map the architecture.** Read the solution and project files, any architecture docs, the composition root (`Startup`/`Program`), and the dependency graph between projects. Note modules, data stores, message brokers, caches, background workers and external services.
3. **Sweep for signals.** Run the searches in B.4. Each hit is a lead, not a claim.
4. **Read the hot spots in depth.** For each lead, open the implementation. Decide whether it holds a real engineering decision: concurrency, consistency, an algorithm, isolation, failure handling, scale. Discard thin wrappers.
5. **Collect evidence.** For every claim that survives, record:
   - file paths;
   - tests that exercise it;
   - docs or ADRs that explain it;
   - commit history (`git log --follow <file>`, `git log -S<symbol>`);
   - load-test results, dashboards, production configs.
6. **Check against conditions A.1 and A.4.** Is it in the stable, deployed release? Is it documented? Is it tested? Is it covered by CI? Gaps here weaken the claim, so note them.
7. **Write the report** using the template in B.6, ordered strongest first.

## B.3 Indicator-by-indicator detection guide

For each G-indicator:
- **Counts** describes what qualifies.
- **Does not count** describes look-alikes that don't.
- **Look for** lists code signals.
- **Evidence** lists what to collect.

### G1 Modular design and flexible architecture
- **Counts:**
  - microservices, or a *modular monolith* with enforced boundaries (separate assemblies or packages, separate schemas or databases, ports and adapters, public contracts);
  - plugin systems;
  - hexagonal or clean architecture with real seams;
  - an ongoing extraction of a legacy monolith into bounded contexts.
- **Does not count:** folders named `Services/` and `Repositories/` in one project; layered architecture with no enforced boundaries.
- **Look for:**
  - several projects or packages and their references (`*.csproj` `ProjectReference`, `package.json` workspaces, Go modules, Maven modules);
  - a DbContext or database per module;
  - folders named `Ports/`, `Adapters/`, `Contracts/`, `Public/`;
  - **build-enforced boundaries** (BannedApiAnalyzers / `BannedSymbols.txt`, ArchUnit, dependency-cruiser, NetArchTest);
  - per-module migration histories.
- **Evidence:**
  - a module dependency diagram;
  - the rule that enforces boundaries;
  - the number of modules;
  - how one module talks to another (events or IDs, never joins);
  - an example of a module being extracted without downtime.

### G2 Complexity and optimization of algorithms
- **Counts:**
  - custom data structures (bitsets, inverted indexes, tries, interval trees, priority queues);
  - ranking and tie-breaking rules;
  - matching or pairing;
  - scheduling;
  - scoring engines;
  - graph algorithms;
  - spaced repetition;
  - recommendation;
  - query rewrites with measured gains (N+1 removal, server-side aggregation, CTEs, index-only scans);
  - bounded-memory streaming;
  - batching.
- **Does not count:** sorting a list with LINQ; a simple `GroupBy`; calling a library sort.
- **Look for:**
  - `BitOperations`, `ulong[]`, `Span<`, `stackalloc`, `PriorityQueue`, custom `IComparer`;
  - files named `*Index*`, `*Ranking*`, `*Calculator*`, `*Scoring*`, `*Scheduler*`, `*Matcher*`, `*Policy*`;
  - raw SQL with `WITH ... AS`;
  - window functions (`ROW_NUMBER`, `RANK`, `DENSE_RANK`, `OVER (`);
  - performance docs with before/after numbers;
  - benchmarks (`BenchmarkDotNet`).
- **Evidence:**
  - complexity (big-O) before and after;
  - benchmark or `EXPLAIN ANALYZE` output;
  - unit tests with edge cases (ties, empty input, boundaries);
  - the business rule the algorithm encodes.

### G3 Automation of processing and decisions (rule engine, intelligent automation)
- **Counts:**
  - admin-configurable rules evaluated at runtime (event → condition → action);
  - policy objects;
  - automated awarding, promotion or relegation;
  - automatic placement or grouping;
  - scheduled jobs that make decisions;
  - bots.
- **Does not count:** a hard-coded `if` in a handler; cron jobs that just delete old rows.
- **Look for:**
  - entities named `Rule`, `Action`, `Trigger`, `Policy`, `Condition`;
  - listeners that read configuration from the database and dispatch actions;
  - `*Evaluator`, `*DecisionPolicy`, `*Reconciler`, `*Reshuffler`;
  - Quartz/Hangfire/cron job registrations and what they decide;
  - bot schedulers.
- **Evidence:**
  - how an admin changes behaviour without a deploy;
  - the rule schema;
  - tests covering rule combinations;
  - how often rules run in production.

### G4 Integration and open APIs
- **Counts:**
  - a documented public API (OpenAPI/Swagger);
  - integration with external systems (payment, SSO, SMS/OTP, a separate execution service, a government system);
  - internal service-to-service contracts;
  - webhooks;
  - versioned interfaces;
  - resilient HTTP clients (retry, circuit breaker, timeouts).
- **Does not count:** calling one third-party SDK with defaults.
- **Look for:**
  - `AddHttpClient`, `IHttpClientFactory`, Polly / `AddResilienceHandler`;
  - Swagger/OpenAPI setup;
  - API docs folders;
  - Postman, Bruno or Insomnia collections;
  - gRPC `.proto` files;
  - webhook controllers;
  - port interfaces implemented by adapters.
- **Evidence:**
  - the integration list with protocol and direction;
  - API docs;
  - E2E collections;
  - failure handling at each integration point.

### G5 and G11 Load handling and horizontal/vertical scalability
- **Counts:**
  - stateless app instances with shared state in Redis or the database;
  - caching layers with invalidation;
  - per-instance caches that stay correct when you scale out (versioned generations, pointer checks);
  - queue-based load levelling;
  - rate limiting;
  - connection pooling;
  - partitioning;
  - **load tests with results** (k6, JMeter, Gatling, Locust);
  - capacity planning per user count.
- **Does not count:** "it runs on a big server"; using a cache with no invalidation story.
- **Look for:**
  - a `k6/`, `jmeter/` or `loadtest/` folder;
  - Grafana dashboards;
  - load-test reports;
  - `AddRateLimiter`, `IDistributedCache`, FusionCache, `IMemoryCache` with expiry and invalidation;
  - Redis key-layout docs;
  - process-local gates such as `SemaphoreSlim`, and whether they would still hold with a second instance;
  - Kubernetes HPA, `replicas:`.
- **Evidence:**
  - throughput and latency at load, and the breakpoint;
  - which component saturates first;
  - the scale-out story;
  - cache hit ratios.

### G6 Data analysis (statistical, predictive, prescriptive)
- **Counts:**
  - analytics computed server-side:
    - per-user statistics;
    - cohort or league metrics;
    - progress indicators;
    - dashboards;
  - prediction (difficulty estimation, churn, mastery);
  - prescriptive suggestions (what to study next).
- **Does not count:** a count endpoint; exporting raw rows to Excel.
- **Look for:**
  - `*Statistics*`, `*Metrics*`, `*Report*`, `*Indicator*`, `*Analytics*`;
  - aggregate SQL;
  - materialized views;
  - reporting endpoints;
  - BI integrations.
- **Evidence:**
  - which metrics are computed, how, and on what volume;
  - who uses them (admins, teachers, students).

### G7 Workflow engine / BPMN
- **Counts:**
  - explicit state machines with guarded transitions (ticket life cycles, approval flows, exam attempt states, pairing with approval or rollback);
  - sagas;
  - BPMN engines (Camunda, Elsa, Temporal);
  - multi-actor processes with role-based steps.
- **Does not count:** a `status` enum changed freely by any endpoint.
- **Look for:**
  - status enums together with transition methods that refuse invalid moves;
  - `Saga`, `StateMachine`, `Workflow`;
  - Elsa/Temporal/Camunda packages;
  - multi-step approval entities;
  - version/concurrency tokens on workflow aggregates.
- **Evidence:**
  - a state diagram (Mermaid);
  - transition tests;
  - which roles drive which transitions.

### G8 Dynamic configurability and adaptability
- **Counts:**
  - behaviour changed at runtime from the database or admin panel (scoring modes, weights, ranges, league tiers, feature flags, per-tenant settings);
  - options bound per environment with validation;
  - definitions **frozen into each attempt** (snapshotting) so a configuration change can't corrupt work in progress;
  - feature flags that disable whole modules.
- **Does not count:** an `appsettings.json` value read once.
- **Look for:**
  - entities ending in `Config`, `Settings`, `Definition`, `Template`;
  - `IOptionsMonitor`, `ValidateOnStart`;
  - `Enabled` flags per module;
  - `snapshotJson` or other immutable captures;
  - back-office endpoints that change behaviour.
- **Evidence:**
  - the list of configurable behaviours;
  - an example where an admin changed the product with no deploy;
  - the snapshot or versioning design.

### G9 Data and knowledge life cycle
- **Counts:**
  - defined stages for data:
    - live → grace period → frozen or archived → purged;
    - year-end snapshots;
    - retention;
  - legacy-data migrations run while live, with verification;
  - backfills;
  - soft delete with history;
  - audit trails;
  - progress resets that keep history.
- **Does not count:** EF migrations that only add columns.
- **Look for:**
  - `*Archive*`, `*Freezer*`, `*Backfill*`, `*Migrator*`, `*Snapshot*`, `*Retention*`, `*Reset*`;
  - background services that run once at startup;
  - SQL backfill scripts;
  - migration-verification docs.
- **Evidence:**
  - a life-cycle diagram;
  - the volume moved;
  - how correctness was checked;
  - rollback plans.

### G10 Multi-layer security (communications, data, identity, operations)
- **Counts:**
  - each layer separately:
    - TLS and encryption in transit;
    - encryption or hashing at rest;
    - identity (JWT, OTP or MFA, SSO);
    - authorization (roles, ownership checks);
    - operations (rate limiting, audit logs, secret management);
  - **isolation of untrusted input or code** (sandboxes, `setrlimit`, seccomp, containers, process-tree kill, output caps);
  - trusted-URL allow-lists;
  - security test reports.
- **Does not count:** `[Authorize]` alone; "we use HTTPS".
- **Look for:**
  - auth middleware;
  - OTP and MFA flows;
  - password hashing;
  - `AddRateLimiter`;
  - `setrlimit` / `RLIMIT_`, `Process.Kill(entireProcessTree`, container user or seccomp settings;
  - allow-list validators;
  - security checklists;
  - penetration-test reports;
  - dependency scanning.
- **Evidence:**
  - a table of layers and controls;
  - the threat model for any untrusted-code feature;
  - security test results.

### G12 Distributed, multi-user, real-time, omni-channel
- **Counts:**
  - real-time multi-user interaction (matchmaking, live duels, shared rooms, chat);
  - presence and heartbeats;
  - concurrency control between users (optimistic concurrency, unique constraints, conditional updates);
  - several clients sharing one backend (web, mobile, admin panel);
  - push notifications.
- **Does not count:** many users each using the app on their own.
- **Look for:**
  - SignalR / WebSocket hubs, SSE, long polling;
  - Redis sets and sorted sets used as queues;
  - TTL heartbeats;
  - `match`/`ticket`/`pairing` entities;
  - `IsConcurrencyToken`, `xmin`, `version` columns;
  - push and notification services.
- **Evidence:**
  - a sequence diagram of the real-time flow;
  - how races are prevented;
  - concurrent-user figures.

### G13 Event-driven and real-time event processing
- **Counts:**
  - integration events across modules or services;
  - a transactional outbox;
  - durable queues;
  - idempotent consumers;
  - dead-letter handling and replay;
  - event-sourced projections;
  - reacting to events in near real time.
- **Does not count:** in-process `INotification` used only to fire an email.
- **Look for:**
  - Wolverine, MassTransit, NServiceBus, Kafka, RabbitMQ;
  - `Outbox`, `PublishAsync`, `[WolverineHandler]`, `IConsumer<`;
  - queue declarations;
  - dead-letter queue config and replay services;
  - per-event idempotency keys or unique indexes.
- **Evidence:**
  - the event catalogue (producer → consumer);
  - the delivery guarantee;
  - the idempotency strategy;
  - the dead-letter replay design;
  - an event-flow diagram.

### G14 Varied access levels and dynamic roles
- **Counts:**
  - roles and permissions stored as data and editable at runtime;
  - scoped access (per school, organization, tenant);
  - several actor types (student, teacher, support, technical, admin, content admin).
- **Does not count:** a hard-coded `IsAdmin` flag.
- **Look for:**
  - `Role`, `RoleAccess`, `Permission`, `Claim` entities;
  - role-management endpoints;
  - custom authorize attributes reading roles from data;
  - organization- or tenant-scoped queries.
- **Evidence:**
  - the role and permission model;
  - how a new role is created without a deploy;
  - scope enforcement.

### G15 Operational intelligence (recommender, behaviour analysis)
- **Counts:**
  - personalization from user history (spaced repetition, adaptive daily quizzes, difficulty adjusted to performance);
  - recommendations;
  - matching on skill or league;
  - anomaly or cheat detection;
  - LLM features with guardrails.
- **Does not count:** showing the newest items; random selection.
- **Look for:**
  - answer-history stores;
  - `*Review*`, `*Recommend*`, `*Adaptive*`, `*Difficulty*`;
  - matchmaking by rating or league;
  - LLM client calls and prompt files;
  - `#if` blocks for AI features (check whether they are enabled).
- **Evidence:**
  - the signal used;
  - the selection algorithm;
  - the measured effect;
  - whether it is enabled in production.

### G16 Observability, monitoring, alerting
- **Counts:**
  - distributed tracing;
  - metrics;
  - structured logging with correlation;
  - error tracking;
  - dashboards and alert rules;
  - health checks;
  - recording rules;
  - runbooks.
- **Does not count:** `Console.WriteLine`; default logging only.
- **Look for:**
  - `AddOpenTelemetry`, Prometheus exporters, Sentry, Serilog sinks;
  - `HealthChecks`;
  - Grafana JSON;
  - alert rules;
  - log scopes with correlation IDs;
  - runbooks.
- **Evidence:**
  - screenshots of dashboards;
  - the list of alerts;
  - an incident that observability helped resolve.

## B.4 Signal sweep: ready-to-run searches

Run these from the repository root. Exclude build output, vendored code, migrations and worktrees. Every hit is a lead; read it before you claim anything.

```bash
X='--exclude-dir=obj --exclude-dir=bin --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=.claude --exclude-dir=Migrations'

# Architecture and boundaries (G1)
find . -name '*.csproj' -not -path '*/obj/*' | sort
grep -rl $X 'BannedSymbols\|NetArchTest\|ArchUnit' .
grep -rn $X 'class .*DbContext\b' --include=*.cs . | grep -v Tests

# Algorithms (G2)
grep -rln $X -E 'BitOperations|stackalloc|PriorityQueue<|IComparer<|ROW_NUMBER|DENSE_RANK|OVER \(|WITH [a-zA-Z_]+ AS' .
find . -not -path '*/obj/*' -iname '*Index*.cs' -o -iname '*Ranking*.cs' -o -iname '*Scoring*.cs' -o -iname '*Calculator*.cs' -o -iname '*Matcher*.cs'

# Rules, automation, jobs (G3)
grep -rln $X -E 'IJob\b|AddQuartz|RecurringJob|BackgroundService|IHostedService|Evaluator|DecisionPolicy|Reconciler' --include=*.cs .

# Integration (G4)
grep -rn $X -E 'AddHttpClient|AddResilienceHandler|Polly|AddSwaggerGen|AddOpenApi|Grpc' --include=*.cs .

# Load, cache, scale (G5/G11)
ls -d k6 jmeter loadtest* locust* 2>/dev/null
grep -rln $X -E 'IDistributedCache|IFusionCache|IMemoryCache|IConnectionMultiplexer|AddRateLimiter|SemaphoreSlim' --include=*.cs .

# Workflow and state machines (G7)
grep -rln $X -E 'StateMachine|Saga|Workflow|Elsa|Temporal|Camunda' .
grep -rn $X -E 'enum \w*(Status|State)\b' --include=*.cs .

# Configurability and snapshots (G8)
grep -rln $X -E 'IOptionsMonitor|ValidateOnStart|snapshot|Snapshot|FeatureFlag|:Enabled' --include=*.cs .

# Data life cycle (G9)
find . -not -path '*/obj/*' \( -iname '*Archive*' -o -iname '*Backfill*' -o -iname '*Freezer*' -o -iname '*Migrator*' -o -iname '*Retention*' \)

# Security and sandboxing (G10)
grep -rln $X -E 'RLIMIT_|setrlimit|entireProcessTree|seccomp|AddAuthentication|Otp|OTP|HashPassword|BCrypt|AllowList|TrustedUrl' .

# Real-time and concurrency (G12)
grep -rln $X -E 'Hub\b|SignalR|WebSocket|IsConcurrencyToken|xmin|\.version\+\+|heartbeat|Heartbeat|KeyExpire|SetAdd' --include=*.cs .

# Events (G13)
grep -rln $X -E 'Wolverine|MassTransit|RabbitMQ|Kafka|Outbox|IIntegrationEvent|dead.letter|DeadLetter' .

# Roles (G14)
grep -rln $X -E 'class (Role|Permission|RoleAccess)\b|Authorize\(Role' --include=*.cs .

# Intelligence (G15)
grep -rln $X -E 'Recommend|Adaptive|Difficulty|Review|ChatCompletion|OpenAI|LLM' --include=*.cs .

# Observability (G16)
grep -rn $X -E 'AddOpenTelemetry|Prometheus|UseSentry|Serilog|AddHealthChecks|BeginScope' --include=*.cs .

# Know-how evidence (A.4)
git rev-list --count HEAD; git shortlog -sn | head; ls .gitlab-ci.yml .github/workflows Jenkinsfile 2>/dev/null
find . -maxdepth 2 -name '*Tests*' -o -maxdepth 2 -name '*.Test'
```

Adapt the patterns for other stacks. Java: `@Scheduled`, `@KafkaListener`, Spring Statemachine. Node: BullMQ, socket.io. Python: Celery, asyncio, FastAPI.

## B.5 Evidence for condition A.4

Technical-complexity claims are much stronger when backed by A.4 evidence. For each item, check and record:

| A.4 item | What to check | Typical gap to flag |
|---|---|---|
| K1 design/architecture docs | `docs/`, ADRs, Mermaid or C4 diagrams, SRS, backlog | Diagrams out of date; no SRS |
| K2 knowledge management | Wiki, Confluence or Notion links, `docs/` freshness (`git log -- docs`) | Documentation not updated with the code |
| K3 dev infrastructure | Dockerfiles, compose files, CI config, package mirrors | — |
| K4 traceable history | Commit count, contributors, message quality, linked issues | Vague messages ("fix", "update") hurt *Commit Hygiene* |
| K5 CI/CD | Pipeline stages: build, **test**, deploy | **Pipeline that does not run tests** |
| K6 versioning | Tags, SemVer, release notes, staging/production branches | No tags or release notes |
| K7 QA/QC | Test projects, E2E collections, static analysis (SonarQube, analyzers) | No security tests; no QA reports |
| K8 support | A ticketing module or external desk | — |
| K9 coverage | Coverage tooling (coverlet, JaCoCo, Istanbul) and reports | **Coverage not measured** |
| K10 DevOps maturity | Containers, monitoring, alerting, incident runbooks | Manual deploy steps |
| K11–K13 team | (Not in the code) roles, staffing and CVs come from the company | — |

## B.6 Output template

For each claim, write one block. Order them strongest first, and put the 3–5 most defensible claims at the top.

```markdown
### <Short name of the capability>
- **Indicator:** G<n> <name> (Persian: <term>) · Function criterion: F<n> "<criterion>" (if any)
- **What it does:** one or two sentences in product terms.
- **Why it is technically complex:** the hard problem (concurrency, scale, isolation, correctness under failure, algorithmic cost) and the design that solves it.
- **Where:** `path/to/File.cs`, `path/to/Other.cs` (key classes and methods)
- **Evidence:** tests (`path`), docs (`path`), load-test or benchmark results, production signals, commits.
- **Built in-house:** yes/no; what it replaces (supports A.4 "domestic know-how").
- **Caveats:** anything partial, disabled, or not yet in production.
```

Finish the report with:
1. A table of indicators G1–G16, each marked *strong / moderate / none*, with the claims that cover it.
2. The A.4 gap list (B.5).
3. Suggested quick wins that would strengthen the file, for example adding tests and coverage to CI.

## B.7 Pitfalls

- **Counting the same mechanism twice.** One Redis cache is not three claims (G5, G11, G12). Name it once and list all its indicators.
- **Confusing documentation with implementation.** A proposal doc or PRD is not a feature. Check that the code exists, is wired into the composition root, and is enabled in production configuration.
- **Feature flags and `#if` blocks.** Code behind a disabled flag (e.g. a module whose `Enabled` setting defaults to false, or `#if SOMEAI`) is not in production. Say so.
- **Worktrees, branches and leftovers.** Search only the real source tree. Exclude `.claude/worktrees`, stray legacy folders and vendored code.
- **Over-engineering is not complexity.** Locks, semaphores or counter rows added to plain CRUD where a unique index would do are not engineering depth. Don't present them as such, because evaluators may see them as immaturity.
- **Tests that prove nothing.** Unit tests with heavy mocks don't prove behaviour under concurrency or load. Prefer integration tests, load tests and production metrics as evidence for G5, G11, G12 and G13.
- **Ignoring the production-stage condition.** A brilliant algorithm in a branch fails A.1. Tie claims to the stable, deployed release.
