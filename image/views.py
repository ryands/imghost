import os
import hashlib
import urllib2
import tempfile
import shutil

from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
# App specific imports
from image.models import Image
from image.base62 import base62
import settings

def image_handler(files, request):
    tmp = tempfile.mkstemp()
    md5 = hashlib.md5()
    orig = files.name
    fext = orig[orig.rfind('.')+1:]
    f = os.fdopen(tmp[0], "wb+")
    for chunk in files.chunks():
        f.write(chunk)
        md5.update(chunk)
    f.close()

    img = Image()
    try:
        next_id = Image.objects.order_by('-id')[0].id + 1
    except IndexError:
        next_id = settings.IMAGE_ID_OFFSET + 1

    img.id = next_id
    img.base62 = base62(next_id)
    img.filename = base62(next_id) + "." + fext.lower()
    img.orig_filename = orig
    img.type = '' # todo
    img.description = '' # not implemented yet.
    img.uploader = request.user
    img.md5sum = md5.hexdigest()
    image_file = os.path.join(settings.MEDIA_ROOT,img.filename)
    thumbnail = os.path.join(settings.MEDIA_ROOT, 'thumbs', img.filename)

    try:
        img.save()
    except IntegrityError, e:
        os.unlink(tmp[1]) # delete the uploaded file if it already exists
        return HttpResponseRedirect( settings.MEDIA_URL + Image.objects.get(md5sum=img.md5sum).filename)
    shutil.move(tmp[1], image_file)
    os.system("/usr/bin/convert %s -thumbnail 150x150 %s" % (image_file, thumbnail))

@login_required
def upload(request):
    fileCount = 0
    if request.method == 'GET':
        return render_to_response('upload.html', {'url': request.GET.get('url', ''),}, context_instance=RequestContext(request))
    elif request.method == 'POST':
        if request.POST['upload_type'] == 'file':
            for files in request.FILES.getlist('upload_file'):
                image_handler(files, request)
                fileCount += 1
        elif request.POST['upload_type'] == 'url':
            remote_image = urllib2.urlopen(request.POST['upload_url'])
            data = remote_image.read()
            md5.update(data)
            fext = request.POST['upload_url'][-3:]
            orig = request.POST['upload_url']
            
            f = os.fdopen(tmp[0], "wb+")
            f.write(data)
            f.close()
    return render_to_response('list_images.html',
            {'images': Image.objects.order_by('-id')[:fileCount],
             'settings': settings},
             context_instance=RequestContext(request))

@login_required
def view_image(request, id):
    return render_to_response('view_image.html', 
        { 'image': Image.objects.get(base62=id), 
          'settings':settings},
        context_instance=RequestContext(request))

@login_required
def list_images(request, page=0):
    return render_to_response('list_images.html', 
            { 'page':page, 
              'images': Image.objects.order_by('id'), 
              'settings': settings},
            context_instance=RequestContext(request))

@login_required
def user_images(request, user=None):
    if user == None:
        user = request.user
    else:
        user = User.objects.get(username=user)
    
    return render_to_response('list_images.html',
        {'images': Image.objects.filter(uploader=user), 'settings':settings,}, context_instance=RequestContext(request))
