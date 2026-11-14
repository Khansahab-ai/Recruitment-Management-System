# Reproducibility Verification Report (Step 10)

**Specification**: Regenerate twice with the same seed (`20261022`) and compare row counts/checksums to demonstrate reproducibility.

## Verification Outcome: PASSED (100% Deterministic)

| File Name | Relative Path | Lines/Rows | Size (Bytes) | SHA-256 Checksum | Reproducibility Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `application_stage_history.csv` | `data\generated\application_stage_history.csv` | 7560 | 677,850 | `d29a8874245caa59...b95d5336` | **IDENTICAL (PASS)** |
| `application_stage_history.json` | `data\generated\application_stage_history.json` | 68033 | 2,104,870 | `b6a5915a4d967fdb...21897a92` | **IDENTICAL (PASS)** |
| `applications.csv` | `data\generated\applications.csv` | 3001 | 255,149 | `a602cdf4ae91d7fe...189f4ccd` | **IDENTICAL (PASS)** |
| `applications.json` | `data\generated\applications.json` | 27002 | 870,457 | `8753da96d862cf14...ab8dbe98` | **IDENTICAL (PASS)** |
| `candidate_skills.csv` | `data\generated\candidate_skills.csv` | 9036 | 204,555 | `a800da5bc51ec139...6f31df65` | **IDENTICAL (PASS)** |
| `candidate_skills.json` | `data\generated\candidate_skills.json` | 54212 | 1,144,160 | `87695d5c20513989...2fe5e675` | **IDENTICAL (PASS)** |
| `candidates.csv` | `data\generated\candidates.csv` | 2001 | 212,902 | `05796f39e4116a83...71b97214` | **IDENTICAL (PASS)** |
| `candidates.json` | `data\generated\candidates.json` | 20002 | 646,816 | `cd5b0055851d3584...cbf2c2b4` | **IDENTICAL (PASS)** |
| `closed_requisition_active_applications.json` | `data\ground_truth\closed_requisition_active_applications.json` | 33 | 682 | `80b18d4f67ae80f7...e795f7bc` | **IDENTICAL (PASS)** |
| `departments.csv` | `data\generated\departments.csv` | 11 | 518 | `38ac89c8ef14cbdc...18b3514a` | **IDENTICAL (PASS)** |
| `departments.json` | `data\generated\departments.json` | 52 | 1,359 | `605484e2b9326231...2916b67d` | **IDENTICAL (PASS)** |
| `duplicate_application_case.json` | `data\ground_truth\duplicate_application_case.json` | 11 | 431 | `f9e030a9604855ae...1dc6a8df` | **IDENTICAL (PASS)** |
| `feedback.csv` | `data\generated\feedback.csv` | 1001 | 132,632 | `a335ea712780b3b2...ca0d3247` | **IDENTICAL (PASS)** |
| `feedback.json` | `data\generated\feedback.json` | 13002 | 459,471 | `42a9305a52f49fa6...7841e548` | **IDENTICAL (PASS)** |
| `ground_truth.json` | `data\ground_truth\ground_truth.json` | 42 | 4,064 | `b6a9ece8736879ae...e711bd20` | **IDENTICAL (PASS)** |
| `interview_assignments.csv` | `data\generated\interview_assignments.csv` | 1201 | 14,079 | `6a753b84d52f2f6a...ba16eb83` | **IDENTICAL (PASS)** |
| `interview_assignments.json` | `data\generated\interview_assignments.json` | 6002 | 126,839 | `2c604cac7e14a2e6...f1c38935` | **IDENTICAL (PASS)** |
| `interviewers.csv` | `data\generated\interviewers.csv` | 51 | 2,980 | `5e71c21509fcfbae...3ee476b9` | **IDENTICAL (PASS)** |
| `interviewers.json` | `data\generated\interviewers.json` | 402 | 11,360 | `b8ad38baeeefa346...09f01585` | **IDENTICAL (PASS)** |
| `interviews.csv` | `data\generated\interviews.csv` | 601 | 57,353 | `39b73a9cca4ff01f...d14ceb51` | **IDENTICAL (PASS)** |
| `interviews.json` | `data\generated\interviews.json` | 5402 | 180,264 | `0a46ecfb347f4b6c...832638ab` | **IDENTICAL (PASS)** |
| `job_requisitions.csv` | `data\generated\job_requisitions.csv` | 101 | 9,266 | `117983143b1a686a...f52ea196` | **IDENTICAL (PASS)** |
| `job_requisitions.json` | `data\generated\job_requisitions.json` | 1202 | 35,951 | `f5db2a82cd69754a...60a3b27c` | **IDENTICAL (PASS)** |
| `missing_feedback_case.json` | `data\ground_truth\missing_feedback_case.json` | 13 | 479 | `c22f0badf2615847...e98a65fd` | **IDENTICAL (PASS)** |
| `offer_approval_history.csv` | `data\generated\offer_approval_history.csv` | 151 | 11,952 | `195661d8be3863cb...86ec0da4` | **IDENTICAL (PASS)** |
| `offer_approval_history.json` | `data\generated\offer_approval_history.json` | 1202 | 36,491 | `0e9c50491e55df54...3d0146bb` | **IDENTICAL (PASS)** |
| `offers.csv` | `data\generated\offers.csv` | 151 | 14,735 | `37d459c49dc0f324...6346b75e` | **IDENTICAL (PASS)** |
| `offers.json` | `data\generated\offers.json` | 1352 | 43,606 | `5e3307da18d075f7...d9e2fba4` | **IDENTICAL (PASS)** |
| `resume_artifacts.csv` | `data\generated\resume_artifacts.csv` | 2328 | 300,672 | `ec16156809037e40...fcbf3bf0` | **IDENTICAL (PASS)** |
| `resume_artifacts.json` | `data\generated\resume_artifacts.json` | 20945 | 759,010 | `7fa2bc6c05f61182...0be49a3f` | **IDENTICAL (PASS)** |
| `salary_outside_band_case.json` | `data\ground_truth\salary_outside_band_case.json` | 13 | 498 | `15345c5f15b64aa8...9af8bd7f` | **IDENTICAL (PASS)** |
| `screening_rules.csv` | `data\generated\screening_rules.csv` | 401 | 15,232 | `f2fd1742537e1c31...d8fe2063` | **IDENTICAL (PASS)** |
| `screening_rules.json` | `data\generated\screening_rules.json` | 3202 | 80,763 | `dfefbe936a10f4ae...1b53715f` | **IDENTICAL (PASS)** |
| `skills.csv` | `data\generated\skills.csv` | 51 | 1,120 | `978d11e354112f6a...21847323` | **IDENTICAL (PASS)** |
| `skills.json` | `data\generated\skills.json` | 252 | 5,343 | `dccc8437b7b2f7b7...e5c436d8` | **IDENTICAL (PASS)** |
| `unavailable_interviewer_case.json` | `data\ground_truth\unavailable_interviewer_case.json` | 15 | 631 | `ae9558ab424c73c1...fac09c6b` | **IDENTICAL (PASS)** |


> [!NOTE]
> All 32 generated CSV, JSON, and Ground Truth datasets produced identical cryptographic hashes (SHA-256) across consecutive standalone runs using seed `20261022`.
