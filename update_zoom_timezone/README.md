# Script: update\_zoom\_timezone.py

## Purpose
Updates the timezone of Zoom users based on a provided CSV file.

## Usage
```bash
python update_zoom_timezone/update_zoom_timezone.py users.csv
```

## CSV Format
| email | timezone |
|---|---|
| user1@example.com | America/Montreal |
| user2@example.com | Europe/London |

## Output
- Logs success or failure for each user.
- Displays updated timezones.

## Dependencies
- requests

## Example
See the examples/sample_users.csv file for input format.