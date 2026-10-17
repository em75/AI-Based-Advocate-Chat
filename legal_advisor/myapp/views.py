from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
import json
from .models import *
from .decorators import login_required_custom, user_login_required, advocate_login_required, admin_login_required
from django.db.models import Q
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
import datetime as dt
from django.core.mail import send_mail
from django.conf import settings
import random
from django.utils import timezone

import nltk

nltk.download("punkt")
nltk.download("wordnet")


def index(request):
    return render(request, "index.html")


def contact(request):
    return render(request, "contact.html")


# Create your views here.


def logins(request):
    if request.POST:
        email = request.POST["email"]
        passw = request.POST["password"]
        print(email)
        print(passw)
        user = authenticate(username=email, password=passw)
        print(user)

        if user is not None:
            login(request, user)
            if user.userType == "Admin":
                messages.info(request, "Login Success")
                return redirect("/admhome")
            elif user.userType == "User":
                # Clear Advocate session key if present
                if "aid" in request.session:
                    del request.session["aid"]
                
                id = user.id
                email = user.username
                request.session["uid"] = id
                request.session["email"] = email
                messages.info(request, "Login Success")
                return redirect("/user_home")
            elif user.userType == "Advocate":
                # Clear User session key if present
                if "uid" in request.session:
                    del request.session["uid"]

                id = user.id
                email = user.username
                request.session["aid"] = id
                request.session["email"] = email

                messages.info(request, "Login Success")
                return redirect("/advocatehome")
        else:
            print("Hiii")
            messages.error(request, "Invalid Username/Password")
    return render(request, "login.html")


def logout_view(request):
    """Logout function for all user types"""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have been logged out successfully.")
    return redirect("/login/")


def Userregister(request):
    current_date = datetime.today().strftime("%Y-%m-%d")
    print(current_date)
    if request.POST:
        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        dob = request.POST["dob"]
        gender = request.POST["gender"]
        address = request.POST["address"]
        ac_no = request.POST["ac_no"]
        aadhaar = request.POST["aadhaar"]
        password = request.POST["password"]
        image = request.FILES["image"]

        if Login.objects.filter(username=email).exists():
            messages.error(request, "Email is Already Exists")
            return redirect("/login")
        else:
            logUser = Login.objects.create_user(
                username=email,
                password=password,
                userType="User",
                viewPass=password,
                is_active=1,
            )
            logUser.save()

            userReg = UserRegistration.objects.create(
                name=name,
                email=email,
                phone=phone,
                gender=gender,
                address=address,
                Account_no=ac_no,
                aadhaar=aadhaar,
                dob=dob,
                loginid=logUser,
                image=image,
            )
            userReg.save()
    return render(request, "userReg.html", {"current_date": current_date})


def AdvocateReg(request):
    view=Case_Category.objects.all()
    current_date = datetime.today().strftime("%Y-%m-%d")
    print(current_date)
    if request.POST:
        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        dob = request.POST["dob"]
        gender = request.POST["gender"]
        address = request.POST["address"]
        password = request.POST["password"]
        district = request.POST["district"]
        education = request.POST["education"]
        category = request.POST["cases"]
        code = request.POST["code"]
        image = request.FILES["image"]
        files = request.FILES["files"]

        if Login.objects.filter(username=email).exists():
            messages.error(request, "Email is Already Exists")
            return redirect("/login")
        else:
            logUser = Login.objects.create_user(
                username=email,
                password=password,
                userType="Advocate",
                viewPass=password,
                is_active=0,
            )
            logUser.save()

            userReg = Advocate.objects.create(
                name=name,
                email=email,
                phone=phone,
                files=files,
                gender=gender,
                address=address,
                dob=dob,
                category=category,
                qualification=education,
                district=district,
                loginid=logUser,
                image=image,
                code=code,
            )
            userReg.save()
            return HttpResponseRedirect("/Regpay?email=" + email)
    return render(request, "AdvocateReg.html", {"current_date": current_date,"view": view})


def Regpay(request):
    emial = request.GET.get("email")
    if request.POST:
        up = Advocate.objects.filter(email=emial).update(Regfee="Paid")
        messages.info(request, "Registered Successfully")
        return redirect("/login")
    return render(request, "Regpayment.html")


@admin_login_required
def admhome(request):
    return render(request, "Admins/index.html")


@advocate_login_required
def advocatehome(request):
    return render(request, "Advocate/index.html")


@user_login_required
def userhome(request):
    return render(request, "User/index.html")


@admin_login_required
def admviewusers(request):
    view = UserRegistration.objects.all()
    return render(request, "Admins/users.html", {"view": view})


@admin_login_required
def adm_delete_user(request):
    id = request.GET.get("id")
    Login.objects.filter(id=id).delete()
    messages.info(request, "User Deleted Successfully")
    return redirect("/admviewusers")


@admin_login_required
def admviewadvocate(request):
    view = Advocate.objects.all()
    return render(request, "Admins/advocates.html", {"view": view})


@admin_login_required
def add_case_category(request):
    if request.POST:
        Category = request.POST.get("Category")
        Decsription = request.POST.get("desc")

        add = Case_Category.objects.create(Category=Category, Description=Decsription)
        add.save()
        messages.info(request, "Category Added Successfully")
    return render(request, "Admins/add_case_category.html")


@admin_login_required
def addbns_section(request):
    if request.POST:
        bns = request.POST.get("bns")
        Decsription = request.POST.get("desc")

        add = BNS_sections.objects.create(BNS=bns, Description=Decsription)
        add.save()
        messages.info(request, "BNS Sections Added Successfully")
    view = BNS_sections.objects.all()
    return render(request, "Admins/addbns_section.html", {"view": view})


@admin_login_required
def delete_bns(request):
    id = request.GET.get("id")
    BNS_sections.objects.filter(id=id).delete()
    messages.info(request, "BNS Section Deleted Successfully")
    return redirect("/addbns_section")


@user_login_required
def userview_Advocate(request):
    vie = Advocate.objects.filter(loginid__is_active=1)
    print(vie)
    return render(request, "User/advocate_view.html", {"vie": vie})


@user_login_required
def user_home(request):
    return render(request, "User/index.html")


@user_login_required
def user_add_feed(request):
    id=request.GET['id']
    uid = request.session["uid"]
    ad=Advocate.objects.get(id=id)
    Uid = UserRegistration.objects.get(loginid=uid)
    current_date = datetime.today().strftime("%Y-%m-%d")
    if request.POST:
        sub = request.POST.get("exampleForm")
        feedback = request.POST.get("feedback")

        add = Feedback.objects.create(
            sub=sub, Feedback=feedback,aid=ad ,uid=Uid,date=current_date, Type="User"
        )
        add.save()
        messages.info(request, "Feedback Successfully")
        return redirect('/userhome')
    return render(request, "User/add_feedback.html")


@user_login_required
def user_view_bns(request):
    view = BNS_sections.objects.all()
    return render(request, "User/view_bns.html", {"view": view})


@user_login_required
def user_book_case(request):
    email = request.GET.get("email")
    aid = Advocate.objects.get(email=email)
    uid = request.user.id
    Uid = UserRegistration.objects.get(loginid=uid)
    current_date = datetime.today().strftime("%Y-%m-%d")
    view = Advocate.objects.filter(email=email)
    if request.POST:
        sub = request.POST.get("sub")
        desc = request.POST.get("desc")

        add = Case_request.objects.create(
            user=Uid, advocate=aid, sub=sub, date=current_date, desc=desc
        )
        add.save()
        messages.info(request, "Request Added Successfully")
    return render(request, "User/case_book.html", {"view": view})


@user_login_required
def user_view_request(request):
    uid = request.session["uid"]
    email = request.session["email"]
    Uid = UserRegistration.objects.get(loginid=uid)
    view = Case_request.objects.filter(user__email=email)
    return render(request, "User/user_view_request.html", {"view": view})


@advocate_login_required
def adv_view_request(request):
    uid = request.session["aid"]
    Uid = Advocate.objects.get(loginid=uid)

    print("Advocate :", uid)
    view = Case_request.objects.filter(request="pending", advocate=Uid.id)
    ap = Case_request.objects.filter(request="Approved", advocate=Uid.id).exclude(status__in=["Completed", "Failed"])
    rj = Case_request.objects.filter(
        Q(request="Rejected", advocate=Uid.id) | 
        Q(request="Approved", advocate=Uid.id, status__in=["Completed", "Failed"])
    )
    return render(
        request, "Advocate/view_case_request.html", {"view": view, "ap": ap, "rj": rj}
    )


@advocate_login_required
def approve_case_request(request):
    rid = request.GET.get("id")
    approve = Case_request.objects.filter(id=rid).update(request="Approved")
    messages.info(request, "Request Accepted")
    return redirect("/adv_view_request")


@admin_login_required
def reject_case_request(request):
    rid = request.GET.get("id")
    approve = Case_request.objects.filter(id=rid).update(request="Rejected")
    messages.info(request, "Request Rejected")
    return redirect("/adm_view_request")


@admin_login_required
def approve_advocate(request):
    id = request.GET.get("id")
    approve = Login.objects.filter(id=id).update(is_active=1)
    messages.info(request, "Request Accepted")
    return redirect("/admviewadvocate")


@admin_login_required
def reject_advocate(request):
    id = request.GET.get("id")
    reject = Login.objects.filter(id=id).delete()
    messages.info(request, "Request Rejected")
    return redirect("/admviewadvocate")




@advocate_login_required
def advocate_add_feed(request):
    aid = request.session["aid"]
    aaid = Advocate.objects.get(loginid=aid)
    current_date = datetime.today().strftime("%Y-%m-%d")

    if request.POST:
        sub = request.POST.get("exampleForm")
        feedback = request.POST.get("feedback")
        uid = request.POST.get("uid")  # Get selected user from the form

        user_instance = UserRegistration.objects.get(id=uid)  # Fetch user object

        add = Feedback.objects.create(
            sub=sub,
            Feedback=feedback,
            aid=aaid,
            uid=user_instance,  # Link to corresponding user
            date=current_date,
            Type="Advocate",
        )
        add.save()
        messages.info(request, "Feedback Added Successfully")
        return redirect('/advocatehome')

    users = UserRegistration.objects.all()  # Fetch all users for selection
    return render(request, "Advocate/add_feedback.html", {"users": users})


@advocate_login_required
def view_feedback_user(request):
    aid = request.session["aid"]
    adv = Advocate.objects.get(loginid=aid)
    view = Feedback.objects.filter(aid=adv, Type="User")
    return render(request, 'Advocate/view_feedback_user.html', {'view': view})

@advocate_login_required
def adv_view_bns(request):
    view = BNS_sections.objects.all()
    return render(request, "Advocate/view_bns.html", {"view": view})


# def adv_view_approved_case(request):
#     current_date = datetime.today().strftime("%Y-%m-%d")
#     print(current_date)
#     aid = request.session["aid"]
#     aaid = Advocate.objects.get(loginid=aid)
#     rid = request.GET.get("id")
#     rrid = Case_request.objects.get(id=rid)
#     uid = request.GET.get("uid")
#     uuid = UserRegistration.objects.get(id=uid)
#     print("userid", uuid.id)
#     view = Case_request.objects.filter(request="Approved", id=rid)

#     if "files" in request.POST:
#         status = request.POST.get("status")
#         date = request.POST.get("date")
#         case = Case_request.objects.filter(id=rid).update(date=date, status=status)
#         return HttpResponse(
#             "<script>alert('Status Updated');window.location='/adv_view_request'</script>"
#         )

#     elif "Describe" in request.POST:
#         desc = request.POST.get("desc")
#         fees = request.POST.get("fees")
#         file = request.FILES["file"]
#         if Case_details.objects.filter(desc=desc, fees=fees).exists():
#             messages.success(request, "Already Exists")
#         else:
#             upload = Case_details.objects.create(
#                 desc=desc,
#                 fees=fees,
#                 rid_id=rrid.id,
#                 file=file,
#                 user_id=uuid.id,
#                 advocate_id=aaid.id,
#                 status="NotPaid",
#             )
#             upload.save()
#             messages.success(request, "Files Uploaded")
#             return HttpResponse(
#                 "<script>alert('File And Fees Uploaded');window.location='/adv_view_request'</script>"
#             )
#         # else:
#         #     messages.info(request, "Please Select Petitions from Case Request")
#     return render(
#         request, "Advocate/cases.html", {"view": view, "current_date": current_date}
#     )

@advocate_login_required
def adv_view_approved_case(request):
    current_date = datetime.today().strftime("%Y-%m-%d")
    print(current_date)
    aid = request.session["aid"]
    aaid = Advocate.objects.get(loginid=aid)
    rid = request.GET.get("id")
    rrid = Case_request.objects.get(id=rid)
    uid = request.GET.get("uid")
    uuid = UserRegistration.objects.get(id=uid)
    print("userid", uuid.id)
    view = Case_request.objects.filter(request="Approved", id=rid)

    if request.method == "POST":
        status = request.POST.get("status")
        date = request.POST.get("date")
        desc = request.POST.get("desc")
        fees = request.POST.get("fees")
        file = request.FILES.get("file")
        
        # Update case status
        Case_request.objects.filter(id=rid).update(date=date, status=status)
        
        # Send Email Notification
        try:
            subject = 'Case Status Update - AdvoBook'
            message = f'Dear {uuid.name},\n\nYour case status for "{rrid.sub}" has been updated to: {status}.\n\nAdvocate: {aaid.name}\n\nThank you for choosing AdvoBook.'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [uuid.email]
            send_mail(subject, message, email_from, recipient_list)
        except Exception as e:
            print(f"Email error: {e}")
        
        # Upload case details if provided
        if desc and fees and file:
            if not Case_details.objects.filter(desc=desc, fees=fees).exists():
                upload = Case_details.objects.create(
                    desc=desc,
                    fees=fees,
                    rid_id=rrid.id,
                    file=file,
                    user_id=uuid.id,
                    advocate_id=aaid.id,
                    status="NotPaid",
                )
                upload.save()
                messages.success(request, "Status Updated and Files Uploaded")
            else:
                messages.success(request, "Already Exists")
        else:
            messages.success(request, "Status Updated")
        
        return HttpResponse(
            "<script>alert('Operation Successful');window.location='/adv_view_request'</script>"
        )

    return render(
        request, "Advocate/cases.html", {"view": view, "current_date": current_date}
    )


@advocate_login_required
def view_payment_details(request):
    aid=request.session['aid']
    adv=Advocate.objects.get(loginid=aid)
    data=Case_details.objects.filter(advocate=adv)
    return render(request,'Advocate/view_payment_details.html',{'data':data})


@user_login_required
def user_profile(request):
    uid = request.session["uid"]
    view = UserRegistration.objects.filter(loginid=uid)

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        password = request.POST.get("password")
        image = request.FILES.get("image")

        if image:
            userid = UserRegistration.objects.get(loginid=uid)
            userid.image = image
            userid.save()

            up = UserRegistration.objects.filter(loginid=uid).update(
                name=name, email=email, phone=phone, address=address
            )

            pas_up = Login.objects.get(id=uid)
            pas_up.set_password(password)
            pas_up.viewPass = password
            pas_up.save()

            HttpResponse(
                "<script>alert('profile updated');window.location='/user_profile'</script>"
            )

        else:
            up = UserRegistration.objects.filter(loginid=uid).update(
                name=name, email=email, phone=phone, address=address
            )

            pas_up = Login.objects.get(id=uid)
            pas_up.set_password(password)
            pas_up.viewPass = password
            pas_up.save()

            HttpResponse(
                "<script>alert('profile updated');window.location='/user_profile'</script>"
            )

    return render(request, "User/profile.html", {"view": view})


@user_login_required
def user_case_files(request):
    rid = request.GET.get('rid')
    view = Case_details.objects.filter(rid_id=rid)
    return render(request, "User/user_case_files.html", {"view": view})


def chat(request):
    import chatgui

    return redirect("/")


@user_login_required
def payment_page(request):
    amut = request.GET.get("amt")
    cid = request.GET.get("cid")

    if request.POST:
        up = Case_details.objects.filter(id=cid, status="NotPaid").update(
            status="Paid"
        )
        return redirect("/Applied_success")
    return render(request, "User/payment_page.html", {"amount": amut})


@user_login_required
def payment_view(request):
    uid = request.session["uid"]
    view = Case_details.objects.filter(user=uid)
    return render(request, "User/payment_details.html", {"view": view})


def Applied_success(request):
    return render(request, "User/Applied_success.html")


@user_login_required
def userchat(request):
    uid = request.session["uid"]
    Uid = UserRegistration.objects.get(loginid=uid)
    # Artists
    name = ""
    pimage = ""
    note_content = ""
    aid = request.GET.get("aid")
    email = request.GET.get("email")
    
    # Filter only advocates that the user has a relationship (Case Request) with
    artistData = Advocate.objects.filter(case_request__user=Uid).distinct()
    
    getChatData = Chat.objects.filter(Q(uid=Uid) & Q(Advo__email=email))
    print("getChatData ", getChatData)
    current_time = datetime.now().time()
    formatted_time = current_time.strftime("%H:%M")
    userid = UserRegistration.objects.get(loginid__id=uid)
    
    if aid:
        # Security Check: Ensure the user has a request with this advocate
        if not Case_request.objects.filter(user=Uid, advocate__email=email).exists():
             return redirect('/userchat')
             
        advocate_id = Advocate.objects.get(email=email)
        name = advocate_id.name
        pimage = advocate_id.image
        
        # Load existing notes for this advocate-user pair (Shared with Advocate)
        note_obj, created = CaseNote.objects.get_or_create(advocate=advocate_id, user=userid)
        note_content = note_obj.content

    if request.POST:
        message = request.POST.get("message", "")
        attached_file = request.FILES.get("file", None)
        sendMsg = Chat.objects.create(
            uid=userid,
            message=message,
            file=attached_file,
            Advo=advocate_id,
            time=formatted_time,
            utype="USER",
        )
        sendMsg.save()
    return render(
        request,
        "User/chat.html",
        {
            "artistData": artistData,
            "getChatData": getChatData,
            "artistid": name,
            "image": pimage,
            "note_content": note_content,
            "email": email,
        },
    )


@advocate_login_required
def reply(request):
    email = request.session["email"]
    uid = request.session["aid"]
    Aid = Advocate.objects.get(loginid=uid)
    print(uid)
    name = ""
    pimage = ""
    note_content = ""
    
    # Filter only users who have sent a request to this advocate
    userData = UserRegistration.objects.filter(case_request__advocate=Aid).distinct()
    
    id = request.GET.get("uid")
    uemail = request.GET.get("email")
    print("User Details :", id)
    
    if id:
        # Security Check: Ensure the advocate has a request from this user
        if not Case_request.objects.filter(advocate=Aid, user__loginid=id).exists():
            return redirect('/reply')
            
        UserId = UserRegistration.objects.get(email=uemail)
    getChatData = Chat.objects.filter(Q(Advo__loginid=uid) & Q(uid__email=uemail))
    print("HELLO", getChatData)
    current_time = datetime.now().time()
    formatted_time = current_time.strftime("%H:%M")
    advo_id = Advocate.objects.get(email=email)
    advo = advo_id.id
    if id:
        userid = UserRegistration.objects.get(loginid=id)
        name = userid.name
        pimage = userid.image
        print("userid : ", userid)
        print("name : ", name)
        print("image : ", pimage)
        # Load existing notes for this advocate-user pair
        note_obj, created = CaseNote.objects.get_or_create(advocate=Aid, user=userid)
        note_content = note_obj.content
    if request.POST:
        message = request.POST.get("message", "")
        attached_file = request.FILES.get("file", None)
        sendMsg = Chat.objects.create(
            uid=userid,
            message=message,
            file=attached_file,
            Advo_id=advo,
            time=formatted_time,
            utype="ADVOCATE",
        )
        sendMsg.save()
    return render(
        request,
        "Advocate/chat.html",
        {
            "userData": userData,
            "getChatData": getChatData,
            "userid": name,
            "image": pimage,
            "note_content": note_content,
            "user_email": uemail,
        },
    )


@admin_login_required
def admviewfeedback(request):
    view = Feedback.objects.all()
    return render(request, "Admins/view_feedback.html", {"view": view})


def udp(request):
    dele = Login.objects.filter(id=9).update(is_active=1)
    return HttpResponse("deleted")


@admin_login_required
def delete_feedback(request):
    fid = request.GET.get("fid")
    if fid:
        dele = Feedback.objects.filter(id=fid).delete()
        return HttpResponse(
            "<script>alert('Feedback Deleted');window.location='/admviewfeedback';</script>"
        )


@user_login_required
def add_rating(request):
    uid = request.session.get("uid")
    Uid = UserRegistration.objects.get(loginid=uid)
    aid = request.GET.get("aid")
    email = request.GET.get("email")
    Aid = Advocate.objects.get(loginid=aid)
    rid = request.GET.get("rid")
    Rid = Case_request.objects.get(id=rid)

    if request.method == "POST":
        rating = request.POST.get("rating")
        if Rating.objects.filter(uid=Uid).exists():
            return HttpResponse(
                "<script>alert('Rating Already Added');window.location='/user_view_request';</script>"
            )
        else:
            add = Rating.objects.create(aid=Aid, rid=Rid, rating=rating, uid=Uid)
            add.save()
            ratings = Rating.objects.filter(aid=Aid)
            total_ratings = ratings.count()
            if total_ratings > 0:
                total_sum = sum(r.rating for r in ratings)
                avg_rating = total_sum / total_ratings
                print("totalSum: ", total_sum)
                print("Avg.rating: ", avg_rating)
                update = Advocate.objects.filter(email=email).update(
                    advo_rating=avg_rating
                )
                return HttpResponse(
                    "<script>alert('Rating Added');window.location='/user_view_request';</script>"
                )

    return render(request, "User/add_rating.html")





@user_login_required
def view_feedback_advocate(request):
    view = Feedback.objects.filter(Type="User")
    return render(request, 'User/view_feedback_advocate.html', {'view': view})


@user_login_required
def user_view_my_feedback(request):
    uid = request.session["uid"]
    uu = UserRegistration.objects.get(loginid=uid)
    view = Feedback.objects.filter(uid=uu, Type="User")
    return render(request, 'User/user_my_feedback.html', {'view': view})


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def save_note(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email_param = data.get("user_email") # This is the OTHER person's email
        content = data.get("content", "")
        
        if "aid" in request.session:
            # Advocate is saving a note for a User
            aid = request.session["aid"]
            advocate = Advocate.objects.get(loginid=aid)
            user = UserRegistration.objects.get(email=email_param)
        else:
            return JsonResponse({"status": "unauthorized"}, status=401)
            
        note, created = CaseNote.objects.get_or_create(advocate=advocate, user=user)
        note.content = content
        note.save()
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)

def forgot_password_request(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if not email:
            messages.error(request, "Please enter your email.")
            return render(request, "forgot_password_request.html")

        # Use __iexact for case-insensitive lookup
        if Login.objects.filter(username__iexact=email).exists():
            user_obj = Login.objects.get(username__iexact=email)
            actual_email = user_obj.username # Get the primary email/username
            
            # Generate 6-digit OTP
            otp = str(random.randint(100000, 999999))
            # Delete any existing OTPs for children of this actual_email
            OTPModel.objects.filter(email=actual_email).delete()
            # Save new OTP
            OTPModel.objects.create(email=actual_email, otp=otp)
            
            # Send Email
            try:
                subject = 'Password Reset OTP'
                message = f'Your 6-digit OTP for password reset is: {otp}. It will expire in 10 minutes.'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [actual_email]
                print(f"DEBUG: Attempting to send OTP {otp} to {actual_email}")
                send_mail(subject, message, email_from, recipient_list, fail_silently=False)
                
                request.session['reset_email'] = actual_email
                messages.info(request, "OTP has been sent to your email.")
                return redirect('/verify_otp/')
            except Exception as e:
                print(f"Mail sending error: {e}")
                messages.error(request, "Failed to send email. Please check your connection or contact support.")
        else:
            messages.error(request, "This email address is not registered with us.")
    return render(request, "forgot_password_request.html")

def verify_otp(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('/forgot_password_request/')
        
    if request.method == "POST":
        otp_entered = request.POST.get("otp")
        try:
            otp_record = OTPModel.objects.get(email=email, otp=otp_entered)
            if not otp_record.is_expired():
                request.session['otp_verified'] = True
                return redirect('/reset_password/')
            else:
                messages.error(request, "OTP has expired. Please request a new one.")
                return redirect('/forgot_password_request/')
        except OTPModel.DoesNotExist:
            messages.error(request, "Invalid OTP.")
            
    return render(request, "otp_verification.html", {"email": email})

def reset_password(request):
    email = request.session.get('reset_email')
    if not email or not request.session.get('otp_verified'):
        return redirect('/forgot_password_request/')
        
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        
        if new_password == confirm_password:
            user = Login.objects.get(username=email)
            user.set_password(new_password)
            user.viewPass = new_password
            user.save()
            
            # Clean up
            OTPModel.objects.filter(email=email).delete()
            del request.session['reset_email']
            del request.session['otp_verified']
            
            messages.success(request, "Password reset successfully. Please login with your new password.")
            return redirect('/login/')
        else:
            messages.error(request, "Passwords do not match.")
            
    return render(request, "reset_password.html")






from django.shortcuts import render
from openai import OpenAI

def ai_case_prediction(request):
    answer = ""

    if request.method == "POST":
        user_question = request.POST.get("question")
        prompt = f"Analyze this legal case and predict outcome (WIN/LOSS) with confidence score and reasoning: {user_question}"

        client = OpenAI(
            api_key="GROQ_API_KEY",
            base_url="https://api.groq.com/openai/v1"
        )

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        answer = response.choices[0].message.content
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
             return JsonResponse({"answer": answer})

    return render(request, "User/ai_case_prediction.html", {
        "answer": answer
    })