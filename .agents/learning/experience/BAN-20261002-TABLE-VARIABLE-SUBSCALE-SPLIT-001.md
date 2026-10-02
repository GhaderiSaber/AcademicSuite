# Behavior Analysis Report: BAN-20261002-TABLE-VARIABLE-SUBSCALE-SPLIT-001

## 1. Context and Trigger
- **Trajectory ID**: TRJ-20261002-TABLE-VARIABLE-SUBSCALE-SPLIT-001
- **Trigger Event**: FDB-20261002-TABLE-VARIABLE-SUBSCALE-SPLIT-001 (User Feedback)
- **Target Agent**: `coding-agent` / `academic-writer`
- **Target Capability**: `CHAPTER4`

## 2. Observable Failure
The trajectory audit revealed that Chapter 4 tables (e.g., Table 13, 15, 16, 19, 24) exhibited severe structural failures:
1. **Merged Columns**: Parent variables and subscales were concatenated into a single column (`متغیر/سازه`).
2. **Flattened Row Numbers**: Sequence numbers (e.g., `۱.`) were embedded directly inside textual data cells.
3. **Catastrophic Markdown Corruption**: Non-idempotent scripts prepended identical table delimiter tokens (`| ۱ | ۱ | ۱ |`) iteratively up to 9 times across multiple `.md` files without checking for existing headers.

## 3. Root Cause Diagnosis
The agent attempted to retrofit a 3-column table structure by executing naive, unanchored regex prepends and string concatenations across markdown deliverables. Because the scripts lacked idempotency guards, successive batch executions recursively duplicated the header and data cell tokens. Additionally, initial table generation failed to structurally separate the parent variable from the subscale, instead merging them into a single column and embedding row numbers directly into text strings.

## 4. Prescribed Counterfactual Behavior
1. **Native 3-Column Prefix**: All psychometric tables MUST structurally implement 3 distinct prefix columns natively upon generation: `ردیف` (Sequential Integer), `متغیر` (Parent Construct), and `مؤلفه` (Subscale/Dimension).
2. **Zero Regex Table Mutation**: Agents MUST NEVER mutate markdown or docx tables using unanchored batch regex prepending (`re.sub` or naive string splitting/concatenation).
3. **DOM-Based Idempotency**: All table refactoring must be idempotent and rely strictly on DOM parsing (e.g., `xml.etree.ElementTree` / `python-docx`) or complete table regeneration from clean arrays, asserting the presence of the 3-column prefix before proceeding. Update validators to strictly fail-close if merged columns or concatenated row numbers are detected.
