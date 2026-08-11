from main_scanner import scan_website
from report_generator import generate_report

result = scan_website("github.com")

print(generate_report(result))
