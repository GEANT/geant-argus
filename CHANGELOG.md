# Changelog

All notable changes to this project will be documented in this file.

## [0.30] - 2025-04-18
- DBOARD3-1174: add management command for sending expired blacklists email
- DBOARD3-1197: Stop backpropagating acks through alarms api
- DBOARD3-1203: show incident as Stuck when still Active 1 minute after it started clearing
- DBOARD3-1205: Add title texts to incident status badges
- DBOARD3-1207: Add link to short-lived alarms to navbar
- Support v1.36.0
  - Condensed incident list layout
  - Add timeframe dropdown to limit incident list to recent incidents
  - Some style changes
  - Use FontAwesome icons instead of unicode symbols

## [0.29] - 2025-04-18
- Promote metadata v0a5 to v1, remove support for v0a4

## [0.28] - 2025-04-02
- Update Django to 5.1
- DBOARD3-1176: Add version api endpoint

## [0.27] - 2025-03-31
- Simplify initial setup for new checkouts
- Make Severity badges more obvious
- Ack Reminder as a user preference
- Support Argus v1.34.1
- Truncate long descriptions in incident list instead of word wrapping them

## [0.26] - 2025-03-11
- Add templatediff.py for detecting important changes to tempates in argus-server
- Support Argus v1.33.0
- Support filtering by ticket ref
