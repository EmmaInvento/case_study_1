# Self-assessment questionnaire on company security measures

Select only one answer per question, referring to the company’s current situation

**Exercise form:** shortened and adapted from a real assessment questionnaire; these ten questions focus on security practices. **Case profile:** essential entity by scenario assumption.

## Section 1. Security organization

### 1. Which situation describes the roles and responsibilities for cybersecurity, including coordination of the function?

ID: `ciso_appointment_status`

- `A` — The security organization is approved and communicated internally, with defined roles and responsibilities and an up-to-date list of the people assigned, with or without the CISO title.
- `B` — Some people perform security tasks, but the organization, responsibilities, approval, communication or list of assigned people are absent or incomplete.
- `C` — No person performs or coordinates cybersecurity tasks
- `D` — Information not available.

## Section 2. External services and suppliers

### 2. Which situation describes the supplier-provided IT services used by the company, including cloud services and external platforms?

ID: `cloud_and_external_service_usage_level`

- `A` — They are used and all are listed in an up-to-date inventory identifying the service and supplier.
- `B` — They are used, but the inventory is missing, incomplete or not up to date.
- `C` — An up-to-date survey identifies no supplier-provided IT services, including cloud services.
- `D` — Information not available.

### 3. For suppliers that may affect the security of systems and networks (through access, data or continuity), which situation describes the inventory and risk assessment?

ID: `critical_supplier_count_range`

- `A` — Such suppliers are present: they are listed in an up-to-date inventory with a contact person and type of supply, and the risk associated with their supplies is assessed and documented.
- `B` — Such suppliers are present, but the inventory is absent, incomplete or not up to date, or the risk assessment of their supplies is absent or incomplete.
- `C` — An up-to-date survey has identified no suppliers with a possible impact on the security of systems and networks.
- `D` — Information not available.

## Section 3. Access and authentication

### 4. For remote access to company systems and networks, which situation describes the list of accessible systems and their respective access methods?

ID: `remote_access_status`

- `A` — Remote access is permitted and an up-to-date list includes all accessible systems and, for each one, the access method.
- `B` — Remote access is permitted, but the list is missing, incomplete or not up to date.
- `C` — An up-to-date survey confirms that no company system or network is remotely accessible.
- `D` — Information not available.

### 5. If remote access to company information systems exists (for example servers, applications, cloud services and network devices), which situation describes the methods used, the permitted activities and the security measures applied?

ID: `remote_access_alternative_modes`

- `A` — Only the VPN is used; for each accessible system, permitted activities are defined and documented and security measures for access are applied.
- `B` — Methods other than the VPN are used, including alongside the VPN; for each accessible system, permitted activities are defined and documented and security measures for access are applied.
- `C` — At least one remote access method is used, but permitted activities or security measures are not defined, documented or applied for all accessible systems.
- `D` — Information not available.

**Shown only if** `remote_access_status` is `A` or `B`.

### 6. Has the company implemented multi-factor authentication (MFA) systems?

ID: `mfa_implementation_status`

- `1` — MFA implemented on all critical systems (email, VPN, cloud, business management system)
- `2` — MFA implemented only on some systems
- `3` — MFA not implemented but being planned
- `4` — MFA not implemented and not planned

## Section 4. Data protection

### 7. Does the company allow the use of removable devices?

ID: `removable_media_policy_status`

- `1` — The company allows unrestricted use of removable devices.
- `2` — The company allows only company-owned or authorized removable devices.
- `3` — The company does not allow the use of removable devices.

Note: for example, USB flash drives, external hard drives, or other removable media.

### 8. Does the company back up critical data?

ID: `critical_data_backup_status`

- `1` — Frequent automatic backups (daily or more often), with an offsite or cloud copy, tested periodically
- `2` — Automatic backups without an offsite copy, tested periodically
- `3` — Manual or irregular backups
- `4` — No structured backup system

## Section 5. Incident management and improvement

### 9. Which situation describes the contact details for reporting incidents and the roles responsible for communications with CSIRT Italia?

ID: `security_contact_email`

- `A` — Actively staffed contact channels are available; a point of contact and a deputy, a CSIRT liaison and any deputies are identified within the organization; the incident plan includes contact details and communication methods.
- `B` — Contact details or designated people are identified, but at least one of the following is missing: the definition of the responsible roles, contact information in the plan or communication methods.
- `C` — Neither contact details nor people responsible for incident communications are identified.
- `D` — Information not available.

### 10. Over the last two years, which situation describes significant incidents and the review of the risk assessment and incident management plan?

ID: `recent_security_incident_status`

- `A` — No significant incident; the risk assessment and incident management plan have been reviewed within the planned timeframes.
- `B` — At least one significant incident; both have been reviewed within the planned timeframes and after each event, incorporating lessons learned into the plan where relevant.
- `C` — At least one of the planned reviews, periodic or following a significant incident, has not been completed, including the incorporation of lessons learned when required.
- `D` — Information not available.
