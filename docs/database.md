# Database Design

## Users

| Field | Type |
|---------|---------|
| id | UUID |
| name | VARCHAR |
| email | VARCHAR |
| password_hash | TEXT |
| created_at | TIMESTAMP |

## Websites

| Field | Type |
|---------|---------|
| id | UUID |
| user_id | UUID |
| domain | VARCHAR |
| verified | BOOLEAN |
| created_at | TIMESTAMP |

## Scans

| Field | Type |
|---------|---------|
| id | UUID |
| website_id | UUID |
| status | VARCHAR |
| started_at | TIMESTAMP |
| completed_at | TIMESTAMP |

## Findings

| Field | Type |
|---------|---------|
| id | UUID |
| scan_id | UUID |
| severity | VARCHAR |
| title | VARCHAR |
| description | TEXT |
| recommendation | TEXT |

## Reports

| Field | Type |
|---------|---------|
| id | UUID |
| scan_id | UUID |
| security_score | INTEGER |
| summary | TEXT |
| generated_at | TIMESTAMP |
