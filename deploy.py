#!/usr/bin/env python3
"""Deploy static files to Cloudflare Pages via Direct Upload API."""
import hashlib, json, os, sys, requests

CF_TOKEN = "_5nuUGVS2o0_pv0gRr2CJJbRCB8E6ngpfib72chV"
ACCOUNT_ID = "b58e8b2e31173f56751f3913ae4358fb"
PROJECT = "hireology-brand-hub"
EXCLUDE_DIRS = {'reference', 'node_modules', '.git'}

def deploy():
    manifest = {}
    files = []
    
    for root, dirs, filenames in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in filenames:
            if f.startswith('.') or f == 'deploy.py':
                continue
            filepath = os.path.join(root, f)
            path = '/' + filepath.lstrip('./')
            with open(filepath, 'rb') as fh:
                content = fh.read()
            h = hashlib.sha256(content).hexdigest()
            manifest[path] = h
            files.append((h, filepath, content))
    
    print(f"Deploying {len(files)} files...")
    
    # Use requests with proper multipart encoding
    multipart = {'manifest': (None, json.dumps(manifest), 'application/json')}
    for h, filepath, content in files:
        multipart[h] = (os.path.basename(filepath), content, 'application/octet-stream')
    
    r = requests.post(
        f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/pages/projects/{PROJECT}/deployments",
        headers={'Authorization': f'Bearer {CF_TOKEN}'},
        files=multipart,
        timeout=120
    )
    
    d = r.json()
    if d.get('success'):
        url = d['result'].get('url', 'unknown')
        print(f"✅ Deployed: {url}")
        print(f"   Production: https://{PROJECT}.pages.dev")
        return True
    else:
        print(f"❌ Failed: {d.get('errors')}")
        return False

if __name__ == '__main__':
    deploy()
