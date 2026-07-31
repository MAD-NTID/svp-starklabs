# Application Security Engineer

A security alert has been triggered at StarkLab R&D after an unauthorized user gained access to the intern portal using a hidden testing credential left behind in the production code.

The Application Security Engineer is tasked with investigating the security incident, identifying the vulnerability, removing the security risk, and improving the application's security practices.

---

# Security Incident Investigation

## Security Report #5821

**Project:**  
StarkLab R&D Intern Portal

**Priority:**  
Critical

**Reported by:**  
Security Operations Center (SOC)

**Problem:**  
An unauthorized user successfully accessed the intern portal using credentials that were not assigned to any active user account.

**Affected Version:**  
v10.8.7

**Last Known Secure Version:**  
v10.8.6

---

## Incident Details

The SOC detected suspicious login activity from an unknown account.

Initial investigation found:

- The attacker successfully authenticated into the portal.
- The account was not registered in the intern database.
- The credentials used were discovered inside the application source code.
- The credentials appeared to have been created for testing purposes.

The security team suspects that a StarkLab intern accidentally left testing credentials in the production application during development.

---

# Test Account

Use the provided security testing environment.
