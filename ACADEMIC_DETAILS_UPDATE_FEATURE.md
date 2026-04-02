# User Management - Academic Details Update Feature

## Changes Made

### 1. Removed Student Creation from Add User Modal
- Students now register themselves through the normal registration page
- Admin can only add Faculty and Admin users
- Added note: "Note: Students register themselves"

### 2. Added "Update Academic Details" Option for Students
- New menu item appears in the three dots dropdown ONLY for students
- Allows admin to update:
  - Roll Number
  - Program (e.g., B.Tech)
  - Semester (1-8)
  - Department
  - Last SGPA (0-10)
  - Current CGPA (0-10)
  - Attendance Percentage (0-100)

### 3. New Backend Routes

#### GET /admin/students/<user_id>/academic
- Fetches current academic details for a student
- Returns: rollNumber, program, semester, department, sgpa, cgpa, attendance_percentage

#### PUT /admin/students/<user_id>/academic
- Updates academic details for a student
- Accepts: rollNumber, program, semester, department, sgpa, cgpa, attendance_percentage
- Validates and converts data types (int for semester, float for grades)

### 4. Frontend Components

#### New Modal: Academic Details Modal
- Opens when admin clicks "Update Academic Details" for a student
- Pre-fills with current student data
- Validates input ranges (SGPA/CGPA: 0-10, Attendance: 0-100, Semester: 1-8)

#### JavaScript Functions Added:
- `openAcademicModal(user)` - Opens the modal and loads student data
- `fetchStudentAcademicData(userId)` - Fetches current academic details from backend
- `saveAcademicDetails()` - Saves updated academic details to backend

## How It Works

### Student Registration Flow:
1. Student goes to registration page
2. Student fills in basic details (name, email, password)
3. Student account is created with default academic values (0.0 CGPA, 0% attendance)
4. Welcome email is sent to student

### Admin Updates Academic Details:
1. Admin logs in and goes to User Management
2. Admin finds the student in the list
3. Admin clicks three dots → "Update Academic Details"
4. Modal opens with current student data
5. Admin updates CGPA, SGPA, attendance, etc.
6. Admin clicks "Save Academic Details"
7. Data is saved to database
8. Student can now see updated data in their dashboard

## Database Fields Updated

**Student Table:**
- `rollNumber` - Student's roll number (e.g., 22BCE024)
- `program` - Academic program (e.g., B.Tech, M.Tech)
- `semester` - Current semester (1-8)
- `department` - Department (CSE, ECE, Mechanical)
- `sgpa` - Last semester GPA (0.00-10.00)
- `cgpa` - Cumulative GPA (0.00-10.00)
- `attendance_percentage` - Attendance percentage (0-100)

## UI Changes

### Add User Modal:
- Role dropdown now only shows: Faculty, Admin
- Removed: Student option
- Added note explaining students register themselves

### User Table Actions (Three Dots Menu):
- **For All Users:**
  - Edit Access (change role and permissions)
  - Remove User (delete user)

- **For Students Only:**
  - Update Academic Details (NEW - updates CGPA, SGPA, attendance)

## Testing

### Test Adding Faculty:
1. Click "Add New User"
2. Fill in: Name, Email, Password
3. Select Role: Faculty
4. Select Department
5. Click "Create Faculty Account"
6. Check: User created, email sent

### Test Updating Student Academic Details:
1. Find a student in the user list
2. Click three dots → "Update Academic Details"
3. Update: SGPA = 8.5, CGPA = 8.3, Attendance = 85
4. Click "Save Academic Details"
5. Check: Data saved successfully
6. Login as that student and verify data shows in dashboard

## Benefits

✅ Students can self-register (reduces admin workload)
✅ Admin maintains control over academic data
✅ Separation of concerns (registration vs academic updates)
✅ Academic data is accurate and admin-verified
✅ Students can't manipulate their own grades/attendance
✅ Clean workflow for both students and admins
