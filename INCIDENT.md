# Incident Drill: Staging High Error Rate

## Summary

On 3 November 2026, fault injection was deliberately enabled on the staging
environment to simulate an application incident. The `/simulate-error`
endpoint returned HTTP 500 responses, Prometheus detected the sustained high
5xx rate, and Grafana displayed the corresponding structured ERROR logs.

Production was not affected.

## Timeline

- Fault injection was enabled on `app-staging` only with
  `ENABLE_FAULT_INJECTION=true`.
- Repeated requests were sent to `http://localhost:5001/simulate-error`.
- The endpoint returned HTTP 500 responses and emitted structured ERROR logs.
- The first recorded ERROR log evidence was at approximately
  `2026-11-03T11:54:14.787Z`.
- Prometheus evaluated `SystemHealthHighErrorRate` as firing for the staging
  environment after the error rate remained above 5% for two minutes. The
  alert became active at approximately `2026-11-03T11:41:45Z`.
- Grafana showed the error-rate incident and the related application logs.
- Fault injection was disabled and staging was recreated/restarted.
- Recovery was confirmed: staging was healthy, `ENABLE_FAULT_INJECTION=false`,
  and the alert returned to inactive by approximately
  `2026-11-03T12:11:15Z`.

## Evidence

The Grafana log evidence showed:

```text
level: ERROR
message: Simulated application fault
endpoint: /simulate-error
method: GET
status: 500
environment: staging
```

The Prometheus alert evidence showed:

```text
Alert: SystemHealthHighErrorRate
Environment: staging
State: FIRING
Condition: HTTP 5xx error rate above 5% for 2 minutes
```

## Root cause

The fault was intentional. The staging-only environment variable
`ENABLE_FAULT_INJECTION=true` caused `/simulate-error` to return HTTP 500 and
log an ERROR event. No production fault injection was enabled.

## Recovery

Fault injection was disabled and the staging container was restarted/recreated
with `ENABLE_FAULT_INJECTION=false`. The staging health and metrics endpoints
returned successfully, and Prometheus later showed the high-error-rate alert
as inactive.

## Prevention

Keep fault injection disabled by default and explicitly restrict it to staging.
Retain the Prometheus high-error-rate alert and Grafana ERROR-log panel so that
similar incidents are detected and diagnosed quickly.
