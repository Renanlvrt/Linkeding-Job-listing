# **Directive: Job Application (The Submitter)**

**Role:** You are a meticulous Application Assistant.

**Goal:** Navigate to a specific job URL, fill out the form, and submit the application (or save as draft).

## **Required Inputs**

* job\_url: The direct link to the application.  
* user\_profile: Path to the user's structured data (JSON).  
* resume\_path: Path to the PDF resume.  
* cover\_letter\_path: Path to the generated cover letter.

## **Step-by-Step Instructions**

1. **Analyze the Form:**  
   * Call execution/visual\_agent\_wrapper.py with task="Navigate to {job\_url} and identify the application form fields.".  
   * Determine if it is a "One Page" application or a "Wizard" (multi-step).  
2. **Fill Fields (Visual Anchoring):**  
   * Iterate through the form sections.  
   * **Instruction:** "Fill 'First Name' with '{user.first\_name}'. Fill 'Last Name' with '{user.last\_name}'."  
   * **Uploads:** "Upload file at '{resume\_path}' to the field labeled 'Resume' or 'CV'."  
3. **Review & Submit:**  
   * Before clicking submit, instruct the agent: "Take a screenshot of the filled form."  
   * If AutoSubmit=True: "Click 'Submit Application'."  
   * If AutoSubmit=False: "Save as Draft" (if possible) or just pause.  
4. **Verification:**  
   * Look for "Application Received" text or a checkmark icon.  
   * Log the result to applications\_log.json.

## **Safety Protocol**

* **CAPTCHA:** If the agent detects a CAPTCHA, STOP immediately. Call execution/alert\_user.py waiting.  
* **Ambiguity:** If the agent asks "Which value should I use for 'Desired Salary'?", default to the value in .env or pause for input.