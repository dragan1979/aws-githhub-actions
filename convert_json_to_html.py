import json
import os
import sys 
from jinja2 import Template

# Define the HTML template structure
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Checkov Security Scan Report</title>
	<style>
		body { font-family: sans-serif; margin: 20px; background-color: #f4f7f9; color: #333; }
		.container { max-width: 1200px; margin: auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
		h1 { color: #004d99; border-bottom: 2px solid #eee; padding-bottom: 10px; }
		h2 { color: #d9534f; margin-top: 20px; }
		table { width: 100%; border-collapse: collapse; margin-top: 15px; }
		th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
		th { background-color: #004d99; color: white; }
		tr:hover { background-color: #f5f5f5; }
		.success { background-color: #5cb85c; color: white; padding: 5px; border-radius: 4px; }
		.failure { background-color: #d9534f; color: white; padding: 5px; border-radius: 4px; }
		.summary p { margin: 5px 0; }
		.code-block { background-color: #eee; padding: 10px; border-radius: 4px; overflow-x: auto; font-family: monospace; }
		.soft-fail { background-color: #f0ad4e; color: white; padding: 5px; border-radius: 4px; }
		.failed-checks-section h2 { color: #d9534f; }
	</style>
</head>
<body>
	<div class="container">
		<h1>Checkov Security Scan Report</h1>

		{% if summary %}
		<div class="summary">
			<h2>Scan Summary</h2>
			<p><strong>Resource Scanned:</strong> {{ summary.resource_count }}</p>
			<p><strong>Checkov Version:</strong> {{ summary.checkov_version }}</p>
			<p><strong>Scanning Time:</strong> {{ summary.scanning_time }} seconds</p>
			<p><strong>Failed Checks:</strong> <span class="failure">{{ summary.failed }}</span></p>
			<p><strong>Passed Checks:</strong> <span class="success">{{ summary.passed }}</span></p>
			<p><strong>Skipped Checks:</strong> {{ summary.skipped }}</p>
		</div>
		{% endif %}

        <div class="failed-checks-section">
			<h2>Failed Checks Details ({{ results.failed_checks | length }})</h2>
			{% if results.failed_checks %}
			<table>
				<thead>
					<tr>
						<th>Check ID</th>
						<th>Name</th>
						<th>File Path</th>
						<th>Resource</th>
						<th>Violation Line</th>
					</tr>
				</thead>
				<tbody>
					{% for check in results.failed_checks %}
					<tr>
						<td>{{ check.check_id }}</td>
						<td>{{ check.check_name }}</td>
						<td>{{ check.file_path }}</td>
						<td>{{ check.resource }}</td>
						<td>{{ check.file_line_range[0] }}</td>
					</tr>
					{% endfor %}
				</tbody>
			</table>
			{% else %}
			<p class="success">No checks failed! Infrastructure is secure.</p>
			{% endif %}
        </div>

	</div>
</body>
</html>
"""

def generate_html_report(json_filepath, html_filepath):
	"""
	Reads a Checkov JSON report and generates an HTML file.
	"""
	
	try:
		with open(json_filepath, 'r') as f:
			data = json.load(f)
	except FileNotFoundError:
		print(f"Error: JSON report not found at {json_filepath}. Cannot generate HTML.", file=sys.stderr)
		return
	except IsADirectoryError:
		print(f"Error: Path {json_filepath} is a directory. Cannot read as a file.", file=sys.stderr)
		return
	except json.JSONDecodeError:
		print(f"Error: Invalid JSON format in {json_filepath}.", file=sys.stderr)
		return

	# Handle case where Checkov outputs a list of results (for multiple frameworks/files)
	if isinstance(data, list):
		# Find the first result object that contains the summary
		data = next((item for item in data if 'summary' in item), {})
	elif not isinstance(data, dict):
		# Ensure data is a dictionary if it wasn't a list
		data = {}

	# Extract the 'results' dictionary, which contains passed_checks, failed_checks, etc.
	report_data = data.get('results', {})
	
	# Extract summary data for easy display
	summary = {
		'failed': data.get('summary', {}).get('failed', 0),
		'passed': data.get('summary', {}).get('passed', 0),
		'skipped': data.get('summary', {}).get('skipped', 0),
		'resource_count': data.get('summary', {}).get('resource_count', 0),
		'checkov_version': data.get('summary', {}).get('checkov_version', 'N/A'),
		'scanning_time': data.get('summary', {}).get('scanning_time', 0.0),
	}
    
	# Add the detailed check lists to the summary data for the template access
	# This ensures keys like 'failed_checks' are available in the 'results' object for Jinja2
	if 'failed_checks' not in report_data:
		report_data['failed_checks'] = []
	
	# Render the template with the extracted data
	template = Template(HTML_TEMPLATE)
	html_content = template.render(
		summary=summary,
		results=report_data
	)

	# Write the HTML content to the output file
	try:
		with open(html_filepath, 'w') as f:
			f.write(html_content)
		print(f"Successfully generated HTML report at {html_filepath}")
	except IOError as e:
		print(f"Error writing HTML file: {e}", file=sys.stderr)

if __name__ == "__main__":
	# Ensure we can run the script manually or via the workflow
	if len(sys.argv) < 3:
		# Fallback to common paths used in the workflow
		default_json_path = 'reports/checkov_report.json'
		default_html_path = 'reports/checkov_report.html'
		print(f"Using default paths: {default_json_path} -> {default_html_path}")
		generate_html_report(default_json_path, default_html_path)
	else:
		# Use paths provided via command line
		json_path = sys.argv[1]
		html_path = sys.argv[2]
		generate_html_report(json_path, html_path)