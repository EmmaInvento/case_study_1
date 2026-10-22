# Aurora Grid Inc. — company dossier

**Case as of:** 9 October 2026. All company details and records below are fictional.

For this teaching exercise, Aurora Grid Inc. is assumed to be an essential entity under the applicable Italian NIS2/ACN scenario. The fictional Inc. suffix does not determine jurisdiction or legal classification.

Aurora selected one answer for each question in the [exercise questionnaire](security-questionnaire.md). Its selected answers and the company records below are inputs to the assessment. Read the records together; a narrow excerpt does not describe every system or control.

## Selected questionnaire answers

Question 5 is shown because Aurora selected **B** for question 4.

| # | Area | Question | Selected answer |
| ---: | --- | --- | --- |
| 1 | Security organization | Which situation describes the roles and responsibilities for cybersecurity, including coordination of the function? | **B** — Some people perform security tasks, but the organization, responsibilities, approval, communication or list of assigned people are absent or incomplete. |
| 2 | External services and suppliers | Which situation describes the supplier-provided IT services used by the company, including cloud services and external platforms? | **A** — They are used and all are listed in an up-to-date inventory identifying the service and supplier. |
| 3 | External services and suppliers | For suppliers that may affect the security of systems and networks (through access, data or continuity), which situation describes the inventory and risk assessment? | **B** — Such suppliers are present, but the inventory is absent, incomplete or not up to date, or the risk assessment of their supplies is absent or incomplete. |
| 4 | Access and authentication | For remote access to company systems and networks, which situation describes the list of accessible systems and their respective access methods? | **B** — Remote access is permitted, but the list is missing, incomplete or not up to date. |
| 5 | Access and authentication | If remote access to company information systems exists (for example servers, applications, cloud services and network devices), which situation describes the methods used, the permitted activities and the security measures applied? | **C** — At least one remote access method is used, but permitted activities or security measures are not defined, documented or applied for all accessible systems. |
| 6 | Access and authentication | Has the company implemented multi-factor authentication (MFA) systems? | **2** — MFA implemented only on some systems |
| 7 | Data protection | Does the company allow the use of removable devices? | **2** — The company allows only company-owned or authorized removable devices. |
| 8 | Data protection | Does the company back up critical data? | **1** — Frequent automatic backups (daily or more often), with an offsite or cloud copy, tested periodically |
| 9 | Incident management and improvement | Which situation describes the contact details for reporting incidents and the roles responsible for communications with CSIRT Italia? | **C** — Neither contact details nor people responsible for incident communications are identified. |
| 10 | Incident management and improvement | Over the last two years, which situation describes significant incidents and the review of the risk assessment and incident management plan? | **B** — At least one significant incident; both have been reviewed within the planned timeframes and after each event, incorporating lessons learned into the plan where relevant. |

## Company records

Each ID names one dated record in this fictional client case. Use the ID and date when citing it. Records about the same subject can have different scopes; read them together before drawing a conclusion.

### AR-01 · 2026-06-15

risk assessment approved on 2026-06-15: the complete list of information and network systems relevant to this case comprises the operations management system and the administrative cloud environment, including its administrative console and managed application data. The document requires MFA for every enabled account on both systems and a monthly restoration check of the usability of the data backups actually produced for both.

### AR-02 · 2026-10-04

excerpt from the continuity plan and backup log, checked on 2026-10-04: since 2026-06-20, the operations management system's data and the administrative cloud environment's application data have been backed up daily to a cloud/offsite repository; the plan calls for a monthly test restoration. The technical inventory from the same day explicitly confirms that neither system has configuration backups and that no offline backup copies exist: the only available copies are in the cloud/offsite repository.

### AR-03 · 2026-10-04

restoration test log: on 2026-07-04, 2026-08-04, 2026-09-04 and 2026-10-04, operators restored both the operations management system's data and the administrative cloud environment's application data in isolated environments from the preceding day's daily data backups. Each test record attests that the restored data could be opened and were intact and usable, with a successful result validated by the operations manager. The tests concern the data backups actually produced; they do not attest to configuration backups or offline copies.

### AR-04 · 2026-10-05

export of the cloud administrative console's authentication configuration as of 2026-10-05: two administrative accounts that are still active have MFA disabled. The console belongs to the administrative cloud environment classified as relevant in AR-01; the export records no approved derogations or exceptions for these accounts.

### AR-05 · 2026-10-08

Some IT staff perform security tasks informally. There is no defined cybersecurity organization approved by the management and governing bodies and communicated internally, and there is no up-to-date list of assigned people. Neither a point of contact and deputy nor a CSIRT liaison and deputies have been identified, and there are no staffed channels for reporting incidents. An incident plan exists and documents phases, notification and reporting, but it has no contact details or methods for internal and external communication. The address security@rete-aurora.invalid is an unstaffed, non-operational placeholder, not an incident-reporting channel.

### AR-06 · 2026-10-08

excerpt dated 2026-10-08 from inventory and risk-assessment records: the list of relevant information and network systems referred to in AR-01 is kept up to date and includes the operations management system and the administrative cloud environment, including its console. The up-to-date inventory of supplier-provided IT services includes every service used, including cloud services, and identifies each service and supplier. The up-to-date inventory of supplies with a potential security impact covers every such supplier in this case: the cloud provider and two maintenance suppliers with system access, with a contact person and type of supply for each. The documented assessment of system risks identifies, analyzes and weighs those risks, but assesses the supplies only by access level and access to intellectual property/data; it omits the impact of a severe disruption, recovery times and costs, and supplier roles and responsibilities.

### AR-07 · 2026-10-08

Remote access is permitted through a company jump host and an old maintenance RDP service reachable from the Internet; both paths reach the operations management host, a relevant system. No dedicated list of remotely accessible systems and their access methods is maintained, separately from the general list of relevant systems. For the jump host, permitted activities are documented and MFA and access restrictions are applied; for the old RDP service, permitted activities are undocumented and both MFA and restrictions on connection origin are absent. The assessment of authentication methods considers account privileges, system criticality and permitted operations and requires MFA for all accounts on the two relevant systems. MFA is active for ordinary application accounts on the operations management system, for VPN and for email, but not for the old RDP maintenance account or two active administrative accounts on the cloud console; there are no documented derogations (see AR-04 for the console).

### AR-08 · 2026-10-08

Only company-owned or authorized removable media are allowed. Relevant data held on laptops, smartphones and authorized USB media are encrypted with protocols and algorithms considered secure and state of the art in the risk assessment; one maintenance tablet containing relevant operational data is unencrypted, with no documented, reasoned legal or technical exception. Autorun is not disabled on permitted removable media, and no antimalware scan is performed before use. There are no reasoned, documented legal or technical exceptions for leaving autorun enabled or omitting the pre-use scan.

### AR-09 · 2026-10-08

The malware-related outage of the operations management system is the only significant incident in the last two years: the closure record of 2026-10-06 expressly classifies it as significant. The risk assessment and incident plan both met their planned annual review schedule, with reviews on 2026-06-15 and 2026-06-16 respectively; after the incident on 2026-08-18, they were reviewed on 2026-09-02 and 2026-09-04 respectively. Relevant lessons learned were incorporated into the plan, although the contact and communication gaps in AR-05 remain. No other significant incidents or further organizational or threat-exposure changes requiring a review occurred during the period.

### AR-10 · 2026-10-09

**Source document:** PO-26 policy, RM-26 risk-management plan and treatment tracker; inspected on 2026-10-09

PO-26 is Aurora Grid's applicable documented cybersecurity risk-management policy under GV.PO-01. It was formally adopted and approved by the governing and management bodies on 2026-06-10 and communicated to the competent organizational units. RM-26 implements PO-26's risk-management rules and has applied to both relevant systems since 2026-06-15. RM-26 was reviewed and kept current on 2026-09-02 after the significant incident. The documented plan assigns a risk-process owner and defines identification, analysis, evaluation, treatment and monitoring stages, recurring monthly checks and an escalation route in accordance with PO-26. The treatment tracker contains dated implementation and monitoring entries for recorded system and supplier-dependency risks, including assigned owners and follow-up decisions. The 2026-10-09 inspection confirms that the plan and its cycle are operating. This evidence concerns this risk-management policy and plan, not other GV.PO policy areas. It does not assert that every scenario in an individual risk assessment was captured, nor does approval or communication of PO-26 establish the cybersecurity organization or incident-contact structure absent in AR-05.

### AR-11 · 2026-10-09

**Source document:** security-impacting-supplier inventory extract and contact-field verification; inspected on 2026-10-09

The current inventory includes exactly the cloud provider and the two maintenance suppliers that can affect system security. For each of these three supplies, the maintained record identifies the individual supply contact person, that person's current email address and direct telephone number, and the type of supply. A inventory-owner check on 2026-10-09 verified the contact fields and the inventory's currency. These are supplier relationship contacts; they are not Aurora Grid's channels for reporting cybersecurity incidents and do not designate its CSIRT Italia liaison.

### AR-12 · 2026-10-09

**Source document:** 2026-09-02 system-risk assessment and dependency-scenario register, spot-checked on 2026-10-09

The documented assessment identifies, analyses and evaluates recorded risks to both relevant systems. Its dependency-scenario register includes the cloud provider's access and data risks, but a prolonged outage of the maintenance supplier's remote maintenance service, on which recovery of the operations management system depends, has no scenario identifier, likelihood or impact analysis, or risk evaluation. This is a specific omission in the general network-and-information-system risk assessment, independent of the separate supply-assessment checklist. That separate assessment still covers only supplier access level and access to intellectual property or data, and still lacks the severe-disruption, recovery-time-and-cost, and supplier-governance fields described in AR-06. The complete risk-management process documented in AR-10 does not cure these omissions in its execution.

### AR-13 · 2026-10-09

**Source document:** AS-26 internal asset, service and application register; approved on 2026-10-07 and inspected on 2026-10-09

AS-26 is maintained as the complete current inventory of Aurora Grid's network and information systems, the services composing them and all associated software applications, with an internal approval record for every entry. It includes both relevant systems from AR-01 and their enabling services, commercial cloud-console and host software, open-source network tooling, the custom operations application and the API-accessible maintenance application. The internal operations owner approved the entries on 2026-10-07 and confirmed their currency on 2026-10-09. AS-26 lists system and application identity but contains neither an approved inventory of external network flows nor, for each remotely accessible target, its corresponding access method; see AR-17 and AR-18.

### AR-14 · 2026-10-09

**Source document:** BC-26 business-continuity plan, implementation record and drill log; inspected on 2026-10-09

BC-26 was approved and implemented on 2026-06-16, reviewed after the 2026-08-18 significant incident on 2026-09-04, and remains current for the operations management system and administrative cloud environment. It documents continuity objectives and needs, scope, operational roles and alternates, main internal control-room contacts and channels and the already-inventoried cloud provider's operational restoration contact and channel, conditions for activating and deactivating continuity procedures, and required resources including the existing cloud/offsite data backups, standby operational capacity and redundancy. A drill record dated 2026-09-05 confirms that the operational continuity procedure was exercised. The cloud provider is one of the three security-impacting suppliers recorded in AR-06 and AR-11; no additional supplier is introduced. These operational continuity contacts are not staffed cybersecurity-incident reporting channels or designated CSIRT Italia contacts; the incident-plan gaps in AR-05 remain. BC-26 does not contain the recovery priorities, operation-specific recovery procedures and objectives of a disaster-recovery plan.

### AR-15 · 2026-10-09

**Source document:** plan-register and document-owner check; inspected on 2026-10-09

The document owner and current plan register confirm that no disaster-recovery plan has been defined, approved or implemented for either relevant system. No other controlled document provides an operation recovery order, operation-specific recovery procedures and recovery objectives for both systems. BC-26 and the monthly successful tests of data backups remain in place, but neither is represented as a disaster-recovery plan.

### AR-16 · 2026-10-09

**Source document:** cyber-event monitoring service and configuration review; inspected on 2026-10-09

For both relevant systems, the cyber-event monitoring service is not configured or operated to monitor remote access, perimeter router and firewall activities, significant administrative events, or successful and failed access to network resources, endpoints and applications for event detection. The monitoring owner confirms no other process performs that monitoring. This is a finding about active cybersecurity-event monitoring, not about whether raw audit logs are generated or retained. Raw remote-access and privileged-account logging remains bounded by the evidence in AR-19.

### AR-17 · 2026-10-09

**Source document:** network-flow inventory register check; inspected on 2026-10-09

The network architecture owner confirms that no current inventory of network flows between Aurora Grid's network and information systems and the external environment is maintained and approved by internal actors. A one-off description of the jump-host and legacy RDP paths exists, but it is not a maintained or internally approved inventory of external flows. The complete system, service and application register AS-26 in AR-13 does not contain such flows.

### AR-18 · 2026-10-09

**Source document:** remote-access list content check across maintained registers; inspected on 2026-10-09

The maintained general system register AS-26 includes the names of the relevant systems but has no fields pairing every remotely accessible target with its corresponding access method. A check of all other maintained registers likewise finds no current list with that paired content. The jump-host and legacy Internet-reachable RDP routes to the operations management host appear only in a one-off access review note, not a maintained list. The deficiency is missing content in any qualifying maintained register, not the absence of a separate document.

### AR-19 · 2026-10-09

**Source document:** limited raw-access-log sample and evidence-request record; inspected on 2026-10-09

A sample raw VPN session log dated 2026-10-07 was available. Configuration and export evidence for legacy RDP remote sessions and for the two active cloud administrative accounts was not available to the case reviewer, so the current record cannot establish whether all remote access and all access using administrative privileges are logged. The sample does not establish complete coverage; the unavailable evidence is not proof that those events are unlogged. AR-16 addresses active event monitoring, a distinct control.

### AR-20 · 2026-10-09

**Source document:** ordinary-user role template and privileged-entitlement evidence request; inspected on 2026-10-09

A standard employee role template shows limited permissions for one ordinary-user group. The current effective entitlements, approval records, duty separation and need-to-know basis for the legacy maintenance account and the two active cloud administrator accounts were not available to the case reviewer. This limited example cannot establish how permissions are assigned across the relevant scope, and no specific breach of least privilege, separation of duties or need to know is established. Missing MFA on those accounts remains a separate documented fact.

## Reading related records

- The supplier register has contact details for its three security-impacting suppliers. These relationship contacts are distinct from Aurora Grid's absent cybersecurity incident-reporting channels and designated CSIRT roles.
- The asset, service and application register is complete for its own scope. It does not provide an approved external-flow inventory or a maintained system-to-remote-method list. A separate document is unnecessary if an integrated register has the needed content; the check of maintained registers found that content missing.
- The risk-management plan is a documented, operating process. A separate check found a supplier-dependency scenario missing from the executed risk assessment, while the detailed assessment of supplies has other recorded gaps.
- The business-continuity plan has operational contacts and resources. The incident plan still lacks reporting and CSIRT contacts. Backup tests concern data actually backed up; they do not establish configuration backups, offline copies or a disaster-recovery plan.
- Active cybersecurity-event monitoring is absent. One raw VPN log sample exists, while other access-log configurations are unverified. A limited ordinary-user permissions example does not settle privileged entitlements.

This dossier supplies company information for the exercise. It contains no assessment result or teacher answer.
