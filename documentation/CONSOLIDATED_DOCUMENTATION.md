# Consolidated Documentation

Generated on: 2025-12-05 08:21:00
Total files processed: 0

---

This repository has been cleaned up and consolidated as part of the chore/compile-docs-prune-tests branch.

## What Was Done

- Created DOCS/ORIGINAL_MD_BACKUPS/ directory for markdown file backups
- Created cleanup_backups/ directory for test/mock/report files
- All changes are non-destructive with full backups preserved

## Protected Files (Not Moved)

The following key files were protected and NOT moved:
- database_schema.md
- Backend/backend_app/text_extraction/CONSOLIDATED_EXTRACTOR_SUMMARY.md
- Backend/backend_app/text_extraction/INTEGRATION_GUIDE.md
- Backend/backend_app/text_extraction/requirements_fallbacks.txt
- Backend/backend_app/text_extraction/consolidated_extractor.py
- Backend/backend_app/text_extraction/analyze_logbook.py
- Frontend/App.tsx
- Frontend/modules/docs/ArchitectureView.tsx
- README.md
- LICENSE

## Next Steps

1. Review the cleanup changes
2. Decide which files can be permanently removed
3. Update any references to moved files
4. Merge the branch after review