# App Management Demo — OpenShift Runbook

A tiny Flask app whose page **color, message, and version change with env vars**,
so config changes and rebuilds are visible on screen.

## 0. Get the code into a git repo
S2I builds pull from git, so push this folder to GitHub/GitLab first:

```bash
cd ocp-app-mgmt-demo
git init && git add . && git commit -m "v1"
git remote add origin https://github.com/<you>/ocp-app-mgmt-demo.git
git push -u origin main
```

## 1. Management ENV — deploy + set config
```bash
oc new-project app-mgmt-demo

# Build + deploy straight from git via Python S2I
oc new-app python:3.11-ubi9~https://github.com/<you>/ocp-app-mgmt-demo.git \
  --name=demo-app
oc expose deployment/demo-app --port=8080
oc expose svc/demo-app          # creates a route

# Seed env config
oc set env deployment/demo-app \
  APP_VERSION=v1 APP_COLOR=#2563eb APP_MESSAGE="Hello from OpenShift"

oc get route demo-app -o jsonpath='{.spec.host}{"\n"}'
```
Open the route → blue page, "Version: v1".

## 2. Config change triggers redeploy
Change an env var. `oc set env` stamps it into the pod template → automatic rollout.
```bash
oc set env deployment/demo-app APP_COLOR=#16a34a APP_MESSAGE="Config changed!"
oc rollout status deployment/demo-app
```
Refresh → page is now green. New pod name proves the redeploy.

> ConfigMap variant (if they ask): mount via `--from=configmap/...`. A bare
> configmap edit does NOT restart pods on its own — use
> `oc rollout restart deployment/demo-app` to force it.

## 3. Rebuild with new code (feature update)
Edit code to ship a "feature", commit, rebuild:
```bash
# in app.py set: FEATURE_BANNER = True
git commit -am "v2: feature banner"
git push

oc set env deployment/demo-app APP_VERSION=v2
oc start-build demo-app --follow    # S2I rebuild from new source
```
The new image + ImageChange trigger rolls out automatically → yellow feature banner appears, Version: v2.

## 4. Rollback
```bash
oc rollout history deployment/demo-app
oc rollout undo deployment/demo-app                 # back one revision
# or target a specific one:
oc rollout undo deployment/demo-app --to-revision=1
oc rollout status deployment/demo-app
```
Page reverts to the previous state (banner gone / old color).

## 5. Show cluster resource
```bash
oc adm top pods -n app-mgmt-demo
oc adm top nodes
oc describe deployment/demo-app
oc get all -n app-mgmt-demo
```

## Reset between runs
```bash
oc delete project app-mgmt-demo
```
