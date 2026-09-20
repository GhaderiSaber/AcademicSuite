# Reporting Consistency Validator

Audits strict APA 7th Edition and Persian academic typography:
- Persian leading zero standard: flags any `.۰۰۱` or `.۰۵` without leading zero.
- Prohibition of $p = .000$: flags any uncorrected zero $p$-value.
- Decoupled numbers: ensures negative signs precede numbers ($-0.32$).
- Cliché detection: audits text for forbidden robotic AI cliches (*«شایان ذکر است که»*).

## Verdicts
- `PASS`: 100% compliant with APA 7 and Persian typography standards.
- `FAIL`: Missing leading zero in Persian, $p = .000$ present, or robotic clichés detected.
