from scanner.main_scanner import scan_website
from scanner.report_generator import generate_report

if __name__ == "__main__":
    result = scan_website("github.com")
    print(generate_report(result))
