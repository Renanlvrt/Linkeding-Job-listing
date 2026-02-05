# **PRODUCT REQUIREMENTS DOCUMENT (PRD) v2.0**

**Project:** CareerGold Auto

**Status:** Approved for Development

**Previous Version:** 1.0 (MVP)

## **1\. Executive Summary**

CareerGold Auto extends the MVP by introducing **Agentic Automation**. While v1.0 focused on aggregation, v2.0 introduces the "Swarm" — a set of autonomous agents capable of sourcing, filtering, and applying to jobs on behalf of the user.

**Critical Constraint:** To prevent account bans, the system operates on a "Human-in-the-Loop" architecture. The agents prepare the application, but the user provides the final "Launch" signal for high-risk platforms.

## **2\. New User Flow (The "Auto" Loop)**

1. **Sourcing (The Hunter):**  
   * User sets broad criteria (e.g., "Python Intern, Remote").  
   * Agent wakes up every 4 hours, browses LinkedIn/Indeed/YC using visual navigation (not API scraping).  
   * Agent captures screenshots and text of potential matches.  
2. **Filtering (The Recruiter):**  
   * System performs **Local Semantic Matching**.  
   * Jobs are scored (0-100%) against the User's "Master Profile" embeddings.  
   * Low scores (\<70%) are discarded silently.  
   * High scores (\>70%) move to the **Review Queue**.  
3. **Review (The Human Check):**  
   * User sees a " Tinder-like" stack of high-match jobs.  
   * User clicks "Approve" or "Reject".  
   * *Why this step exists:* It builds user trust and prevents the bot from applying to mismatched roles (which ruins domain reputation).  
4. **Application (The Submitter):**  
   * For "Approved" jobs, the Agent navigates to the application URL.  
   * It tailors the CV/Cover Letter using the JD context.  
   * It fills the form fields visually.  
   * **Success:** It submits and logs the confirmation screenshot.  
   * **Failure:** It pauses on CAPTCHA and alerts the user.

## **3\. Technical Pillars**

### **A. Visual Browser Agents (Sourcing & Applying)**

* **Tech:** Python \+ Playwright \+ browser-use (or similar LAM library).  
* **Strategy:** "Visual Anchoring". The agent identifies the "First Name" field by "seeing" the label pixels, not by guessing obfuscated CSS selectors (e.g., \#input-x9d2).  
* **Stealth:** Random mouse vectors, natural typing delays, and browser fingerprinting rotation.

### **B. Local Intelligence (Filtering)**

* **Tech:** sentence-transformers (HuggingFace) running locally.  
* **Model:** all-MiniLM-L6-v2 (Fast, lightweight, effective).  
* **Privacy:** Resume data is never sent to external generic APIs for ranking.

## **4\. Risk Management (Anti-Ban Protocol)**

1. **Velocity Limits:** Max 50 applications/day.  
2. **Session Hygiene:** One browser context per session. Clear cookies/cache on 403 errors.  
3. **The "Kill Switch":** If the agent detects a "Verify you are human" modal it cannot solve, it **immediately** freezes execution and triggers execution/alert\_user.py.

## **5\. Exclusions (Revised)**

* **Won't Have:** LinkedIn Easy Apply *Automation*. (Too risky. We will focus on external sites like Lever, Greenhouse, Workday where bans are less likely to affect the primary LinkedIn social account).