# Changelog

All notable changes to this project will be documented in this file.

## [0.37] - 2025-06-27
- DBOARD3-1264: Add Earliest start time
  
## [0.36] - 2025-06-16
- Supporting argus version 2.0.0
  
## [0.34] - 2025-06-04
- DBOARD3-1150: Add close alarm button along bottom bar of incident table
- DBOARD3-1113: Support differentiating users with and users without write permission
- DBOARD3-1239: Limit access to blacklists to those with permissions and source systems
- DBOARD3-1223: Move quick glance close button to top of modal

## [0.33] - 2025-05-15
- DBOARD3-1211: Validate ticket ref updates to be a positive integer
- DBOARD3-1167: Prevent selecting pending incidents for (bulk) update
- DBOARD3-1228: update stuck alarms title text message

## [0.32] - 2025-04-24
- DBOARD3-1209: Add bulk action for updating ticket ref
- Add --full flag to templatediff to show diffs and add documentation

## [0.31] - 2025-04-23
- set default grace period to 5 minutes and make configurable
- add title text to stuck alarm warning triangle
- revert incident list to normal size

## [0.30] - 2025-04-22
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
