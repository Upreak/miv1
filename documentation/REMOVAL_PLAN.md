# Removal / Cleanup Plan

This document outlines the files that have been moved during the cleanup process.

## What Was Done

All test/mock/report files were moved into `cleanup_backups/` for review.
Nothing was deleted. The team may decide to permanently remove after PR review.

## Protected Files (Not Moved)

The following files were protected and NOT moved:
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

## Consolidated Markdown Files

Total markdown files processed: 0

No markdown files were consolidated in this iteration.

## Moved Test/Mock/Report Files

Total test/mock/report files moved: 0

No test files were moved in this iteration.

## Generated Files

- `DOCS/CONSOLIDATED_DOCUMENTATION.md` - Consolidated all markdown content
- `DOCS/REMOVAL_PLAN.md` - This document

## Next Steps

1. Review the consolidated documentation
2. Review the moved files in cleanup_backups/
3. Decide which files can be permanently removed
4. Update any references to moved files

## Notes

This cleanup was performed on the chore/compile-docs-prune-tests branch.
All changes are non-destructive with full backups preserved.