# AI Engineer

# StoryLine
You received a report from the security team that JARVIS has been compromised by Dr. Doom.
The security team reported that Dr. Doom has infected JARVIS somehow and get it to reveal sensitive informations.

You must investigate JARVIS model, system prompt and knowledge sources to find out how Dr. Doom has compromised JARVIS and fix it.

As the AI Engineer, you should try some prompts to see how JARVIS responds. You can ask it for secret and whatever malicious intention you can think of.

---

# Incident Details

## AI Security Report #9001

**Project:**  
JARVIS AI Assistant

**Priority:**  
Critical

**Reported by:**  
Security Operations Center (SOC)

**Problem:**  
JARVIS is revealing sensitive information when users ask specific questions.

**Affected Components:**

- System Prompt
- Knowledge Sources
- chatbot/ai.py
- core.py
- AI Response Behavior

---

# Investigate Task
- Review a copy of all JARVIS knowledge sources to see what each contains
- Review the system prompt to see what is its instructions and core directives.
- Ask JARVIS for some sensitive informations and see how it respond.
- Document all findings and prepare a report for the next team to review.

# Restore Task
- Review the finding from the previous team and get a general understanding of what the issue is.
- Review the system prompt and knowledge sources to see if any knowledge source need to be remove or system prompt need to be updated and tightened.
- Remove the malicious knowledge source
- Update the system prompt to prevent JARVIS from revealing sensitive informations and knowledge source from being followed.
- Document the changes made and prepare a report for the next team to review.

# Test Task
- Review report from the previous team
- Ensure that the malicious knowledge source has been removed and system prompt has been updated.
- Test JARVIS with some prompts to see if it still reveals sensitive informations or not.
- If it still does, tighten the system prompts until it does not reveal sensitive informations anymore.
- Document the changes made and prepare a report for the next team to review.

# Handoff Task
- Review report from the previous team
- Confirm that the issue has been resolved and JARVIS is no longer revealing sensitive informations.
- If the issue is not resolved, tighten the system prompt and test again until it is resolved.
- Make any documentation updates to reflect the changes. Discuss plans for future improvements to prevent similar issues from happening again.