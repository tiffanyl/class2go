from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from courses.common_page_data import get_common_page_data

from courses.files.forms import *
from courses.actions import auth_is_course_admin_view_wrapper

@auth_is_course_admin_view_wrapper
def upload(request):
    course_prefix = request.POST.get("course_prefix")
    course_suffix = request.POST.get("course_suffix")
    common_page_data = get_common_page_data(request, course_prefix, course_suffix)

    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES, course=common_page_data['course'])
        if form.is_valid():
            new_file = form.save(commit=False)
            new_file.course = common_page_data['course']
            new_file.index = new_file.section.getNextIndex()
            new_file.mode = 'draft'
            new_file.handle = course_prefix + "--" + course_suffix

            new_file.save()
            new_file.create_ready_instance()
            return redirect('courses.views.course_materials', course_prefix, course_suffix)
    else:
        form = FileUploadForm(course=common_page_data['course'])

    return render(request, 'files/upload.html',
            {'common_page_data': common_page_data,
             'form': form,
             })

@auth_is_course_admin_view_wrapper
def delete_file(request):
    try:
        common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    except:
        raise Http404

    file = File.objects.get(id=request.POST.get("file_id"))
    file.delete()
    file.image.delete()

    return redirect(request.META['HTTP_REFERER'])
