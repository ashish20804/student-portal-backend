# Troubleshooting Guide for User Management

## What I Fixed
1. ✅ Added Flask-Mail imports to admin_routes.py
2. ✅ Implemented actual email sending function
3. ✅ Fixed Student model field (attendance_percentage)
4. ✅ Added validation for required fields
5. ✅ Added error logging and better error messages
6. ✅ Improved frontend error handling

## How to Test

### Method 1: Using the Frontend
1. Start Flask server: `python run.py`
2. Open browser and navigate to user management page
3. Open browser console (F12) to see logs
4. Try to add a user
5. Check console for:
   - 📤 Request payload being sent
   - 📥 Server response
   - Any error messages

### Method 2: Using the Test Script
1. Start Flask server: `python run.py`
2. Update admin credentials in `test_add_user.py`
3. Run: `python test_add_user.py`
4. Check terminal output for detailed logs

### Method 3: Check Flask Server Logs
When you submit the form, check the Flask terminal for:
- ✅ User created: [name] ([email]) - Role: [role]
- ✅ Email sent to: [email]
- ⚠️ Email failed but user created: [error]
- ❌ Error creating user: [error]

## Common Issues and Solutions

### Issue 1: "Server connection failed"
**Cause:** Backend not running or wrong URL
**Solution:** 
- Ensure Flask server is running on port 5000
- Check `BASE_URL` in user_management.js matches your server

### Issue 2: "Email already exists"
**Cause:** User with that email already in database
**Solution:** 
- Use a different email
- Or delete the existing user first

### Issue 3: "Roll number is required for students"
**Cause:** Student form submitted without roll number
**Solution:** 
- Fill in the roll number field in Step 2
- Check that roll_no is being sent in the payload

### Issue 4: Email not sending
**Cause:** Gmail SMTP issues or wrong credentials
**Solution:** 
- Check config.py has correct Gmail credentials
- Ensure "App Password" is used (not regular password)
- User will still be created, just email won't send

### Issue 5: "Access Denied: Admin role required"
**Cause:** Not logged in as admin
**Solution:** 
- Login with admin credentials
- Check JWT token is valid

### Issue 6: Database constraint error
**Cause:** Missing required fields or duplicate data
**Solution:** 
- Check all required fields are filled
- Ensure roll number is unique for students
- Check database constraints

## What to Check in Browser Console

Open browser console (F12) and look for:

```javascript
📤 Submitting user data: {
  name: "...",
  email: "...",
  password: "...",
  role: "...",
  department: "..."
}

📥 Server response: {
  message: "Faculty added successfully. Credentials sent via email."
}
```

## What to Check in Flask Terminal

Look for these logs:
```
✅ User created: Test User (test@nirmauni.ac.in) - Role: faculty
✅ Email sent to: test@nirmauni.ac.in
```

Or error messages:
```
❌ Error creating user: [specific error]
⚠️ Email failed but user created: [email error]
```

## Database Verification

Check if user was created in database:
```sql
SELECT * FROM user WHERE email = 'test@nirmauni.ac.in';
SELECT * FROM student WHERE userId = [userId];
SELECT * FROM faculty WHERE userId = [userId];
```

## Email Configuration Check

Verify in `app/config.py`:
```python
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = '22bce024@nirmauni.ac.in'
MAIL_PASSWORD = 'bkbo hflc uueh yucp'  # App password
```

## Next Steps

1. **Start the server** and try adding a user
2. **Check browser console** for request/response
3. **Check Flask terminal** for server logs
4. **Tell me the specific error** you see so I can help further

The error message will tell us exactly what's wrong:
- Frontend error → JavaScript/network issue
- Backend error → Database/validation issue
- Email error → SMTP/configuration issue
