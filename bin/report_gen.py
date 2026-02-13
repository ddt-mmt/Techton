#!/usr/bin/env python3
import sys
import csv
import json
import statistics
import os
from datetime import datetime

def format_id_number(value, decimal_places=None):
    if isinstance(value, (int, float)):
        if decimal_places is not None:
            # Format float with specified decimal places
            num_str = f"{value:,.{decimal_places}f}"
        else:
            # Format integer or float without specific decimal places (e.g., for thousands)
            num_str = f"{value:,}"
        
        # Replace default thousands separator (,) with point (.)
        # and default decimal separator (.) with comma (,)
        if ',' in num_str and '.' in num_str: # Both thousands and decimal
            parts = num_str.split('.')
            integer_part = parts[0].replace(',', '.')
            decimal_part = parts[1]
            return f"{integer_part},{decimal_part}"
        elif ',' in num_str: # Only thousands (implies integer like)
            return num_str.replace(',', '.')
        elif '.' in num_str: # Only decimal (no thousands)
            return num_str.replace('.', ',')
        else: # Simple integer
            return num_str
    return str(value)

# Configuration
TEMPLATE_HTML = """

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Techton Audit Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-color: #38bdf8;
            --danger-color: #f87171;
            --success-color: #4ade80;
            --warning-color: #facc15;
        }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            margin: 0;
            padding: 40px;
            line-height: 1.6;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 1px solid #334155;
        }
        .brand {
            font-size: 1.8rem;
            font-weight: 800;
            color: var(--accent-color);
            letter-spacing: -0.025em;
        }
        .meta-info {
            text-align: right;
            font-size: 0.85rem;
            color: var(--text-secondary);
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 24px;
            margin-bottom: 40px;
        }
        .card {
            background-color: var(--card-bg);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid #334155;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .stat-label {
            color: var(--text-secondary);
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }
        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #fff;
        }
        .chart-container {
            background-color: var(--card-bg);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            height: 400px;
            width: 100%;
            box-sizing: border-box;
            border: 1px solid #334155;
            position: relative;
        }
        .table-container {
            background-color: var(--card-bg);
            border-radius: 16px;
            padding: 24px;
            overflow-x: auto;
            border: 1px solid #334155;
            margin-bottom: 24px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }
        th, td {
            text-align: left;
            padding: 16px;
            border-bottom: 1px solid #334155;
        }
        th {
            color: var(--text-secondary);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
        }
        tr:last-child td { border-bottom: none; }
        
        /* Utility */
        .text-success { color: var(--success-color); }
        .text-danger { color: var(--danger-color); }
        .text-warning { color: var(--warning-color); }
        .text-accent { color: var(--accent-color); }
        
        .sub-stat {
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-top: 4px;
        }
    </style>
</head>
<body>

    <div class="header">
        <div class="brand">
            <span>⚡ TECHTON</span>
            <span style="font-weight: 400; color: white;">Audit Report</span>
        </div>
        <div class="meta-info">
            <div>Target: <strong>{{ target }}</strong></div>
            <div>Date: {{ date }}</div>
            <div>Mode: {{ mode }}</div>
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <div class="stat-label">Status</div>
            <div class="stat-value {{ grade_class }}">{{ grade }}</div>
        </div>
        <div class="card">
            <div class="stat-label">Total Requests</div>
            <div class="stat-value">{{ total_requests }}</div>
            <div class="sub-stat">{{ rps }} Req/s (Avg)</div>
        </div>
        <div class="card">
            <div class="stat-label">Success / Fail</div>
            <div class="stat-value">
                <span class="text-success">{{ success_percentage }}%</span> / <span class="text-danger">{{ fail_percentage }}%</span>
            </div>
            <div class="sub-stat">{{ success_count }} OK / {{ fail_count }} Errors</div>
        </div>
        <div class="card">
            <div class="stat-label">Avg Latency</div>
            <div class="stat-value {{ latency_class }}">{{ avg_latency }}</div>
            <div class="sub-stat">P90: {{ p90_latency }} / P95: {{ p95_latency }}</div>
        </div>
    </div>

    <div class="card" style="margin-bottom: 30px;">
        <h3 style="margin-top: 0;">Executive Summary</h3>
        <p>{{ summary }}</p>
        <h4 style="margin-top: 20px; color: var(--warning-color);">Recommendations</h4>
        <ul style="list-style-type: disc; padding-left: 20px;">
            {{ recommendations_list }}
        </ul>
    </div>

    <div class="chart-container">
        <canvas id="latencyChart"></canvas>
    </div>

    <div class="chart-container">
        <canvas id="throughputChart"></canvas>
    </div>

    <div class="table-container">
        <h3 style="margin-top: 0;">{{ error_section_title }}</h3>
        <table>
            <thead>
                <tr>
                    <th>{{ col_1_title }}</th>
                    <th>{{ col_2_title }}</th>
                </tr>
            </thead>
            <tbody>
                {{ error_rows }}
            </tbody>
        </table>
    </div>

    <script>
        const ctxLat = document.getElementById('latencyChart').getContext('2d');
        const latencyChart = new Chart(ctxLat, {
            type: 'line',
            data: {
                labels: {{ time_labels }},
                datasets: [{
                    label: 'Avg Latency (seconds)',
                    data: {{ latency_data }},
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: { labels: { color: '#94a3b8' } },
                    title: { display: true, text: 'Latency Trend (Lower is Better)', color: '#f8fafc', font: { size: 16 } },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.parsed.y.toFixed(3) + 's';
                            }
                        }
                    }
                },
                scales: {
                    y: { 
                        grid: { color: '#334155' }, 
                        ticks: { color: '#94a3b8', callback: function(value) { return value + 's'; } },
                        title: { display: true, text: 'Seconds', color: '#64748b' }
                    },
                    x: { 
                        grid: { color: '#334155' }, 
                        ticks: { color: '#94a3b8', maxTicksLimit: 20 },
                        title: { display: true, text: 'Test Duration (s)', color: '#64748b' }
                    }
                }
            }
        });

        const ctxTp = document.getElementById('throughputChart').getContext('2d');
        const throughputChart = new Chart(ctxTp, {
            type: 'bar',
            data: {
                labels: {{ time_labels }},
                datasets: [{
                    label: 'Successful Requests/s',
                    data: {{ throughput_data }},
                    backgroundColor: '#22c55e',
                },
                {
                    label: 'Errors/s',
                    data: {{ error_data }},
                    backgroundColor: '#ef4444',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: { labels: { color: '#94a3b8' } },
                    title: { display: true, text: 'Throughput & Stability', color: '#f8fafc', font: { size: 16 } }
                },
                scales: {
                    y: { 
                        grid: { color: '#334155' }, 
                        ticks: { color: '#94a3b8' },
                        title: { display: true, text: 'Requests per Second', color: '#64748b' }
                    },
                    x: { 
                        grid: { color: '#334155' }, 
                        ticks: { color: '#94a3b8', maxTicksLimit: 20 },
                        title: { display: true, text: 'Test Duration (s)', color: '#64748b' }
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

def parse_csv(file_path):
    data = []
    has_http = False
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if not rows: return []
            
            for row in rows[:50]:
                if row.get('metric_name') == 'http_req_duration':
                    has_http = True
                    break
            
            for row in rows:
                item = {}
                try:
                    ts = float(row.get('timestamp', row.get('timeStamp', 0))) * 1000
                    if ts > 10000000000000: ts /= 1000
                    item['ts'] = int(ts)
                    m_name = row.get('metric_name')
                    m_val = float(row.get('metric_value', 0))
                    
                    if has_http:
                        if m_name == 'http_req_duration':
                             item['lat'] = m_val
                             item['success'] = True
                             item['msg'] = ''
                             data.append(item)
                    else:
                        if m_name == 'iteration_duration':
                             item['lat'] = m_val
                             item['success'] = True
                             item['msg'] = ''
                             data.append(item)
                        elif m_name == 'checks':
                             msg = row.get('check', 'Check Failed')
                             if m_val == 0.0 and "success" not in msg:
                                 item['lat'] = 0
                                 item['success'] = False
                                 item['msg'] = msg
                                 data.append(item)
                except ValueError:
                    continue
    except Exception as e:
        print(f"CSV Parse Error: {e}")
        return []
    return data

def main():
    if len(sys.argv) < 5:
        print("Usage: report_gen.py <csv_file> <target> <mode> <output_html> [vus] [duration]")
        sys.exit(1)

    csv_file = sys.argv[1]
    target = sys.argv[2]
    mode = sys.argv[3]
    output_file = sys.argv[4]
    
    vus = 0
    duration = 0
    if len(sys.argv) > 5:
        vus = int(sys.argv[5])
    if len(sys.argv) > 6:
        try:
            duration = int(str(sys.argv[6]).replace("s", ""))
        except:
            duration = 60

    if not os.path.exists(csv_file):
        with open(output_file, 'w') as f:
            f.write(f"<h1>Error: Data file not found at {csv_file}</h1>")
        sys.exit(0)

    data = parse_csv(csv_file)
    if not data:
        with open(output_file, 'w') as f:
            f.write(f"<h1>No metric data found in {csv_file}</h1>")
        sys.exit(0)

    # Analysis
    total_reqs = len(data)
    latencies = [d['lat'] for d in data if d['success']]
    
    # Latency calc in seconds
    avg_lat_ms = statistics.mean(latencies) if latencies else 0
    max_lat_ms = max(latencies) if latencies else 0
    
    avg_lat_s = avg_lat_ms / 1000
    max_lat_s = max_lat_ms / 1000

    p90_lat_s = 0
    p95_lat_s = 0
    if latencies:
        latencies.sort()
        p90_lat_s = (latencies[int(len(latencies) * 0.9)]) / 1000
        p95_lat_s = (latencies[int(len(latencies) * 0.95)]) / 1000

    errors = [d for d in data if not d['success']]
    error_count = len(errors)
    success_count = total_reqs - error_count
    
    success_percentage = (success_count / total_reqs * 100) if total_reqs > 0 else 0
    fail_percentage = (error_count / total_reqs * 100) if total_reqs > 0 else 0

    # Group by Second
    start_ts = data[0]['ts']
    time_series = {}
    for d in data:
        ts = d['ts']
        if ts > 1000000000000: offset = int((ts - start_ts) / 1000)
        else: offset = int(ts - start_ts)
        if offset < 0: offset = 0
        
        if offset not in time_series:
            time_series[offset] = {'count': 0, 'lat_sum': 0, 'errors': 0}
        
        if d['success']:
            time_series[offset]['count'] += 1
            time_series[offset]['lat_sum'] += d['lat']
        else:
            time_series[offset]['errors'] += 1

    sorted_secs = sorted(time_series.keys())
    chart_labels = []
    chart_lat = []
    chart_tp = []
    chart_err = []
    
    peak_rps = 0
    
    if sorted_secs:
        max_sec = sorted_secs[-1]
        for s in range(max_sec + 1):
            if s in time_series:
                item = time_series[s]
                total_in_sec = item['count'] + item['errors']
                if total_in_sec > peak_rps: peak_rps = total_in_sec
                
                chart_labels.append(f"{s}s")
                # Convert lat to seconds for chart
                avg_sec_lat = (item['lat_sum'] / item['count']) / 1000 if item['count'] > 0 else 0
                chart_lat.append(round(avg_sec_lat, 3))
                chart_tp.append(item['count'])
                chart_err.append(item['errors'])
            else:
                chart_labels.append(f"{s}s")
                chart_lat.append(0)
                chart_tp.append(0)
                chart_err.append(0)

    actual_duration = len(sorted_secs)
    rps = int(total_reqs / actual_duration) if actual_duration > 0 else 0
    
    premature_stop = actual_duration < (duration - 5)
    status_label = "COMPLETED"
    status_msg = f"Test successfully completed. Sustained avg load of {format_id_number(rps)} Req/s over {format_id_number(actual_duration)}s."
    recommendations = []

    if premature_stop:
        status_label = "CRASHED"
        status_msg = f"SERVER STOPPED EARLY (Survived {format_id_number(actual_duration)}s / {format_id_number(duration)}s)"
        recommendations.append("Critical: The server stopped responding before the test finished.")
    
    if fail_percentage > 5:
        status_label = "UNSTABLE"
        recommendations.append(f"High Failure Rate ({format_id_number(fail_percentage, 2)}%). Check AD logs for authentication rejections.")
    
    if avg_lat_s > 2.0:
         recommendations.append("High Latency (>2s) detected. User experience is severely degraded.")
    
    if vus > 500 and status_label == "COMPLETED" and avg_lat_s < 1.0:
        status_msg = f"Excellent Performance. Sustained {format_id_number(vus)} VUs with healthy latency."

    # Dynamic "Top Errors" or "Performance Stats"
    if error_count > 0:
        error_section_title = "Top Error Messages"
        col_1_title = "Error Message"
        col_2_title = "Count"
        
        error_counts = {}
        for e in errors:
            msg = e.get('msg', 'Unknown Error')
            error_counts[msg] = error_counts.get(msg, 0) + 1
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        rows_html = ""
        for msg, count in sorted_errors:
            rows_html += f"<tr><td>{msg}</td><td>{format_id_number(count)}</td></tr>"
        
        rows_html += '<tr><td colspan="2" style="font-size: 0.8rem; color: var(--text-secondary); padding-top: 15px;">This table shows the most frequent error messages, which may indicate specific problems with authentication, network, or server configuration.</td></tr>'

    else:
        error_section_title = "System Performance Metrics"
        col_1_title = "Metric"
        col_2_title = "Value"
        
        # Show nice stats instead of empty error table
        rows_html = (
            f"<tr><td><strong>Peak Throughput</strong></td><td>{format_id_number(peak_rps)} Req/s</td></tr>"
            f"<tr><td><strong>Average Throughput</strong></td><td>{format_id_number(rps)} Req/s</td></tr>"
            f"<tr><td><strong>P90 Latency</strong></td><td>{format_id_number(p90_lat_s, 3)}s</td></tr>"
            f"<tr><td><strong>P95 Latency</strong></td><td>{format_id_number(p95_lat_s, 3)}s</td></tr>"
            f"<tr><td><strong>Stability Score</strong></td><td><span class='text-success'>100%</span></td></tr>"
        )

    lat_class = "text-success"
    if avg_lat_s > 0.5: lat_class = "text-warning"
    if avg_lat_s > 2.0: lat_class = "text-danger"
    
    grade_class = "text-success"
    if status_label != "COMPLETED": grade_class = "text-danger"
    if status_label == "UNSTABLE": grade_class = "text-warning"
    
    recs_html = "".join([f"<li>{r}</li>" for r in recommendations])
    if not recs_html: recs_html = "<li>No specific issues detected. System performing within normal parameters.</li>"

    html = TEMPLATE_HTML.replace("{{ target }}", target) \
                        .replace("{{ date }}", datetime.now().strftime("%Y-%m-%d %H:%M")) \
                        .replace("{{ mode }}", mode) \
                        .replace("{{ total_requests }}", format_id_number(total_reqs)) \
                        .replace("{{ rps }}", format_id_number(rps)) \
                        .replace("{{ success_count }}", format_id_number(success_count)) \
                        .replace("{{ fail_count }}", format_id_number(error_count)) \
                        .replace("{{ success_percentage }}", format_id_number(success_percentage, 1)) \
                        .replace("{{ fail_percentage }}", format_id_number(fail_percentage, 1)) \
                        .replace("{{ avg_latency }}", f"{format_id_number(avg_lat_s, 3)}s") \
                        .replace("{{ max_latency }}", f"{format_id_number(max_lat_s, 3)}s") \
                        .replace("{{ p90_latency }}", f"{format_id_number(p90_lat_s, 3)}s") \
                        .replace("{{ p95_latency }}", f"{format_id_number(p95_lat_s, 3)}s") \
                        .replace("{{ latency_class }}", lat_class) \
                        .replace("{{ grade }}", status_label) \
                        .replace("{{ grade_class }}", grade_class) \
                        .replace("{{ summary }}", status_msg) \
                        .replace("{{ recommendations_list }}", recs_html) \
                        .replace("{{ time_labels }}", json.dumps(chart_labels)) \
                        .replace("{{ latency_data }}", json.dumps(chart_lat)) \
                        .replace("{{ throughput_data }}", json.dumps(chart_tp)) \
                        .replace("{{ error_data }}", json.dumps(chart_err)) \
                        .replace("{{ error_section_title }}", error_section_title) \
                        .replace("{{ col_1_title }}", col_1_title) \
                        .replace("{{ col_2_title }}", col_2_title) \
                        .replace("{{ error_rows }}", rows_html)

    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"Report generated: {output_file}")

if __name__ == "__main__":
    main()