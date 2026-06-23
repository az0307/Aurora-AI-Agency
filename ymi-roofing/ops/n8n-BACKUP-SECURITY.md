# n8n Backup & Security Guide — Y.M.I Roofing

## BACKING UP WORKFLOWS

### Method 1: JSON Export (Recommended)
1. In n8n, open the workflow
2. Click the ⋮ menu (top right) → "Download"
3. Save the .json file to your backup folder
4. Name it: `ymi-lead-capture-YYYY-MM-DD.json`

### Method 2: Full Instance Backup
If self-hosting n8n via Docker:
```bash
# Backup the database
docker exec n8n-postgres pg_dump -U n8n n8n > n8n-backup-$(date +%Y%m%d).sql

# Backup the .n8n config folder
tar -czf n8n-config-$(date +%Y%m%d).tar.gz ~/.n8n
```

## SECURITY CHECKLIST

- [ ] Change default n8n credentials (if not using SSO)
- [ ] Enable 2FA on your n8n account
- [ ] Restrict webhook access: set `allowedOrigins` to your actual domain (not `*`)
- [ ] Store Twilio credentials in n8n "Credentials" (not hardcoded in workflows)
- [ ] Rotate Twilio Auth Token every 90 days
- [ ] Enable n8n execution logging for audit trail
- [ ] Set up n8n user roles (if multi-user)
- [ ] Backup workflows before making changes

## WEBHOOK SECURITY

### Current Setting (Development):
```json
"options": { "allowedOrigins": "*" }
```

### Production Setting:
```json
"options": { "allowedOrigins": "https://ymiroofing.com.au" }
```

If using Cloudflare Pages + custom domain, set to:
```json
"options": { "allowedOrigins": "https://ymiroofing.com.au,https://www.ymiroofing.com.au" }
```

## TROUBLESHOOTING

| Problem | Likely Cause | Fix |
|---------|-----------|-----|
| No SMS received | Twilio not connected | Check credentials in n8n |
| No sheet entry | Sheet ID wrong / no access | Verify ID, share sheet with n8n service account |
| Form submits but no response | Webhook URL wrong | Check line 883 in index.html matches n8n URL |
| CORS error in browser | allowedOrigins mismatch | Update to match actual domain |
| Duplicate leads | No dedup logic | Add phone number check before SMS node |

## MONITORING

Set up a weekly check:
1. Submit a test lead via the website
2. Verify SMS arrives within 30 seconds
3. Verify Google Sheet has new row
4. Check n8n execution log for errors
