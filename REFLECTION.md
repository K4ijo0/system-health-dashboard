# Individual Reflection

## 1. Continuous Delivery and Continuous Deployment

Continuous Delivery means that every change is automatically built, tested,
and made ready for production, but a person approves the production release.
Continuous Deployment goes one step further by deploying every change to
production automatically when all checks pass. My project uses Continuous
Delivery because Jenkins deploys the release to staging, runs smoke tests,
checks Prometheus, and then waits for approval before production. This gives
the team an opportunity to review the change and the evidence before it
affects the live environment.

For a payment service, I would initially choose Continuous Delivery. Payments
are high risk, and an approval gate provides an additional change-control
point for checking migrations, security impact, monitoring coverage, and
rollback readiness. The automated tests and staging deployment still make the
process fast and repeatable. To convert this workflow to Continuous
Deployment, I would remove the Jenkins `input` approval step and allow the
validated release to deploy automatically to production. I would only make
that change after adding stronger automated checks, canary deployment, and
clear rollback criteria.

## 2. Most useful metric or log during the incident

The quickest high-level insight during the incident came from the
`SystemHealthHighErrorRate` Prometheus alert. It showed that the staging
environment had more than five percent HTTP 5xx responses for the required
period. This immediately indicated that the service was responding, but many
requests were failing. The Grafana ERROR log then provided the quickest detail
about why the failures occurred. It showed a JSON event with
`level=ERROR`, the message `Simulated application fault`, the
`/simulate-error` endpoint, HTTP status `500`, and `environment=staging`.

The metric identified the size and impact of the problem, while the log
identified the endpoint and cause. The main thing missing from the application
logs was a request or correlation ID. A correlation ID would be useful if one
user request passed through several services and produced several log lines.
The logs could also include the application version and container ID to make
release comparison easier. For this small project, the existing fields were
enough to diagnose the deliberately injected fault quickly.

## 3. How metrics and logs complement each other

Metrics and logs answer different operational questions. Metrics are
aggregated numerical measurements that are efficient for dashboards, trends,
and alerts. In this project, Prometheus collects `http_requests_total`,
`http_request_duration_seconds`, and `app_info`. These metrics showed whether
the staging and production services were up, how many requests were failing,
and how latency was changing. They allowed the high-error-rate alert to detect
the incident without someone reading every request.

Logs provide the detailed context behind a metric change. Promtail collected
the application JSON logs and sent them to Loki, where Grafana could filter
them by environment and log level. During the incident, the error-rate metric
showed that staging was unhealthy, while the ERROR log showed that
`/simulate-error` returned HTTP 500 and recorded the message `Simulated
application fault`.

Together, the two data types support a useful workflow: metrics detect and
measure the problem, then logs explain the individual events that caused it.
Metrics are better for alerting; logs are better for investigation and
diagnosis.

## 4. Alert threshold to tune before production

The threshold I would tune before going live is the `HighErrorRate` rule,
which currently fires when more than five percent of requests return HTTP 5xx
responses for two minutes. The threshold is understandable for this project,
but a five percent rate can be noisy for a service with very low traffic. For
example, one failed request out of ten could trigger the alert even though
the sample is too small to represent a real service-wide problem.

I would add a minimum request-rate condition or use a longer evaluation window
for low-volume periods. I would also compare the threshold with the normal
baseline for each endpoint. A lower threshold detects incidents earlier but
can create alert fatigue. A higher threshold reduces noise but may miss a
slowly developing customer-impacting problem. The trade-off is therefore
between false positives and missed incidents. I would begin with a warning
alert at five percent and a critical alert at a higher level or after a longer
duration. I would review the alert history after deployment and adjust it
using real traffic rather than choosing a value only from the test scenario.

## 5. Remaining manual step and how to reduce its risk

The remaining manual step is the production approval in Jenkins. Staging is
deployed automatically, but the `main` pipeline pauses after the staging smoke
tests and Prometheus verification. A person must approve the same release
image before Jenkins deploys it to production. This is useful for a high-risk
service because it provides a final review point, but it also adds waiting
time and can become a bottleneck if the approver is unavailable.

I would reduce the risk by making the approval decision evidence-based. The
approval screen should link to the staging test result, image tag, dashboard,
alert status, change ticket, and rollback tag. I would also define an approved
change window and a backup approver. Over time, low-risk changes could use
automated policy checks, while high-risk changes would continue to require a
person. Canary deployment would further reduce risk by sending a small amount
of production traffic to the new image before full rollout. The approval gate
would remain for sensitive changes, but the surrounding automation would make
the decision faster, clearer, and safer.
