import urllib.request, json
data = json.loads(urllib.request.urlopen('https://api.github.com/repos/your_username/your_repo/actions/runs?per_page=5').read())
for r in data['workflow_runs']:
    print(f"Run {r['id']}: {r['status']} - {r['conclusion']} - {r['created_at']}")
