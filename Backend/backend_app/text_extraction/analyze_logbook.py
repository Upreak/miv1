"""
analyze_logbook.py

Simple script to analyze extraction logbook and provide insights.
"""

import sqlite3
from pathlib import Path
import json

def analyze_extraction_logbook(db_path: Path = Path("logs/extraction_logbook.db")):
    """
    Analyze extraction logbook and print insights.
    """
    if not db_path.exists():
        print(f"Logbook database not found at {db_path}")
        return
    
    conn = sqlite3.connect(str(db_path))
    
    # Basic stats
    total_attempts = conn.execute("SELECT COUNT(*) FROM extraction_logs").fetchone()[0]
    successful_attempts = conn.execute("SELECT COUNT(*) FROM extraction_logs WHERE success=1").fetchone()[0]
    failed_attempts = total_attempts - successful_attempts
    
    print(f"=== EXTRACTION LOGBOOK ANALYSIS ===")
    print(f"Total attempts: {total_attempts}")
    print(f"Successful: {successful_attempts}")
    print(f"Failed: {failed_attempts}")
    print(f"Success rate: {(successful_attempts/total_attempts*100):.1f}%" if total_attempts > 0 else "0.0%")
    print()
    
    # Success by module
    print("=== SUCCESS BY MODULE ===")
    cursor = conn.execute("""
        SELECT success_module, COUNT(*) as count, AVG(quality_score) as avg_score
        FROM extraction_logs 
        WHERE success=1 
        GROUP BY success_module 
        ORDER BY count DESC
    """)
    for module, count, avg_score in cursor.fetchall():
        print(f"{module}: {count} successes (avg quality: {avg_score:.1f})")
    print()
    
    # Failure by module
    print("=== FAILURES BY MODULE ===")
    cursor = conn.execute("""
        SELECT success_module, COUNT(*) as count
        FROM extraction_logs 
        WHERE success=0 
        GROUP BY success_module 
        ORDER BY count DESC
    """)
    for module, count in cursor.fetchall():
        print(f"{module}: {count} failures")
    print()
    
    # Average quality score by module
    print("=== AVERAGE QUALITY SCORE BY MODULE ===")
    cursor = conn.execute("""
        SELECT success_module, AVG(quality_score) as avg_score, MIN(quality_score) as min_score, MAX(quality_score) as max_score
        FROM extraction_logs 
        GROUP BY success_module 
        ORDER BY avg_score DESC
    """)
    for module, avg_score, min_score, max_score in cursor.fetchall():
        print(f"{module}: avg={avg_score:.1f}, min={min_score:.1f}, max={max_score:.1f}")
    print()
    
    # Recent attempts
    print("=== RECENT ATTEMPTS (Last 10) ===")
    cursor = conn.execute("""
        SELECT timestamp, file_path, success_module, success, quality_score, extracted_length
        FROM extraction_logs 
        ORDER BY id DESC 
        LIMIT 10
    """)
    for timestamp, file_path, success_module, success, quality_score, extracted_length in cursor.fetchall():
        status = "SUCCESS" if success else "FAILED"
        print(f"{timestamp} | {Path(file_path).name} | {success_module} | {status} | score={quality_score:.1f} | length={extracted_length}")
    print()
    
    # Attempts breakdown
    print("=== ATTEMPT BREAKDOWN ===")
    cursor = conn.execute("SELECT attempts_json FROM extraction_logs LIMIT 50")
    attempt_counts = {}
    for row in cursor.fetchall():
        attempts = json.loads(row[0])
        for attempt in attempts:
            module = attempt['module']
            attempt_counts[module] = attempt_counts.get(module, 0) + 1
    
    for module, count in sorted(attempt_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{module}: {count} total attempts")
    
    conn.close()

if __name__ == "__main__":
    analyze_extraction_logbook()