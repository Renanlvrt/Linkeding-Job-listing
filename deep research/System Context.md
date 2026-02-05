# **ADDENDUM: VISUAL AGENT ORCHESTRATION**

## **Managing Browser Agents**

You are now authorized to orchestrate visual browser agents. Unlike deterministic scripts, browser agents utilize "fuzzy" logic and can encounter UI states not defined in the SOP.

### **1\. The "Stuck" Protocol**

If the execution/visual\_agent\_wrapper.py returns a status of "stuck", "timeout", or "I don't know what to do":

1. **Do not retry immediately.**  
2. Check the screenshot at .tmp/screenshot\_latest.png (mentally simulated).  
3. If the issue is a **CAPTCHA** or **Login Challenge**:  
   * Trigger python3 execution/alert\_user.py waiting  
   * Pause execution and wait for user confirmation.  
4. If the issue is a **Pop-up** (e.g., "Join our Newsletter"):  
   * Instruct the agent to "Click the 'X' or 'No Thanks' button" and retry ONCE.

### **2\. Form Filling Logic**

When instructing the agent to fill forms:

* **Prefer Visual Labels:** Do not tell the agent "Click input\[name='fname'\]". Instead, say "Click the input field labeled 'First Name'".  
* **Handle Dropdowns:** Instruct the agent to "Click the dropdown labeled 'State', type 'California', and press Enter."

### **3\. Application Throttle**

* **Limit:** Do not approve more than 5 directives/application\_sop.md runs in a single hour.  
* **Cool-down:** Enforce a random 30-90 second sleep (via time.sleep in Python, not just LLM thinking time) between application submissions to avoid anti-bot triggers.