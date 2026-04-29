# Zoom Script Library

A collection of independent Python scripts that extend Zoom's admin portal capabilities in managing a Zoom environment.

> **Note**
>
> The following repository is a personal, open-source project shared by the app creator and not an officially supported Zoom Communications, Inc. sample application. Zoom Communications, Inc., its employees and affiliates are not responsible for the use and maintenance of this application. Please use these sample scripts for inspiration, exploration and experimentation at your own risk and enjoyment. You may reach out to the app creator and broader Zoom Developer community on https://devforum.zoom.us/ for technical discussion and assistance, but understand there is no service level agreement support for this application. Thank you and happy coding!

## 📋 List of Available Scripts
1. [**add\_sso**](add_sso) — Bulk add the SSO login method to Zoom users.
2. [**add\_user\_to\_group**](add_user_to_group) — Bulk add Zoom users to groups.
3. [**download\_transcripts**](download_transcripts) — Bulk download transcripts from multiple Zoom Meetings.
4. [**list\_users**](list_users) — Fetch and export all active Zoom users.
5. [**update\_zoom\_timezone**](update_zoom_timezone) — Bulk update Zoom user timezones.
6. [**zoom\_user\_export**](zoom_user_export) — Fetch and export login types for all Zoom users.
7. [**zprec**](zprec) — Bulk export call recordings from Zoom Phone for a specific date range.

## 📁 Structure
Each script lives in its own folder, with:
- A `README.md` describing usage and purpose.
- The Python script files.
- Optional `/examples` folder containing example input files.

## ⚙️ Installation
```bash
git clone https://github.com/ericlosier/zoom-script-library.git
cd zoom-script-library
pip install -r requirements.txt
```

## 📚 Creating a Zoom Server‐to‐Server OAuth App
Full instructions can be found in [**this Wiki page**](https://github.com/ericlosier/zoom-script-library/wiki/Creating-a-Zoom-Server%E2%80%90to%E2%80%90Server-OAuth-App).

## ⚖️ License
MIT License