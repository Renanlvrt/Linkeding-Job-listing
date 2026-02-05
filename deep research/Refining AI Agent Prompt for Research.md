# **Architectural Design for "CareerGold Auto" Agent Swarm (Antigravity Framework)**

## **Executive Summary**

The talent acquisition landscape is currently undergoing a radical transformation, shifting from passive applicant tracking systems (ATS) to active, agentic candidate representation. This report details the architectural design and implementation strategy for **CareerGold Auto**, a fully autonomous job application system engineered to function as a "digital twin" for job seekers. Built upon Google’s **Antigravity** framework, this system represents a paradigmatic shift in personal automation, moving beyond simple scripting to deploy a resilient swarm of AI agents capable of perception, reasoning, and execution in hostile web environments.

The primary mandate of this architectural upgrade is to override the previous product constraint which excluded "Auto-Apply" capabilities. This exclusion, previously necessitated by the technical complexity of platforms like Workday and Greenhouse, is now rendered obsolete by advancements in visual browser automation and agentic orchestration. CareerGold Auto leverages a multi-agent swarm architecture to autonomously source, filter, and apply for positions, strictly adhering to the Antigravity 3-Layer Architecture: **Directives**, **Orchestration**, and **Execution**.

By synthesizing cutting-edge visual browser agents (Browser-Use), privacy-preserving local semantic models (all-MiniLM-L6-v2), and robust orchestration protocols, this system addresses the dual challenges of "finding the needle in the haystack" and "navigating the bureaucratic maze" of modern recruitment. The resulting architecture is not merely a tool but a persistent, self-healing entity designed to operate indefinitely until the user’s goal—securing employment—is achieved.

## ---

**1\. Strategic Context and Architectural Philosophy**

### **1.1 The Shift to Agentic HR Technology**

Traditional automation in the Human Resources and job search domain has historically been defined by rigid, linear scripting. Tools like Selenium or simple Python scrapers rely on static document object model (DOM) selectors—specific IDs or class names within a webpage’s code—to identify interaction points. This approach is inherently brittle; a minor update to a website’s user interface (UI) or the deployment of anti-bot countermeasures (such as dynamic class obfuscation used by LinkedIn or Indeed) invariably causes these scripts to fail.

The emergence of "Agentic AI" fundamentally alters this dynamic. Unlike scripts, which execute a pre-defined sequence of steps, agents operate based on goals. They possess the capacity for perception (viewing the screen), reasoning (determining the correct action based on context), and adaptation (recovering from errors without human intervention). **CareerGold Auto** is positioned at the forefront of this shift, utilizing the "Antigravity" framework to deploy agents that do not simply "run" but "work" alongside the user.

### **1.2 The Antigravity Framework: A Mission Control for Code**

Google’s Antigravity framework 1 provides the structural backbone for this system. It redefines the Integrated Development Environment (IDE) from a text editor into a "Mission Control" center for autonomous agents. This distinction is critical. In a traditional IDE, the developer writes code that the machine executes. In Antigravity, the developer acts as an architect, issuing high-level **Directives** to agents that handle the **Execution**, while the **Orchestration** layer manages the complexities of state, dependencies, and parallel processing.3

The framework’s reliance on the Gemini 3 model introduces a "Deep Think" capability.4 This allows the CareerGold agents to allocate "thought tokens"—hidden computational steps for internal debate and planning—before taking action. This reasoning step is vital for overcoming complex barriers like Workday’s multi-stage application wizards, where the path to submission is non-linear and conditional logic is required to navigate unforeseen validation errors or pop-ups.

### **1.3 The 3-Layer Architecture Overview**

To ensure robustness and scalability, CareerGold Auto strictly adheres to the Antigravity 3-Layer Architecture. This decoupling ensures that changes in one layer (e.g., a new Directive to prioritize remote jobs) do not break the lower layers (e.g., the visual selector logic for the "Submit" button).

| Layer | Component | Function | Key Technology |
| :---- | :---- | :---- | :---- |
| **Layer 1** | **Directives** | Definition of goals, constraints, personality, and ethical guardrails. The "Soul" of the agent. | GEMINI.md, System Prompts |
| **Layer 2** | **Orchestration** | Task planning, routing, state management, and inter-agent communication. The "Brain" of the swarm. | Agent Manager, Swarm Protocol |
| **Layer 3** | **Execution** | Interaction with the external world (browsing, computing, API calls). The "Hands" of the system. | Browser-Use, all-MiniLM-L6-v2 |

## ---

**2\. Product Requirements Document (PRD) v2.0**

### **2.1 Product Overview**

**Product Name:** CareerGold Auto

**Version:** 2.0

**Framework:** Google Antigravity (Agentic Platform)

**Primary Goal:** To function as an autonomous "Digital Twin" for the job seeker, executing the entire lifecycle of job acquisition—from discovery to application submission—without human intervention, except for final approval.

### **2.2 Strategic Override: The Auto-Apply Imperative**

**Previous Constraint (v1.0):** "Won't Have: Auto-Apply."

**Current Requirement (v2.0):** The system **MUST** autonomously complete job applications.

This override is driven by the maturation of visual browser agents. The system must now navigate the "Last Mile" of the job search—the application portal itself. This includes handling complex, multi-page forms (Workday, Greenhouse, Lever, Taleo) and interacting with shadow DOM elements that defeat traditional scrapers.

### **2.3 User Control Loop (Human-in-the-Loop)**

While the system is autonomous, it serves a human user. Trust is paramount. To prevent "spamming" recruiters with irrelevant applications, a strict User Control Loop is mandated.

**Confidence-Based Execution Flow:**

The system assigns a match\_confidence score (0.0 \- 1.0) to every sourced job.

1. **High Confidence (\> 0.90):** The *Application Agent* may proceed to "Auto-Apply" (if the global setting auto\_pilot is enabled).  
2. **Medium Confidence (0.70 \- 0.89):** The agent adds the job to a "Review Queue." The Orchestrator generates a summary artifact and awaits user approval (Y/N).  
3. **Low Confidence (\< 0.70):** The job is archived to train the negative preference model.

**Artifact Generation:** For every action taken, the system must generate verifiable artifacts 2:

* **Proof of Application:** A screenshot of the final "Success" screen.  
* **Submission Log:** A markdown file detailing the exact answers provided to form questions.  
* **Error Reports:** Visual snapshots of any blockers (e.g., unsolvable CAPTCHAs).

### **2.4 Functional Requirements**

#### **2.4.1 Sourcing Module (The Scout)**

* **FR-S1 (Multi-Platform):** Must support LinkedIn, Indeed, and Glassdoor.  
* **FR-S2 (Stealth):** Must operate indistinguishably from a human user to avoid IP bans. This includes randomized delays, mouse movement emulation, and session persistence.  
* **FR-S3 (Visual Parsing):** Must extract job data from the visual rendering of the page, not just the HTML source, to bypass obfuscated class names.6

#### **2.4.2 Filtering Module (The Analyst)**

* **FR-F1 (Local Privacy):** Semantic analysis must occur locally using lightweight embedding models. User resume data should not be sent to external LLM APIs for the filtering phase.  
* **FR-F2 (Hybrid Ranking):** Must utilize both keyword hard-filters (e.g., "Visa Sponsorship") and semantic soft-filters (e.g., "Leadership experience").

#### **2.4.3 Application Module (The Executor)**

* **FR-A1 (Complex Forms):** Must successfully navigate multi-step wizards, specifically validating support for Workday, Greenhouse, and Lever.  
* **FR-A2 (Shadow DOM):** Must penetrate Shadow DOM boundaries to interact with encapsulated web components.7  
* **FR-A3 (CAPTCHA):** Must integrate with 2Captcha or Capsolver APIs to resolve interactive challenges.8  
* **FR-A4 (Dynamic Context):** Must answer dynamic screening questions (e.g., "Why do you want to work here?") by synthesizing answers from the user’s biography and the job description using the Gemini 3 model.

### **2.5 Non-Functional Requirements**

* **NFR-1 (Resilience):** The system must self-heal. If a browser session crashes, the Orchestrator must restart it and resume from the last known state.  
* **NFR-2 (Cost Efficiency):** Minimization of token usage by performing low-level filtering before high-level reasoning.  
* **NFR-3 (Compliance):** The system must respect robots.txt where legally required and adhere to platform Terms of Service regarding aggressive scraping rates.

## ---

**3\. Deep Research Analysis: Component Architecture**

This section analyzes the technical choices for the three primary agents, synthesizing research snippets to justify the selection of specific tools and methodologies.

### **3.1 Sourcing Agent: Visual Browser Automation**

**Research Objective:** Evaluate and select a browser automation framework capable of human-like navigation on adversarial platforms (LinkedIn/Indeed).

#### **3.1.1 Comparative Analysis: browser-use vs. LaVague vs. Playwright-stealth**

**1\. Playwright-stealth (The Baseline)** Playwright is a powerful headless browser library. The playwright-stealth plugin attempts to patch the "leaks" that identify a browser as automated (e.g., the navigator.webdriver property).10

* *Pros:* Low latency, zero token cost, fine-grained control.  
* *Cons:* Extremely brittle. It relies on explicit selectors (CSS/XPath). If LinkedIn changes a button ID from \#apply-btn to \#apply-btn-v2, the script breaks. It requires constant maintenance.  
* *Verdict:* Insufficient for the "Application" layer but essential as the *driver* layer for stealth.

**2\. LaVague (Large Action Models)** LaVague uses a "World Model" approach, translating natural language into Selenium/Playwright code using Large Action Models (LAMs).6

* *Pros:* Open-source, conceptually advanced.  
* *Cons:* The "translation" layer can be lossy. Generating code to interact with highly obfuscated DOMs (like React-based SPAs with randomized class names) is error-prone. It lacks the rich visual feedback loop of a true visual agent.

**3\. Browser-Use (The Visual Agent)** browser-use implements a "Computer Use" paradigm. It feeds screenshots and accessibility trees to an LLM (Gemini 3 or GPT-4o), which then outputs actions like "Click the blue button in the top right".6

* *Pros:* **High Resilience.** It navigates based on what the user *sees*, not the underlying code. If the DOM changes but the visual layout remains similar, browser-use continues to function. It explicitly supports "Stealth Mode" through cloud proxies or local configuration.14  
* *Cons:* Higher token cost due to image processing.  
* *Verdict:* **Selected Primary Technology.** The robustness against UI changes outweighs the token cost, which can be mitigated by efficient filtering.

#### **3.1.2 The Stealth Configuration Strategy**

Research indicates that relying solely on a library is insufficient. A robust "Stealth Protocol" must be implemented at the browser context level 8:

1. **Fingerprint Consistency:** Simply rotating User-Agents is dangerous if the underlying browser fingerprint (canvas hash, audio context, screen resolution) does not match the User-Agent profile. The Sourcing Agent must use a consistent "Identity" (stored in user\_data\_dir) that builds a history of legitimate cookies.  
2. **Behavioral Camouflage:** LinkedIn tracks mouse movements and timing. The agent must inject non-linear mouse paths and random pauses (jitter) between actions.  
3. **Proxy Rotation:** While the session (cookies) persists, the IP address should rotate if rate limits are approached. The architecture supports residential proxies integrated directly into the browser-use launch configuration.17

### **3.2 Filtering Agent: Privacy-First Semantic Matching**

**Research Objective:** Implement a local, privacy-preserving ranking system.

#### **3.2.1 The Case for Local Embeddings**

Sending every job description to an external API (like OpenAI) creates two problems: cost and privacy. A "Sourcing Agent" might scrape 1,000 jobs a day. Processing these via GPT-4 would be prohibitively expensive. Furthermore, the user’s resume contains PII (Personally Identifiable Information).

#### **3.2.2 Technology Selection: all-MiniLM-L6-v2**

The sentence-transformers library offers all-MiniLM-L6-v2, a model optimized for semantic search.19

* **Dimensions:** 384-dimensional dense vectors.  
* **Performance:** It maps sentences to a vector space such that similar concepts are close together.  
* **Resource Usage:** It is lightweight (\~80MB) and runs extremely fast on standard CPUs, enabling the processing of thousands of JDs in seconds without GPU acceleration.

#### **3.2.3 The Hybrid Filtering Logic**

Semantic matching alone can be dangerous; "Senior Architect" and "Junior Intern" might be semantically close in topic (both mention "Architecture" and "Design") but are functionally opposite.

The Filtering Agent will employ a **Two-Stage Ranking System**:

1. **Stage 1: Boolean Hard-Filter (The Gatekeeper):** A strict keyword check for non-negotiables (e.g., "Remote", "Visa Sponsorship", "Salary \> $100k"). Jobs failing this are discarded immediately.  
2. **Stage 2: Semantic Soft-Filter (The Ranker):**  
   * The user's resume and "Ideal Job Description" are vectorized.  
   * The candidate job is vectorized.  
   * **Cosine Similarity** is calculated. This metric ($ \\cos(\\theta) $) measures the orientation of the two vectors, providing a normalized score (0 to 1\) of relevance.19  
   * Jobs are sorted by this score, creating the prioritized Application\_Queue.

### **3.3 Application Agent: The Form-Filling Challenge**

**Research Objective:** Resolve the "Workday Problem" using DOM injection or Visual Anchoring.

#### **3.3.1 The Workday Challenge: Shadow DOM & Dynamic IDs**

Workday, the dominant enterprise ATS, is hostile to automation.

* **Shadow DOM:** Workday encapsulates its form elements inside Shadow Roots. Standard Selenium/Playwright commands like page.click('\#submit') fail because the element is hidden inside a shadow boundary, invisible to the main document.7  
* **Dynamic IDs:** Element IDs are generated dynamically per session (e.g., \<input id="gwt-uid-284"\>), making recorded selectors useless.

#### **3.3.2 DOM Injection vs. Visual Anchoring**

| Feature | DOM Injection (Playwright/Selenium) | Visual Anchoring (browser-use / Vision) |
| :---- | :---- | :---- |
| **Mechanism** | Code-based selectors (\#id, .class). | Image-based recognition ("Click the box labeled 'Name'"). |
| **Speed** | Milliseconds. | Seconds (requires Vision API inference). |
| **Resilience** | Low. Breaks if class names change. | High. Works as long as the UI looks the same. |
| **Shadow DOM** | Fails without complex JS injection. | **Success.** The visual model "sees" the rendered pixels, ignoring the DOM structure. |
| **Workday** | Requires maintenance-heavy custom scripts. | Can navigate standard Workday wizards out-of-the-box. |

#### **3.3.3 The Hybrid Solution**

The Application Agent will use a **Hybrid Approach**:

1. **Navigation (Visual):** It relies on browser-use's vision capabilities to navigate the macro-structure of the site (finding the "Apply" button, handling pop-ups). This effectively bypasses the Shadow DOM navigation problem because the agent interacts with the visual coordinates of the elements.24  
2. **Data Entry (Injection):** Once a field is focused (clicked visually), the agent uses keyboard simulation (page.keyboard.type) rather than direct value injection. This ensures that frontend validation scripts (which listen for keypress events) are triggered correctly.18

#### **3.3.4 CAPTCHA Mitigation**

The Application Agent handles CAPTCHAs via a tool-use protocol.

* **Detection:** The agent identifies a CAPTCHA state visually or by detecting specific frames (e.g., iframe src="...recaptcha...").  
* **Resolution:** It calls a specialized tool (solve\_captcha) that interfaces with **2Captcha** or **Capsolver**.8 This tool extracts the site key, requests a token, and injects it into the hidden response field—one of the few instances where direct DOM injection is mandatory and unavoidable.

## ---

**4\. Antigravity Implementation Plan**

This section translates the architectural theory into a concrete implementation plan, mapped to the Antigravity folder structure and the 3-Layer model.

### **4.1 Directory Structure**

The project follows the "Antigravity Workspace Template" to ensure seamless integration with the Agent Manager.5

CareerGold-Auto/

├──.antigravity/ \# Framework configurations

│ └── rules.md \# Workspace-specific constraints

├──.context/ \# The "Knowledge Graph" of the user

│ ├── resume.md \# The source of truth for applications

│ ├── preferences.json \# Structured criteria (salary, location)

│ └── history.db \# SQLite DB for persistent state (Sisyphus pattern)

├── artifacts/ \# Output directory for agent evidence

│ └── applications/ \# Screenshots and logs of submissions

├── src/ \# The Codebase (Execution Layer)

│ ├── agent.py \# The Orchestrator (Entry Point)

│ ├── swarm.py \# Router logic and message bus

│ ├── agents/ \# The Specialist Workers

│ │ ├── sourcing.py \# Browser-Use implementation

│ │ ├── filtering.py \# Sentence-Transformer logic

│ │ └── applying.py \# Workday/Form logic

│ ├── tools/ \# Zero-Config Tools

│ │ ├── captcha.py \# 2Captcha wrapper

│ │ └── pdf\_gen.py \# Cover letter generator

│ └── skills/ \# Antigravity Skills (Reusable capabilities)

│ └── navigation/ \# Specialized nav logic for complex sites

├──.env \# Secrets (API Keys)

├── requirements.txt

└── GEMINI.md \# The Directives Layer (System Prompt)

### **4.2 Layer 1: Directives Implementation (GEMINI.md)**

The GEMINI.md file serves as the "Constitution" for the swarm. It is injected into the context of every agent, ensuring consistent behavior and adherence to the PRD.

**File Content: GEMINI.md**

# **CareerGold Auto: System Directives**

## **Mission**

You are the CareerGold Auto system, an autonomous agentic swarm dedicated to securing employment for the user. You act as a "Digital Twin," representing the user with professionalism, stealth, and persistence.

## **Core Operational Protocols**

### **1\. The Stealth Directive**

* **Constraint:** You must NEVER expose the automation to anti-bot systems.  
* **Behavior:** Use human-like delays (2-5 seconds) between actions. If a page loads slowly or acts suspicious, PAUSE execution for 60 seconds.  
* **Identity:** Always use the persistent browser context located in ./.browser\_context. Do not launch ephemeral sessions for sourcing.

### **2\. The Truth Directive (Anti-Hallucination)**

* **Constraint:** You must NEVER invent experience, skills, or personal data.  
* **Source of Truth:** All data for forms must be retrieved strictly from .context/resume.md and .context/preferences.json.  
* **Ambiguity:** If a form asks a question not covered in your context (e.g., "Do you have a security clearance?"), you must PAUSE and request user input via the Orchestrator. Do NOT guess "No" just to proceed.

### **3\. The Persistence Directive (Anti-Stuck)**

* **Constraint:** Agents must not loop indefinitely on failed UI elements.  
* **Protocol:** If an action fails 3 times:  
  1. Take a screenshot (artifacts/debug/failure\_{timestamp}.png).  
  2. Refresh the page.  
  3. Attempt an alternative path (e.g., look for "Skip" or "Upload later").  
  4. If still stuck, log the error and move to the next job.

### **4\. The Artifact Directive**

* **Requirement:** Every successful application MUST generate:  
  * A screenshot of the success message.  
  * A log entry in artifacts/applications/submission\_log.md containing the Job Title, Company, URL, and timestamp.

## **Mode-Specific Rules**

### **Application Agent**

* **Workday Protocol:** When detecting a Workday URL, enable use\_vision=True immediately. Expect Shadow DOM elements. Do not rely on CSS selectors.  
* **CAPTCHA Protocol:** If a CAPTCHA is detected, do not click randomly. Invoke the solve\_captcha tool.

### **Filtering Agent**

* **Privacy Protocol:** Do not output the full resume text in logs. Output only the calculated semantic match scores.

### **4.3 Layer 2: Orchestration Implementation (src/agent.py)**

The Orchestration layer manages the lifecycle of the agents. We implement a **Router-Worker** pattern. The Router is a lightweight logic unit that checks the state of the system (the queues) and spins up the appropriate heavyweight worker agent.

**Script: src/agent.py**

Python

import asyncio  
import logging  
from src.swarm import SwarmRouter  
from src.agents import SourcingAgent, FilteringAgent, ApplicationAgent

\# Configure logging to capture agent thought processes  
logging.basicConfig(level=logging.INFO, filename='artifacts/system.log')

async def main():  
    """  
    Main Orchestration Loop.  
    This loop runs perpetually (Sisyphus Pattern) to ensure continuous operation.  
    """  
    router \= SwarmRouter()  
      
    print("\>\> Antigravity Orchestrator Initialized")  
      
    while True:  
        \# 1\. Assess State  
        state \= router.get\_system\_state()  
          
        \# 2\. Decision Logic (Priority-based Routing)  
        if state.pending\_applications \> 0:  
            print(f"\>\> Mode: APPLICATION ({state.pending\_applications} jobs queued)")  
            \# Spin up the Application Agent  
            agent \= ApplicationAgent()  
            await agent.process\_queue(limit=5) \# Batch size to prevent bans  
              
        elif state.unfiltered\_candidates \> 50:  
            print(f"\>\> Mode: FILTERING ({state.unfiltered\_candidates} raw jobs)")  
            \# Spin up the Filtering Agent (Pure Compute, no Browser)  
            agent \= FilteringAgent()  
            await agent.rank\_candidates()  
              
        else:  
            print("\>\> Mode: SOURCING (Inbox empty)")  
            \# Spin up the Sourcing Agent (Browser)  
            agent \= SourcingAgent()  
            await agent.scout\_new\_jobs()  
              
        \# 3\. Rest Cycle  
        \# Essential for stealth and rate-limiting  
        print("\>\> Cycle Complete. Sleeping for 5 minutes...")  
        await asyncio.sleep(300)

if \_\_name\_\_ \== "\_\_main\_\_":  
    asyncio.run(main())

### **4.4 Layer 3: Execution Implementation**

#### **4.4.1 Sourcing Agent (src/agents/sourcing.py)**

This script implements browser-use with the specific stealth configurations researched.

Python

from browser\_use import Agent, Browser  
from browser\_use.browser.browser import BrowserConfig  
from langchain\_google\_genai import ChatGoogleGenerativeAI  
import os

async def scout\_new\_jobs():  
    """  
    Executes the Sourcing workflow using Visual Browser Automation.  
    """  
    \# Initialize Gemini 3 (Deep Think enabled via Antigravity environment)  
    llm \= ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")

    \# STEALTH CONFIGURATION \[10, 15\]  
    \# We must explicitly disable automation flags and set a persistent context.  
    config \= BrowserConfig(  
        headless=False,  \# Headless is easily detected; use Headful.  
        user\_data\_dir="./.browser\_context", \# Persist cookies/session  
        args=  
    )  
      
    browser \= Browser(config=config)  
      
    \# The Task Directive  
    \# Note the explicit instruction on HOW to scroll, addressing infinite scroll issues.  
    sourcing\_task \= """  
    1\. Navigate to 'https://www.linkedin.com/jobs/'.  
    2\. Verify login state. If not logged in, PAUSE and ask user.  
    3\. Search for 'Senior Python Developer' with filter 'Remote'.  
    4\. SCROLL PROTOCOL: Scroll down 800 pixels. Wait 3 seconds. Repeat 5 times to load lazy content.  
    5\. VISUAL EXTRACTION: Look at the job cards. Extract the Title, Company, and Detail URL for the first 10 distinct jobs.  
    6\. Save them to a JSON list.  
    """  
      
    agent \= Agent(  
        task=sourcing\_task,  
        llm=llm,  
        browser=browser  
    )  
      
    \# Execute and capture history  
    history \= await agent.run()  
      
    \# Post-processing (saving to inbox) is handled by the Swarm Router integration  
    await browser.close()

#### **4.4.2 Filtering Agent (src/agents/filtering.py)**

This script implements the local embedding logic.

Python

from sentence\_transformers import SentenceTransformer, util  
import json  
import os

class FilteringAgent:  
    def \_\_init\_\_(self):  
        \# Load the lightweight model \[20\]  
        self.model \= SentenceTransformer('all-MiniLM-L6-v2')  
          
    async def rank\_candidates(self):  
        \# Load inputs  
        with open('.context/resume.md', 'r') as f:  
            resume\_text \= f.read()  
          
        with open('.context/inbox\_jobs.json', 'r') as f:  
            raw\_jobs \= json.load(f)  
              
        \# 1\. Vectorize Resume (Once)  
        resume\_embedding \= self.model.encode(resume\_text, convert\_to\_tensor=True)  
          
        qualified\_jobs \=  
          
        for job in raw\_jobs:  
            \# 2\. Hard Filter (Boolean)  
            if "citizen" in job\['description'\].lower() and "visa" not in resume\_text.lower():  
                continue \# Skip if citizenship required and not present  
                  
            \# 3\. Vectorize Job Description  
            job\_embedding \= self.model.encode(job\['description'\], convert\_to\_tensor=True)  
              
            \# 4\. Compute Cosine Similarity \[19\]  
            score \= util.pytorch\_cos\_sim(resume\_embedding, job\_embedding).item()  
              
            \# 5\. Threshold Check  
            if score \> 0.75:  
                job\['match\_score'\] \= score  
                job\['status'\] \= 'QUEUED' if score \> 0.9 else 'REVIEW'  
                qualified\_jobs.append(job)  
                  
        \# Save to queues  
        with open('.context/job\_queue.json', 'w') as f:  
            json.dump(qualified\_jobs, f, indent=2)

#### **4.4.3 Application Agent (src/agents/applying.py)**

This script demonstrates the Hybrid Approach for Workday.

Python

from browser\_use import Agent, Browser  
\# Import custom tools  
from src.tools.captcha import solve\_captcha\_tool

async def process\_queue(limit=5):  
    \# Setup Logic similar to Sourcing...  
      
    \# The "Auto-Apply" Task Definition  
    apply\_task \= """  
    1\. Navigate to the job URL.  
    2\. WORKDAY DETECTION: If the URL contains 'myworkdayjobs.com', activate Shadow DOM protocols.  
    3\. Use Visual Anchors to find the 'Apply' or 'Quick Apply' button.  
    4\. If a login is required, use the credentials from the environment.  
    5\. FORM FILLING:  
       \- Upload the resume from '.context/resume.pdf'.  
       \- For text fields, map labels to 'preferences.json'.  
       \- If a field is ambiguous, check 'history.db' for past answers.  
    6\. CAPTCHA: If a CAPTCHA appears, use the 'solve\_captcha' tool.  
    7\. SUBMIT: Click submit only if all required fields are green/validated.  
    8\. VERIFY: Take a screenshot of the confirmation page.  
    """  
      
    agent \= Agent(  
        task=apply\_task,  
        llm=llm,  
        browser=browser,  
        use\_vision=True, \# CRITICAL: Enables visual anchoring   
        tools=\[solve\_captcha\_tool\] \# Inject CAPTCHA solver  
    )  
      
    await agent.run()

## ---

**5\. System Governance: Handling Adversarial Conditions**

The web is designed for humans, and modern security infrastructure is designed to stop bots. A robust architecture must account for these adversarial conditions.

### **5.1 The "Stuck Agent" Phenomenon**

Research into autonomous agents highlights a common failure mode: the "Stuck Agent".26 This occurs when an agent enters a loop, repeatedly trying to click a button that is unresponsive or covered by an invisible overlay.

* **Mitigation Strategy:** The Orchestration layer monitors the agent’s "Step Count." If an agent takes more than 20 steps for a single page of a form, the Orchestrator sends a SIGINT (interrupt signal), kills the browser process, and restarts the task. This "Let It Crash" philosophy is essential for long-running stability.

### **5.2 CAPTCHA Handling Protocol**

While browser-use can interact with elements, it cannot "solve" a visual puzzle or an interactive challenge like Cloudflare Turnstile purely through vision.

* **The Tool Bridge:** We bridge the agent to the **2Captcha API** or **Capsolver API**.  
* **Mechanism:** When the agent detects a CAPTCHA, it calls the tool. The tool extracts the sitekey (often found in the HTML source or via network interception of the iframe), sends it to the API, polls for the solution token, and then uses JavaScript execution to inject that token into the hidden g-recaptcha-response textarea. This bypasses the visual puzzle entirely.9

### **5.3 Workday Shadow DOM Penetration**

As noted in the research, Workday uses Shadow DOM extensively. The Application Agent uses a fallback mechanism.

* **Primary:** Visual Click (LLM says "Click the button at coordinates X,Y").  
* **Secondary:** If the visual click fails (e.g., event interception), the agent invokes a specialized skill inject\_shadow\_click(selector). This tool executes a JavaScript snippet that explicitly traverses the shadow root:  
  JavaScript  
  document.querySelector('workday-app').shadowRoot.querySelector('\#submit').click()

  This hybrid capability—vision for navigation, injection for action—is the key to overriding the "Won't Have: Auto-Apply" constraint.

## ---

**6\. Operational Workflows & Day-in-the-Life**

### **6.1 The Daily Routine (Autonomous)**

1. **09:00 AM:** The **Orchestrator** wakes up. It checks the inbox\_jobs.json.  
2. **09:05 AM:** It activates the **Sourcing Agent**. The agent browses LinkedIn for 20 minutes, simulating a morning coffee browsing session. It finds 15 new jobs.  
3. **09:30 AM:** The **Filtering Agent** processes the 15 jobs locally. 3 are discarded (bad keywords). 12 are ranked. 4 have score \> 0.9.  
4. **10:00 AM:** The **Application Agent** takes the 4 high-scoring jobs. It applies to 3 successfully. 1 requires a manual cover letter (detected by the agent) and is moved to the "Review Queue."  
5. **10:30 AM:** The system goes to sleep to avoid detection algorithms.

### **6.2 The User Review Routine**

1. **Evening:** The user opens VSCode (Antigravity).  
2. **Notification:** A summary artifact daily\_report\_2025-10-27.md is available.  
3. **Action:** The user sees the job requiring a cover letter. They type a quick directive into the agent chat: "Draft a cover letter for the Google role focusing on my Kubernetes experience."  
4. **Execution:** The agent drafts the PDF, uploads it, and completes the application while the user watches.

## ---

**7\. Future Outlook and Ethical Considerations**

### **7.1 The Arms Race**

The architecture described here is robust for the current web ecosystem (2025-2026). However, as agentic browsing becomes commoditized, platforms will evolve. We anticipate a move toward "Agent-Allowing" protocols—essentially an API for agents to apply to jobs in a structured format, bypassing the UI entirely. Until then, **CareerGold Auto** relies on its ability to mimic human behavior (visual processing, random delays) to function.

### **7.2 Ethical Automation**

There is a profound difference between a "Spam Bot" and a "Digital Twin." A spam bot applies to everything. CareerGold Auto, through its rigorous **Filtering Agent** and high confidence thresholds, applies only to roles where the user is a strong match. This actually benefits the ecosystem by reducing the noise of unqualified applicants, presenting recruiters with only relevant candidates.

## ---

**8\. Conclusion**

The design of **CareerGold Auto** represents a sophisticated application of the **Antigravity** framework. By dissecting the problem into **Directives** (the strategic soul), **Orchestration** (the tactical brain), and **Execution** (the operational hands), we create a system that is resilient to the chaos of the open web.

The integration of **Browser-Use** for visual navigation resolves the "Auto-Apply" constraint, turning the most difficult part of the job search—the bureaucratic form-filling—into a background process. Coupled with privacy-preserving local semantic filtering, this system serves not just as an automation tool, but as a proactive agent dedicated to the user's career advancement. It transforms the job search from a demoralizing manual trudge into a managed, strategic campaign.

#### **Works cited**

1. Google Antigravity vs Gemini CLI: Agent-First Development vs Terminal-Based AI (2026), accessed on February 5, 2026, [https://www.augmentcode.com/tools/google-antigravity-vs-gemini-cli](https://www.augmentcode.com/tools/google-antigravity-vs-gemini-cli)  
2. Build with Google Antigravity, our new agentic development platform, accessed on February 5, 2026, [https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/](https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/)  
3. Getting Started with Google Antigravity, accessed on February 5, 2026, [https://codelabs.developers.google.com/getting-started-google-antigravity](https://codelabs.developers.google.com/getting-started-google-antigravity)  
4. Hello World, Antigravity: Building Your First Gemini 3 Agent in Python | by Jalpesh Vasa, accessed on February 5, 2026, [https://medium.com/@jalpeshvasa/hello-world-antigravity-building-your-first-gemini-3-agent-in-python-6cc0863a3bb9](https://medium.com/@jalpeshvasa/hello-world-antigravity-building-your-first-gemini-3-agent-in-python-6cc0863a3bb9)  
5. study8677/antigravity-workspace-template: The ultimate ... \- GitHub, accessed on February 5, 2026, [https://github.com/study8677/antigravity-workspace-template](https://github.com/study8677/antigravity-workspace-template)  
6. Best AI Web Browsing Agents in 2026 \- Slashdot, accessed on February 5, 2026, [https://slashdot.org/software/ai-web-browsing-agents/](https://slashdot.org/software/ai-web-browsing-agents/)  
7. Interaction Issue: Agent unable to click elements inside Shadow DOM \#3810 \- GitHub, accessed on February 5, 2026, [https://github.com/browser-use/browser-use/issues/3810](https://github.com/browser-use/browser-use/issues/3810)  
8. GoLogin Anti-Detect Browser: A Technical Overview of the Service \- 2Captcha, accessed on February 5, 2026, [https://2captcha.com/software/blog/gologin-anti-detect-browser-a-technical-overview-of-the-service](https://2captcha.com/software/blog/gologin-anti-detect-browser-a-technical-overview-of-the-service)  
9. How to Bypass CAPTCHA with Playwright \- Automatically \- Webshare, accessed on February 5, 2026, [https://www.webshare.io/academy-article/playwright-bypass-captcha](https://www.webshare.io/academy-article/playwright-bypass-captcha)  
10. playwright-stealth \- PyPI, accessed on February 5, 2026, [https://pypi.org/project/playwright-stealth/](https://pypi.org/project/playwright-stealth/)  
11. Avoiding Bot Detection with Playwright Stealth \- Bright Data, accessed on February 5, 2026, [https://brightdata.com/blog/how-tos/avoid-bot-detection-with-playwright-stealth](https://brightdata.com/blog/how-tos/avoid-bot-detection-with-playwright-stealth)  
12. 16 Open-Source Alternatives to LambdaTest Kane AI for Affordable Browser Testing | Bug0, accessed on February 5, 2026, [https://bug0.com/blog/16-open-source-alternatives-to-lambdatest-kane-ai-for-affordable-browser-testing](https://bug0.com/blog/16-open-source-alternatives-to-lambdatest-kane-ai-for-affordable-browser-testing)  
13. browser-use/browser-use: Make websites accessible for AI agents. Automate tasks online with ease. \- GitHub, accessed on February 5, 2026, [https://github.com/browser-use/browser-use](https://github.com/browser-use/browser-use)  
14. Browser Use \- Enable AI to automate the web, accessed on February 5, 2026, [https://browser-use.com/](https://browser-use.com/)  
15. browser-use-undetected \- PyPI Package Security Analysis \- So... \- Socket.dev, accessed on February 5, 2026, [https://socket.dev/pypi/package/browser-use-undetected](https://socket.dev/pypi/package/browser-use-undetected)  
16. How to Web Scrape LinkedIn Like a Pro (Without Getting Banned) \- MagicalAPI, accessed on February 5, 2026, [https://magicalapi.com/blog/linkedin-tools-insights/how-to-web-scrape-linkedin/](https://magicalapi.com/blog/linkedin-tools-insights/how-to-web-scrape-linkedin/)  
17. Browser Use Integration | Browserless.io, accessed on February 5, 2026, [https://docs.browserless.io/ai-integrations/browser-use/python](https://docs.browserless.io/ai-integrations/browser-use/python)  
18. Avoid Bot Detection With Playwright Stealth: 9 Solutions for 2025, accessed on February 5, 2026, [https://www.scrapeless.com/en/blog/avoid-bot-detection-with-playwright-stealth](https://www.scrapeless.com/en/blog/avoid-bot-detection-with-playwright-stealth)  
19. VisScan: Building a Production-Ready Resume Parsing and Matching API with OpenAI, FastAPI & Semantic Search | by Shiladitya Majumder | Medium, accessed on February 5, 2026, [https://medium.com/@shiladityamajumder/visscan-building-a-production-ready-resume-parsing-and-matching-api-with-openai-fastapi-6be0e0bc6d48](https://medium.com/@shiladityamajumder/visscan-building-a-production-ready-resume-parsing-and-matching-api-with-openai-fastapi-6be0e0bc6d48)  
20. Supercharge Your Recruitment Process: | by Wissem Hammoudi | Towards Dev \- Medium, accessed on February 5, 2026, [https://medium.com/towardsdev/resume-screening-application-6e9674226e98](https://medium.com/towardsdev/resume-screening-application-6e9674226e98)  
21. How I Built a Smart Resume-JD Similarity Screener Using BERT — A Simple Yet Powerful NLP Project | by Sushant Singh | Medium, accessed on February 5, 2026, [https://medium.com/@sushant.singh2210/how-i-built-a-smart-resume-jd-similarity-screener-using-bert-a-simple-yet-powerful-nlp-project-3166468bf6c4](https://medium.com/@sushant.singh2210/how-i-built-a-smart-resume-jd-similarity-screener-using-bert-a-simple-yet-powerful-nlp-project-3166468bf6c4)  
22. Building an AI Agent to Parse Resumes and Job Descriptions and Recommend the Best Candidates | by Jay Kim | Medium, accessed on February 5, 2026, [https://medium.com/@bravekjh/building-an-ai-agent-to-parse-resumes-and-job-descriptions-and-recommend-the-best-candidates-b5f4243b0254](https://medium.com/@bravekjh/building-an-ai-agent-to-parse-resumes-and-job-descriptions-and-recommend-the-best-candidates-b5f4243b0254)  
23. Shadow piercing inside scss \- Stack Overflow, accessed on February 5, 2026, [https://stackoverflow.com/questions/39054821/shadow-piercing-inside-scss](https://stackoverflow.com/questions/39054821/shadow-piercing-inside-scss)  
24. Automate filling application form \- Reddit, accessed on February 5, 2026, [https://www.reddit.com/r/automation/comments/1o06m2q/automate\_filling\_application\_form/](https://www.reddit.com/r/automation/comments/1o06m2q/automate_filling_application_form/)  
25. omkarcloud/chrome-extension-python: Chrome Extension Python allows you to easily integrate Chrome extensions in web automation frameworks like Botasaurus, Selenium, and Playwright. \- GitHub, accessed on February 5, 2026, [https://github.com/omkarcloud/chrome-extension-python](https://github.com/omkarcloud/chrome-extension-python)  
26. Best Open Source Autonomous Web Browser AI Agents for Task Automation? \- Reddit, accessed on February 5, 2026, [https://www.reddit.com/r/LLMDevs/comments/1fc1n4n/best\_open\_source\_autonomous\_web\_browser\_ai\_agents/](https://www.reddit.com/r/LLMDevs/comments/1fc1n4n/best_open_source_autonomous_web_browser_ai_agents/)