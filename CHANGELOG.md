# Changelog
**Repository:** `IRIS-data-pipeline`
**Description:** `Tracks all notable changes, version history, and roadmap toward 1.0.0 following Semantic Versioning.`
**SPDX-License-Identifier:** OGL-UK-3.0
All notable changes to this repository will be documented in this file.
This project follows **Semantic Versioning (SemVer)** ([semver.org](https://semver.org/)), using the format:
 `[MAJOR].[MINOR].[PATCH]`
 - **MAJOR** (`X.0.0`) – Incompatible API/feature changes that break backward compatibility.
 - **MINOR** (`0.X.0`) – Backward-compatible new features, enhancements, or functionality changes.
 - **PATCH** (`0.0.X`) – Backward-compatible bug fixes, security updates, or minor corrections.
 - **Pre-release versions** – Use suffixes such as `-alpha`, `-beta`, `-rc.1` (e.g., `2.1.0-beta.1`).
 - **Build metadata** – If needed, use `+build` (e.g., `2.1.0+20250314`).

 ---

 ## [0.90.0] – 2025-03-28

 ### Initial Public Release (Pre-Stable)

 This is the first public release of this repository under NDTP's open-source governance model.
 Since this release is **pre-1.0.0**, changes may still occur that are **not fully backward-compatible**.

 #### Initial Features
 - View a choropleth map, summarising average EPC ratings per ward
 - Search for a property via address
 - Filter properties based on EPC rating, building type, postcode, drawn area and flagged status
 - Filter properties based on further attributes (roof type, insulation type etc)
 - View details (roof type, EPC rating, insulation type etc) of properties
 - Download details of properties
 - Flag a property to signal it's under investigation
 - Unflagging a property with a rationale
 - Viewing the reason why a property was unflagged

 #### Known Limitations
 - Some components are subject to change before `1.0.0`.
 - APIs may evolve based on partner feedback and internal testing.

 ---

 ## Future Roadmap to `1.0.0`

 The `0.90.x` series is part of NDTP’s **pre-stable development cycle**, meaning:
 - **Minor versions (`0.91.0`, `0.92.0`...) introduce features and improvements** leading to a stable `1.0.0`.
 - **Patch versions (`0.90.1`, `0.90.2`...) contain only bug fixes and security updates**.
 - **Backward compatibility is NOT guaranteed until `1.0.0`**, though NDTP aims to minimise breaking changes.

 Once `1.0.0` is reached, future versions will follow **strict SemVer rules**.