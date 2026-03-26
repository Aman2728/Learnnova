from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Assignment, AssignmentSubmission
from apps.courses.models import Course
from apps.users.models import User   # ✅ IMPORTANT
from .models import AssignmentSubmission


# ✅ CREATE ASSIGNMENT (FILE + LINK)
@csrf_exempt
def create_assignment(request):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        teacher_id = request.POST.get("teacher_id")
        course_id = request.POST.get("course_id")

        if not teacher_id:
            return JsonResponse({"error": "Teacher ID required"}, status=400)

        if not course_id:
            return JsonResponse({"error": "Course ID required"}, status=400)

        teacher = User.objects.get(id=teacher_id)
        course = Course.objects.get(id=course_id)

        assignment = Assignment.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            language=request.POST.get('language'),
            due_date=request.POST.get('due_date'),
            course=course,
            teacher=teacher,
            link=request.POST.get('link'),
            file=request.FILES.get('file')
        )

        return JsonResponse({
            "message": "Assignment created successfully"
        })

    except Exception as e:
        print("ERROR:", e)
        return JsonResponse({"error": str(e)}, status=500)


# ✅ TEACHER ASSIGNMENTS
@csrf_exempt
def teacher_assignments(request):

    if request.method != "GET":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        teacher_id = request.GET.get("teacher_id")

        if not teacher_id:
            return JsonResponse({"error": "Teacher ID required"}, status=400)

        assignments = Assignment.objects.filter(teacher_id=teacher_id)

        data = []

        for a in assignments:

            # ✅ GET SUBMISSIONS FOR THIS ASSIGNMENT
            submissions = AssignmentSubmission.objects.filter(assignment=a)

            submission_data = []

            for s in submissions:
                student = User.objects.get(id=s.student_id)

                submission_data.append({
                    "student_name": student.username,
                    "file": s.file.url if s.file else None
                })

            data.append({
                "id": a.id,
                "title": a.title,
                "language": a.language,
                "due_date": a.due_date,
                "file": a.file.url if a.file else None,
                "link": a.link,
                "total_submissions": submissions.count(),   # ✅ count
                "submissions": submission_data              # ✅ list
            })

        return JsonResponse({
            "assignments": data
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
# ✅ STUDENT ASSIGNMENTS
@csrf_exempt
def student_assignments(request):

    if request.method != "GET":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        student_id = request.GET.get("student_id")

        if not student_id:
            return JsonResponse({"error": "Student ID required"}, status=400)

        student = User.objects.get(id=student_id)

        if student.role != "student":
            return JsonResponse({"error": "Unauthorized"}, status=403)

        # courses where student enrolled
        courses = Course.objects.filter(students=student)

        assignments = Assignment.objects.filter(course__in=courses)

        data = []

        # ✅ LOOP FIXED
        for a in assignments:

            # ✅ CHECK IF STUDENT SUBMITTED
            submitted = AssignmentSubmission.objects.filter(
                assignment_id=a.id,
                student_id=student.id
            ).exists()

            data.append({
                "id": a.id,
                "title": a.title,
                "description": a.description,
                "due_date": a.due_date,
                "course": a.course.title,
                "teacher": a.teacher.username,
                "file": a.file.url if a.file else None,
                "link": a.link,
                "submitted": submitted
            })

        return JsonResponse({
            "assignments": data
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ✅ SUBMIT ASSIGNMENT
@csrf_exempt
def submit_assignment(request):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        assignment_id = request.POST.get("assignment_id")
        student_id = request.POST.get("student_id")
        file = request.FILES.get("file")

        if not assignment_id or not student_id:
            return JsonResponse({"error": "Missing data"}, status=400)

        if not file:
            return JsonResponse({"error": "File is required"}, status=400)

        # ✅ check already submitted
        existing = AssignmentSubmission.objects.filter(
            assignment_id=assignment_id,
            student_id=student_id
        ).first()

        if existing:
            # 🔁 update file instead of creating new
            existing.file = file
            existing.save()

            return JsonResponse({
                "message": "Assignment updated successfully"
            })

        # ✅ new submission
        AssignmentSubmission.objects.create(
            assignment_id=assignment_id,
            student_id=student_id,
            file=file
        )

        return JsonResponse({
            "message": "Assignment submitted successfully"
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



@csrf_exempt
def assignment_submissions(request):

    if request.method != "GET":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        assignment_id = request.GET.get("assignment_id")

        if not assignment_id:
            return JsonResponse({"error": "Assignment ID required"}, status=400)

        submissions = AssignmentSubmission.objects.filter(assignment_id=assignment_id)

        data = []

        for s in submissions:
            student = User.objects.get(id=s.student_id)

            data.append({
                "student": student.username,
                "file": s.file.url if s.file else None
            })

        return JsonResponse({
            "submissions": data
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)