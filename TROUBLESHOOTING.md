# Troubleshooting Guide

## Common Issues & Solutions

### CSV Won't Import in Excel

**Symptom:** Columns misaligned, extra blank columns

**Solution:**
```bash
# Convert to UTF-8 without BOM
iconv -f utf-8 -t utf-8-spawn spreadsheets/csv/*.csv > cleaned.csv
# Or use Notepad++ → Encoding → UTF-8 (no BOM)
